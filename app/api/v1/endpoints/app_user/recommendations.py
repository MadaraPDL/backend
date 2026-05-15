from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import MyRecommendationResponse
from app.services.app_user import get_my_recommendation, list_my_recommendations


router = APIRouter(prefix="/me/recommendations", tags=["App User"])


@router.get("", response_model=list[MyRecommendationResponse])
async def list_my_recommendations_endpoint(
    user_subscription_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    recommendation_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyRecommendationResponse]:
    return await list_my_recommendations(
        db=db,
        current_user=current_user,
        user_subscription_id=user_subscription_id,
        status=status_filter,
        recommendation_type=recommendation_type,
        limit=limit,
        offset=offset,
    )


@router.get("/{recommendation_id}", response_model=MyRecommendationResponse)
async def get_my_recommendation_endpoint(
    recommendation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyRecommendationResponse:
    recommendation = await get_my_recommendation(
        db=db,
        current_user=current_user,
        recommendation_id=recommendation_id,
    )

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return recommendation