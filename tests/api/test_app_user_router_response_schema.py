from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.schemas.app_user.routers import MyRouterResponse


def test_app_user_router_response_excludes_admin_only_fields() -> None:
    router = SimpleNamespace(
        id=uuid4(),
        isp_id=uuid4(),
        user_subscription_id=uuid4(),
        assigned_by_admin_id=uuid4(),
        router_name="Home Router",
        router_model="Simulator Router",
        router_ip="192.168.1.1",
        mac_address="AA:BB:CC:DD:EE:FF",
        api_endpoint="http://192.168.1.1/admin",
        username="admin",
        password_encrypted="encrypted-secret",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    response = MyRouterResponse.model_validate(router).model_dump()

    assert "id" in response
    assert "user_subscription_id" in response
    assert "router_name" in response
    assert "router_model" in response
    assert "status" in response

    assert "isp_id" not in response
    assert "assigned_by_admin_id" not in response
    assert "router_ip" not in response
    assert "mac_address" not in response
    assert "api_endpoint" not in response
    assert "username" not in response
    assert "password_encrypted" not in response
