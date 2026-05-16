from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    ISPAdminRecommendationGenerationResponse,
    ISPAdminRecommendationResponse,
)
from app.services.recommendations import (
    PredictionNotFoundForRecommendationError,
    PredictionNotReadyForRecommendationError,
    generate_recommendation_for_prediction,
)


router = APIRouter(prefix="/recommendations")


@router.post(
    "/predictions/{prediction_id}/generate",
    response_model=ISPAdminRecommendationGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_recommendation_for_prediction_endpoint(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminRecommendationGenerationResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    try:
        result = await generate_recommendation_for_prediction(
            db=db,
            prediction_id=prediction_id,
            isp_id=current_admin.isp_id,
        )
    except PredictionNotFoundForRecommendationError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        ) from None
    except PredictionNotReadyForRecommendationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None

    await db.commit()
    await db.refresh(result.recommendation)

    return ISPAdminRecommendationGenerationResponse(
        recommendation=ISPAdminRecommendationResponse.model_validate(
            result.recommendation
        ),
        created=result.created,
        predicted_usage_gb=result.predicted_usage_gb,
        current_plan_limit_gb=result.current_plan_limit_gb,
        recommended_plan_limit_gb=result.recommended_plan_limit_gb,
    )
