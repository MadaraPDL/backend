from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.models.user_subscription import UserSubscription


def _recommendation_isp_scope(isp_id: UUID):
    return (
        AppUser.isp_id == isp_id,
        UserSubscription.user_id == AppUser.id,
        Recommendation.user_id == AppUser.id,
        Recommendation.user_subscription_id == UserSubscription.id,
        or_(
            Recommendation.prediction_id.is_(None),
            and_(
                Recommendation.prediction_id == Prediction.id,
                Prediction.user_id == AppUser.id,
                Prediction.user_subscription_id == UserSubscription.id,
            ),
        ),
    )


def _recommendation_scope_statement(isp_id: UUID):
    return (
        select(Recommendation)
        .select_from(Recommendation)
        .join(AppUser, Recommendation.user_id == AppUser.id)
        .join(UserSubscription, Recommendation.user_subscription_id == UserSubscription.id)
        .outerjoin(Prediction, Recommendation.prediction_id == Prediction.id)
        .where(*_recommendation_isp_scope(isp_id))
    )


async def list_recommendations_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    status: str | None = None,
    user_id: UUID | None = None,
    subscription_id: UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Recommendation]:
    stmt = (
        _recommendation_scope_statement(isp_id)
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if status is not None:
        stmt = stmt.where(Recommendation.status == status)

    if user_id is not None:
        stmt = stmt.where(Recommendation.user_id == user_id)

    if subscription_id is not None:
        stmt = stmt.where(Recommendation.user_subscription_id == subscription_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_recommendation_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    recommendation_id: UUID,
) -> Recommendation | None:
    stmt = _recommendation_scope_statement(isp_id).where(
        Recommendation.id == recommendation_id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
