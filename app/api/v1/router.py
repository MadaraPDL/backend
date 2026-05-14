from fastapi import APIRouter

from app.api.v1.endpoints import app_user, auth, health, isp_admin, platform_admin


api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router)
api_router.include_router(platform_admin.router)
api_router.include_router(isp_admin.router)
api_router.include_router(app_user.router)
