from fastapi import APIRouter

from app.api.v1.endpoints.app_user import summary, subscriptions


router = APIRouter()

router.include_router(summary.router)
router.include_router(subscriptions.router)
