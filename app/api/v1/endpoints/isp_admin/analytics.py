from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import ISPAdminAnalyticsSummaryResponse
from app.services.isp_admin import get_isp_admin_analytics_summary


router = APIRouter(prefix="/analytics")


@router.get(
    "/summary",
    response_model=ISPAdminAnalyticsSummaryResponse,
)
async def get_analytics_summary_endpoint(
    period_start: datetime | None = Query(default=None),
    period_end: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminAnalyticsSummaryResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    if (
        period_start is not None
        and period_end is not None
        and period_end < period_start
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="period_end cannot be before period_start",
        )

    return await get_isp_admin_analytics_summary(
        db=db,
        isp_id=current_admin.isp_id,
        period_start=period_start,
        period_end=period_end,
    )
