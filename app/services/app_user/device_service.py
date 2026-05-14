from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.device import Device


async def list_my_devices(
    db: AsyncSession,
    current_user: AppUser,
    router_id: UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Device]:
    stmt = (
        select(Device)
        .where(Device.user_id == current_user.id)
        .order_by(Device.updated_at.desc())
    )

    if router_id is not None:
        stmt = stmt.where(Device.router_id == router_id)

    if status is not None:
        stmt = stmt.where(Device.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_device(
    db: AsyncSession,
    current_user: AppUser,
    device_id: UUID,
) -> Device | None:
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == current_user.id,
        )
    )

    return result.scalar_one_or_none()
