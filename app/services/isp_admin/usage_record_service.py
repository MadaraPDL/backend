from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage_record import UsageRecord
from app.schemas.isp_admin.usage_records import ISPAdminDailyUsageResponse, ISPAdminUsageTotalsResponse
from app.services.isp_admin.ownership_scope import (
    apply_usage_record_isp_ownership_scope,
)



def _decimal_or_zero(value: object):
    from decimal import Decimal

    if value is None:
        return Decimal("0")

    return Decimal(str(value))


def _usage_total_expression():
    return func.coalesce(
        UsageRecord.total_mb,
        UsageRecord.upload_mb + UsageRecord.download_mb,
    )


def _build_totals_response(row) -> ISPAdminUsageTotalsResponse:
    return ISPAdminUsageTotalsResponse(
        upload_mb=_decimal_or_zero(row.upload_mb),
        download_mb=_decimal_or_zero(row.download_mb),
        total_mb=_decimal_or_zero(row.total_mb),
        record_count=int(row.record_count or 0),
        first_record_start=row.first_record_start,
        last_record_end=row.last_record_end,
    )


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
    stmt = apply_usage_record_isp_ownership_scope(
        select(UsageRecord),
        isp_id=isp_id,
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

    stmt = (
        stmt.order_by(UsageRecord.record_start.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_usage_record_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    usage_record_id: UUID,
) -> UsageRecord | None:
    stmt = apply_usage_record_isp_ownership_scope(
        select(UsageRecord),
        isp_id=isp_id,
    ).where(UsageRecord.id == usage_record_id)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()



async def list_daily_usage_for_isp(
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
    days: int = 7,
) -> list[ISPAdminDailyUsageResponse]:
    if start_at is None and end_at is None:
        now = datetime.utcnow()
        today_start = datetime(year=now.year, month=now.month, day=now.day)
        start_at = today_start - timedelta(days=max(days - 1, 0))

    total_expr = _usage_total_expression()
    usage_date_expr = func.date(UsageRecord.record_start).label("usage_date")

    def build_daily_stmt():
        stmt = apply_usage_record_isp_ownership_scope(
            select(
                usage_date_expr,
                func.coalesce(func.sum(UsageRecord.upload_mb), 0).label("upload_mb"),
                func.coalesce(func.sum(UsageRecord.download_mb), 0).label("download_mb"),
                func.coalesce(func.sum(total_expr), 0).label("total_mb"),
                func.count(UsageRecord.id).label("record_count"),
                func.min(UsageRecord.record_start).label("first_record_start"),
                func.max(UsageRecord.record_end).label("last_record_end"),
            ),
            isp_id=isp_id,
        ).group_by(usage_date_expr).order_by(usage_date_expr.desc())

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

        return stmt

    if device_id is not None:
        result = await db.execute(build_daily_stmt())

        return [
            ISPAdminDailyUsageResponse(
                usage_date=row.usage_date,
                totals=_build_totals_response(row),
            )
            for row in result
        ]

    official_result = await db.execute(
        build_daily_stmt().where(UsageRecord.device_id.is_(None))
    )
    estimated_result = await db.execute(
        build_daily_stmt().where(UsageRecord.device_id.is_not(None))
    )

    rows_by_date = {}

    for row in official_result:
        rows_by_date[row.usage_date] = row

    for row in estimated_result:
        rows_by_date.setdefault(row.usage_date, row)

    return [
        ISPAdminDailyUsageResponse(
            usage_date=row.usage_date,
            totals=_build_totals_response(row),
        )
        for row in sorted(
            rows_by_date.values(),
            key=lambda item: item.usage_date,
            reverse=True,
        )
    ]
