from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.device import Device
from app.models.usage_record import UsageRecord
from app.schemas.app_user import (
    MyDailyUsageResponse,
    MyDeviceUsageResponse,
    MyUsageRecordResponse,
    MyUsageSummaryResponse,
    MyUsageTotalsResponse,
)


def _decimal_or_zero(value: object) -> Decimal:
    if value is None:
        return Decimal("0")

    return Decimal(str(value))


def _usage_total_expression():
    return func.coalesce(
        UsageRecord.total_mb,
        UsageRecord.upload_mb + UsageRecord.download_mb,
    )


def _build_totals_response(row) -> MyUsageTotalsResponse:
    return MyUsageTotalsResponse(
        upload_mb=_decimal_or_zero(row.upload_mb),
        download_mb=_decimal_or_zero(row.download_mb),
        total_mb=_decimal_or_zero(row.total_mb),
        record_count=int(row.record_count or 0),
        first_record_start=row.first_record_start,
        last_record_end=row.last_record_end,
    )


def _apply_usage_filters(
    stmt,
    user_subscription_id: UUID | None = None,
    router_id: UUID | None = None,
    device_id: UUID | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
):
    if user_subscription_id is not None:
        stmt = stmt.where(UsageRecord.user_subscription_id == user_subscription_id)

    if router_id is not None:
        stmt = stmt.where(UsageRecord.router_id == router_id)

    if device_id is not None:
        stmt = stmt.where(UsageRecord.device_id == device_id)

    if start_at is not None:
        stmt = stmt.where(UsageRecord.record_start >= start_at)

    if end_at is not None:
        stmt = stmt.where(UsageRecord.record_end <= end_at)

    return stmt


