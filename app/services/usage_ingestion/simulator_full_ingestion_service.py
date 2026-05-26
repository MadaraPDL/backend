from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.device_network_policy import DeviceNetworkPolicy
from app.models.router import Router
from app.services.alerts import generate_policy_failed_alert_for_policy
from app.services.usage_ingestion.simulator_device_service import (
    SimulatorDeviceIngestionResult,
    run_simulator_device_ingestion_for_router,
)
from app.core.simulator_scenarios import (
    DEFAULT_SIMULATOR_SCENARIO,
    SimulatorScenario,
)
from app.services.usage_ingestion.simulator_usage_service import (
    SimulatorUsageIngestionResult,
    run_simulator_usage_ingestion_for_router,
)


@dataclass(frozen=True)
class SimulatorFullIngestionResult:
    device_ingestion: SimulatorDeviceIngestionResult
    usage_ingestion: SimulatorUsageIngestionResult
    scenario: SimulatorScenario
    policy_failure_alert_created: bool = False


async def _create_policy_failure_scenario_alert(
    *,
    db: AsyncSession,
    router_id: UUID,
) -> bool:
    router_result = await db.execute(
        select(Router).where(Router.id == router_id)
    )
    router = router_result.scalar_one_or_none()

    if router is None or router.user_subscription_id is None:
        return False

    device_result = await db.execute(
        select(Device)
        .where(
            Device.router_id == router_id,
            Device.status == "connected",
        )
        .order_by(Device.updated_at.desc())
        .limit(1)
    )
    device = device_result.scalar_one_or_none()

    if device is None:
        return False

    policy = DeviceNetworkPolicy(
        device_id=device.id,
        router_id=router_id,
        requested_by_user_id=device.user_id,
        policy_type="bandwidth_limit",
        bandwidth_limit_mbps=Decimal("1"),
        download_limit_mbps=Decimal("1"),
        upload_limit_mbps=Decimal("1"),
        status="failed",
        failure_reason=(
            "Simulator policy failure scenario: router rejected the bandwidth rule."
        ),
        is_active=False,
    )
    policy.router = router

    db.add(policy)
    await db.flush()

    return await generate_policy_failed_alert_for_policy(
        db=db,
        policy=policy,
    )


async def run_full_simulator_ingestion_for_router(
    db: AsyncSession,
    router_id: UUID,
    isp_id: UUID | None = None,
    record_start: datetime | None = None,
    record_end: datetime | None = None,
    scenario: SimulatorScenario = DEFAULT_SIMULATOR_SCENARIO,
) -> SimulatorFullIngestionResult:
    device_result = await run_simulator_device_ingestion_for_router(
        db=db,
        router_id=router_id,
        isp_id=isp_id,
        scenario=scenario,
    )

    usage_result = await run_simulator_usage_ingestion_for_router(
        db=db,
        router_id=router_id,
        isp_id=isp_id,
        record_start=record_start,
        record_end=record_end,
        scenario=scenario,
    )
    policy_failure_alert_created = False

    if scenario == "policy_failure":
        policy_failure_alert_created = await _create_policy_failure_scenario_alert(
            db=db,
            router_id=router_id,
        )

    return SimulatorFullIngestionResult(
        device_ingestion=device_result,
        usage_ingestion=usage_result,
        scenario=scenario,
        policy_failure_alert_created=policy_failure_alert_created,
    )
