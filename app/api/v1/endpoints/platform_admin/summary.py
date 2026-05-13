from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin_role
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.platform_admin import PlatformAdminSummaryResponse
from app.services.platform_admin import get_platform_admin_summary

router = APIRouter(prefix="/summary")


@router.get(
    "",
    response_model=PlatformAdminSummaryResponse,
)
async def get_platform_admin_summary_endpoint(
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> PlatformAdminSummaryResponse:
    return await get_platform_admin_summary(db=db)