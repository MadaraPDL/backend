from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.device import Device
from app.models.device_network_policy import DeviceNetworkPolicy
from app.schemas.app_user import MyDevicePolicyCreate


async def list_my_device_policies(
    *,
    db: AsyncSession,
    current_user: AppUser,
    device_id: UUID | None = None,
    status: str | None = None,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[DeviceNetworkPolicy]:
    stmt = (
        select(DeviceNetworkPolicy)
        .where(DeviceNetworkPolicy.requested_by_user_id == current_user.id)
        .order_by(DeviceNetworkPolicy.requested_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if device_id is not None:
        stmt = stmt.where(DeviceNetworkPolicy.device_id == device_id)

    if status is not None:
        stmt = stmt.where(DeviceNetworkPolicy.status == status)

    if is_active is not None:
        stmt = stmt.where(DeviceNetworkPolicy.is_active == is_active)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_device_policy(
    *,
    db: AsyncSession,
    current_user: AppUser,
    policy_id: UUID,
) -> DeviceNetworkPolicy | None:
    stmt = select(DeviceNetworkPolicy).where(
        DeviceNetworkPolicy.id == policy_id,
        DeviceNetworkPolicy.requested_by_user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def _resolve_directional_limits(
    data: MyDevicePolicyCreate,
) -> tuple[Decimal | None, Decimal | None, Decimal | None]:
    download_limit = data.download_limit_mbps or data.bandwidth_limit_mbps
    upload_limit = data.upload_limit_mbps or data.bandwidth_limit_mbps

    legacy_limit = data.bandwidth_limit_mbps
    if legacy_limit is None and download_limit is not None and download_limit == upload_limit:
        legacy_limit = download_limit

    return legacy_limit, download_limit, upload_limit


async def deactivate_my_device_policy(
    *,
    db: AsyncSession,
    current_user: AppUser,
    policy_id: UUID,
) -> DeviceNetworkPolicy | None:
    policy = await get_my_device_policy(
        db=db,
        current_user=current_user,
        policy_id=policy_id,
    )

    if policy is None:
        return None

    policy.is_active = False
    policy.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(policy)

    return policy


async def create_my_device_policy(
    *,
    db: AsyncSession,
    current_user: AppUser,
    data: MyDevicePolicyCreate,
) -> DeviceNetworkPolicy | None:
    device_stmt = select(Device).where(
        Device.id == data.device_id,
        Device.user_id == current_user.id,
    )
    device_result = await db.execute(device_stmt)
    device = device_result.scalar_one_or_none()

    if device is None:
        return None

    legacy_limit, download_limit, upload_limit = _resolve_directional_limits(data)
    now = datetime.now(UTC)

    active_policy_result = await db.execute(
        select(DeviceNetworkPolicy).where(
            DeviceNetworkPolicy.device_id == device.id,
            DeviceNetworkPolicy.requested_by_user_id == current_user.id,
            DeviceNetworkPolicy.policy_type == data.policy_type,
            DeviceNetworkPolicy.is_active.is_(True),
        )
    )

    for active_policy in active_policy_result.scalars().all():
        active_policy.is_active = False
        active_policy.updated_at = now

    policy = DeviceNetworkPolicy(
        device_id=device.id,
        router_id=device.router_id,
        requested_by_user_id=current_user.id,
        policy_type=data.policy_type,
        bandwidth_limit_mbps=legacy_limit,
        download_limit_mbps=download_limit,
        upload_limit_mbps=upload_limit,
        priority_level=(
            5 if data.policy_type == "device_priority" else data.priority_level
        ),
    )

    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    return policy
