from fastapi import APIRouter

from app.api.v1.endpoints.platform_admin import admin_invitations, isps

router = APIRouter(
    prefix="/platform-admin",
    tags=["Platform Admin"],
)

router.include_router(isps.router)
router.include_router(admin_invitations.router)