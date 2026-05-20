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


def test_profile_update_challenge_returns_authenticator_prompt(api_client, monkeypatch):
    admin_id = uuid4()
    account = SimpleNamespace(
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
    )

    async def override_current_account():
        return CurrentAccount(account_type="admin", account=account)

    async def fake_create_profile_update_challenge(*args, **kwargs):
        return (
            SimpleNamespace(expires_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
            "profile-update-challenge-token",
            None,
        )

    monkeypatch.setattr(
        me_endpoint,
        "create_profile_update_challenge",
        fake_create_profile_update_challenge,
    )

    app.dependency_overrides[me_endpoint.get_current_account] = override_current_account

    try:
        response = api_client.post(
            "/api/v1/auth/me/profile-update-challenge",
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        app.dependency_overrides.pop(me_endpoint.get_current_account, None)

    assert response.status_code == 200

    body = response.json()
    assert body["challenge_token"] == "profile-update-challenge-token"
    assert body["method"] == "authenticator"
    assert "authenticator" in body["message"]


def test_update_me_identity_returns_updated_account(api_client, monkeypatch):
    admin_id = uuid4()
    account = SimpleNamespace(
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
    )

    async def override_current_account():
        return CurrentAccount(account_type="admin", account=account)

    async def fake_update_current_account_identity(**kwargs):
        account.email = kwargs["email"]
        account.username = kwargs["username"]
        return account

    monkeypatch.setattr(
        me_endpoint,
        "update_current_account_identity",
        fake_update_current_account_identity,
    )

    app.dependency_overrides[me_endpoint.get_current_account] = override_current_account

    try:
        response = api_client.patch(
            "/api/v1/auth/me/identity",
            headers={"Authorization": "Bearer test-token"},
            json={
                "email": "new-platform@example.com",
                "username": "new_platform_admin",
                "mfa_challenge_token": "profile-update-challenge-token",
                "mfa_code": "123456",
            },
        )
    finally:
        app.dependency_overrides.pop(me_endpoint.get_current_account, None)

    assert response.status_code == 200

    body = response.json()
    assert body["email"] == "new-platform@example.com"
    assert body["username"] == "new_platform_admin"
