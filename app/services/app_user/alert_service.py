from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.app_user import AppUser


async def list_my_alerts(
        *,
        db: AsyncSession,
        current_user: AppUser,
        status: str | None = None,
        severity: str | None = None,
        alert_type: str | None = None,
        limit: int = 20,
        offset: int = 0,
) -> list[Alert]:
    stmt= (
        select(Alert)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if status is not None:
        stmt = stmt.where(Alert.status == status)


    if severity is not None:
        stmt = stmt.where(Alert.severity == severity)


    if alert_type is not None:
        stmt = stmt.where(Alert.alert_type == alert_type)


    result = await db.execute(stmt)
    return result.scalars().all()


async def get_my_alert(
        *,
        db: AsyncSession,
        current_user: AppUser,
        alert_id: UUID,
) -> Alert | None:
    stmt = select(Alert).where(
        Alert.id == alert_id,
        Alert.user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_my_alert_as_read(
        *,
        db : AsyncSession,
        current_user: AppUser,
        alert_id: UUID,
) -> Alert | None:
    alert = await get_my_alert(
        db=db,
        current_user=current_user,
        alert_id=alert_id,
    )

    if alert is None:
        return None
    
    if alert.status != "read":
        alert.status = "read"
        alert.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(alert)


    return alert