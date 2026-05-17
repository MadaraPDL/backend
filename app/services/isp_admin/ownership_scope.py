from __future__ import annotations

from uuid import UUID

from app.models.app_user import AppUser
from app.models.router import Router
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription


def apply_router_isp_ownership_scope(stmt, *, isp_id: UUID):
    return (
        stmt.join(
            UserSubscription,
            Router.user_subscription_id == UserSubscription.id,
        )
        .join(
            AppUser,
            UserSubscription.user_id == AppUser.id,
        )
        .where(
            Router.isp_id == isp_id,
            AppUser.isp_id == isp_id,
        )
    )


def apply_usage_record_isp_ownership_scope(stmt, *, isp_id: UUID):
    return (
        stmt.join(
            Router,
            UsageRecord.router_id == Router.id,
        )
        .join(
            UserSubscription,
            UsageRecord.user_subscription_id == UserSubscription.id,
        )
        .join(
            AppUser,
            UsageRecord.user_id == AppUser.id,
        )
        .where(
            Router.user_subscription_id == UserSubscription.id,
            UserSubscription.user_id == AppUser.id,
            Router.isp_id == isp_id,
            AppUser.isp_id == isp_id,
        )
    )

