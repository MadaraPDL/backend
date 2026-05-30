from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.app_user import AppUser
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.services.notifications import notify_recommendation_push


UPGRADE_THRESHOLD_PERCENT = Decimal("100")
DOWNGRADE_THRESHOLD_PERCENT = Decimal("60")
PLAN_BUFFER_MULTIPLIER = Decimal("1.10")
MODEL_VERSION = "rule_based_recommendation_v1"


@dataclass(frozen=True)
class RecommendationGenerationResult:
    recommendation: Recommendation
    created: bool
    predicted_usage_gb: Decimal
    current_plan_limit_gb: Decimal
    recommended_plan_limit_gb: Decimal | None


class RecommendationGenerationError(RuntimeError):
    """Base error for recommendation generation failures."""


class PredictionNotFoundForRecommendationError(RecommendationGenerationError):
    """Raised when prediction does not exist or is outside the allowed ISP scope."""


class PredictionNotReadyForRecommendationError(RecommendationGenerationError):
    """Raised when prediction cannot be used for recommendation generation."""


def _usage_percent(
    *,
    predicted_usage_gb: Decimal,
    plan_limit_gb: Decimal,
) -> Decimal:
    if plan_limit_gb <= 0:
        return Decimal("0")

    return (predicted_usage_gb / plan_limit_gb) * Decimal("100")


