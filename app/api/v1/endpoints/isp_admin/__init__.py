from fastapi import APIRouter

from app.api.v1.endpoints.isp_admin import summary, user_invitations


router = APIRouter(
    prefix="/isp-admin",
    tags=["ISP Admin"],
)

router.include_router(summary.router)
router.include_router(user_invitations.router)
