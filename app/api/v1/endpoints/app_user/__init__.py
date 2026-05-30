from fastapi import APIRouter

from app.api.v1.endpoints.app_user import (
    alerts,
    devices,
    routers,
    subscriptions,
    plans,
    summary,
    usage,
    predictions,
    recommendations,
    plan_change_requests,
    device_policies,
    push_tokens,
)


router = APIRouter()

router.include_router(alerts.router)
router.include_router(summary.router)
router.include_router(subscriptions.router)
router.include_router(plans.router)
router.include_router(routers.router)
router.include_router(devices.router)
router.include_router(usage.router)
router.include_router(predictions.router)
router.include_router(recommendations.router)
router.include_router(plan_change_requests.router)
router.include_router(device_policies.router)
router.include_router(push_tokens.router)
