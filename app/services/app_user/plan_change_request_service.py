from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.recommendation import Recommendation
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.app_user import (
    MyPlanChangeRequestCreate,
    MyRecommendationPlanChangeRequestCreate,
)


_RECOMMENDATION_TYPE_TO_REQUEST_TYPE = {
    "upgrade_plan": "upgrade",
    "downgrade_plan": "downgrade",
}


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


async def _get_owned_subscription(
    *,
    db: AsyncSession,
    current_user: AppUser,
    subscription_id: UUID,
) -> UserSubscription | None:
    stmt = select(UserSubscription).where(
        UserSubscription.id == subscription_id,
        UserSubscription.user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_active_isp_plan(
    *,
    db: AsyncSession,
    current_user: AppUser,
    plan_id: UUID,
) -> SubscriptionPlan | None:
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.id == plan_id,
        SubscriptionPlan.isp_id == current_user.isp_id,
        SubscriptionPlan.is_active.is_(True),
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_owned_recommendation(
    *,
    db: AsyncSession,
    current_user: AppUser,
    recommendation_id: UUID,
) -> Recommendation | None:
    stmt = select(Recommendation).where(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _has_pending_request_for_recommendation(
    *,
    db: AsyncSession,
    current_user: AppUser,
    recommendation_id: UUID,
) -> bool:
    stmt = select(SubscriptionChangeRequest.id).where(
        SubscriptionChangeRequest.user_id == current_user.id,
        SubscriptionChangeRequest.recommendation_id == recommendation_id,
        SubscriptionChangeRequest.status == "pending",
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def create_my_plan_change_request(
    *,
    db: AsyncSession,
    current_user: AppUser,
    data: MyPlanChangeRequestCreate,
) -> SubscriptionChangeRequest | None:
    subscription = await _get_owned_subscription(
        db=db,
        current_user=current_user,
        subscription_id=data.user_subscription_id,
    )

    if subscription is None:
        return None

    requested_plan = await _get_active_isp_plan(
        db=db,
        current_user=current_user,
        plan_id=data.requested_plan_id,
    )

    if requested_plan is None:
        return None

    if subscription.plan_id == requested_plan.id:
        return None

    if data.recommendation_id is not None:
        recommendation = await _get_owned_recommendation(
            db=db,
            current_user=current_user,
            recommendation_id=data.recommendation_id,
        )

        if recommendation is None:
            return None

        expected_request_type = _RECOMMENDATION_TYPE_TO_REQUEST_TYPE.get(
            recommendation.recommendation_type
        )

        if expected_request_type is None:
            return None

        if data.request_type != expected_request_type:
            return None

        if recommendation.user_subscription_id != subscription.id:
            return None

        if recommendation.recommendation_plan_id != requested_plan.id:
            return None

        if recommendation.current_plan_id is not None:
            if recommendation.current_plan_id != subscription.plan_id:
                return None

        if await _has_pending_request_for_recommendation(
            db=db,
            current_user=current_user,
            recommendation_id=recommendation.id,
        ):
            return None

        recommendation.status = "accepted"

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


async def create_my_plan_change_request_from_recommendation(
    *,
    db: AsyncSession,
    current_user: AppUser,
    recommendation_id: UUID,
    data: MyRecommendationPlanChangeRequestCreate,
) -> SubscriptionChangeRequest | None:
    recommendation = await _get_owned_recommendation(
        db=db,
        current_user=current_user,
        recommendation_id=recommendation_id,
    )

    if recommendation is None:
        return None

    request_type = _RECOMMENDATION_TYPE_TO_REQUEST_TYPE.get(
        recommendation.recommendation_type
    )

    if request_type is None:
        return None

    if recommendation.recommendation_plan_id is None:
        return None

    subscription = await _get_owned_subscription(
        db=db,
        current_user=current_user,
        subscription_id=recommendation.user_subscription_id,
    )

    if subscription is None:
        return None

    requested_plan = await _get_active_isp_plan(
        db=db,
        current_user=current_user,
        plan_id=recommendation.recommendation_plan_id,
    )

    if requested_plan is None:
        return None

    if subscription.plan_id == requested_plan.id:
        return None

    if recommendation.current_plan_id is not None:
        if recommendation.current_plan_id != subscription.plan_id:
            return None

    if await _has_pending_request_for_recommendation(
        db=db,
        current_user=current_user,
        recommendation_id=recommendation.id,
    ):
        return None

    change_request = SubscriptionChangeRequest(
        user_id=current_user.id,
        user_subscription_id=subscription.id,
        current_plan_id=subscription.plan_id,
        requested_plan_id=requested_plan.id,
        recommendation_id=recommendation.id,
        request_type=request_type,
        reason=data.reason or recommendation.reason,
    )

    recommendation.status = "accepted"

    db.add(change_request)
    await db.commit()
    await db.refresh(change_request)

    return change_request
