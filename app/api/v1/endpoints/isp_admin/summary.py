from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import ISPAdminSummaryResponse
from app.services.isp_admin import get_isp_admin_summary


router = APIRouter()


@router.get(
    "/summary",
    response_model=ISPAdminSummaryResponse,
)
async def get_isp_admin_summary_endpoint(
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminSummaryResponse:
    return await get_isp_admin_summary(
        db=db,
        isp_id=current_admin.isp_id,
    )