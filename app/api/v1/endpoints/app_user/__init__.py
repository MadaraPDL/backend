from fastapi import APIRouter

from app.api.v1.endpoints.app_user import summary


router = APIRouter()

router.include_router(summary.router)
