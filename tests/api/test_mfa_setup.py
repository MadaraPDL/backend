from types import SimpleNamespace
from uuid import uuid4

import app.api.v1.endpoints.auth.mfa as mfa_endpoint


def valid_setup_payload():
    return {
        "mfa_setup_token": "fake-mfa-setup-token",
        "code": "123456",
    }


def test_mfa_setup_confirm_returns_access_token(api_client, monkeypatch):
    fake_account = SimpleNamespace(
        id=uuid4(),
        full_name="MFA User",
        email="mfa@test.com",
        role="admin",
    )

    async def fake_complete_mfa_setup(*args, **kwargs):
        return fake_account, "admin"

    def fake_build_auth_token_response(*args, **kwargs):
        return {
            "access_token": "fake-access-token",
            "token_type": "bearer",
            "account_type": "admin",
            "account_id": fake_account.id,
            "full_name": fake_account.full_name,
            "email": fake_account.email,
            "role": fake_account.role,
        }

    monkeypatch.setattr(
        mfa_endpoint,
        "complete_mfa_setup",
        fake_complete_mfa_setup,
    )

    monkeypatch.setattr(
        mfa_endpoint,
        "build_auth_token_response",
        fake_build_auth_token_response,
    )

    response = api_client.post(
        "/api/v1/auth/mfa/setup/confirm",
        json=valid_setup_payload(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"] == "fake-access-token"
    assert body["account_type"] == "admin"
    assert body["account_id"] == str(fake_account.id)


def test_mfa_setup_confirm_rejects_invalid_setup(api_client, monkeypatch):
    async def fake_complete_mfa_setup(*args, **kwargs):
        return None

    monkeypatch.setattr(
        mfa_endpoint,
        "complete_mfa_setup",
        fake_complete_mfa_setup,
    )

    response = api_client.post(
        "/api/v1/auth/mfa/setup/confirm",
        json=valid_setup_payload(),
    )

    assert response.status_code == 400
    assert "Invalid or expired MFA setup token or code" in response.json()["detail"]
