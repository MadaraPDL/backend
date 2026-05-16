from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.alert import Alert
from app.services.alerts import alert_generation_service
from app.services.alerts.alert_generation_service import (
    generate_policy_failed_alert_for_policy,
    generate_usage_alerts_for_subscription,
)


class FakeScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeOneResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeDb:
    def __init__(self, execute_values):
        self.execute_values = list(execute_values)
        self.added = []
        self.flush_called = False

    async def execute(self, stmt):
        if not self.execute_values:
            raise AssertionError("Unexpected db.execute call")

        return self.execute_values.pop(0)

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        self.flush_called = True


@pytest.mark.asyncio
async def test_generate_plan_exceed_alert(monkeypatch):
    user_id = uuid4()
    subscription_id = uuid4()

    subscription = SimpleNamespace(
        id=subscription_id,
        user_id=user_id,
        status="active",
        start_date=date.today(),
        plan=SimpleNamespace(
            data_limit_gb=Decimal("0.01"),
        ),
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(subscription),
            FakeScalarResult(Decimal("50")),
        ]
    )

    async def fake_open_alert_exists(**kwargs):
        return False

    async def fake_get_latest_usage_id(**kwargs):
        return uuid4()

    async def fake_get_latest_window_total_mb(**kwargs):
        return None

    monkeypatch.setattr(
        alert_generation_service,
        "_open_alert_exists",
        fake_open_alert_exists,
    )
    monkeypatch.setattr(
        alert_generation_service,
        "_get_latest_usage_id",
        fake_get_latest_usage_id,
    )
    monkeypatch.setattr(
        alert_generation_service,
        "_get_latest_window_total_mb",
        fake_get_latest_window_total_mb,
    )

    result = await generate_usage_alerts_for_subscription(
        db=db,
        user_subscription_id=subscription_id,
    )

    assert result.alerts_created == 1
    assert result.plan_exceed_alert_created is True
    assert db.flush_called is True
    assert len(db.added) == 1

    alert = db.added[0]

    assert isinstance(alert, Alert)
    assert alert.user_id == user_id
    assert alert.user_subscription_id == subscription_id
    assert alert.alert_type == "plan_exceed_risk"
    assert alert.severity == "critical"
    assert alert.status == "unread"


@pytest.mark.asyncio
async def test_generate_policy_failed_alert_for_policy():
    user_id = uuid4()
    subscription_id = uuid4()
    device_id = uuid4()

    policy = SimpleNamespace(
        router=SimpleNamespace(
            user_subscription_id=subscription_id,
        ),
        requested_by_user_id=user_id,
        device_id=device_id,
        policy_type="bandwidth_limit",
        failure_reason="Test policy failure.",
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(None),
        ]
    )

    created = await generate_policy_failed_alert_for_policy(
        db=db,
        policy=policy,
    )

    assert created is True
    assert db.flush_called is True
    assert len(db.added) == 1

    alert = db.added[0]

    assert isinstance(alert, Alert)
    assert alert.user_id == user_id
    assert alert.user_subscription_id == subscription_id
    assert alert.device_id == device_id
    assert alert.alert_type == "policy_failed"
    assert alert.severity == "high"
    assert alert.status == "unread"
    assert "Test policy failure." in alert.message


@pytest.mark.asyncio
async def test_generate_policy_failed_alert_skips_duplicate_unread_alert():
    policy = SimpleNamespace(
        router=SimpleNamespace(
            user_subscription_id=uuid4(),
        ),
        requested_by_user_id=uuid4(),
        device_id=uuid4(),
        policy_type="bandwidth_limit",
        failure_reason="Duplicate failure.",
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(uuid4()),
        ]
    )

    created = await generate_policy_failed_alert_for_policy(
        db=db,
        policy=policy,
    )

    assert created is False
    assert db.flush_called is False
    assert db.added == []
