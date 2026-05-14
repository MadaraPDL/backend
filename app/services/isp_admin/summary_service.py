from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.router import Router
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin.summary import ISPAdminSummaryResponse, StatusCounts


def _build_status_counts(rows: list[tuple[str, int]]) -> StatusCounts:
    data = {"total": 0}

    for status, count in rows:
        if status is None:
            continue

        data[status] = count
        data["total"] += count

    return StatusCounts(**data)


async def _count_by_status(
    db: AsyncSession,
    model,
    *,
    isp_id: UUID,
) -> StatusCounts:
    result = await db.execute(
        select(model.status, func.count(model.id))
        .where(model.isp_id == isp_id)
        .group_by(model.status)
    )

    return _build_status_counts(list(result.all()))


async def _count_plans(
    db: AsyncSession,
    *,
    isp_id: UUID,
) -> StatusCounts:
    result = await db.execute(
        select(SubscriptionPlan.is_active, func.count(SubscriptionPlan.id))
        .where(SubscriptionPlan.isp_id == isp_id)
        .group_by(SubscriptionPlan.is_active)
    )

    counts = StatusCounts()

    for is_active, count in result.all():
        counts.total += count

        if is_active:
            counts.active += count
        else:
            counts.inactive += count

    return counts


async def _count_subscriptions(
    db: AsyncSession,
    *,
    isp_id: UUID,
) -> StatusCounts:
    result = await db.execute(
        select(UserSubscription.status, func.count(UserSubscription.id))
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(UserSubscription.status)
    )

    return _build_status_counts(list(result.all()))


async def get_isp_admin_summary(
    db: AsyncSession,
    *,
    isp_id: UUID,
) -> ISPAdminSummaryResponse:
    users = await _count_by_status(db, AppUser, isp_id=isp_id)
    plans = await _count_plans(db, isp_id=isp_id)
    subscriptions = await _count_subscriptions(db, isp_id=isp_id)
    routers = await _count_by_status(db, Router, isp_id=isp_id)

    return ISPAdminSummaryResponse(
        isp_id=str(isp_id),
        users=users,
        plans=plans,
        subscriptions=subscriptions,
        routers=routers,
    )
