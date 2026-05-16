from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from ipaddress import ip_address
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.device_connection_log import DeviceConnectionLog
from app.models.router import Router
from app.services.usage_ingestion.simulator_usage_service import (
    RouterNotFoundForIngestionError,
    RouterNotReadyForIngestionError,
)


@dataclass(frozen=True)
class SimulatorDevicePayload:
    device_name: str
    mac_address: str
    ip_address: str
    device_type: str


@dataclass(frozen=True)
class SimulatorDeviceIngestionResult:
    router_id: UUID
    user_id: UUID
    user_subscription_id: UUID
    devices_seen: int
    devices_created: int
    devices_updated: int
    connection_logs_created: int


def _router_mac_prefix(router_id: UUID) -> str:
    raw = router_id.hex.upper()
    return f"02:{raw[0:2]}:{raw[2:4]}:{raw[4:6]}"


def _connection_event_type(previous_status: str | None) -> str:
    if previous_status == "connected":
        return "connected"

    return "reconnected"


def _build_simulator_devices(router_id: UUID) -> list[SimulatorDevicePayload]:
    prefix = _router_mac_prefix(router_id)

    return [
        SimulatorDevicePayload(
            device_name="Simulator Phone",
            mac_address=f"{prefix}:10:01",
            ip_address="192.168.1.21",
            device_type="phone",
        ),
        SimulatorDevicePayload(
            device_name="Simulator Laptop",
            mac_address=f"{prefix}:10:02",
            ip_address="192.168.1.22",
            device_type="laptop",
        ),
        SimulatorDevicePayload(
            device_name="Simulator Smart TV",
            mac_address=f"{prefix}:10:03",
            ip_address="192.168.1.23",
            device_type="smart_tv",
        ),
    ]


async def run_simulator_device_ingestion_for_router(
    db: AsyncSession,
    router_id: UUID,
    isp_id: UUID | None = None,
) -> SimulatorDeviceIngestionResult:
    now = datetime.now(timezone.utc)

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
            "Only active routers can ingest simulator devices."
        )

    if router.user_subscription is None:
        raise RouterNotReadyForIngestionError(
            "Router must be linked to a user subscription before device ingestion."
        )

    user_subscription = router.user_subscription

    if user_subscription.status != "active":
        raise RouterNotReadyForIngestionError(
            "Router subscription must be active before device ingestion."
        )

    payloads = _build_simulator_devices(router.id)

    devices_created = 0
    devices_updated = 0
    connection_logs_created = 0

    for payload in payloads:
        device_stmt = select(Device).where(
            Device.router_id == router.id,
            Device.mac_address == payload.mac_address,
        )

        device_result = await db.execute(device_stmt)
        device = device_result.scalar_one_or_none()

        previous_status = device.status if device is not None else None

        if device is None:
            device = Device(
                router_id=router.id,
                user_id=user_subscription.user_id,
                device_name=payload.device_name,
                mac_address=payload.mac_address,
                ip_address=ip_address(payload.ip_address),
                device_type=payload.device_type,
                status="connected",
                last_seen=now,
                updated_at=now,
            )
            db.add(device)
            await db.flush()

            db.add(
                DeviceConnectionLog(
                    device_id=device.id,
                    router_id=router.id,
                    event_type="connected",
                    ip_address=ip_address(payload.ip_address),
                    details="Simulator discovered new connected device.",
                    event_time=now,
                )
            )

            devices_created += 1
            connection_logs_created += 1
            continue

        device.user_id = user_subscription.user_id
        device.device_name = payload.device_name
        device.ip_address = ip_address(payload.ip_address)
        device.device_type = payload.device_type
        device.status = "connected"
        device.last_seen = now
        device.updated_at = now

        db.add(
            DeviceConnectionLog(
                device_id=device.id,
                router_id=router.id,
                event_type=_connection_event_type(previous_status),
                ip_address=ip_address(payload.ip_address),
                details="Simulator confirmed device is connected.",
                event_time=now,
            )
        )

        devices_updated += 1
        connection_logs_created += 1

    await db.flush()

    return SimulatorDeviceIngestionResult(
        router_id=router.id,
        user_id=user_subscription.user_id,
        user_subscription_id=user_subscription.id,
        devices_seen=len(payloads),
        devices_created=devices_created,
        devices_updated=devices_updated,
        connection_logs_created=connection_logs_created,
    )


