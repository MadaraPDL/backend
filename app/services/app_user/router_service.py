from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.router import Router
from app.models.user_subscription import UserSubscription


async def list_my_routers(
    db: AsyncSession,
    current_user: AppUser,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Router]:
    stmt = (
        select(Router)
        .join(UserSubscription, Router.user_subscription_id == UserSubscription.id)
        .where(UserSubscription.user_id == current_user.id)
        .order_by(Router.created_at.desc())
    )

    if status is not None:
        stmt = stmt.where(Router.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_router(
    db: AsyncSession,
    current_user: AppUser,
    router_id: UUID,
) -> Router | None:
    result = await db.execute(
        select(Router)
        .join(UserSubscription, Router.user_subscription_id == UserSubscription.id)
        .where(
            Router.id == router_id,
            UserSubscription.user_id == current_user.id,
        )
    )

    return result.scalar_one_or_none()
