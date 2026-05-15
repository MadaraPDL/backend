from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.recommendation import Recommendation


async def list_my_recommendations(
        *,
        db: AsyncSession,
        current_user: AppUser,
        user_subscription_id: UUID | None = None,
        status: str | None = None,
        recommendation_type: str | None = None,
        limit: int = 50,
        offset: int =0,
) -> list[Recommendation]:
    stmt = (
        select(Recommendation)
        .where(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if user_subscription_id is not None:
        stmt = stmt.where(Recommendation.user_subscription_id == user_subscription_id)

    if status is not None:
        stmt = stmt.where(Recommendation.status == status)

    if recommendation_type is not None:
        stmt = stmt.where(Recommendation.recommendation_type == recommendation_type)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_recommendation(
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