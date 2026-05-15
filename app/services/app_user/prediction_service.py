from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.prediction import Prediction


async def list_my_predictions(
    *,
    db: AsyncSession,
    current_user: AppUser,
    user_subscription_id: UUID | None = None,
    risk_level: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Prediction]:
    stmt = (
        select(Prediction)
        .where(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if user_subscription_id is not None:
        stmt = stmt.where(Prediction.user_subscription_id == user_subscription_id)

    if risk_level is not None:
        stmt = stmt.where(Prediction.risk_level == risk_level)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_prediction(
    *,
    db: AsyncSession,
    current_user: AppUser,
    prediction_id: UUID,
) -> Prediction | None:
    stmt = select(Prediction).where(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
