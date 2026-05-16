from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.app_user.alert_service import (
    get_my_alert,
    list_my_alerts,
)
from app.services.isp_admin.alert_service import (
    get_alert_for_isp,
    list_alerts_for_isp,
)


class FakeScalarResult:
    def __init__(self, value=None):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeScalars:
    def all(self):
        return []


class FakeListResult:
    def scalars(self):
        return FakeScalars()


class CapturingDb:
    def __init__(self, result):
        self.result = result
        self.statements = []

    async def execute(self, stmt):
        self.statements.append(stmt)
        return self.result


def _compiled_sql(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": False}))


def _compiled_params(stmt) -> set:
    compiled = stmt.compile(compile_kwargs={"literal_binds": False})
    return set(compiled.params.values())


@pytest.mark.asyncio
async def test_app_user_list_alerts_filters_by_current_user_id():
    user_id = uuid4()
    current_user = SimpleNamespace(id=user_id)
    db = CapturingDb(FakeListResult())

    await list_my_alerts(
        db=db,
        current_user=current_user,
    )

    assert len(db.statements) == 1

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "alerts.user_id" in sql
    assert user_id in params


@pytest.mark.asyncio
async def test_app_user_get_alert_requires_current_user_id_and_alert_id():
    user_id = uuid4()
    alert_id = uuid4()
    current_user = SimpleNamespace(id=user_id)
    db = CapturingDb(FakeScalarResult())

    await get_my_alert(
        db=db,
        current_user=current_user,
        alert_id=alert_id,
    )

    assert len(db.statements) == 1

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "alerts.id" in sql
    assert "alerts.user_id" in sql
    assert alert_id in params
    assert user_id in params


@pytest.mark.asyncio
async def test_isp_admin_list_alerts_filters_by_isp_id():
    isp_id = uuid4()
    db = CapturingDb(FakeListResult())

    await list_alerts_for_isp(
        db=db,
        isp_id=isp_id,
    )

    assert len(db.statements) == 1

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "JOIN app_users" in sql
    assert "alerts.user_id = app_users.id" in sql
    assert "app_users.isp_id" in sql
    assert isp_id in params


@pytest.mark.asyncio
async def test_isp_admin_get_alert_requires_alert_id_and_isp_id():
    isp_id = uuid4()
    alert_id = uuid4()
    db = CapturingDb(FakeScalarResult())

    await get_alert_for_isp(
        db=db,
        isp_id=isp_id,
        alert_id=alert_id,
    )

    assert len(db.statements) == 1

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "JOIN app_users" in sql
    assert "alerts.user_id = app_users.id" in sql
    assert "alerts.id" in sql
    assert "app_users.isp_id" in sql
    assert alert_id in params
    assert isp_id in params


@pytest.mark.asyncio
async def test_isp_admin_list_alerts_keeps_isp_scope_when_extra_filters_are_used():
    isp_id = uuid4()
    user_id = uuid4()
    device_id = uuid4()
    db = CapturingDb(FakeListResult())

    await list_alerts_for_isp(
        db=db,
        isp_id=isp_id,
        user_id=user_id,
        device_id=device_id,
        alert_type="policy_failed",
        severity="high",
        status="unread",
    )

    assert len(db.statements) == 1

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "app_users.isp_id" in sql
    assert "alerts.user_id" in sql
    assert "alerts.device_id" in sql
    assert "alerts.alert_type" in sql
    assert "alerts.severity" in sql
    assert "alerts.status" in sql

    assert isp_id in params
    assert user_id in params
    assert device_id in params
    assert "policy_failed" in params
    assert "high" in params
    assert "unread" in params
