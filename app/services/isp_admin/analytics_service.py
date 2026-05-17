from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.app_user import AppUser
from app.models.recommendation import Recommendation
from app.models.router import Router
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import ISPAdminAnalyticsSummaryResponse
from app.services.isp_admin.ownership_scope import apply_usage_record_isp_ownership_scope


async def _count(db: AsyncSession, stmt) -> int:
    result = await db.execute(stmt)
    return int(result.scalar_one() or 0)


async def get_isp_admin_analytics_summary(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> ISPAdminAnalyticsSummaryResponse:
    total_users = await _count(
        db,
        select(func.count()).select_from(AppUser).where(AppUser.isp_id == isp_id),
    )
    active_users = await _count(
        db,
        select(func.count()).select_from(AppUser).where(
            AppUser.isp_id == isp_id,
            AppUser.status == "active",
        ),
    )

    total_subscriptions = await _count(
        db,
        select(func.count()).select_from(UserSubscription).join(
            AppUser,
            UserSubscription.user_id == AppUser.id,
        ).where(AppUser.isp_id == isp_id),
    )
    active_subscriptions = await _count(
        db,
        select(func.count()).select_from(UserSubscription).join(
            AppUser,
            UserSubscription.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            UserSubscription.status == "active",
        ),
    )

    total_routers = await _count(
        db,
        select(func.count()).select_from(Router).where(Router.isp_id == isp_id),
    )
    active_routers = await _count(
        db,
        select(func.count()).select_from(Router).where(
            Router.isp_id == isp_id,
            Router.status == "active",
        ),
    )

    pending_plan_change_requests = await _count(
        db,
        select(func.count()).select_from(SubscriptionChangeRequest).join(
            AppUser,
            SubscriptionChangeRequest.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            SubscriptionChangeRequest.status == "pending",
        ),
    )
    approved_plan_change_requests = await _count(
        db,
        select(func.count()).select_from(SubscriptionChangeRequest).join(
            AppUser,
            SubscriptionChangeRequest.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            SubscriptionChangeRequest.status == "approved",
        ),
    )
    rejected_plan_change_requests = await _count(
        db,
        select(func.count()).select_from(SubscriptionChangeRequest).join(
            AppUser,
            SubscriptionChangeRequest.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            SubscriptionChangeRequest.status == "rejected",
        ),
    )

    total_alerts = await _count(
        db,
        select(func.count()).select_from(Alert).join(
            AppUser,
            Alert.user_id == AppUser.id,
        ).where(AppUser.isp_id == isp_id),
    )
    unread_alerts = await _count(
        db,
        select(func.count()).select_from(Alert).join(
            AppUser,
            Alert.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            Alert.status == "unread",
        ),
    )
    critical_alerts = await _count(
        db,
        select(func.count()).select_from(Alert).join(
            AppUser,
            Alert.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            Alert.severity == "critical",
        ),
    )

    total_recommendations = await _count(
        db,
        select(func.count()).select_from(Recommendation).join(
            AppUser,
            Recommendation.user_id == AppUser.id,
        ).where(AppUser.isp_id == isp_id),
    )
    new_recommendations = await _count(
        db,
        select(func.count()).select_from(Recommendation).join(
            AppUser,
            Recommendation.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            Recommendation.status == "new",
        ),
    )
    accepted_recommendations = await _count(
        db,
        select(func.count()).select_from(Recommendation).join(
            AppUser,
            Recommendation.user_id == AppUser.id,
        ).where(
            AppUser.isp_id == isp_id,
            Recommendation.status == "accepted",
        ),
    )

    usage_stmt = apply_usage_record_isp_ownership_scope(
        select(func.coalesce(func.sum(UsageRecord.total_mb), 0)).select_from(UsageRecord),
        isp_id=isp_id,
    )

    if period_start is not None:
        usage_stmt = usage_stmt.where(UsageRecord.record_start >= period_start)

    if period_end is not None:
        usage_stmt = usage_stmt.where(UsageRecord.record_end <= period_end)

    usage_result = await db.execute(usage_stmt)
    total_usage_mb = Decimal(str(usage_result.scalar_one() or 0))
    total_usage_gb = total_usage_mb / Decimal("1024")

    return ISPAdminAnalyticsSummaryResponse(
        isp_id=isp_id,
        generated_at=datetime.now(timezone.utc),
        period_start=period_start,
        period_end=period_end,
        total_users=total_users,
        active_users=active_users,
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        total_routers=total_routers,
        active_routers=active_routers,
        pending_plan_change_requests=pending_plan_change_requests,
        approved_plan_change_requests=approved_plan_change_requests,
        rejected_plan_change_requests=rejected_plan_change_requests,
        total_alerts=total_alerts,
        unread_alerts=unread_alerts,
        critical_alerts=critical_alerts,
        total_recommendations=total_recommendations,
        new_recommendations=new_recommendations,
        accepted_recommendations=accepted_recommendations,
        total_usage_mb=total_usage_mb,
        total_usage_gb=total_usage_gb,
    )




