from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import app.api.v1.endpoints.auth.me as me_endpoint
from app.api.dependencies import CurrentAccount
from app.main import app


def test_auth_me_returns_admin_role_and_mfa_shape(api_client):
    admin_id = uuid4()

    async def override_current_account():
        return CurrentAccount(
            account_type="admin",
            account=SimpleNamespace(
                id=admin_id,
                full_name="Platform Admin",
                email="platform@example.com",
                username="platform_admin",
                role="platform_admin",
                status="active",
                email_verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                mfa_enabled=True,
                mfa_required=True,
                preferred_mfa_method="authenticator",
            ),
        )

    app.dependency_overrides[me_endpoint.get_current_account] = override_current_account

    try:
        response = api_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.pop(me_endpoint.get_current_account, None)

    assert response.status_code == 200

    body = response.json()

    assert body == {
        "account_type": "admin",
        "account_id": str(admin_id),
        "full_name": "Platform Admin",
        "email": "platform@example.com",
        "username": "platform_admin",
        "role": "platform_admin",
        "status": "active",
        "email_verified_at": "2026-01-01T00:00:00Z",
        "mfa_enabled": True,
        "mfa_required": True,
        "preferred_mfa_method": "authenticator",
    }
