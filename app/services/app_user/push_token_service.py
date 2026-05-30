from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.app_user_push_token import AppUserPushToken
from app.schemas.app_user.push_tokens import PushTokenRegisterRequest


async def register_my_push_token(
    *,
    db: AsyncSession,
    current_user: AppUser,
    payload: PushTokenRegisterRequest,
) -> AppUserPushToken:
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(AppUserPushToken).where(
            AppUserPushToken.expo_push_token == payload.expo_push_token
        )
    )
    token = result.scalar_one_or_none()

    if token is None:
        token = AppUserPushToken(
            user_id=current_user.id,
            expo_push_token=payload.expo_push_token,
            platform=payload.platform,
            device_id=payload.device_id,
            permission_status=payload.permission_status,
            is_active=True,
            last_registered_at=now,
            disabled_at=None,
            updated_at=now,
        )
        db.add(token)
    else:
        token.user_id = current_user.id
        token.platform = payload.platform
        token.device_id = payload.device_id
        token.permission_status = payload.permission_status
        token.is_active = True
        token.last_registered_at = now
        token.disabled_at = None
        token.updated_at = now

    await db.commit()
    await db.refresh(token)

    return token


async def list_my_push_tokens(
    *,
    db: AsyncSession,
    current_user: AppUser,
    active_only: bool = True,
) -> list[AppUserPushToken]:
    query = select(AppUserPushToken).where(
        AppUserPushToken.user_id == current_user.id
    )

    if active_only:
        query = query.where(AppUserPushToken.is_active.is_(True))

    query = query.order_by(AppUserPushToken.last_registered_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def disable_my_push_token(
    *,
    db: AsyncSession,
    current_user: AppUser,
    token_id: UUID,
) -> AppUserPushToken | None:
    result = await db.execute(
        select(AppUserPushToken).where(
            AppUserPushToken.id == token_id,
            AppUserPushToken.user_id == current_user.id,
        )
    )
    token = result.scalar_one_or_none()

    if token is None:
        return None

    now = datetime.now(timezone.utc)
    token.is_active = False
    token.disabled_at = now
    token.updated_at = now

    await db.commit()
    await db.refresh(token)

    return token
