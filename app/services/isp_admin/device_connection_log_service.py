from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_connection_log import DeviceConnectionLog
from app.models.router import Router


async def list_device_connection_logs_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    router_id: UUID | None = None,
    device_id: UUID | None = None,
    event_type: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[DeviceConnectionLog]:
    stmt = (
        select(DeviceConnectionLog)
        .join(Router, DeviceConnectionLog.router_id == Router.id)
        .where(Router.isp_id == isp_id)
        .order_by(DeviceConnectionLog.event_time.desc())
        .limit(limit)
        .offset(offset)
    )

    if router_id is not None:
        stmt = stmt.where(DeviceConnectionLog.router_id == router_id)

    if device_id is not None:
        stmt = stmt.where(DeviceConnectionLog.device_id == device_id)

    if event_type is not None:
        stmt = stmt.where(DeviceConnectionLog.event_type == event_type)

    if start_at is not None:
        stmt = stmt.where(DeviceConnectionLog.event_time >= start_at)

    if end_at is not None:
        stmt = stmt.where(DeviceConnectionLog.event_time <= end_at)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_device_connection_log_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    connection_log_id: UUID,
) -> DeviceConnectionLog | None:
    stmt = (
        select(DeviceConnectionLog)
        .join(Router, DeviceConnectionLog.router_id == Router.id)
        .where(
            DeviceConnectionLog.id == connection_log_id,
            Router.isp_id == isp_id,
        )
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
