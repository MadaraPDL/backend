from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import (
    ISPAdminIntelligenceRunItem,
    ISPAdminIntelligenceRunResponse,
)
from app.services.predictions import (
    SubscriptionNotFoundForPredictionError,
    SubscriptionNotReadyForPredictionError,
    generate_usage_prediction_for_subscription,
)
from app.services.recommendations import (
    PredictionNotFoundForRecommendationError,
    PredictionNotReadyForRecommendationError,
    generate_recommendation_for_prediction,
)


async def list_active_subscription_ids_for_isp(
    db: AsyncSession,
    isp_id: UUID,
) -> list[UUID]:
    stmt = (
        select(UserSubscription.id)
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(
            AppUser.isp_id == isp_id,
            UserSubscription.status == "active",
        )
        .order_by(UserSubscription.created_at.desc())
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_existing_prediction_for_today(
    db: AsyncSession,
    subscription_id: UUID,
) -> Prediction | None:
    today = datetime.now(timezone.utc).date()

    result = await db.execute(
        select(Prediction)
        .where(
            Prediction.user_subscription_id == subscription_id,
            Prediction.prediction_date == today,
        )
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )

    return result.scalar_one_or_none()


async def get_existing_recommendation_for_prediction(
    db: AsyncSession,
    prediction_id: UUID,
) -> Recommendation | None:
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.prediction_id == prediction_id)
        .order_by(Recommendation.created_at.desc())
        .limit(1)
    )

    return result.scalar_one_or_none()


async def run_intelligence_for_isp(
    db: AsyncSession,
    isp_id: UUID,
) -> ISPAdminIntelligenceRunResponse:
    subscription_ids = await list_active_subscription_ids_for_isp(
        db=db,
        isp_id=isp_id,
    )

    items: list[ISPAdminIntelligenceRunItem] = []
    predictions_created = 0
    recommendations_created = 0
    skipped = 0
    failed = 0

    for subscription_id in subscription_ids:
        try:
            existing_prediction = await get_existing_prediction_for_today(
                db=db,
                subscription_id=subscription_id,
            )

            if existing_prediction is None:
                prediction_result = await generate_usage_prediction_for_subscription(
                    db=db,
                    user_subscription_id=subscription_id,
                    isp_id=isp_id,
                    prediction_date=None,
                )
                prediction = prediction_result.prediction
                predictions_created += 1
                prediction_message = "Prediction generated."
            else:
                prediction = existing_prediction
                prediction_message = "Today's prediction already exists."

            existing_recommendation = await get_existing_recommendation_for_prediction(
                db=db,
                prediction_id=prediction.id,
            )

            if existing_recommendation is None:
                recommendation_result = await generate_recommendation_for_prediction(
                    db=db,
                    prediction_id=prediction.id,
                    isp_id=isp_id,
                )
                recommendation = recommendation_result.recommendation

                if recommendation_result.created:
                    recommendations_created += 1

                recommendation_message = "Recommendation generated."
            else:
                recommendation = existing_recommendation
                recommendation_message = "Recommendation already exists."

            if existing_prediction is not None and existing_recommendation is not None:
                skipped += 1
                status = "skipped"
            else:
                status = "processed"

            items.append(
                ISPAdminIntelligenceRunItem(
                    subscription_id=str(subscription_id),
                    status=status,
                    prediction_id=str(prediction.id),
                    recommendation_id=str(recommendation.id),
                    message=f"{prediction_message} {recommendation_message}",
                )
            )

        except (
            SubscriptionNotFoundForPredictionError,
            SubscriptionNotReadyForPredictionError,
            PredictionNotFoundForRecommendationError,
            PredictionNotReadyForRecommendationError,
        ) as exc:
            skipped += 1
            items.append(
                ISPAdminIntelligenceRunItem(
                    subscription_id=str(subscription_id),
                    status="skipped",
                    message=str(exc),
                )
            )

        except Exception as exc:
            failed += 1
            items.append(
                ISPAdminIntelligenceRunItem(
                    subscription_id=str(subscription_id),
                    status="failed",
                    message=exc.__class__.__name__,
                )
            )

    return ISPAdminIntelligenceRunResponse(
        subscriptions_checked=len(subscription_ids),
        predictions_created=predictions_created,
        recommendations_created=recommendations_created,
        skipped=skipped,
        failed=failed,
        items=items,
    )
