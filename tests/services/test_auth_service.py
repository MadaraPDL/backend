from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.auth_service import start_login


@pytest.mark.asyncio
async def test_login_requires_mfa_setup(monkeypatch):
    fake_account = SimpleNamespace(
        id=uuid4(),
        full_name="Test Admin",
        email="admin@test.com",
        role="isp_admin",
        mfa_required=True,
        mfa_enabled=False,
    )

    async def fake_authenticate_account(*args, **kwargs):
        return fake_account

    async def fake_build_mfa_setup_response(*args, **kwargs):
        return {
            "mfa_setup_required": True,
            "message": "MFA setup is required before this account can complete login.",
            "account_type": "admin",
            "account_id": fake_account.id,
            "method": "authenticator",
            "mfa_setup_token": "fake-setup-token",
            "authenticator_secret": "FAKESECRET123",
            "authenticator_uri": "otpauth://totp/PulseFi:admin@test.com",
        }

    monkeypatch.setattr(
        "app.services.auth_service.authenticate_account",
        fake_authenticate_account,
    )

    monkeypatch.setattr(
        "app.services.auth_service.build_mfa_setup_response",
        fake_build_mfa_setup_response,
    )

    result = await start_login(
        db=None,
        account_type="admin",
        identifier="admin@test.com",
        password="password123",
    )

    assert result is not None

    response_data, raw_email_code = result

    assert raw_email_code is None
    assert response_data["mfa_setup_required"] is True
    assert response_data["account_id"] == fake_account.id

@pytest.mark.asyncio
async def test_login_returns_token_when_mfa_not_required(monkeypatch):
    fake_account = SimpleNamespace(
        id=uuid4(),
        full_name="Normal User",
        email="user@test.com",
        role=None,
        mfa_required=False,
        mfa_enabled=False,
    )

    async def fake_authenticate_account(*args, **kwargs):
        return fake_account

    def fake_build_auth_token_response(*args, **kwargs):
        return {
            "access_token": "fake-token",
            "token_type": "bearer",
        }

    monkeypatch.setattr(
        "app.services.auth_service.authenticate_account",
        fake_authenticate_account,
    )

    monkeypatch.setattr(
        "app.services.auth_service.build_auth_token_response",
        fake_build_auth_token_response,
    )

    result = await start_login(
        db=None,
        account_type="app_user",
        identifier="user@test.com",
        password="password123",
    )

    assert result is not None

    response_data, raw_email_code = result

    assert raw_email_code is None
    assert response_data["access_token"] == "fake-token"


@pytest.mark.asyncio
async def test_login_requires_mfa_challenge_when_enabled(monkeypatch):
    fake_account = SimpleNamespace(
        id=uuid4(),
        full_name="Secure Admin",
        email="secure@test.com",
        role="isp_admin",
        mfa_required=True,
        mfa_enabled=True,
        preferred_mfa_method="authenticator",
    )

    async def fake_authenticate_account(*args, **kwargs):
        return fake_account

    async def fake_create_mfa_challenge(*args, **kwargs):
        challenge = SimpleNamespace(
            expires_at="2099-01-01T00:00:00Z",
        )

        return (
            challenge,
            "challenge-token",
            None,
        )

    monkeypatch.setattr(
        "app.services.auth_service.authenticate_account",
        fake_authenticate_account,
    )

    monkeypatch.setattr(
        "app.services.auth_service.create_mfa_challenge",
        fake_create_mfa_challenge,
    )

    result = await start_login(
        db=None,
        account_type="admin",
        identifier="secure@test.com",
        password="password123",
    )

    assert result is not None

    response_data, raw_email_code = result

    assert response_data["mfa_required"] is True
    assert response_data["challenge_token"] == "challenge-token"

@pytest.mark.asyncio
async def test_login_blocks_email_mfa_without_email_delivery_in_production(monkeypatch):
    import app.services.auth_service as auth_service

    fake_account = SimpleNamespace(
        id=uuid4(),
        full_name="Email MFA User",
        email="emailmfa@test.com",
        role=None,
        mfa_required=True,
        mfa_enabled=True,
        preferred_mfa_method="email",
    )

    async def fake_authenticate_account(*args, **kwargs):
        return fake_account

    async def fake_create_mfa_challenge(*args, **kwargs):
        raise AssertionError("Email MFA challenge should not be created without email delivery.")

    monkeypatch.setattr(
        "app.services.auth_service.authenticate_account",
        fake_authenticate_account,
    )

    monkeypatch.setattr(
        "app.services.auth_service.create_mfa_challenge",
        fake_create_mfa_challenge,
    )

    monkeypatch.setattr(
        auth_service,
        "settings",
        SimpleNamespace(DEBUG=False, EMAIL_DELIVERY_ENABLED=False),
    )

    with pytest.raises(auth_service.EmailDeliveryRequiredError):
        await start_login(
            db=None,
            account_type="app_user",
            identifier="emailmfa@test.com",
            password="password123",
        )
