from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import AppUserSummaryResponse
from app.services.app_user import build_app_user_summary


router = APIRouter(prefix="/me", tags=["App User"])


@router.get(
    "/summary",
    response_model=AppUserSummaryResponse,
)
async def get_my_summary_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> AppUserSummaryResponse:
    return await build_app_user_summary(
        db=db,
        current_user=current_user,
    )
