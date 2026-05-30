from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.models.device import Device
from app.models.device_connection_log import DeviceConnectionLog
from app.models.device_network_policy import DeviceNetworkPolicy
from app.models.router import Router
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription
from app.services.notifications import (
    notify_new_device_push,
    notify_usage_alert_push,
)


WARNING_USAGE_PERCENT = Decimal("50")
HIGH_USAGE_PERCENT = Decimal("80")
PLAN_EXCEEDED_PERCENT = Decimal("100")
RAPID_HIGH_USAGE_24H_GB = Decimal("5")
RAPID_HIGH_USAGE_1H_GB = Decimal("2")
RAPID_HIGH_USAGE_INGESTION_WINDOW_GB = Decimal("2")
RAPID_HIGH_USAGE_INGESTION_WINDOW_MINUTES = 10
RAPID_HIGH_USAGE_SINGLE_UPDATE_GB = Decimal("2")
UNUSUAL_USAGE_MULTIPLIER = Decimal("3")
MIN_PREVIOUS_WINDOWS_FOR_ANOMALY = 3
MIN_UNUSUAL_USAGE_MB = Decimal("100")
MB_PER_GB = Decimal("1024")
PLAN_ALERT_REPEAT_WINDOW_HOURS = 24
RAPID_ALERT_REPEAT_WINDOW_MINUTES = 30


@dataclass(frozen=True)
class AlertGenerationResult:
    alerts_created: int
    usage_alerts_created: int = 0
    new_device_alerts_created: int = 0
    high_usage_alert_created: bool = False
    plan_exceed_alert_created: bool = False
    unusual_consumption_alert_created: bool = False


def _decimal_or_zero(value: object) -> Decimal:
    if value is None:
        return Decimal("0")

    return Decimal(str(value))


def _usage_total_expression():
    return func.coalesce(
        UsageRecord.total_mb,
        UsageRecord.upload_mb + UsageRecord.download_mb,
    )


def _format_decimal(value: Decimal, places: str = "0.01") -> str:
    return str(value.quantize(Decimal(places)))


async def _open_alert_exists(
    *,
    db: AsyncSession,
    user_id: UUID,
    user_subscription_id: UUID,
    alert_type: str,
    connection_log_id: UUID | None = None,
    title: str | None = None,
    since_created_at: datetime | None = None,
) -> bool:
    stmt = (
        select(Alert.id)
        .where(
            Alert.user_id == user_id,
            Alert.user_subscription_id == user_subscription_id,
            Alert.alert_type == alert_type,
            Alert.status == "unread",
        )
        .limit(1)
    )

    if connection_log_id is not None:
        stmt = stmt.where(Alert.connection_log_id == connection_log_id)

    if title is not None:
        stmt = stmt.where(Alert.title == title)

    if since_created_at is not None:
        stmt = stmt.where(Alert.created_at >= since_created_at)

    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def _get_latest_usage_id(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    record_start: datetime | None = None,
    record_end: datetime | None = None,
) -> UUID | None:
    stmt = select(UsageRecord.id).where(
        UsageRecord.user_subscription_id == user_subscription_id,
    )

    if record_start is not None:
        stmt = stmt.where(UsageRecord.record_start == record_start)

    if record_end is not None:
        stmt = stmt.where(UsageRecord.record_end == record_end)

    stmt = stmt.order_by(UsageRecord.created_at.desc()).limit(1)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_latest_window_total_mb(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    record_start: datetime | None,
    record_end: datetime | None,
) -> Decimal | None:
    if record_start is None or record_end is None:
        return None

    total_expr = _usage_total_expression()

    stmt = select(func.coalesce(func.sum(total_expr), 0)).where(
        UsageRecord.user_subscription_id == user_subscription_id,
        UsageRecord.record_start == record_start,
        UsageRecord.record_end == record_end,
    )

    result = await db.execute(stmt)
    return _decimal_or_zero(result.scalar_one_or_none())




async def _get_recent_ingestion_total_mb(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    since_created_at: datetime,
) -> Decimal:
    total_expr = _usage_total_expression()

    stmt = select(func.coalesce(func.sum(total_expr), 0)).where(
        UsageRecord.user_subscription_id == user_subscription_id,
        UsageRecord.created_at >= since_created_at,
    )

    result = await db.execute(stmt)
    return _decimal_or_zero(result.scalar_one_or_none())


