from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_isp_admin
from app.models.admin import Admin


router = APIRouter()


@router.get("/summary")
async def get_isp_admin_summary(
    current_admin: Admin = Depends(get_current_isp_admin),
) -> dict:
    return {
        "message": "ISP Admin summary endpoint is ready.",
        "admin_id": str(current_admin.id),
        "isp_id": str(current_admin.isp_id),
    }
