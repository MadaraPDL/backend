from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import (
    UserSubscriptionCreateRequest,
    UserSubscriptionUpdateRequest,
)


async def get_app_user_for_subscription_assignment(
    db: AsyncSession,
    isp_id: UUID,
    user_id: UUID,
) -> AppUser | None:
    result = await db.execute(
        select(AppUser).where(
            AppUser.id == user_id,
            AppUser.isp_id == isp_id,
        )
    )

    return result.scalar_one_or_none()


async def get_plan_for_subscription_assignment(
    db: AsyncSession,
    isp_id: UUID,
    plan_id: UUID,
) -> SubscriptionPlan | None:
    result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.id == plan_id,
            SubscriptionPlan.isp_id == isp_id,
        )
    )

    return result.scalar_one_or_none()


async def create_user_subscription_for_isp(
    db: AsyncSession,
    request: UserSubscriptionCreateRequest,
    current_admin: Admin,
) -> UserSubscription:
    subscription = UserSubscription(
        user_id=request.user_id,
        plan_id=request.plan_id,
        subscription_label=(
            request.subscription_label.strip()
            if request.subscription_label
            else None
        ),
        assigned_by_admin_id=current_admin.id,
        start_date=request.start_date,
        end_date=request.end_date,
        status=request.status,
        auto_renew=request.auto_renew,
    )

    db.add(subscription)
    await db.flush()
    await db.refresh(subscription)

    return subscription


async def list_user_subscriptions_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    user_id: UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[UserSubscription]:
    stmt = (
        select(UserSubscription)
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .order_by(UserSubscription.created_at.desc())
    )

    if user_id is not None:
        stmt = stmt.where(UserSubscription.user_id == user_id)

    if status is not None:
        stmt = stmt.where(UserSubscription.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_user_subscription_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    subscription_id: UUID,
) -> UserSubscription | None:
    result = await db.execute(
        select(UserSubscription)
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(
            UserSubscription.id == subscription_id,
            AppUser.isp_id == isp_id,
        )
    )

    return result.scalar_one_or_none()


async def update_user_subscription_for_isp(
    db: AsyncSession,
    subscription: UserSubscription,
    request: UserSubscriptionUpdateRequest,
) -> UserSubscription:
    update_data = request.model_dump(exclude_unset=True)

    if (
        "subscription_label" in update_data
        and update_data["subscription_label"] is not None
    ):
        update_data["subscription_label"] = update_data["subscription_label"].strip()

    for field, value in update_data.items():
        setattr(subscription, field, value)

    subscription.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(subscription)

    return subscription
