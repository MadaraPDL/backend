from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.usage_ingestion import simulator_full_ingestion_service
from app.services.usage_ingestion.simulator_device_service import (
    _build_simulator_devices,
    _connection_event_type,
)
from app.services.usage_ingestion.simulator_full_ingestion_service import (
    run_full_simulator_ingestion_for_router,
)


def test_simulator_device_payloads_are_deterministic_for_router():
    router_id = uuid4()

    first_payloads = _build_simulator_devices(router_id)
    second_payloads = _build_simulator_devices(router_id)

    assert first_payloads == second_payloads
    assert len(first_payloads) == 3

    mac_addresses = [payload.mac_address for payload in first_payloads]

    assert len(mac_addresses) == len(set(mac_addresses))
    assert all(mac.startswith("02:") for mac in mac_addresses)


def test_simulator_connection_event_type_uses_allowed_values():
    assert _connection_event_type(None) == "reconnected"
    assert _connection_event_type("disconnected") == "reconnected"
    assert _connection_event_type("connected") == "connected"

    # Regression guard: the database check constraint rejected "seen".
    assert _connection_event_type("connected") != "seen"


@pytest.mark.asyncio
async def test_full_simulator_ingestion_runs_devices_before_usage(monkeypatch):
    calls: list[str] = []

    router_id = uuid4()
    isp_id = uuid4()
    user_id = uuid4()
    subscription_id = uuid4()
    record_start = datetime(2026, 5, 16, 9, 0, tzinfo=timezone.utc)
    record_end = datetime(2026, 5, 16, 10, 0, tzinfo=timezone.utc)

    async def fake_device_ingestion(db, router_id, isp_id=None):
        calls.append("devices")

        return SimpleNamespace(
            router_id=router_id,
            user_id=user_id,
            user_subscription_id=subscription_id,
            devices_seen=3,
            devices_created=0,
            devices_updated=3,
            connection_logs_created=3,
        )

    async def fake_usage_ingestion(
        db,
        router_id,
        isp_id=None,
        record_start=None,
        record_end=None,
    ):
        calls.append("usage")

        assert record_start == datetime(2026, 5, 16, 9, 0, tzinfo=timezone.utc)
        assert record_end == datetime(2026, 5, 16, 10, 0, tzinfo=timezone.utc)

        return SimpleNamespace(
            router_id=router_id,
            user_id=user_id,
            user_subscription_id=subscription_id,
            record_start=record_start,
            record_end=record_end,
            records_created=3,
            upload_mb=10,
            download_mb=90,
            total_mb=100,
        )

    monkeypatch.setattr(
        simulator_full_ingestion_service,
        "run_simulator_device_ingestion_for_router",
        fake_device_ingestion,
    )
    monkeypatch.setattr(
        simulator_full_ingestion_service,
        "run_simulator_usage_ingestion_for_router",
        fake_usage_ingestion,
    )

    result = await run_full_simulator_ingestion_for_router(
        db=None,
        router_id=router_id,
        isp_id=isp_id,
        record_start=record_start,
        record_end=record_end,
    )

    assert calls == ["devices", "usage"]
    assert result.device_ingestion.devices_updated == 3
    assert result.usage_ingestion.records_created == 3
