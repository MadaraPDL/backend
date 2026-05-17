from uuid import uuid4

from sqlalchemy import select

from app.models.router import Router
from app.models.usage_record import UsageRecord
from app.services.isp_admin.ownership_scope import (
    apply_router_isp_ownership_scope,
    apply_usage_record_isp_ownership_scope,
)


def _compiled_sql(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": False}))


def test_router_isp_ownership_scope_uses_full_router_subscription_user_chain() -> None:
    stmt = apply_router_isp_ownership_scope(
        select(Router),
        isp_id=uuid4(),
    )

    sql = _compiled_sql(stmt)

    assert "routers.user_subscription_id = user_subscriptions.id" in sql
    assert "user_subscriptions.user_id = app_users.id" in sql
    assert "routers.isp_id" in sql
    assert "app_users.isp_id" in sql


def test_usage_record_isp_ownership_scope_uses_full_usage_router_subscription_user_chain() -> None:
    stmt = apply_usage_record_isp_ownership_scope(
        select(UsageRecord),
        isp_id=uuid4(),
    )

    sql = _compiled_sql(stmt)

    assert "usage_records.router_id = routers.id" in sql
    assert "usage_records.user_subscription_id = user_subscriptions.id" in sql
    assert "usage_records.user_id = app_users.id" in sql
    assert "routers.user_subscription_id = user_subscriptions.id" in sql
    assert "user_subscriptions.user_id = app_users.id" in sql
    assert "routers.isp_id" in sql
    assert "app_users.isp_id" in sql
