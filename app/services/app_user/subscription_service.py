from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.app_user import AppUser
from app.models.user_subscription import UserSubscription


async def list_my_subscriptions(
    db: AsyncSession,
    current_user: AppUser,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[UserSubscription]:
    stmt = (
        select(UserSubscription)
        .options(selectinload(UserSubscription.plan))
        .where(UserSubscription.user_id == current_user.id)
        .order_by(UserSubscription.created_at.desc())
    )

    if status is not None:
        stmt = stmt.where(UserSubscription.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_subscription(
    db: AsyncSession,
    current_user: AppUser,
    subscription_id: UUID,
) -> UserSubscription | None:
    result = await db.execute(
        select(UserSubscription)
        .options(selectinload(UserSubscription.plan))
        .where(
            UserSubscription.id == subscription_id,
            UserSubscription.user_id == current_user.id,
        )
    )

    return result.scalar_one_or_none()
