from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import PushTokenRegisterRequest, PushTokenResponse
from app.services.app_user import (
    disable_my_push_token,
    list_my_push_tokens,
    register_my_push_token,
)
from app.services.notifications import dispatch_push_to_user

router = APIRouter(prefix="/me/push-tokens", tags=["App User"])


@router.post("", response_model=PushTokenResponse)
async def register_my_push_token_endpoint(
    payload: PushTokenRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> PushTokenResponse:
    return await register_my_push_token(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.post("/test")
async def send_test_push_notification_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> dict[str, int]:
    result = await dispatch_push_to_user(
        db=db,
        user_id=current_user.id,
        title="PulseFi test notification",
        body="Push notifications are connected for this device.",
        data={
            "screen": "Alerts",
            "type": "test_push",
        },
    )

    return {
        "attempted": result.attempted,
        "accepted": result.accepted,
        "failed": result.failed,
    }


@router.get("", response_model=list[PushTokenResponse])
async def list_my_push_tokens_endpoint(
    active_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[PushTokenResponse]:
    return await list_my_push_tokens(
        db=db,
        current_user=current_user,
        active_only=active_only,
    )


@router.delete("/{token_id}", response_model=PushTokenResponse)
async def disable_my_push_token_endpoint(
    token_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> PushTokenResponse:
    token = await disable_my_push_token(
        db=db,
        current_user=current_user,
        token_id=token_id,
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Push token not found",
        )

    return token
