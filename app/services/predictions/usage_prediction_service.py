from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.app_user import AppUser
from app.models.prediction import Prediction
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription


MB_PER_GB = Decimal("1024")
MODEL_VERSION = "rule_based_v1"


@dataclass(frozen=True)
class PredictionGenerationResult:
    prediction: Prediction
    days_elapsed: int
    total_cycle_days: int
    observed_usage_gb: Decimal
    average_daily_usage_gb: Decimal


class PredictionGenerationError(RuntimeError):
    """Base error for prediction generation failures."""


class SubscriptionNotFoundForPredictionError(PredictionGenerationError):
    """Raised when subscription does not exist or is outside the allowed ISP scope."""


class SubscriptionNotReadyForPredictionError(PredictionGenerationError):
    """Raised when subscription cannot be used for prediction generation."""


def _decimal_or_zero(value: object) -> Decimal:
    if value is None:
        return Decimal("0")

    return Decimal(str(value))


def _usage_total_expression():
    return func.coalesce(
        UsageRecord.total_mb,
        UsageRecord.upload_mb + UsageRecord.download_mb,
    )


def _countable_usage_filter():
    # Simulator stores one official total row plus estimated per-device rows.
    # Predictions must use the official total and ignore estimated rows,
    # otherwise projected usage is doubled.
    return or_(
        UsageRecord.source.is_(None),
        UsageRecord.source != "simulator_estimated_device",
    )


def _safe_days_between(start_date: date, end_date: date) -> int:
    days = (end_date - start_date).days + 1
    return max(days, 1)


def _as_date(value: date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()

    return value


def _risk_level(
    *,
    predicted_usage_gb: Decimal,
    plan_limit_gb: Decimal,
) -> str:
    if plan_limit_gb <= 0:
        return "low"

    usage_percent = (predicted_usage_gb / plan_limit_gb) * Decimal("100")

    if usage_percent >= Decimal("100"):
        return "high"

    if usage_percent >= Decimal("80"):
        return "medium"

    return "low"


def _confidence_score(
    *,
    days_elapsed: int,
    record_count: int,
) -> Decimal:
    score = Decimal("0.50")

    score += Decimal(str(min(days_elapsed, 10))) * Decimal("0.03")
    score += Decimal(str(min(record_count, 20))) * Decimal("0.005")

    return min(score, Decimal("0.95")).quantize(Decimal("0.01"))


async def generate_usage_prediction_for_subscription(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
    isp_id: UUID | None = None,
    prediction_date: date | None = None,
) -> PredictionGenerationResult:
    final_prediction_date = prediction_date or date.today()

    stmt = (
        select(UserSubscription)
        .options(
            selectinload(UserSubscription.user),
            selectinload(UserSubscription.plan),
        )
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(UserSubscription.id == user_subscription_id)
    )

    if isp_id is not None:
        stmt = stmt.where(AppUser.isp_id == isp_id)

    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if subscription is None:
        raise SubscriptionNotFoundForPredictionError("Subscription not found.")

    if subscription.status != "active":
        raise SubscriptionNotReadyForPredictionError(
            "Only active subscriptions can be used for prediction generation."
        )

    if subscription.plan is None:
        raise SubscriptionNotReadyForPredictionError(
            "Subscription must have a plan before prediction generation."
        )

    period_start = subscription.start_date

    if subscription.end_date is not None:
        period_end = subscription.end_date
    else:
        period_end = period_start + timedelta(days=29)

    if period_end < period_start:
        raise SubscriptionNotReadyForPredictionError(
            "Subscription period is invalid."
        )

    effective_today = min(final_prediction_date, period_end)

    if effective_today < period_start:
        raise SubscriptionNotReadyForPredictionError(
            "Prediction date cannot be before subscription start date."
        )

    total_expr = _usage_total_expression()

    usage_stmt = select(
        func.coalesce(func.sum(total_expr), 0).label("total_mb"),
        func.count(UsageRecord.id).label("record_count"),
        func.min(UsageRecord.record_start).label("first_usage_at"),
        func.max(UsageRecord.record_end).label("latest_usage_at"),
    ).where(
        UsageRecord.user_subscription_id == subscription.id,
        UsageRecord.record_start >= period_start,
        UsageRecord.record_end <= effective_today + timedelta(days=1),
        _countable_usage_filter(),
    )

    usage_result = await db.execute(usage_stmt)
    usage_row = usage_result.one()

    observed_usage_mb = _decimal_or_zero(usage_row.total_mb)
    observed_usage_gb = observed_usage_mb / MB_PER_GB

    calendar_days_elapsed = _safe_days_between(period_start, effective_today)
    total_cycle_days = _safe_days_between(period_start, period_end)

    first_usage_at = usage_row.first_usage_at
    latest_usage_at = usage_row.latest_usage_at

    if first_usage_at is not None and latest_usage_at is not None:
        active_usage_days = _safe_days_between(
            _as_date(first_usage_at),
            _as_date(latest_usage_at),
        )
        days_elapsed = min(calendar_days_elapsed, active_usage_days)
    else:
        days_elapsed = calendar_days_elapsed

    days_elapsed = max(days_elapsed, 1)

    average_daily_usage_gb = observed_usage_gb / Decimal(str(days_elapsed))
    predicted_usage_gb = average_daily_usage_gb * Decimal(str(total_cycle_days))

    predicted_usage_gb = predicted_usage_gb.quantize(Decimal("0.01"))
    average_daily_usage_gb = average_daily_usage_gb.quantize(Decimal("0.01"))
    observed_usage_gb = observed_usage_gb.quantize(Decimal("0.01"))

    risk_level = _risk_level(
        predicted_usage_gb=predicted_usage_gb,
        plan_limit_gb=subscription.plan.data_limit_gb,
    )

    confidence_score = _confidence_score(
        days_elapsed=days_elapsed,
        record_count=int(usage_row.record_count or 0),
    )

    existing_prediction_result = await db.execute(
        select(Prediction)
        .where(
            Prediction.user_subscription_id == subscription.id,
            Prediction.prediction_date == final_prediction_date,
        )
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )
    prediction = existing_prediction_result.scalar_one_or_none()

    if prediction is None:
        prediction = Prediction(
            user_id=subscription.user_id,
            user_subscription_id=subscription.id,
            plan_id=subscription.plan_id,
            prediction_date=final_prediction_date,
            period_start=period_start,
            period_end=period_end,
            predicted_usage_gb=predicted_usage_gb,
            confidence_score=confidence_score,
            risk_level=risk_level,
            model_version=MODEL_VERSION,
        )
        db.add(prediction)
    else:
        prediction.plan_id = subscription.plan_id
        prediction.period_start = period_start
        prediction.period_end = period_end
        prediction.predicted_usage_gb = predicted_usage_gb
        prediction.confidence_score = confidence_score
        prediction.risk_level = risk_level
        prediction.model_version = MODEL_VERSION

    await db.flush()
    await db.refresh(prediction)

    return PredictionGenerationResult(
        prediction=prediction,
        days_elapsed=days_elapsed,
        total_cycle_days=total_cycle_days,
        observed_usage_gb=observed_usage_gb,
        average_daily_usage_gb=average_daily_usage_gb,
    )
