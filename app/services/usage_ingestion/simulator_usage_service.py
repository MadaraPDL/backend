from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
import random
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.models.device import Device
from app.models.router import Router
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription
from app.services.isp_admin.ownership_scope import apply_router_isp_ownership_scope
from app.core.simulator_scenarios import (
    DEFAULT_SIMULATOR_SCENARIO,
    SimulatorScenario,
)


MB_PER_GB = Decimal("1024")
PLAN_TARGET_SCENARIOS: dict[SimulatorScenario, Decimal] = {
    "high_usage": Decimal("0.85"),
    "near_plan_limit": Decimal("0.95"),
    "exceeded_plan": Decimal("1.05"),
}
UNTRUSTED_DEVICE_POLICY_ALERT_REPEAT_WINDOW_HOURS = 24


@dataclass(frozen=True)
class SimulatorUsageIngestionResult:
    router_id: UUID
    user_id: UUID
    user_subscription_id: UUID
    record_start: datetime
    record_end: datetime
    records_created: int
    upload_mb: Decimal
    download_mb: Decimal
    total_mb: Decimal
    blocked_devices: int = 0
    policy_alerts_created: int = 0


class UsageIngestionError(RuntimeError):
    """Base error for usage ingestion failures."""


class RouterNotFoundForIngestionError(UsageIngestionError):
    """Raised when the router does not exist or is outside the allowed ISP scope."""


class RouterNotReadyForIngestionError(UsageIngestionError):
    """Raised when a router cannot be used for usage ingestion."""


def _decimal_mb(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))


def _usage_total_expression():
    return func.coalesce(
        UsageRecord.total_mb,
        UsageRecord.upload_mb + UsageRecord.download_mb,
    )


def _countable_usage_filter():
    return or_(
        UsageRecord.source.is_(None),
        UsageRecord.source != "simulator_estimated_device",
    )


def _decimal_or_zero(value: object) -> Decimal:
    if value is None:
        return Decimal("0")

    return Decimal(str(value))


def _split_total_usage(
    *,
    total_mb: Decimal,
    record_count: int,
    scenario: SimulatorScenario,
) -> list[tuple[Decimal, Decimal]]:
    safe_record_count = max(record_count, 1)

    if scenario == "heavy_device_usage" and safe_record_count > 1:
        weights = [Decimal("0.68")]
        remaining_weight = Decimal("0.32")
        tail_weights = [
            Decimal(str(random.uniform(0.6, 1.4)))
            for _ in range(safe_record_count - 1)
        ]
        tail_total = sum(tail_weights, Decimal("0"))
        weights.extend(
            (weight / tail_total) * remaining_weight for weight in tail_weights
        )
    else:
        raw_weights = [
            Decimal(str(random.uniform(0.75, 1.35)))
            for _ in range(safe_record_count)
        ]
        raw_total = sum(raw_weights, Decimal("0"))
        weights = [weight / raw_total for weight in raw_weights]

    amounts: list[tuple[Decimal, Decimal]] = []

    for index, weight in enumerate(weights):
        device_total = (total_mb * weight).quantize(Decimal("0.01"))
        upload_ratio = Decimal(str(random.uniform(0.08, 0.22)))

        if scenario == "heavy_device_usage" and index == 0:
            upload_ratio = Decimal(str(random.uniform(0.04, 0.10)))

        upload_mb = (device_total * upload_ratio).quantize(Decimal("0.01"))
        download_mb = max(device_total - upload_mb, Decimal("0.01"))
        amounts.append((upload_mb, download_mb))

    return amounts


def _default_total_usage_mb(
    *,
    scenario: SimulatorScenario,
    record_count: int,
) -> Decimal:
    safe_record_count = max(record_count, 1)

    if scenario == "heavy_device_usage":
        return _decimal_mb(random.uniform(450, 1200) * safe_record_count)

    if scenario == "high_usage":
        return _decimal_mb(random.uniform(900, 2500) * safe_record_count)

    if scenario == "near_plan_limit":
        return _decimal_mb(random.uniform(1200, 3200) * safe_record_count)

    if scenario == "exceeded_plan":
        return _decimal_mb(random.uniform(1800, 4500) * safe_record_count)

    return _decimal_mb(random.uniform(70, 260) * safe_record_count)