async def _find_existing_new_recommendation(
    *,
    db: AsyncSession,
    prediction_id: UUID,
) -> Recommendation | None:
    stmt = (
        select(Recommendation)
        .where(
            Recommendation.prediction_id == prediction_id,
            Recommendation.status == "new",
        )
        .order_by(Recommendation.created_at.desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()



async def _find_latest_recommendation_for_subscription(
    *,
    db: AsyncSession,
    user_subscription_id: UUID,
) -> Recommendation | None:
    stmt = (
        select(Recommendation)
        .where(Recommendation.user_subscription_id == user_subscription_id)
        .order_by(Recommendation.created_at.desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def _same_recommendation_state(
    *,
    existing: Recommendation,
    recommendation_type: str,
    recommendation_plan_id: UUID | None,
) -> bool:
    return (
        existing.recommendation_type == recommendation_type
        and existing.recommendation_plan_id == recommendation_plan_id
    )


async def _find_smallest_covering_plan(
    *,
    db: AsyncSession,
    isp_id: UUID,
    required_limit_gb: Decimal,
    exclude_plan_id: UUID | None = None,
) -> SubscriptionPlan | None:
    stmt = (
        select(SubscriptionPlan)
        .where(
            SubscriptionPlan.isp_id == isp_id,
            SubscriptionPlan.is_active.is_(True),
            SubscriptionPlan.data_limit_gb >= required_limit_gb,
        )
        .order_by(
            SubscriptionPlan.data_limit_gb.asc(),
            SubscriptionPlan.monthly_price.asc(),
        )
        .limit(1)
    )

    if exclude_plan_id is not None:
        stmt = stmt.where(SubscriptionPlan.id != exclude_plan_id)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _find_downgrade_plan(
    *,
    db: AsyncSession,
    isp_id: UUID,
    current_plan_id: UUID,
    current_plan_limit_gb: Decimal,
    required_limit_gb: Decimal,
) -> SubscriptionPlan | None:
    stmt = (
        select(SubscriptionPlan)
        .where(
            SubscriptionPlan.isp_id == isp_id,
            SubscriptionPlan.is_active.is_(True),
            SubscriptionPlan.id != current_plan_id,
            SubscriptionPlan.data_limit_gb < current_plan_limit_gb,
            SubscriptionPlan.data_limit_gb >= required_limit_gb,
        )
        .order_by(
            SubscriptionPlan.data_limit_gb.asc(),
            SubscriptionPlan.monthly_price.asc(),
        )
        .limit(1)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def _build_recommendation_text(
    *,
    recommendation_type: str,
    current_plan: SubscriptionPlan,
    recommended_plan: SubscriptionPlan | None,
    predicted_usage_gb: Decimal,
    usage_percent: Decimal,
) -> tuple[str, str]:
    predicted_text = str(predicted_usage_gb.quantize(Decimal("0.01")))
    percent_text = str(usage_percent.quantize(Decimal("0.1")))

    if recommendation_type == "upgrade_plan" and recommended_plan is not None:
        return (
            f"Upgrade to {recommended_plan.plan_name}.",
            (
                f"Your predicted usage is {predicted_text} GB, which is "
                f"{percent_text}% of your current {current_plan.plan_name} plan. "
                f"The recommended plan has {recommended_plan.data_limit_gb} GB."
            ),
        )

    if recommendation_type == "downgrade_plan" and recommended_plan is not None:
        return (
            f"Consider switching to {recommended_plan.plan_name}.",
            (
                f"Your predicted usage is {predicted_text} GB, which is only "
                f"{percent_text}% of your current {current_plan.plan_name} plan. "
                f"The recommended plan still covers your predicted usage."
            ),
        )

    if recommendation_type == "stay_current":
        return (
            "Stay on your current plan.",
            (
                f"Your predicted usage is {predicted_text} GB, which is "
                f"{percent_text}% of your current {current_plan.plan_name} plan. "
                "Your current plan looks suitable."
            ),
        )

    return (
        "Monitor your usage closely.",
        (
            f"Your predicted usage is {predicted_text} GB, which is "
            f"{percent_text}% of your current {current_plan.plan_name} plan. "
            "No better active plan was found, so continue monitoring your usage."
        ),
    )


async def generate_recommendation_for_prediction(
    *,
    db: AsyncSession,
    prediction_id: UUID,
    isp_id: UUID | None = None,
) -> RecommendationGenerationResult:
    stmt = (
        select(Prediction)
        .options(
            selectinload(Prediction.plan),
            selectinload(Prediction.user_subscription).selectinload(UserSubscription.user),
        )
        .join(AppUser, Prediction.user_id == AppUser.id)
        .where(Prediction.id == prediction_id)
    )

    if isp_id is not None:
        stmt = stmt.where(AppUser.isp_id == isp_id)

    result = await db.execute(stmt)
    prediction = result.scalar_one_or_none()

    if prediction is None:
        raise PredictionNotFoundForRecommendationError("Prediction not found.")

    if prediction.plan is None:
        raise PredictionNotReadyForRecommendationError(
            "Prediction must be linked to a current plan."
        )

    current_plan = prediction.plan
    predicted_usage_gb = prediction.predicted_usage_gb
    current_plan_limit_gb = current_plan.data_limit_gb

    existing = await _find_existing_new_recommendation(
        db=db,
        prediction_id=prediction.id,
    )

    if existing is not None:
        recommended_limit = None

        if existing.recommendation_plan_id is not None:
            plan_stmt = select(SubscriptionPlan).where(
                SubscriptionPlan.id == existing.recommendation_plan_id
            )
            plan_result = await db.execute(plan_stmt)
            recommended_plan = plan_result.scalar_one_or_none()
            recommended_limit = (
                recommended_plan.data_limit_gb
                if recommended_plan is not None
                else None
            )

        return RecommendationGenerationResult(
            recommendation=existing,
            created=False,
            predicted_usage_gb=predicted_usage_gb,
            current_plan_limit_gb=current_plan_limit_gb,
            recommended_plan_limit_gb=recommended_limit,
        )

    usage_percent = _usage_percent(
        predicted_usage_gb=predicted_usage_gb,
        plan_limit_gb=current_plan_limit_gb,
    )

    recommendation_type = "stay_current"
    recommended_plan: SubscriptionPlan | None = None

    if usage_percent >= UPGRADE_THRESHOLD_PERCENT:
        required_limit = predicted_usage_gb * PLAN_BUFFER_MULTIPLIER
        recommended_plan = await _find_smallest_covering_plan(
            db=db,
            isp_id=current_plan.isp_id,
            required_limit_gb=required_limit,
            exclude_plan_id=current_plan.id,
        )

        recommendation_type = (
            "upgrade_plan"
            if recommended_plan is not None
            else "monitor_usage"
        )

    elif usage_percent <= DOWNGRADE_THRESHOLD_PERCENT:
        required_limit = predicted_usage_gb * PLAN_BUFFER_MULTIPLIER
        recommended_plan = await _find_downgrade_plan(
            db=db,
            isp_id=current_plan.isp_id,
            current_plan_id=current_plan.id,
            current_plan_limit_gb=current_plan_limit_gb,
            required_limit_gb=required_limit,
        )

        recommendation_type = (
            "downgrade_plan"
            if recommended_plan is not None
            else "stay_current"
        )

    text, reason = _build_recommendation_text(
        recommendation_type=recommendation_type,
        current_plan=current_plan,
        recommended_plan=recommended_plan,
        predicted_usage_gb=predicted_usage_gb,
        usage_percent=usage_percent,
    )

    recommendation_plan_id = recommended_plan.id if recommended_plan is not None else None
    latest_recommendation = await _find_latest_recommendation_for_subscription(
        db=db,
        user_subscription_id=prediction.user_subscription_id,
    )

    if latest_recommendation is not None and _same_recommendation_state(
        existing=latest_recommendation,
        recommendation_type=recommendation_type,
        recommendation_plan_id=recommendation_plan_id,
    ):
        today = datetime.now(timezone.utc).date()
        latest_created_date = latest_recommendation.created_at.date()

        # Non-stay-current states should not duplicate unless state changes.
        # stay_current should only create a fresh daily record, not every usage run.
        if recommendation_type != "stay_current" or latest_created_date == today:
            return RecommendationGenerationResult(
                recommendation=latest_recommendation,
                created=False,
                predicted_usage_gb=predicted_usage_gb,
                current_plan_limit_gb=current_plan_limit_gb,
                recommended_plan_limit_gb=(
                    recommended_plan.data_limit_gb
                    if recommended_plan is not None
                    else None
                ),
            )

    recommendation = Recommendation(
        user_id=prediction.user_id,
        user_subscription_id=prediction.user_subscription_id,
        current_plan_id=current_plan.id,
        recommendation_plan_id=recommendation_plan_id,
        prediction_id=prediction.id,
        recommendation_type=recommendation_type,
        recommendation_text=text,
        reason=reason,
        confidence_score=prediction.confidence_score,
        status="new",
    )

    db.add(recommendation)
    await db.flush()
    await db.refresh(recommendation)

    await notify_recommendation_push(
        db=db,
        recommendation=recommendation,
    )

    return RecommendationGenerationResult(
        recommendation=recommendation,
        created=True,
        predicted_usage_gb=predicted_usage_gb,
        current_plan_limit_gb=current_plan_limit_gb,
        recommended_plan_limit_gb=(
            recommended_plan.data_limit_gb
            if recommended_plan is not None
            else None
        ),
    )
