from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
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
from app.services.usage_ingestion.simulator_usage_service import (
    _scenario_total_usage_mb,
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


def test_new_device_scenario_adds_extra_simulated_device():
    router_id = uuid4()

    normal_payloads = _build_simulator_devices(router_id)
    new_device_payloads = _build_simulator_devices(
        router_id,
        scenario="new_device",
    )

    assert len(normal_payloads) == 3
    assert len(new_device_payloads) == 4
    assert new_device_payloads[:3] == normal_payloads
    assert new_device_payloads[-1].mac_address.startswith("02:")


@pytest.mark.asyncio
async def test_plan_limit_simulator_scenarios_create_controlled_usage_amounts():
    class FakeScalarResult:
        def scalar_one_or_none(self):
            return Decimal("0")

    class FakeDb:
        async def execute(self, stmt):
            return FakeScalarResult()

    subscription = SimpleNamespace(
        id=uuid4(),
        start_date=datetime(2026, 5, 1, tzinfo=timezone.utc).date(),
        plan=SimpleNamespace(data_limit_gb=Decimal("1")),
    )

    total_mb = await _scenario_total_usage_mb(
        db=FakeDb(),
        user_subscription=subscription,
        scenario="near_plan_limit",
        record_count=3,
    )

    assert total_mb >= Decimal("972.80")


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

    async def fake_device_ingestion(db, router_id, isp_id=None, scenario="normal_usage"):
        calls.append("devices")
        assert scenario == "heavy_device_usage"

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
        scenario="normal_usage",
    ):
        calls.append("usage")
        assert scenario == "heavy_device_usage"

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
        scenario="heavy_device_usage",
    )

    assert calls == ["devices", "usage"]
    assert result.device_ingestion.devices_updated == 3
    assert result.usage_ingestion.records_created == 3
    assert result.scenario == "heavy_device_usage"
