from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.models.router import Router
from app.models.usage_record import UsageRecord
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
from app.services.alerts import (
    generate_new_device_alerts_for_router,
    generate_usage_alerts_for_subscription,
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


async def get_latest_usage_window_for_subscription(
    db: AsyncSession,
    subscription_id: UUID,
) -> tuple[datetime | None, datetime | None, datetime | None]:
    result = await db.execute(
        select(
            UsageRecord.record_start,
            UsageRecord.record_end,
            UsageRecord.created_at,
        )
        .where(UsageRecord.user_subscription_id == subscription_id)
        .order_by(UsageRecord.created_at.desc(), UsageRecord.record_end.desc())
        .limit(1)
    )
    row = result.one_or_none()

    if row is None:
        return None, None, None

    return row.record_start, row.record_end, row.created_at


async def list_router_ids_for_subscription(
    db: AsyncSession,
    subscription_id: UUID,
    isp_id: UUID,
) -> list[UUID]:
    result = await db.execute(
        select(Router.id)
        .where(
            Router.user_subscription_id == subscription_id,
            Router.isp_id == isp_id,
            Router.status == "active",
        )
        .order_by(Router.created_at.desc())
    )

    return list(result.scalars().all())



def _prediction_needs_refresh(
    *,
    existing_prediction: Prediction | None,
    latest_usage_created_at: datetime | None,
) -> bool:
    if existing_prediction is None:
        return True

    if latest_usage_created_at is None:
        return False

    return latest_usage_created_at > existing_prediction.created_at



async def run_intelligence_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    *,
    include_alert_generation: bool = True,
) -> ISPAdminIntelligenceRunResponse:
    subscription_ids = await list_active_subscription_ids_for_isp(
        db=db,
        isp_id=isp_id,
    )

    items: list[ISPAdminIntelligenceRunItem] = []
    predictions_created = 0
    recommendations_created = 0
    alerts_created = 0
    skipped = 0
    failed = 0
    new_device_event_start = datetime.now(timezone.utc) - timedelta(days=1)

    for subscription_id in subscription_ids:
        try:
            latest_record_start, latest_record_end, latest_usage_created_at = (
                await get_latest_usage_window_for_subscription(
                    db=db,
                    subscription_id=subscription_id,
                )
            )
            item_alerts_created = 0

            if include_alert_generation:
                usage_alert_result = await generate_usage_alerts_for_subscription(
                    db=db,
                    user_subscription_id=subscription_id,
                    latest_record_start=latest_record_start,
                    latest_record_end=latest_record_end,
                )
                router_ids = await list_router_ids_for_subscription(
                    db=db,
                    subscription_id=subscription_id,
                    isp_id=isp_id,
                )
                new_device_alerts_created = 0

                for router_id in router_ids:
                    new_device_result = await generate_new_device_alerts_for_router(
                        db=db,
                        router_id=router_id,
                        event_start=new_device_event_start,
                    )
                    new_device_alerts_created += (
                        new_device_result.new_device_alerts_created
                    )

                item_alerts_created = (
                    usage_alert_result.alerts_created + new_device_alerts_created
                )
                alerts_created += item_alerts_created

            existing_prediction = await get_existing_prediction_for_today(
                db=db,
                subscription_id=subscription_id,
            )

            should_refresh_prediction = _prediction_needs_refresh(
                existing_prediction=existing_prediction,
                latest_usage_created_at=latest_usage_created_at,
            )

            if should_refresh_prediction:
                prediction_result = await generate_usage_prediction_for_subscription(
                    db=db,
                    user_subscription_id=subscription_id,
                    isp_id=isp_id,
                    prediction_date=None,
                )
                prediction = prediction_result.prediction

                if existing_prediction is None:
                    predictions_created += 1
                    prediction_message = "Prediction generated."
                else:
                    prediction_message = "Prediction refreshed in place after new usage."
            else:
                prediction = existing_prediction
                prediction_message = "Today's prediction already exists and is up to date."

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

            if (
                not should_refresh_prediction
                and existing_prediction is not None
                and existing_recommendation is not None
            ):
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
                    alerts_created=item_alerts_created,
                    message=(
                        f"{prediction_message} {recommendation_message} "
                        f"Alerts created: {item_alerts_created}."
                    ),
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
        alerts_created=alerts_created,
        skipped=skipped,
        failed=failed,
        items=items,
    )
