from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.schemas.isp_admin import AppUserUpdateRequest


async def list_app_users_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AppUser]:
    stmt = (
        select(AppUser)
        .where(AppUser.isp_id == isp_id)
        .order_by(AppUser.created_at.desc())
    )

    if status is not None:
        stmt = stmt.where(AppUser.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_app_user_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    user_id: UUID,
) -> AppUser | None:
    result = await db.execute(
        select(AppUser).where(
            AppUser.id == user_id,
            AppUser.isp_id == isp_id,
        )
    )

    return result.scalar_one_or_none()


async def update_app_user_for_isp(
    db: AsyncSession,
    app_user: AppUser,
    request: AppUserUpdateRequest,
) -> AppUser:
    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(app_user, field, value)

    app_user.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(app_user)

    return app_user
