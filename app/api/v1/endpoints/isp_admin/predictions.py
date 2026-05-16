from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    ISPAdminPredictionGenerateRequest,
    ISPAdminPredictionGenerationResponse,
    ISPAdminPredictionResponse,
)
from app.services.predictions import (
    SubscriptionNotFoundForPredictionError,
    SubscriptionNotReadyForPredictionError,
    generate_usage_prediction_for_subscription,
)


router = APIRouter(prefix="/predictions")


@router.post(
    "/subscriptions/{subscription_id}/generate",
    response_model=ISPAdminPredictionGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_prediction_for_subscription_endpoint(
    subscription_id: UUID,
    request: ISPAdminPredictionGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminPredictionGenerationResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    try:
        result = await generate_usage_prediction_for_subscription(
            db=db,
            user_subscription_id=subscription_id,
            isp_id=current_admin.isp_id,
            prediction_date=request.prediction_date,
        )
    except SubscriptionNotFoundForPredictionError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        ) from None
    except SubscriptionNotReadyForPredictionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None

    await db.commit()
    await db.refresh(result.prediction)

    return ISPAdminPredictionGenerationResponse(
        prediction=ISPAdminPredictionResponse.model_validate(result.prediction),
        days_elapsed=result.days_elapsed,
        total_cycle_days=result.total_cycle_days,
        observed_usage_gb=result.observed_usage_gb,
        average_daily_usage_gb=result.average_daily_usage_gb,
    )
