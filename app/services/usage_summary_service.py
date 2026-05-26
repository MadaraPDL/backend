from __future__ import annotations

from datetime import datetime, time, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.subscription_plan import SubscriptionPlan
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription
from app.schemas.usage_summary import UsageConsumptionSummary


MB_PER_GB = Decimal("1024")


def _decimal_or_zero(value: object) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _quantize_gb(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def _quantize_percent(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.1"))


def _usage_total_expression():
    return func.coalesce(
        UsageRecord.total_mb,
        UsageRecord.upload_mb + UsageRecord.download_mb,
    )


async def _sum_usage_mb(
    *,
    db: AsyncSession,
    subscription_id: UUID,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> Decimal:
    total_expr = _usage_total_expression()

    stmt = select(func.coalesce(func.sum(total_expr), 0)).where(
        UsageRecord.user_subscription_id == subscription_id,
    )

    if start_at is not None:
        stmt = stmt.where(UsageRecord.record_start >= start_at)

    if end_at is not None:
        stmt = stmt.where(UsageRecord.record_end <= end_at)

    result = await db.execute(stmt)
    return _decimal_or_zero(result.scalar_one_or_none())


async def _get_last_record_end(
    *,
    db: AsyncSession,
    subscription_id: UUID,
) -> datetime | None:
    result = await db.execute(
        select(func.max(UsageRecord.record_end)).where(
            UsageRecord.user_subscription_id == subscription_id,
        )
    )
    return result.scalar_one_or_none()


async def _build_summary_from_subscription_and_plan(
    *,
    db: AsyncSession,
    subscription: UserSubscription,
    plan: SubscriptionPlan,
) -> UsageConsumptionSummary:
    now = datetime.now(timezone.utc)
    today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    cycle_start = datetime.combine(
        subscription.start_date,
        time.min,
        tzinfo=timezone.utc,
    )

    today_mb = await _sum_usage_mb(
        db=db,
        subscription_id=subscription.id,
        start_at=today_start,
    )
    monthly_mb = await _sum_usage_mb(
        db=db,
        subscription_id=subscription.id,
        start_at=month_start,
    )
    cycle_mb = await _sum_usage_mb(
        db=db,
        subscription_id=subscription.id,
        start_at=cycle_start,
    )
    total_mb = await _sum_usage_mb(
        db=db,
        subscription_id=subscription.id,
    )

    today_gb = _quantize_gb(today_mb / MB_PER_GB)
    monthly_gb = _quantize_gb(monthly_mb / MB_PER_GB)
    cycle_gb = _quantize_gb(cycle_mb / MB_PER_GB)
    total_gb = _quantize_gb(total_mb / MB_PER_GB)

    plan_limit_gb = _decimal_or_zero(plan.data_limit_gb)
    is_unlimited = plan_limit_gb <= 0

    remaining_gb: Decimal | None = None
    usage_percent: Decimal | None = None

    if not is_unlimited:
        remaining_gb = _quantize_gb(max(plan_limit_gb - cycle_gb, Decimal("0")))
        usage_percent = _quantize_percent((cycle_gb / plan_limit_gb) * Decimal("100"))

    last_record_end = await _get_last_record_end(
        db=db,
        subscription_id=subscription.id,
    )

    return UsageConsumptionSummary(
        user_id=subscription.user_id,
        subscription_id=subscription.id,
        plan_id=plan.id,
        plan_name=plan.plan_name,
        subscription_label=subscription.subscription_label,
        subscription_status=subscription.status,
        plan_limit_gb=None if is_unlimited else plan_limit_gb,
        today_usage_gb=today_gb,
        monthly_usage_gb=monthly_gb,
        current_cycle_usage_gb=cycle_gb,
        total_usage_gb=total_gb,
        remaining_gb=remaining_gb,
        usage_percent=usage_percent,
        is_unlimited=is_unlimited,
        cycle_start=subscription.start_date,
        cycle_end=subscription.end_date,
        last_record_end=last_record_end,
    )


async def build_latest_active_usage_summary_for_user(
    *,
    db: AsyncSession,
    user_id: UUID,
    isp_id: UUID | None = None,
) -> UsageConsumptionSummary | None:
    stmt = (
        select(UserSubscription, SubscriptionPlan)
        .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(
            UserSubscription.user_id == user_id,
            UserSubscription.status == "active",
        )
        .order_by(UserSubscription.created_at.desc())
        .limit(1)
    )

    if isp_id is not None:
        stmt = stmt.where(AppUser.isp_id == isp_id)

    result = await db.execute(stmt)
    row = result.one_or_none()

    if row is None:
        return None

    subscription, plan = row

    return await _build_summary_from_subscription_and_plan(
        db=db,
        subscription=subscription,
        plan=plan,
    )




async def build_usage_summaries_for_user(
    *,
    db: AsyncSession,
    user_id: UUID,
    isp_id: UUID | None = None,
) -> list[UsageConsumptionSummary]:
    stmt = (
        select(UserSubscription, SubscriptionPlan)
        .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(UserSubscription.user_id == user_id)
        .order_by(UserSubscription.status.asc(), UserSubscription.created_at.desc())
    )

    if isp_id is not None:
        stmt = stmt.where(AppUser.isp_id == isp_id)

    result = await db.execute(stmt)
    rows = result.all()

    summaries: list[UsageConsumptionSummary] = []

    for subscription, plan in rows:
        summaries.append(
            await _build_summary_from_subscription_and_plan(
                db=db,
                subscription=subscription,
                plan=plan,
            )
        )

    return summaries


async def build_usage_summary_for_subscription(
    *,
    db: AsyncSession,
    subscription_id: UUID,
    user_id: UUID | None = None,
    isp_id: UUID | None = None,
) -> UsageConsumptionSummary | None:
    stmt = (
        select(UserSubscription, SubscriptionPlan)
        .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(UserSubscription.id == subscription_id)
    )

    if user_id is not None:
        stmt = stmt.where(UserSubscription.user_id == user_id)

    if isp_id is not None:
        stmt = stmt.where(AppUser.isp_id == isp_id)

    result = await db.execute(stmt)
    row = result.one_or_none()

    if row is None:
        return None

    subscription, plan = row

    return await _build_summary_from_subscription_and_plan(
        db=db,
        subscription=subscription,
        plan=plan,
    )
