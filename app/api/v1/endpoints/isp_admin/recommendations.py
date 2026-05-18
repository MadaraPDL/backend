from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from app.services.isp_admin import (
    get_recommendation_for_isp,
    list_recommendations_for_isp,
)


router = APIRouter(prefix="/recommendations")


@router.get(
    "",
    response_model=list[ISPAdminRecommendationResponse],
)
async def list_recommendations_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    user_id: UUID | None = Query(default=None),
    subscription_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminRecommendationResponse]:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    recommendations = await list_recommendations_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        status=status_filter,
        user_id=user_id,
        subscription_id=subscription_id,
        limit=limit,
        offset=offset,
    )

    return [
        ISPAdminRecommendationResponse.model_validate(recommendation)
        for recommendation in recommendations
    ]


@router.get(
    "/{recommendation_id}",
    response_model=ISPAdminRecommendationResponse,
)
async def get_recommendation_endpoint(
    recommendation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminRecommendationResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    recommendation = await get_recommendation_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        recommendation_id=recommendation_id,
    )

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return ISPAdminRecommendationResponse.model_validate(recommendation)


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
