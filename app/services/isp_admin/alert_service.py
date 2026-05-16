from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.app_user import AppUser


async def list_alerts_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    user_id: UUID | None = None,
    user_subscription_id: UUID | None = None,
    device_id: UUID | None = None,
    alert_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Alert]:
    stmt = (
        select(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if user_id is not None:
        stmt = stmt.where(Alert.user_id == user_id)

    if user_subscription_id is not None:
        stmt = stmt.where(Alert.user_subscription_id == user_subscription_id)

    if device_id is not None:
        stmt = stmt.where(Alert.device_id == device_id)

    if alert_type is not None:
        stmt = stmt.where(Alert.alert_type == alert_type)

    if severity is not None:
        stmt = stmt.where(Alert.severity == severity)

    if status is not None:
        stmt = stmt.where(Alert.status == status)

    if start_at is not None:
        stmt = stmt.where(Alert.created_at >= start_at)

    if end_at is not None:
        stmt = stmt.where(Alert.created_at <= end_at)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_alert_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    alert_id: UUID,
) -> Alert | None:
    stmt = (
        select(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .where(
            Alert.id == alert_id,
            AppUser.isp_id == isp_id,
        )
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
