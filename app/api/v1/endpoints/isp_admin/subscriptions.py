from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    UserSubscriptionCreateRequest,
    UserSubscriptionResponse,
    UserSubscriptionStatus,
    UserSubscriptionUpdateRequest,
)
from app.services.isp_admin import (
    create_user_subscription_for_isp,
    get_app_user_for_subscription_assignment,
    get_plan_for_subscription_assignment,
    get_user_subscription_for_isp,
    list_user_subscriptions_for_isp,
    update_user_subscription_for_isp,
)


router = APIRouter(prefix="/subscriptions")


@router.post(
    "",
    response_model=UserSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_subscription_endpoint(
    request: UserSubscriptionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> UserSubscriptionResponse:
    app_user = await get_app_user_for_subscription_assignment(
        db=db,
        isp_id=current_admin.isp_id,
        user_id=request.user_id,
    )

    if app_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App User not found",
        )

    plan = await get_plan_for_subscription_assignment(
        db=db,
        isp_id=current_admin.isp_id,
        plan_id=request.plan_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    subscription = await create_user_subscription_for_isp(
        db=db,
        request=request,
        current_admin=current_admin,
    )

    await db.commit()

    return UserSubscriptionResponse.model_validate(subscription)


@router.get(
    "",
    response_model=list[UserSubscriptionResponse],
)
async def list_user_subscriptions_endpoint(
    user_id: UUID | None = Query(default=None),
    status_filter: UserSubscriptionStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[UserSubscriptionResponse]:
    if user_id is not None:
        app_user = await get_app_user_for_subscription_assignment(
            db=db,
            isp_id=current_admin.isp_id,
            user_id=user_id,
        )

        if app_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App User not found",
            )

    subscriptions = await list_user_subscriptions_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        user_id=user_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [
        UserSubscriptionResponse.model_validate(subscription)
        for subscription in subscriptions
    ]


@router.get(
    "/{subscription_id}",
    response_model=UserSubscriptionResponse,
)
async def get_user_subscription_endpoint(
    subscription_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> UserSubscriptionResponse:
    subscription = await get_user_subscription_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        subscription_id=subscription_id,
    )

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User subscription not found",
        )

    return UserSubscriptionResponse.model_validate(subscription)


@router.patch(
    "/{subscription_id}",
    response_model=UserSubscriptionResponse,
)
async def update_user_subscription_endpoint(
    subscription_id: UUID,
    request: UserSubscriptionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> UserSubscriptionResponse:
    subscription = await get_user_subscription_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        subscription_id=subscription_id,
    )

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User subscription not found",
        )

    if request.plan_id is not None:
        plan = await get_plan_for_subscription_assignment(
            db=db,
            isp_id=current_admin.isp_id,
            plan_id=request.plan_id,
        )

        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found",
            )

    updated_subscription = await update_user_subscription_for_isp(
        db=db,
        subscription=subscription,
        request=request,
    )

    await db.commit()

    return UserSubscriptionResponse.model_validate(updated_subscription)
