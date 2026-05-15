from fastapi import APIRouter

from app.api.v1.endpoints.app_user import (
    alerts,
    devices,
    routers,
    subscriptions,
    summary,
    usage,
)


router = APIRouter()

router.include_router(alerts.router)
router.include_router(summary.router)
router.include_router(subscriptions.router)
router.include_router(routers.router)
router.include_router(devices.router)
router.include_router(usage.router)
