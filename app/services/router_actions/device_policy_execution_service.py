from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device_network_policy import DeviceNetworkPolicy
from app.models.router_action_log import RouterActionLog
from app.router_adapters import RouterActionResult, get_router_adapter


POLICY_STATUS_PENDING = "pending"
POLICY_STATUS_APPLIED = "applied"
POLICY_STATUS_FAILED = "failed"

ACTION_TYPE_BANDWIDTH_LIMIT = "bandwidth_limit"
ACTION_TYPE_DEVICE_PRIORITY = "device_priority"

ACTION_STATUS_SUCCESS = "success"
ACTION_STATUS_FAILED = "failed"


async def get_device_policy_for_execution(
    *,
    db: AsyncSession,
    policy_id: UUID,
) -> DeviceNetworkPolicy | None:
    stmt = (
        select(DeviceNetworkPolicy)
        .options(
            selectinload(DeviceNetworkPolicy.device),
            selectinload(DeviceNetworkPolicy.router),
        )
        .where(DeviceNetworkPolicy.id == policy_id)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def _build_command_payload(policy: DeviceNetworkPolicy) -> dict:
    return {
        "policy_id": str(policy.id),
        "policy_type": policy.policy_type,
        "router_id": str(policy.router_id),
        "device_id": str(policy.device_id),
        "bandwidth_limit_mbps": (
            str(policy.bandwidth_limit_mbps)
            if policy.bandwidth_limit_mbps is not None
            else None
        ),
        "priority_level": policy.priority_level,
    }


def _failed_result(
    *,
    action_type: str,
    message: str,
) -> RouterActionResult:
    return RouterActionResult(
        success=False,
        action_type=action_type,
        status=ACTION_STATUS_FAILED,
        message=message,
        error_message=message,
    )


async def _execute_policy_with_adapter(
    *,
    policy: DeviceNetworkPolicy,
) -> RouterActionResult:
    router = policy.router
    device = policy.device
    adapter = get_router_adapter(router)
    capabilities = adapter.get_capabilities(router)

    if policy.policy_type == ACTION_TYPE_BANDWIDTH_LIMIT:
        if not capabilities.can_apply_bandwidth_limit:
            return _failed_result(
                action_type=ACTION_TYPE_BANDWIDTH_LIMIT,
                message="Router does not support bandwidth limits.",
            )

        if policy.bandwidth_limit_mbps is None:
            return _failed_result(
                action_type=ACTION_TYPE_BANDWIDTH_LIMIT,
                message="Bandwidth limit policy requires bandwidth_limit_mbps.",
            )

        return await adapter.apply_bandwidth_limit(
            router=router,
            device=device,
            limit_mbps=policy.bandwidth_limit_mbps,
        )

    if policy.policy_type == ACTION_TYPE_DEVICE_PRIORITY:
        if not capabilities.can_apply_device_priority:
            return _failed_result(
                action_type=ACTION_TYPE_DEVICE_PRIORITY,
                message="Router does not support device priority.",
            )

        if policy.priority_level is None:
            return _failed_result(
                action_type=ACTION_TYPE_DEVICE_PRIORITY,
                message="Device priority policy requires priority_level.",
            )

        return await adapter.apply_device_priority(
            router=router,
            device=device,
            priority_level=policy.priority_level,
        )

    return _failed_result(
        action_type=policy.policy_type,
        message=f"Unsupported device policy type: {policy.policy_type}",
    )


async def execute_device_network_policy(
    *,
    db: AsyncSession,
    policy_id: UUID,
) -> tuple[DeviceNetworkPolicy | None, RouterActionLog | None]:
    policy = await get_device_policy_for_execution(
        db=db,
        policy_id=policy_id,
    )

    if policy is None:
        return None, None

    if policy.status != POLICY_STATUS_PENDING:
        return policy, None

    result = await _execute_policy_with_adapter(policy=policy)
    now = datetime.now(UTC)

    action_log = RouterActionLog(
        router_id=policy.router_id,
        policy_id=policy.id,
        action_type=result.action_type,
        command_payload=_build_command_payload(policy),
        response_payload=result.response_payload,
        status=result.status,
        error_message=result.error_message,
        executed_at=now,
    )

    if result.success:
        policy.status = POLICY_STATUS_APPLIED
        policy.applied_at = now
        policy.failure_reason = None
    else:
        policy.status = POLICY_STATUS_FAILED
        policy.failure_reason = result.error_message or result.message

    policy.updated_at = now

    db.add(action_log)
    await db.commit()
    await db.refresh(policy)
    await db.refresh(action_log)

    return policy, action_log