async def _get_recent_usage_total_mb(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    since_record_start: datetime,
) -> Decimal:
    total_expr = _usage_total_expression()

    stmt = select(func.coalesce(func.sum(total_expr), 0)).where(
        UsageRecord.user_subscription_id == user_subscription_id,
        UsageRecord.record_start >= since_record_start,
    )

    result = await db.execute(stmt)
    return _decimal_or_zero(result.scalar_one_or_none())


async def _get_previous_window_totals_mb(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    before_record_start: datetime,
    limit: int = 10,
) -> list[Decimal]:
    total_expr = _usage_total_expression()

    stmt = (
        select(
            UsageRecord.record_start,
            UsageRecord.record_end,
            func.coalesce(func.sum(total_expr), 0).label("total_mb"),
        )
        .where(
            UsageRecord.user_subscription_id == user_subscription_id,
            UsageRecord.record_end <= before_record_start,
        )
        .group_by(UsageRecord.record_start, UsageRecord.record_end)
        .order_by(UsageRecord.record_end.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    return [_decimal_or_zero(row.total_mb) for row in result.all()]


async def generate_usage_alerts_for_subscription(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    latest_record_start: datetime | None = None,
    latest_record_end: datetime | None = None,
) -> AlertGenerationResult:
    subscription_stmt = (
        select(UserSubscription)
        .options(selectinload(UserSubscription.plan))
        .where(UserSubscription.id == user_subscription_id)
    )

    subscription_result = await db.execute(subscription_stmt)
    subscription = subscription_result.scalar_one_or_none()

    if subscription is None:
        return AlertGenerationResult(alerts_created=0)

    if subscription.status != "active":
        return AlertGenerationResult(alerts_created=0)

    plan = subscription.plan
    plan_limit_mb = plan.data_limit_gb * MB_PER_GB

    if plan_limit_mb <= 0:
        return AlertGenerationResult(alerts_created=0)

    alerts_created = 0
    high_usage_created = False
    plan_exceed_created = False
    unusual_consumption_created = False

    cycle_start = datetime.combine(
        subscription.start_date,
        time.min,
        tzinfo=timezone.utc,
    )

    total_expr = _usage_total_expression()

    cycle_usage_stmt = select(func.coalesce(func.sum(total_expr), 0)).where(
        UsageRecord.user_subscription_id == subscription.id,
        UsageRecord.record_start >= cycle_start,
    )

    cycle_usage_result = await db.execute(cycle_usage_stmt)
    used_mb = _decimal_or_zero(cycle_usage_result.scalar_one_or_none())

    usage_percent = (used_mb / plan_limit_mb) * Decimal("100")
    latest_usage_id = await _get_latest_usage_id(
        db=db,
        user_subscription_id=subscription.id,
        record_start=latest_record_start,
        record_end=latest_record_end,
    )

    if usage_percent >= WARNING_USAGE_PERCENT:
        if usage_percent >= PLAN_EXCEEDED_PERCENT:
            alert_type = "plan_exceed_risk"
            severity = "critical"
            title = "Plan usage limit reached"
        elif usage_percent >= HIGH_USAGE_PERCENT:
            alert_type = "high_usage"
            severity = "high"
            title = "High internet usage"
        else:
            alert_type = "high_usage"
            severity = "medium"
            title = "Usage warning"

        plan_alert_window_start = datetime.now(timezone.utc) - timedelta(
            hours=PLAN_ALERT_REPEAT_WINDOW_HOURS,
        )

        if not await _open_alert_exists(
            db=db,
            user_id=subscription.user_id,
            user_subscription_id=subscription.id,
            alert_type=alert_type,
            title=title,
            since_created_at=plan_alert_window_start,
        ):
            used_gb = used_mb / MB_PER_GB

            db.add(
                Alert(
                    user_id=subscription.user_id,
                    user_subscription_id=subscription.id,
                    usage_id=latest_usage_id,
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    message=(
                        f"You have used about {_format_decimal(used_gb)} GB, "
                        f"which is {_format_decimal(usage_percent, '0.1')}% "
                        f"of your {plan.data_limit_gb} GB plan."
                    ),
                    status="unread",
                )
            )

            alerts_created += 1
            high_usage_created = title == "High internet usage"
            plan_exceed_created = title == "Plan usage limit reached"

    latest_window_total_mb = await _get_latest_window_total_mb(
        db=db,
        user_subscription_id=subscription.id,
        record_start=latest_record_start,
        record_end=latest_record_end,
    )


    if alerts_created == 0 and latest_record_end is not None:
        rapid_reason_total_mb = Decimal("0")
        rapid_threshold_mb = RAPID_HIGH_USAGE_24H_GB * MB_PER_GB
        rapid_window_label = "recent usage"

        # 1) Multiple records created very recently.
        # This catches repeated simulator/ingestion runs in a few minutes.
        recent_ingestion_start = datetime.now(timezone.utc) - timedelta(
            minutes=RAPID_HIGH_USAGE_INGESTION_WINDOW_MINUTES,
        )
        recent_ingestion_total_mb = await _get_recent_ingestion_total_mb(
            db=db,
            user_subscription_id=subscription.id,
            since_created_at=recent_ingestion_start,
        )
        recent_ingestion_threshold_mb = (
            RAPID_HIGH_USAGE_INGESTION_WINDOW_GB * MB_PER_GB
        )

        if recent_ingestion_total_mb >= recent_ingestion_threshold_mb:
            rapid_reason_total_mb = recent_ingestion_total_mb
            rapid_threshold_mb = recent_ingestion_threshold_mb
            rapid_window_label = (
                f"the last {RAPID_HIGH_USAGE_INGESTION_WINDOW_MINUTES} minutes"
            )

        # 2) One latest usage update is large enough by itself.
        if latest_window_total_mb is not None:
            single_update_threshold_mb = RAPID_HIGH_USAGE_SINGLE_UPDATE_GB * MB_PER_GB

            if (
                latest_window_total_mb >= single_update_threshold_mb
                and latest_window_total_mb >= rapid_reason_total_mb
            ):
                rapid_reason_total_mb = latest_window_total_mb
                rapid_threshold_mb = single_update_threshold_mb
                rapid_window_label = "one new usage update"

        # 3) The latest usage window represents about one hour and is high.
        if (
            latest_window_total_mb is not None
            and latest_record_start is not None
            and latest_record_end is not None
        ):
            window_seconds = max(
                (latest_record_end - latest_record_start).total_seconds(),
                0,
            )
            window_hours = (
                Decimal(str(window_seconds)) / Decimal("3600")
                if window_seconds > 0
                else Decimal("0")
            )

            one_hour_threshold_mb = RAPID_HIGH_USAGE_1H_GB * MB_PER_GB

            if (
                window_hours > 0
                and window_hours <= Decimal("1.25")
                and latest_window_total_mb >= one_hour_threshold_mb
                and latest_window_total_mb >= rapid_reason_total_mb
            ):
                rapid_reason_total_mb = latest_window_total_mb
                rapid_threshold_mb = one_hour_threshold_mb
                rapid_window_label = "about one hour"

        # 4) Rolling 24-hour usage is high.
        recent_24h_start = latest_record_end - timedelta(hours=24)
        recent_24h_total_mb = await _get_recent_usage_total_mb(
            db=db,
            user_subscription_id=subscription.id,
            since_record_start=recent_24h_start,
        )
        recent_24h_threshold_mb = RAPID_HIGH_USAGE_24H_GB * MB_PER_GB

        if (
            recent_24h_total_mb >= recent_24h_threshold_mb
            and recent_24h_total_mb >= rapid_reason_total_mb
        ):
            rapid_reason_total_mb = recent_24h_total_mb
            rapid_threshold_mb = recent_24h_threshold_mb
            rapid_window_label = "the last 24 hours"

        if rapid_reason_total_mb >= rapid_threshold_mb:
            rapid_alert_window_start = datetime.now(timezone.utc) - timedelta(
                minutes=RAPID_ALERT_REPEAT_WINDOW_MINUTES,
            )

            if not await _open_alert_exists(
                db=db,
                user_id=subscription.user_id,
                user_subscription_id=subscription.id,
                alert_type="high_usage",
                title="Rapid high internet usage",
                since_created_at=rapid_alert_window_start,
            ):
                recent_total_gb = rapid_reason_total_mb / MB_PER_GB
                threshold_gb = rapid_threshold_mb / MB_PER_GB

                db.add(
                    Alert(
                        user_id=subscription.user_id,
                        user_subscription_id=subscription.id,
                        usage_id=latest_usage_id,
                        alert_type="high_usage",
                        severity="high",
                        title="Rapid high internet usage",
                        message=(
                            f"You used about {_format_decimal(recent_total_gb)} GB in "
                            f"{rapid_window_label}. This is above the rapid usage "
                            f"threshold of about {_format_decimal(threshold_gb)} GB."
                        ),
                        status="unread",
                    )
                )

                alerts_created += 1
                high_usage_created = True

    if alerts_created == 0 and latest_window_total_mb is not None and latest_record_start is not None:
        previous_totals = await _get_previous_window_totals_mb(
            db=db,
            user_subscription_id=subscription.id,
            before_record_start=latest_record_start,
        )

        if len(previous_totals) >= MIN_PREVIOUS_WINDOWS_FOR_ANOMALY:
            previous_average = sum(previous_totals, Decimal("0")) / Decimal(
                str(len(previous_totals))
            )

            unusual_threshold = previous_average * UNUSUAL_USAGE_MULTIPLIER

            if (
                previous_average > 0
                and latest_window_total_mb >= unusual_threshold
                and latest_window_total_mb >= MIN_UNUSUAL_USAGE_MB
            ):
                if not await _open_alert_exists(
                    db=db,
                    user_id=subscription.user_id,
                    user_subscription_id=subscription.id,
                    alert_type="unusual_consumption",
                ):
                    db.add(
                        Alert(
                            user_id=subscription.user_id,
                            user_subscription_id=subscription.id,
                            usage_id=latest_usage_id,
                            alert_type="unusual_consumption",
                            severity="high",
                            title="Unusual internet consumption",
                            message=(
                                "Your latest usage period is much higher than "
                                f"your recent average. Latest usage was "
                                f"{_format_decimal(latest_window_total_mb)} MB, "
                                f"while your recent average was "
                                f"{_format_decimal(previous_average)} MB."
                            ),
                            status="unread",
                        )
                    )

                    alerts_created += 1
                    unusual_consumption_created = True

    if alerts_created:
        await db.flush()

    return AlertGenerationResult(
        alerts_created=alerts_created,
        usage_alerts_created=alerts_created,
        high_usage_alert_created=high_usage_created,
        plan_exceed_alert_created=plan_exceed_created,
        unusual_consumption_alert_created=unusual_consumption_created,
    )


async def generate_new_device_alerts_for_router(
    *,
    db: AsyncSession,
    router_id: UUID,
    event_start: datetime,
) -> AlertGenerationResult:
    stmt = (
        select(DeviceConnectionLog, Device, Router)
        .join(Device, Device.id == DeviceConnectionLog.device_id)
        .join(Router, Router.id == DeviceConnectionLog.router_id)
        .where(
            DeviceConnectionLog.router_id == router_id,
            DeviceConnectionLog.event_time >= event_start,
            DeviceConnectionLog.details == "Simulator discovered new connected device.",
            Router.user_subscription_id.is_not(None),
        )
        .order_by(DeviceConnectionLog.event_time.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return AlertGenerationResult(alerts_created=0)

    first_connection_log, first_device, router = rows[0]

    if router.user_subscription_id is None:
        return AlertGenerationResult(alerts_created=0)

    if await _open_alert_exists(
        db=db,
        user_id=first_device.user_id,
        user_subscription_id=router.user_subscription_id,
        alert_type="new_device_connected",
        title="New device connected",
        since_created_at=event_start,
    ):
        return AlertGenerationResult(alerts_created=0)

    device_names: list[str] = []

    for _, device, _ in rows:
        device_name = device.device_name or "Unknown device"

        if device_name not in device_names:
            device_names.append(device_name)

    visible_names = ", ".join(device_names[:3])
    extra_count = max(len(device_names) - 3, 0)

    if len(device_names) == 1:
        message = f"{visible_names} connected to your router."
    elif extra_count:
        message = (
            f"{len(device_names)} new devices connected to your router: "
            f"{visible_names}, and {extra_count} more."
        )
    else:
        message = (
            f"{len(device_names)} new devices connected to your router: "
            f"{visible_names}."
        )

    db.add(
        Alert(
            user_id=first_device.user_id,
            user_subscription_id=router.user_subscription_id,
            device_id=first_device.id,
            connection_log_id=first_connection_log.id,
            alert_type="new_device_connected",
            severity="medium",
            title="New device connected",
            message=message,
            status="unread",
        )
    )

    await db.flush()

    return AlertGenerationResult(
        alerts_created=1,
        new_device_alerts_created=1,
    )


async def generate_alerts_after_router_ingestion(
    *,
    db: AsyncSession,
    router_id: UUID,
    latest_record_start: datetime | None = None,
    latest_record_end: datetime | None = None,
    device_event_start: datetime | None = None,
    include_new_device_alerts: bool = False,
) -> AlertGenerationResult:
    router_stmt = select(Router).where(Router.id == router_id)
    router_result = await db.execute(router_stmt)
    router = router_result.scalar_one_or_none()

    if router is None or router.user_subscription_id is None:
        return AlertGenerationResult(alerts_created=0)

    usage_result = await generate_usage_alerts_for_subscription(
        db=db,
        user_subscription_id=router.user_subscription_id,
        latest_record_start=latest_record_start,
        latest_record_end=latest_record_end,
    )

    new_device_result = AlertGenerationResult(alerts_created=0)

    if include_new_device_alerts and device_event_start is not None:
        new_device_result = await generate_new_device_alerts_for_router(
            db=db,
            router_id=router.id,
            event_start=device_event_start,
        )

    combined_result = AlertGenerationResult(
        alerts_created=usage_result.alerts_created + new_device_result.alerts_created,
        usage_alerts_created=usage_result.usage_alerts_created,
        new_device_alerts_created=new_device_result.new_device_alerts_created,
        high_usage_alert_created=usage_result.high_usage_alert_created,
        plan_exceed_alert_created=usage_result.plan_exceed_alert_created,
        unusual_consumption_alert_created=usage_result.unusual_consumption_alert_created,
    )

    if combined_result.alerts_created:
        subscription_result = await db.execute(
            select(UserSubscription).where(
                UserSubscription.id == router.user_subscription_id
            )
        )
        subscription = subscription_result.scalar_one_or_none()

        if subscription is not None:
            if combined_result.plan_exceed_alert_created:
                await notify_usage_alert_push(
                    db=db,
                    user_id=subscription.user_id,
                    alert_kind="plan_exceed",
                )
            elif combined_result.high_usage_alert_created:
                await notify_usage_alert_push(
                    db=db,
                    user_id=subscription.user_id,
                    alert_kind="high_usage",
                )

            if combined_result.new_device_alerts_created:
                await notify_new_device_push(
                    db=db,
                    user_id=subscription.user_id,
                )

    return combined_result


async def generate_policy_failed_alert_for_policy(
    *,
    db: AsyncSession,
    policy: DeviceNetworkPolicy,
) -> bool:
    router = policy.router

    if router is None:
        return False

    if router.user_subscription_id is None:
        return False

    user_id = policy.requested_by_user_id
    user_subscription_id = router.user_subscription_id

    existing_stmt = (
        select(Alert.id)
        .where(
            Alert.user_id == user_id,
            Alert.user_subscription_id == user_subscription_id,
            Alert.device_id == policy.device_id,
            Alert.alert_type == "policy_failed",
            Alert.status == "unread",
        )
        .limit(1)
    )

    existing_result = await db.execute(existing_stmt)

    if existing_result.scalar_one_or_none() is not None:
        return False

    failure_reason = policy.failure_reason or "Device policy execution failed."

    db.add(
        Alert(
            user_id=user_id,
            user_subscription_id=user_subscription_id,
            device_id=policy.device_id,
            alert_type="policy_failed",
            severity="high",
            title="Device policy failed",
            message=(
                f"Your {policy.policy_type} device policy could not be applied. "
                f"Reason: {failure_reason}"
            ),
            status="unread",
        )
    )

    await db.flush()

    return True
