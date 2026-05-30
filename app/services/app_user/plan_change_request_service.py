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

_PLAN_CHANGE_REQUEST_TYPES = {"upgrade", "downgrade"}

_CONFIRMATION_TEXT_BY_REQUEST_TYPE = {
    "upgrade": "CHANGE PLAN",
    "downgrade": "CHANGE PLAN",
    "suspend_subscription": "SUSPEND SUBSCRIPTION",
    "suspend_account": "SUSPEND ACCOUNT",
}


_REQUEST_TYPE_LABELS = {
    "upgrade": "plan upgrade",
    "downgrade": "plan downgrade",
    "suspend_subscription": "subscription suspension",
    "suspend_account": "account suspension",
}


class PlanChangeRequestValidationError(ValueError):
    """Raised when an App User service request is invalid."""


def _confirmation_matches(*, request_type: str, confirmation_text: str | None) -> bool:
    expected = _CONFIRMATION_TEXT_BY_REQUEST_TYPE.get(request_type)

    if expected is None:
        return False

    normalized_confirmation = (confirmation_text or "").strip().upper()
    return normalized_confirmation == expected


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


async def _get_isp_plan_by_id(
    *,
    db: AsyncSession,
    current_user: AppUser,
    plan_id: UUID,
) -> SubscriptionPlan | None:
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.id == plan_id,
        SubscriptionPlan.isp_id == current_user.isp_id,
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


async def _has_pending_request_for_subscription(
    *,
    db: AsyncSession,
    current_user: AppUser,
    subscription_id: UUID,
    request_type: str,
) -> bool:
    stmt = select(SubscriptionChangeRequest.id).where(
        SubscriptionChangeRequest.user_id == current_user.id,
        SubscriptionChangeRequest.user_subscription_id == subscription_id,
        SubscriptionChangeRequest.request_type == request_type,
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
        raise PlanChangeRequestValidationError(
            "Selected subscription does not belong to this account."
        )

    if not _confirmation_matches(
        request_type=data.request_type,
        confirmation_text=data.confirmation_text,
    ):
        expected_confirmation = _CONFIRMATION_TEXT_BY_REQUEST_TYPE.get(
            data.request_type,
            "the required confirmation phrase",
        )
        raise PlanChangeRequestValidationError(
            f"Type {expected_confirmation} exactly to confirm this request."
        )

    if data.request_type in _PLAN_CHANGE_REQUEST_TYPES:
        if data.requested_plan_id is None:
            raise PlanChangeRequestValidationError("Select a target plan first.")

        requested_plan = await _get_active_isp_plan(
            db=db,
            current_user=current_user,
            plan_id=data.requested_plan_id,
        )

        if requested_plan is None:
            raise PlanChangeRequestValidationError(
                "Selected target plan is not active or does not belong to this ISP."
            )

        if subscription.plan_id == requested_plan.id:
            raise PlanChangeRequestValidationError(
                "You already have this plan on the selected service line."
            )

    elif data.request_type == "suspend_subscription":
        if subscription.status == "suspended":
            raise PlanChangeRequestValidationError(
                "This subscription is already suspended."
            )

        requested_plan = await _get_isp_plan_by_id(
            db=db,
            current_user=current_user,
            plan_id=subscription.plan_id,
        )

        if requested_plan is None:
            raise PlanChangeRequestValidationError(
                "The current plan for this subscription no longer exists."
            )

    elif data.request_type == "suspend_account":
        if current_user.status == "suspended":
            raise PlanChangeRequestValidationError(
                "Your account is already suspended."
            )

        requested_plan = await _get_isp_plan_by_id(
            db=db,
            current_user=current_user,
            plan_id=subscription.plan_id,
        )

        if requested_plan is None:
            raise PlanChangeRequestValidationError(
                "The current plan for this account no longer exists."
            )

    else:
        raise PlanChangeRequestValidationError("Unsupported service request type.")

    if data.recommendation_id is not None:
        if data.request_type not in _PLAN_CHANGE_REQUEST_TYPES:
            raise PlanChangeRequestValidationError(
                "Recommendations can only create plan upgrade or downgrade requests."
            )

        recommendation = await _get_owned_recommendation(
            db=db,
            current_user=current_user,
            recommendation_id=data.recommendation_id,
        )

        if recommendation is None:
            raise PlanChangeRequestValidationError(
                "Selected recommendation does not belong to this account."
            )

        expected_request_type = _RECOMMENDATION_TYPE_TO_REQUEST_TYPE.get(
            recommendation.recommendation_type
        )

        if expected_request_type is None:
            raise PlanChangeRequestValidationError(
                "Selected recommendation cannot create a plan change request."
            )

        if data.request_type != expected_request_type:
            raise PlanChangeRequestValidationError(
                "Selected recommendation does not match this request type."
            )

        if recommendation.user_subscription_id != subscription.id:
            raise PlanChangeRequestValidationError(
                "Selected recommendation does not match this subscription."
            )

        if recommendation.recommendation_plan_id != requested_plan.id:
            raise PlanChangeRequestValidationError(
                "Selected recommendation does not match the requested plan."
            )

        if recommendation.current_plan_id is not None:
            if recommendation.current_plan_id != subscription.plan_id:
                raise PlanChangeRequestValidationError(
                    "Selected recommendation is no longer valid for your current plan."
                )

        if await _has_pending_request_for_recommendation(
            db=db,
            current_user=current_user,
            recommendation_id=recommendation.id,
        ):
            raise PlanChangeRequestValidationError(
                "A pending request already exists for this recommendation."
            )

        recommendation.status = "accepted"

    if await _has_pending_request_for_subscription(
        db=db,
        current_user=current_user,
        subscription_id=subscription.id,
        request_type=data.request_type,
    ):
        request_label = _REQUEST_TYPE_LABELS.get(data.request_type, "service")
        raise PlanChangeRequestValidationError(
            f"A pending {request_label} request already exists for this service line."
        )

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
