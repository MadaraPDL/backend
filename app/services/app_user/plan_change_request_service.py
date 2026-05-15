from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.recommendation import Recommendation
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.app_user import MyPlanChangeRequestCreate


async def list_my_plan_change_requests(
    *,
    db: AsyncSession,
    current_user: AppUser,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[SubscriptionChangeRequest]:
    stmt = (
        select(SubscriptionChangeRequest)
        .where(SubscriptionChangeRequest.user_id == current_user.id)
        .order_by(SubscriptionChangeRequest.requested_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if status is not None:
        stmt = stmt.where(SubscriptionChangeRequest.status == status)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_plan_change_request(
    *,
    db: AsyncSession,
    current_user: AppUser,
    request_id: UUID,
) -> SubscriptionChangeRequest | None:
    stmt = select(SubscriptionChangeRequest).where(
        SubscriptionChangeRequest.id == request_id,
        SubscriptionChangeRequest.user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_my_plan_change_request(
    *,
    db: AsyncSession,
    current_user: AppUser,
    data: MyPlanChangeRequestCreate,
) -> SubscriptionChangeRequest | None:
    subscription_stmt = select(UserSubscription).where(
        UserSubscription.id == data.user_subscription_id,
        UserSubscription.user_id == current_user.id,
    )
    subscription_result = await db.execute(subscription_stmt)
    subscription = subscription_result.scalar_one_or_none()

    if subscription is None:
        return None

    plan_stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.id == data.requested_plan_id,
        SubscriptionPlan.isp_id == current_user.isp_id,
    )
    plan_result = await db.execute(plan_stmt)
    requested_plan = plan_result.scalar_one_or_none()

    if requested_plan is None:
        return None
    
    if subscription.plan_id == requested_plan.id:
        return None

    if data.recommendation_id is not None:
        recommendation_stmt = select(Recommendation).where(
            Recommendation.id == data.recommendation_id,
            Recommendation.user_id == current_user.id,
        )
        recommendation_result = await db.execute(recommendation_stmt)
        recommendation = recommendation_result.scalar_one_or_none()

        if recommendation is None:
            return None

    change_request = SubscriptionChangeRequest(
        user_id=current_user.id,
        user_subscription_id=subscription.id,
        current_plan_id=subscription.plan_id,
        requested_plan_id=requested_plan.id,
        recommendation_id=data.recommendation_id,
        request_type=data.request_type,
        reason=data.reason,
    )

    db.add(change_request)
    await db.commit()
    await db.refresh(change_request)

    return change_request