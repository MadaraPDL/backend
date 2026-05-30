from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services import intelligence_scheduler


class FakeScalarResult:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class FakeExecuteResult:
    def __init__(self, values):
        self.values = values

    def scalars(self):
        return FakeScalarResult(self.values)


class FakeDB:
    def __init__(self, isp_ids):
        self.isp_ids = isp_ids
        self.committed = False

    async def execute(self, statement):
        return FakeExecuteResult(self.isp_ids)

    async def commit(self):
        self.committed = True


class FakeSessionContext:
    def __init__(self, db):
        self.db = db

    async def __aenter__(self):
        return self.db

    async def __aexit__(self, exc_type, exc, traceback):
        return False


@pytest.mark.asyncio
async def test_scheduler_refreshes_intelligence_without_generating_alerts(monkeypatch):
    isp_id = uuid4()
    fake_db = FakeDB([isp_id])
    calls = []

    async def fake_run_intelligence_for_isp(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            subscriptions_checked=1,
            predictions_created=0,
            recommendations_created=0,
            skipped=1,
            failed=0,
        )

    monkeypatch.setattr(
        intelligence_scheduler,
        "AsyncSessionLocal",
        lambda: FakeSessionContext(fake_db),
    )
    monkeypatch.setattr(
        intelligence_scheduler,
        "run_intelligence_for_isp",
        fake_run_intelligence_for_isp,
    )

    await intelligence_scheduler.run_intelligence_for_all_isps_once()

    assert fake_db.committed is True
    assert len(calls) == 1
    assert calls[0]["isp_id"] == isp_id
    assert calls[0]["include_alert_generation"] is False