async def _get_cycle_usage_mb(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    cycle_start: datetime,
) -> Decimal:
    result = await db.execute(
        select(func.coalesce(func.sum(_usage_total_expression()), 0)).where(
            UsageRecord.user_subscription_id == user_subscription_id,
            UsageRecord.record_start >= cycle_start,
            _countable_usage_filter(),
        )
    )

    return _decimal_or_zero(result.scalar_one_or_none())


async def _untrusted_device_policy_alert_exists(
    *,
    db: AsyncSession,
    user_subscription: UserSubscription,
    device: Device,
    since_created_at: datetime,
) -> bool:
    stmt = (
        select(Alert.id)
        .where(
            Alert.user_id == user_subscription.user_id,
            Alert.user_subscription_id == user_subscription.id,
            Alert.device_id == device.id,
            Alert.alert_type == "policy_failed",
            Alert.title == "Untrusted device usage blocked",
            or_(
                Alert.status == "unread",
                Alert.created_at >= since_created_at,
            ),
        )
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def _add_untrusted_device_policy_alerts(
    *,
    db: AsyncSession,
    router: Router,
    user_subscription: UserSubscription,
    devices: list[Device],
) -> int:
    alerts_created = 0
    repeat_window_start = datetime.now(timezone.utc) - timedelta(
        hours=UNTRUSTED_DEVICE_POLICY_ALERT_REPEAT_WINDOW_HOURS,
    )

    for device in devices:
        if await _untrusted_device_policy_alert_exists(
            db=db,
            user_subscription=user_subscription,
            device=device,
            since_created_at=repeat_window_start,
        ):
            continue

        device_label = device.device_name or device.mac_address

        db.add(
            Alert(
                user_id=user_subscription.user_id,
                user_subscription_id=user_subscription.id,
                device_id=device.id,
                alert_type="policy_failed",
                severity="high",
                title="Untrusted device usage blocked",
                message=(
                    "PulseFi blocked simulated usage for "
                    f"{device_label} because the device is not trusted."
                ),
                status="unread",
            )
        )

        alerts_created += 1

    return alerts_created


async def _scenario_total_usage_mb(
    *,
    db: AsyncSession,
    user_subscription,
    scenario: SimulatorScenario,
    record_count: int,
) -> Decimal:
    plan = user_subscription.plan

    if scenario not in PLAN_TARGET_SCENARIOS or plan is None:
        return _default_total_usage_mb(
            scenario=scenario,
            record_count=record_count,
        )

    plan_limit_mb = Decimal(str(plan.data_limit_gb)) * MB_PER_GB

    if plan_limit_mb <= 0:
        return _default_total_usage_mb(
            scenario=scenario,
            record_count=record_count,
        )

    cycle_start = datetime.combine(
        user_subscription.start_date,
        time.min,
        tzinfo=timezone.utc,
    )
    existing_usage_mb = await _get_cycle_usage_mb(
        db=db,
        user_subscription_id=user_subscription.id,
        cycle_start=cycle_start,
    )
    target_usage_mb = (plan_limit_mb * PLAN_TARGET_SCENARIOS[scenario]).quantize(
        Decimal("0.01")
    )
    minimum_increment_mb = (
        plan_limit_mb * Decimal(str(random.uniform(0.02, 0.05)))
    ).quantize(Decimal("0.01"))

    return max(target_usage_mb - existing_usage_mb, minimum_increment_mb)


async def run_simulator_usage_ingestion_for_router(
    db: AsyncSession,
    router_id: UUID,
    isp_id: UUID | None = None,
    record_start: datetime | None = None,
    record_end: datetime | None = None,
    scenario: SimulatorScenario = DEFAULT_SIMULATOR_SCENARIO,
) -> SimulatorUsageIngestionResult:
    now = datetime.now(timezone.utc)
    final_record_end = record_end or now
    final_record_start = record_start or (final_record_end - timedelta(hours=1))

    if final_record_start >= final_record_end:
        raise RouterNotReadyForIngestionError(
            "record_start must be before record_end."
        )

    stmt = (
        select(Router)
        .options(
            selectinload(Router.user_subscription).selectinload(
                UserSubscription.plan
            )
        )
        .where(Router.id == router_id)
    )

    if isp_id is not None:
        stmt = apply_router_isp_ownership_scope(stmt, isp_id=isp_id)

    result = await db.execute(stmt)
    router = result.scalar_one_or_none()

    if router is None:
        raise RouterNotFoundForIngestionError("Router not found.")

    if router.status != "active":
        raise RouterNotReadyForIngestionError(
            "Only active routers can ingest simulator usage."
        )

    if router.user_subscription is None:
        raise RouterNotReadyForIngestionError(
            "Router must be linked to a user subscription before usage ingestion."
        )

    user_subscription = router.user_subscription

    if user_subscription.status != "active":
        raise RouterNotReadyForIngestionError(
            "Router subscription must be active before usage ingestion."
        )

    if record_start is None and scenario in PLAN_TARGET_SCENARIOS:
        cycle_start = datetime.combine(
            user_subscription.start_date,
            time.min,
            tzinfo=timezone.utc,
        )

        if cycle_start < final_record_end:
            final_record_start = cycle_start

    if final_record_start >= final_record_end:
        raise RouterNotReadyForIngestionError(
            "record_start must be before record_end."
        )

    device_stmt = (
        select(Device)
        .where(
            Device.router_id == router.id,
            Device.user_id == user_subscription.user_id,
            Device.status == "connected",
        )
        .order_by(Device.updated_at.desc())
    )

    device_result = await db.execute(device_stmt)
    devices = list(device_result.scalars().all())

    total_upload_mb = Decimal("0")
    total_download_mb = Decimal("0")
    records_created = 0

    trusted_devices = [device for device in devices if device.is_trusted]
    blocked_devices = [device for device in devices if not device.is_trusted]
    policy_alerts_created = await _add_untrusted_device_policy_alerts(
        db=db,
        router=router,
        user_subscription=user_subscription,
        devices=blocked_devices,
    )

    record_count = max(len(trusted_devices), 1)
    total_usage_mb = await _scenario_total_usage_mb(
        db=db,
        user_subscription=user_subscription,
        scenario=scenario,
        record_count=record_count,
    )
    usage_amounts = _split_total_usage(
        total_mb=total_usage_mb,
        record_count=record_count,
        scenario=scenario,
    )

    if trusted_devices:
        for index, device in enumerate(trusted_devices):
            upload_mb, download_mb = usage_amounts[index]

            db.add(
                UsageRecord(
                    user_id=user_subscription.user_id,
                    user_subscription_id=user_subscription.id,
                    router_id=router.id,
                    device_id=device.id,
                    upload_mb=upload_mb,
                    download_mb=download_mb,
                    record_start=final_record_start,
                    record_end=final_record_end,
                    source="simulator_estimated_device",
                )
            )

            total_upload_mb += upload_mb
            total_download_mb += download_mb
            records_created += 1

        # Demo clarity:
        # device_id=None represents the official router/subscription total.
        # Device rows remain available as estimated per-device breakdown.
        db.add(
            UsageRecord(
                user_id=user_subscription.user_id,
                user_subscription_id=user_subscription.id,
                router_id=router.id,
                device_id=None,
                upload_mb=total_upload_mb,
                download_mb=total_download_mb,
                record_start=final_record_start,
                record_end=final_record_end,
                source="simulator_official_total",
            )
        )
        records_created += 1
    elif not devices:
        upload_mb, download_mb = usage_amounts[0]

        db.add(
            UsageRecord(
                user_id=user_subscription.user_id,
                user_subscription_id=user_subscription.id,
                router_id=router.id,
                device_id=None,
                upload_mb=upload_mb,
                download_mb=download_mb,
                record_start=final_record_start,
                record_end=final_record_end,
                source="simulator",
            )
        )

        total_upload_mb += upload_mb
        total_download_mb += download_mb
        records_created += 1

    await db.flush()

    return SimulatorUsageIngestionResult(
        router_id=router.id,
        user_id=user_subscription.user_id,
        user_subscription_id=user_subscription.id,
        record_start=final_record_start,
        record_end=final_record_end,
        records_created=records_created,
        upload_mb=total_upload_mb,
        download_mb=total_download_mb,
        total_mb=total_upload_mb + total_download_mb,
        blocked_devices=len(blocked_devices),
        policy_alerts_created=policy_alerts_created,
    )
