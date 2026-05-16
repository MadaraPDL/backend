from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.router import Router
from app.models.usage_record import UsageRecord


async def list_usage_records_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    router_id: UUID | None = None,
    user_id: UUID | None = None,
    user_subscription_id: UUID | None = None,
    device_id: UUID | None = None,
    source: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[UsageRecord]:
    stmt = (
        select(UsageRecord)
        .join(Router, UsageRecord.router_id == Router.id)
        .where(Router.isp_id == isp_id)
        .order_by(UsageRecord.record_start.desc())
        .limit(limit)
        .offset(offset)
    )

    if router_id is not None:
        stmt = stmt.where(UsageRecord.router_id == router_id)

    if user_id is not None:
        stmt = stmt.where(UsageRecord.user_id == user_id)

    if user_subscription_id is not None:
        stmt = stmt.where(UsageRecord.user_subscription_id == user_subscription_id)

    if device_id is not None:
        stmt = stmt.where(UsageRecord.device_id == device_id)

    if source is not None:
        stmt = stmt.where(UsageRecord.source == source)

    if start_at is not None:
        stmt = stmt.where(UsageRecord.record_start >= start_at)

    if end_at is not None:
        stmt = stmt.where(UsageRecord.record_end <= end_at)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_usage_record_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    usage_record_id: UUID,
) -> UsageRecord | None:
    stmt = (
        select(UsageRecord)
        .join(Router, UsageRecord.router_id == Router.id)
        .where(
            UsageRecord.id == usage_record_id,
            Router.isp_id == isp_id,
        )
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
