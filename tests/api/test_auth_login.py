from uuid import uuid4

import app.api.v1.endpoints.auth.login as login_endpoint
from app.services.auth_service import EmailDeliveryRequiredError


def valid_login_payload():
    return {
        "account_type": "admin",
        "identifier": "admin@test.com",
        "password": "password123",
    }


def test_login_returns_401_for_invalid_credentials(api_client, monkeypatch):
    async def fake_start_login(*args, **kwargs):
        return None

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)

    response = api_client.post("/api/v1/auth/login", json=valid_login_payload())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_returns_mfa_setup_required_response(api_client, monkeypatch):
    account_id = uuid4()

    async def fake_start_login(*args, **kwargs):
        return (
            {
                "mfa_setup_required": True,
                "message": "MFA setup is required before this account can complete login.",
                "account_type": "admin",
                "account_id": account_id,
                "method": "authenticator",
                "mfa_setup_token": "fake-mfa-setup-token",
                "authenticator_secret": "FAKESECRET123",
                "authenticator_uri": "otpauth://totp/PulseFi:admin@test.com",
            },
            None,
        )

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)

    response = api_client.post("/api/v1/auth/login", json=valid_login_payload())

    assert response.status_code == 200

    body = response.json()

    assert body["mfa_setup_required"] is True
    assert body["account_type"] == "admin"
    assert body["account_id"] == str(account_id)
    assert body["method"] == "authenticator"
    assert body["mfa_setup_token"] == "fake-mfa-setup-token"
    assert body["authenticator_secret"] == "FAKESECRET123"
    assert body["authenticator_uri"].startswith("otpauth://")
    assert "access_token" not in body


def test_login_returns_503_when_email_mfa_needs_email_delivery(api_client, monkeypatch):
    async def fake_start_login(*args, **kwargs):
        raise EmailDeliveryRequiredError

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)

    response = api_client.post("/api/v1/auth/login", json=valid_login_payload())

    assert response.status_code == 503
    assert "Email delivery is not configured" in response.json()["detail"]
