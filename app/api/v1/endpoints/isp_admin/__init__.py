from fastapi import APIRouter

from app.api.v1.endpoints.isp_admin import summary


router = APIRouter(
    prefix="/isp-admin",
    tags=["ISP Admin"],
)

router.include_router(summary.router)
