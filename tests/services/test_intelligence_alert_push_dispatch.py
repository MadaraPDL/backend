import asyncio
from uuid import uuid4

from app.services.alerts import AlertGenerationResult
from app.services.isp_admin import intelligence_service


class DummyDB:
    pass


def test_dispatches_plan_exceed_push(monkeypatch):
    calls = []

    async def fake_usage_push(*, db, user_id, alert_kind):
        calls.append(("usage", user_id, alert_kind))

    async def fake_new_device_push(*, db, user_id):
        calls.append(("new_device", user_id))

    monkeypatch.setattr(
        intelligence_service,
        "notify_usage_alert_push",
        fake_usage_push,
    )
    monkeypatch.setattr(
        intelligence_service,
        "notify_new_device_push",
        fake_new_device_push,
    )

    user_id = uuid4()

    asyncio.run(
        intelligence_service.dispatch_push_for_alert_generation_result(
            db=DummyDB(),
            user_id=user_id,
            alert_generation_result=AlertGenerationResult(
                alerts_created=1,
                plan_exceed_alert_created=True,
            ),
        )
    )

    assert calls == [("usage", user_id, "plan_exceed")]


def test_dispatches_high_usage_push(monkeypatch):
    calls = []

    async def fake_usage_push(*, db, user_id, alert_kind):
        calls.append(("usage", user_id, alert_kind))

    async def fake_new_device_push(*, db, user_id):
        calls.append(("new_device", user_id))

    monkeypatch.setattr(
        intelligence_service,
        "notify_usage_alert_push",
        fake_usage_push,
    )
    monkeypatch.setattr(
        intelligence_service,
        "notify_new_device_push",
        fake_new_device_push,
    )

    user_id = uuid4()

    asyncio.run(
        intelligence_service.dispatch_push_for_alert_generation_result(
            db=DummyDB(),
            user_id=user_id,
            alert_generation_result=AlertGenerationResult(
                alerts_created=1,
                high_usage_alert_created=True,
            ),
        )
    )

    assert calls == [("usage", user_id, "high_usage")]


def test_dispatches_new_device_push(monkeypatch):
    calls = []

    async def fake_usage_push(*, db, user_id, alert_kind):
        calls.append(("usage", user_id, alert_kind))

    async def fake_new_device_push(*, db, user_id):
        calls.append(("new_device", user_id))

    monkeypatch.setattr(
        intelligence_service,
        "notify_usage_alert_push",
        fake_usage_push,
    )
    monkeypatch.setattr(
        intelligence_service,
        "notify_new_device_push",
        fake_new_device_push,
    )

    user_id = uuid4()

    asyncio.run(
        intelligence_service.dispatch_push_for_alert_generation_result(
            db=DummyDB(),
            user_id=user_id,
            alert_generation_result=AlertGenerationResult(
                alerts_created=1,
                new_device_alerts_created=1,
            ),
        )
    )

    assert calls == [("new_device", user_id)]


def test_dispatches_usage_and_new_device_push(monkeypatch):
    calls = []

    async def fake_usage_push(*, db, user_id, alert_kind):
        calls.append(("usage", user_id, alert_kind))

    async def fake_new_device_push(*, db, user_id):
        calls.append(("new_device", user_id))

    monkeypatch.setattr(
        intelligence_service,
        "notify_usage_alert_push",
        fake_usage_push,
    )
    monkeypatch.setattr(
        intelligence_service,
        "notify_new_device_push",
        fake_new_device_push,
    )

    user_id = uuid4()

    asyncio.run(
        intelligence_service.dispatch_push_for_alert_generation_result(
            db=DummyDB(),
            user_id=user_id,
            alert_generation_result=AlertGenerationResult(
                alerts_created=2,
                high_usage_alert_created=True,
                new_device_alerts_created=1,
            ),
        )
    )

    assert calls == [
        ("usage", user_id, "high_usage"),
        ("new_device", user_id),
    ]
