from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal

from app.models.app_user_push_token import AppUserPushToken
from app.models.recommendation import Recommendation
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.services.notifications.expo_push_service import (
    ExpoPushMessage,
    ExpoPushSendResult,
    send_expo_push_notifications,
)


logger = logging.getLogger(__name__)


RECOMMENDATION_PUSH_TYPES = {
    "upgrade_plan",
    "downgrade_plan",
    "monitor_usage",
}


def empty_push_result() -> ExpoPushSendResult:
    return ExpoPushSendResult(
        attempted=0,
        accepted=0,
        failed=0,
        tickets=[],
        errors=[],
    )


async def list_active_expo_tokens_for_user(
    *,
    db: AsyncSession,
    user_id: UUID,
) -> list[str]:
    result = await db.execute(
        select(AppUserPushToken.expo_push_token).where(
            AppUserPushToken.user_id == user_id,
            AppUserPushToken.is_active.is_(True),
            AppUserPushToken.permission_status == "granted",
        )
    )

    return list(result.scalars().all())


def build_push_messages_for_user(
    *,
    expo_push_tokens: list[str],
    title: str,
    body: str,
    data: dict[str, Any],
) -> list[ExpoPushMessage]:
    return [
        ExpoPushMessage(
            to=token,
            title=title,
            body=body,
            data=data,
        )
        for token in expo_push_tokens
    ]


async def list_active_expo_tokens_for_user_isolated(
    *,
    user_id: UUID,
) -> list[str]:
    async with AsyncSessionLocal() as push_db:
        return await list_active_expo_tokens_for_user(
            db=push_db,
            user_id=user_id,
        )


async def dispatch_push_to_user(
    *,
    db: AsyncSession,
    user_id: UUID,
    title: str,
    body: str,
    data: dict[str, Any],
) -> ExpoPushSendResult:
    # Push dispatch is intentionally isolated from the caller transaction.
    # A push lookup/send failure must never abort simulator, intelligence,
    # alert, recommendation, or service-request business logic.
    _ = db

    try:
        expo_push_tokens = await list_active_expo_tokens_for_user_isolated(
            user_id=user_id,
        )
    except Exception as exc:
        logger.warning("Skipping push dispatch because token lookup failed: %s", exc)
        return empty_push_result()

    if not expo_push_tokens:
        return empty_push_result()

    messages = build_push_messages_for_user(
        expo_push_tokens=expo_push_tokens,
        title=title,
        body=body,
        data=data,
    )

    try:
        return await send_expo_push_notifications(messages)
    except Exception as exc:
        logger.warning("Skipping push dispatch because Expo send failed: %s", exc)
        return empty_push_result()


async def notify_usage_alert_push(
    *,
    db: AsyncSession,
    user_id: UUID,
    alert_kind: str,
) -> ExpoPushSendResult:
    if alert_kind == "plan_exceed":
        title = "Plan usage limit reached"
        body = "Open PulseFi to review your current internet usage."
    else:
        title = "High internet usage"
        body = "Open PulseFi to review your latest usage alert."

    return await dispatch_push_to_user(
        db=db,
        user_id=user_id,
        title=title,
        body=body,
        data={
            "screen": "Alerts",
            "type": alert_kind,
        },
    )


async def notify_new_device_push(
    *,
    db: AsyncSession,
    user_id: UUID,
) -> ExpoPushSendResult:
    return await dispatch_push_to_user(
        db=db,
        user_id=user_id,
        title="New device connected",
        body="Open PulseFi to review the new device on your network.",
        data={
            "screen": "Alerts",
            "type": "new_device_connected",
        },
    )


def should_notify_recommendation(recommendation: Recommendation) -> bool:
    return recommendation.recommendation_type in RECOMMENDATION_PUSH_TYPES


async def notify_recommendation_push(
    *,
    db: AsyncSession,
    recommendation: Recommendation,
) -> ExpoPushSendResult:
    if not should_notify_recommendation(recommendation):
        return empty_push_result()

    return await dispatch_push_to_user(
        db=db,
        user_id=recommendation.user_id,
        title="PulseFi recommendation update",
        body="Open PulseFi to review your latest plan recommendation.",
        data={
            "screen": "More",
            "section": "insights",
            "recommendation_id": str(recommendation.id),
            "type": recommendation.recommendation_type,
        },
    )


async def notify_plan_request_review_push(
    *,
    db: AsyncSession,
    change_request: SubscriptionChangeRequest,
) -> ExpoPushSendResult:
    if change_request.status not in {"approved", "rejected"}:
        return empty_push_result()

    title = (
        "Service request approved"
        if change_request.status == "approved"
        else "Service request rejected"
    )

    return await dispatch_push_to_user(
        db=db,
        user_id=change_request.user_id,
        title=title,
        body="Open PulseFi to review your service request update.",
        data={
            "screen": "More",
            "section": "planRequest",
            "request_id": str(change_request.id),
            "status": change_request.status,
            "type": "plan_request_update",
        },
    )
