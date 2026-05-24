from fastapi import APIRouter

from app.api.v1.endpoints.platform_admin import (
    admin_invitations,
    isp_admins,
    isps,
    platform_admin_invitations,
    platform_admins,
    summary,
)

router = APIRouter(
    prefix="/platform-admin",
    tags=["Platform Admin"],
)

router.include_router(isps.router)
router.include_router(admin_invitations.router)
router.include_router(isp_admins.router)
router.include_router(platform_admin_invitations.router)
router.include_router(platform_admins.router)
router.include_router(summary.router)
