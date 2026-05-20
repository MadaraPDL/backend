from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import MySubscriptionPlanSummary
from app.services.app_user import list_my_available_plans


router = APIRouter(prefix="/me/plans", tags=["App User"])


@router.get("", response_model=list[MySubscriptionPlanSummary])
async def list_my_available_plans_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MySubscriptionPlanSummary]:
    plans = await list_my_available_plans(
        db=db,
        current_user=current_user,
    )

    return [MySubscriptionPlanSummary.model_validate(plan) for plan in plans]
