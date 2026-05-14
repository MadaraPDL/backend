from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import MySubscriptionResponse
from app.services.app_user import (
    get_my_subscription,
    list_my_subscriptions,
)


SubscriptionStatusFilter = Literal[
    "pending",
    "active",
    "suspended",
    "expired",
    "cancelled",
]


router = APIRouter(prefix="/me/subscriptions", tags=["App User"])


@router.get(
    "",
    response_model=list[MySubscriptionResponse],
)
async def list_my_subscriptions_endpoint(
    status_filter: SubscriptionStatusFilter | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MySubscriptionResponse]:
    subscriptions = await list_my_subscriptions(
        db=db,
        current_user=current_user,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [
        MySubscriptionResponse.model_validate(subscription)
        for subscription in subscriptions
    ]


@router.get(
    "/{subscription_id}",
    response_model=MySubscriptionResponse,
)
async def get_my_subscription_endpoint(
    subscription_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MySubscriptionResponse:
    subscription = await get_my_subscription(
        db=db,
        current_user=current_user,
        subscription_id=subscription_id,
    )

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    return MySubscriptionResponse.model_validate(subscription)