async def get_my_usage_summary(
    db: AsyncSession,
    current_user: AppUser,
    user_subscription_id: UUID | None = None,
    router_id: UUID | None = None,
    device_id: UUID | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> MyUsageSummaryResponse:
    total_expr = _usage_total_expression()

    stmt = select(
        func.coalesce(func.sum(UsageRecord.upload_mb), 0).label("upload_mb"),
        func.coalesce(func.sum(UsageRecord.download_mb), 0).label("download_mb"),
        func.coalesce(func.sum(total_expr), 0).label("total_mb"),
        func.count(UsageRecord.id).label("record_count"),
        func.min(UsageRecord.record_start).label("first_record_start"),
        func.max(UsageRecord.record_end).label("last_record_end"),
    ).where(UsageRecord.user_id == current_user.id)

    stmt = _apply_usage_filters(
        stmt,
        user_subscription_id=user_subscription_id,
        router_id=router_id,
        device_id=device_id,
        start_at=start_at,
        end_at=end_at,
    )

    result = await db.execute(stmt)
    row = result.one()

    return MyUsageSummaryResponse(
        user_id=current_user.id,
        totals=_build_totals_response(row),
    )



async def list_my_daily_usage(
    db: AsyncSession,
    current_user: AppUser,
    user_subscription_id: UUID | None = None,
    router_id: UUID | None = None,
    device_id: UUID | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    days: int = 7,
) -> list[MyDailyUsageResponse]:
    if start_at is None and end_at is None:
        start_at = datetime.utcnow() - timedelta(days=max(days - 1, 0))

    total_expr = _usage_total_expression()
    usage_date_expr = func.date(UsageRecord.record_start).label("usage_date")

    stmt = (
        select(
            usage_date_expr,
            func.coalesce(func.sum(UsageRecord.upload_mb), 0).label("upload_mb"),
            func.coalesce(func.sum(UsageRecord.download_mb), 0).label("download_mb"),
            func.coalesce(func.sum(total_expr), 0).label("total_mb"),
            func.count(UsageRecord.id).label("record_count"),
            func.min(UsageRecord.record_start).label("first_record_start"),
            func.max(UsageRecord.record_end).label("last_record_end"),
        )
        .where(UsageRecord.user_id == current_user.id)
        .group_by(usage_date_expr)
        .order_by(usage_date_expr.desc())
    )

    stmt = _apply_usage_filters(
        stmt,
        user_subscription_id=user_subscription_id,
        router_id=router_id,
        device_id=device_id,
        start_at=start_at,
        end_at=end_at,
    )

    result = await db.execute(stmt)

    return [
        MyDailyUsageResponse(
            usage_date=row.usage_date,
            totals=_build_totals_response(row),
        )
        for row in result
    ]


async def list_my_device_usage(
    db: AsyncSession,
    current_user: AppUser,
    router_id: UUID | None = None,
    status: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[MyDeviceUsageResponse]:
    total_expr = _usage_total_expression()

    join_conditions = [
        UsageRecord.device_id == Device.id,
        UsageRecord.user_id == current_user.id,
    ]

    if start_at is not None:
        join_conditions.append(UsageRecord.record_start >= start_at)

    if end_at is not None:
        join_conditions.append(UsageRecord.record_end <= end_at)

    stmt = (
        select(
            Device,
            func.coalesce(func.sum(UsageRecord.upload_mb), 0).label("upload_mb"),
            func.coalesce(func.sum(UsageRecord.download_mb), 0).label("download_mb"),
            func.coalesce(func.sum(total_expr), 0).label("total_mb"),
            func.count(UsageRecord.id).label("record_count"),
            func.min(UsageRecord.record_start).label("first_record_start"),
            func.max(UsageRecord.record_end).label("last_record_end"),
        )
        .outerjoin(UsageRecord, and_(*join_conditions))
        .where(Device.user_id == current_user.id)
        .group_by(Device.id)
        .order_by(Device.updated_at.desc())
    )

    if router_id is not None:
        stmt = stmt.where(Device.router_id == router_id)

    if status is not None:
        stmt = stmt.where(Device.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)

    responses: list[MyDeviceUsageResponse] = []

    for row in result:
        device = row.Device

        responses.append(
            MyDeviceUsageResponse(
                id=device.id,
                router_id=device.router_id,
                device_name=device.device_name,
                mac_address=device.mac_address,
                ip_address=device.ip_address,
                device_type=device.device_type,
                is_trusted=device.is_trusted,
                status=device.status,
                first_seen=device.first_seen,
                last_seen=device.last_seen,
                updated_at=device.updated_at,
                usage=_build_totals_response(row),
            )
        )

    return responses


async def get_my_device_usage(
    db: AsyncSession,
    current_user: AppUser,
    device_id: UUID,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> MyDeviceUsageResponse | None:
    total_expr = _usage_total_expression()

    join_conditions = [
        UsageRecord.device_id == Device.id,
        UsageRecord.user_id == current_user.id,
    ]

    if start_at is not None:
        join_conditions.append(UsageRecord.record_start >= start_at)

    if end_at is not None:
        join_conditions.append(UsageRecord.record_end <= end_at)

    stmt = (
        select(
            Device,
            func.coalesce(func.sum(UsageRecord.upload_mb), 0).label("upload_mb"),
            func.coalesce(func.sum(UsageRecord.download_mb), 0).label("download_mb"),
            func.coalesce(func.sum(total_expr), 0).label("total_mb"),
            func.count(UsageRecord.id).label("record_count"),
            func.min(UsageRecord.record_start).label("first_record_start"),
            func.max(UsageRecord.record_end).label("last_record_end"),
        )
        .outerjoin(UsageRecord, and_(*join_conditions))
        .where(
            Device.id == device_id,
            Device.user_id == current_user.id,
        )
        .group_by(Device.id)
    )

    result = await db.execute(stmt)
    row = result.one_or_none()

    if row is None:
        return None

    device = row.Device

    return MyDeviceUsageResponse(
        id=device.id,
        router_id=device.router_id,
        device_name=device.device_name,
        mac_address=device.mac_address,
        ip_address=device.ip_address,
        device_type=device.device_type,
        is_trusted=device.is_trusted,
        status=device.status,
        first_seen=device.first_seen,
        last_seen=device.last_seen,
        updated_at=device.updated_at,
        usage=_build_totals_response(row),
    )


def build_usage_record_response(record: UsageRecord) -> MyUsageRecordResponse:
    total_mb = record.total_mb

    if total_mb is None:
        total_mb = record.upload_mb + record.download_mb

    return MyUsageRecordResponse(
        id=record.id,
        user_subscription_id=record.user_subscription_id,
        router_id=record.router_id,
        device_id=record.device_id,
        upload_mb=record.upload_mb,
        download_mb=record.download_mb,
        total_mb=total_mb,
        record_start=record.record_start,
        record_end=record.record_end,
        source=record.source,
        created_at=record.created_at,
    )


async def list_my_usage_records(
    db: AsyncSession,
    current_user: AppUser,
    user_subscription_id: UUID | None = None,
    router_id: UUID | None = None,
    device_id: UUID | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[MyUsageRecordResponse]:
    stmt = (
        select(UsageRecord)
        .where(UsageRecord.user_id == current_user.id)
        .order_by(UsageRecord.record_start.desc())
    )

    stmt = _apply_usage_filters(
        stmt,
        user_subscription_id=user_subscription_id,
        router_id=router_id,
        device_id=device_id,
        start_at=start_at,
        end_at=end_at,
    )

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    records = list(result.scalars().all())

    return [build_usage_record_response(record) for record in records]
