from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import MyPredictionResponse
from app.services.app_user import get_my_prediction, list_my_predictions


router = APIRouter(prefix="/me/predictions", tags=["App User"])

@router.get("", response_model=list[MyPredictionResponse])

async def list_my_predictions_endpoint(
   user_subscription_id: UUID | None = Query(default=None),
   risk_level: str | None = Query(default=None),
   limit: int = Query(default=50, ge=1, le=100),
   offset: int = Query(default=0, ge=0),
   db: AsyncSession = Depends(get_db),
   current_user: AppUser = Depends(get_current_app_user),     
) -> list[MyPredictionResponse]:
    return await list_my_predictions(
        db=db,
        current_user=current_user,
        user_subscription_id=user_subscription_id,
        risk_level=risk_level,
        limit=limit,
        offset=offset,
    )

@router.get("/{prediction_id}", response_model=MyPredictionResponse)

async def get_my_prediction_endpoint(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyPredictionResponse:
    prediction = await get_my_prediction(
        db=db,
        current_user=current_user,
        prediction_id=prediction_id,
    )

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    return prediction