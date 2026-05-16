from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import ISPAdminPlanChangeRequestReviewRequest


async def list_plan_change_requests_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    user_id: UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[SubscriptionChangeRequest]:
    stmt = (
        select(SubscriptionChangeRequest)
        .join(AppUser, SubscriptionChangeRequest.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .order_by(SubscriptionChangeRequest.requested_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if user_id is not None:
        stmt = stmt.where(SubscriptionChangeRequest.user_id == user_id)

    if status is not None:
        stmt = stmt.where(SubscriptionChangeRequest.status == status)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_plan_change_request_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    request_id: UUID,
) -> SubscriptionChangeRequest | None:
    stmt = (
        select(SubscriptionChangeRequest)
        .join(AppUser, SubscriptionChangeRequest.user_id == AppUser.id)
        .where(
            SubscriptionChangeRequest.id == request_id,
            AppUser.isp_id == isp_id,
        )
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_subscription_for_plan_change_request(
    db: AsyncSession,
    change_request: SubscriptionChangeRequest,
) -> UserSubscription | None:
    result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.id == change_request.user_subscription_id,
            UserSubscription.user_id == change_request.user_id,
        )
    )

    return result.scalar_one_or_none()


async def _get_active_requested_plan_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    change_request: SubscriptionChangeRequest,
) -> SubscriptionPlan | None:
    result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.id == change_request.requested_plan_id,
            SubscriptionPlan.isp_id == isp_id,
            SubscriptionPlan.is_active.is_(True),
        )
    )

    return result.scalar_one_or_none()


async def review_plan_change_request_for_isp(
    db: AsyncSession,
    change_request: SubscriptionChangeRequest,
    current_admin: Admin,
    request: ISPAdminPlanChangeRequestReviewRequest,
) -> SubscriptionChangeRequest | None:
    if change_request.status != "pending":
        return None

    if current_admin.isp_id is None:
        return None

    now = datetime.now(timezone.utc)
    admin_response = (
        request.admin_response.strip()
        if request.admin_response is not None
        else None
    )

    if request.decision == "approve":
        subscription = await _get_subscription_for_plan_change_request(
            db=db,
            change_request=change_request,
        )

        if subscription is None:
            return None

        requested_plan = await _get_active_requested_plan_for_isp(
            db=db,
            isp_id=current_admin.isp_id,
            change_request=change_request,
        )

        if requested_plan is None:
            return None

        subscription.plan_id = requested_plan.id
        subscription.updated_at = now
        change_request.status = "approved"

    elif request.decision == "reject":
        change_request.status = "rejected"

    change_request.reviewed_by_admin_id = current_admin.id
    change_request.reviewed_at = now
    change_request.admin_response = admin_response
    change_request.updated_at = now

    await db.flush()
    await db.refresh(change_request)

    return change_request
