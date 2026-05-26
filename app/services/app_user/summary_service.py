from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.user_subscription import UserSubscription
from app.schemas.app_user import AppUserSummaryResponse
from app.services.usage_summary_service import (
    build_latest_active_usage_summary_for_user,
    build_usage_summaries_for_user,
)


async def build_app_user_summary(
    db: AsyncSession,
    current_user: AppUser,
) -> AppUserSummaryResponse:
    total_subscriptions_result = await db.execute(
        select(func.count(UserSubscription.id)).where(
            UserSubscription.user_id == current_user.id,
        )
    )

    active_subscriptions_result = await db.execute(
        select(func.count(UserSubscription.id)).where(
            UserSubscription.user_id == current_user.id,
            UserSubscription.status == "active",
        )
    )

    total_subscriptions = int(total_subscriptions_result.scalar_one())
    active_subscriptions = int(active_subscriptions_result.scalar_one())
    usage_summary = await build_latest_active_usage_summary_for_user(
        db=db,
        user_id=current_user.id,
        isp_id=current_user.isp_id,
    )
    usage_summaries = await build_usage_summaries_for_user(
        db=db,
        user_id=current_user.id,
        isp_id=current_user.isp_id,
    )

    return AppUserSummaryResponse(
        id=current_user.id,
        isp_id=current_user.isp_id,
        full_name=current_user.full_name,
        email=current_user.email,
        username=current_user.username,
        phone_number=current_user.phone_number,
        status=current_user.status,
        email_verified_at=current_user.email_verified_at,
        created_at=current_user.created_at,
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        usage_summary=usage_summary,
        usage_summaries=usage_summaries,
    )
