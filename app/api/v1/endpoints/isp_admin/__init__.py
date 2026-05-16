from fastapi import APIRouter

from app.api.v1.endpoints.isp_admin import (
    device_connection_logs,
    plans,
    router_action_logs,
    routers,
    subscriptions,
    summary,
    usage_ingestion,
    usage_records,
    user_invitations,
    users,
)


router = APIRouter(
    prefix="/isp-admin",
    tags=["ISP Admin"],
)

router.include_router(summary.router)
router.include_router(user_invitations.router)
router.include_router(users.router)
router.include_router(plans.router)
router.include_router(subscriptions.router)
router.include_router(routers.router)
router.include_router(router_action_logs.router)
router.include_router(usage_ingestion.router)
router.include_router(usage_records.router)
router.include_router(device_connection_logs.router)
