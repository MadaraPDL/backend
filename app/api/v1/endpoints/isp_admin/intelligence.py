from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import ISPAdminIntelligenceRunResponse
from app.services.isp_admin import run_intelligence_for_isp


router = APIRouter(prefix="/intelligence")


@router.post(
    "/run",
    response_model=ISPAdminIntelligenceRunResponse,
)
async def run_intelligence_endpoint(
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminIntelligenceRunResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    result = await run_intelligence_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
    )

    await db.commit()

    return result
