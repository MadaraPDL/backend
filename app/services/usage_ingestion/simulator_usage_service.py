from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.router import Router
from app.models.usage_record import UsageRecord


@dataclass(frozen=True)
class SimulatorUsageIngestionResult:
    router_id: UUID
    user_id: UUID
    user_subscription_id: UUID
    record_start: datetime
    record_end: datetime
    records_created: int
    upload_mb: Decimal
    download_mb: Decimal
    total_mb: Decimal


class UsageIngestionError(RuntimeError):
    """Base error for usage ingestion failures."""


class RouterNotFoundForIngestionError(UsageIngestionError):
    """Raised when the router does not exist or is outside the allowed ISP scope."""


class RouterNotReadyForIngestionError(UsageIngestionError):
    """Raised when a router cannot be used for usage ingestion."""


def _decimal_mb(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))


def _generate_usage_amounts(device_index: int = 0) -> tuple[Decimal, Decimal]:
    upload_mb = random.uniform(2, 35) + device_index
    download_mb = random.uniform(25, 220) + (device_index * 3)

    return _decimal_mb(upload_mb), _decimal_mb(download_mb)


async def run_simulator_usage_ingestion_for_router(
    db: AsyncSession,
    router_id: UUID,
    isp_id: UUID | None = None,
    record_start: datetime | None = None,
    record_end: datetime | None = None,
) -> SimulatorUsageIngestionResult:
    now = datetime.now(timezone.utc)
    final_record_end = record_end or now
    final_record_start = record_start or (final_record_end - timedelta(hours=1))

    if final_record_start >= final_record_end:
        raise RouterNotReadyForIngestionError(
            "record_start must be before record_end."
        )

    stmt = (
        select(Router)
        .options(selectinload(Router.user_subscription))
        .where(Router.id == router_id)
    )

    if isp_id is not None:
        stmt = stmt.where(Router.isp_id == isp_id)

    result = await db.execute(stmt)
    router = result.scalar_one_or_none()

    if router is None:
        raise RouterNotFoundForIngestionError("Router not found.")

    if router.status != "active":
        raise RouterNotReadyForIngestionError(
            "Only active routers can ingest simulator usage."
        )

    if router.user_subscription is None:
        raise RouterNotReadyForIngestionError(
            "Router must be linked to a user subscription before usage ingestion."
        )

    user_subscription = router.user_subscription

    if user_subscription.status != "active":
        raise RouterNotReadyForIngestionError(
            "Router subscription must be active before usage ingestion."
        )

    device_stmt = (
        select(Device)
        .where(
            Device.router_id == router.id,
            Device.user_id == user_subscription.user_id,
            Device.status == "connected",
        )
        .order_by(Device.updated_at.desc())
    )

    device_result = await db.execute(device_stmt)
    devices = list(device_result.scalars().all())

    total_upload_mb = Decimal("0")
    total_download_mb = Decimal("0")
    records_created = 0

    if devices:
        for index, device in enumerate(devices):
            upload_mb, download_mb = _generate_usage_amounts(device_index=index)

            db.add(
                UsageRecord(
                    user_id=user_subscription.user_id,
                    user_subscription_id=user_subscription.id,
                    router_id=router.id,
                    device_id=device.id,
                    upload_mb=upload_mb,
                    download_mb=download_mb,
                    record_start=final_record_start,
                    record_end=final_record_end,
                    source="simulator",
                )
            )

            total_upload_mb += upload_mb
            total_download_mb += download_mb
            records_created += 1
    else:
        upload_mb, download_mb = _generate_usage_amounts()

        db.add(
            UsageRecord(
                user_id=user_subscription.user_id,
                user_subscription_id=user_subscription.id,
                router_id=router.id,
                device_id=None,
                upload_mb=upload_mb,
                download_mb=download_mb,
                record_start=final_record_start,
                record_end=final_record_end,
                source="simulator",
            )
        )

        total_upload_mb += upload_mb
        total_download_mb += download_mb
        records_created += 1

    await db.flush()

    return SimulatorUsageIngestionResult(
        router_id=router.id,
        user_id=user_subscription.user_id,
        user_subscription_id=user_subscription.id,
        record_start=final_record_start,
        record_end=final_record_end,
        records_created=records_created,
        upload_mb=total_upload_mb,
        download_mb=total_download_mb,
        total_mb=total_upload_mb + total_download_mb,
    )
