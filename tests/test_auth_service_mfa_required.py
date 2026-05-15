from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services import auth_service


@pytest.mark.asyncio
async def test_start_login_returns_mfa_setup_when_mfa_required_but_not_enabled(
    monkeypatch,
):
    account = SimpleNamespace(
        id=uuid4(),
        full_name="ISP Admin",
        email="isp-admin@example.com",
        role="isp_admin",
        mfa_required=True,
        mfa_enabled=False,
    )

    async def fake_authenticate_account(
        db,
        account_type,
        identifier,
        password,
    ):
        return account

    async def fake_build_mfa_setup_response(
        db,
        account,
        account_type,
    ):
        return {
            "mfa_setup_required": True,
            "account_type": account_type,
            "account_id": account.id,
            "message": "MFA setup is required before this account can complete login.",
        }

    def fail_if_normal_token_is_created(
        account,
        account_type,
    ):
        raise AssertionError(
            "A normal login token must not be issued before required MFA setup."
        )

    monkeypatch.setattr(
        auth_service,
        "authenticate_account",
        fake_authenticate_account,
    )
    monkeypatch.setattr(
        auth_service,
        "build_mfa_setup_response",
        fake_build_mfa_setup_response,
    )
    monkeypatch.setattr(
        auth_service,
        "build_auth_token_response",
        fail_if_normal_token_is_created,
    )

    response_data, raw_email_code = await auth_service.start_login(
        db=None,
        account_type="admin",
        identifier="isp-admin@example.com",
        password="correct-password",
    )

    assert raw_email_code is None
    assert response_data["mfa_setup_required"] is True
    assert response_data["account_type"] == "admin"
    assert response_data["account_id"] == account.id


@pytest.mark.asyncio
async def test_start_login_allows_token_when_mfa_is_not_required_and_not_enabled(
    monkeypatch,
):
    account = SimpleNamespace(
        id=uuid4(),
        full_name="App User",
        email="user@example.com",
        role=None,
        mfa_required=False,
        mfa_enabled=False,
    )

    async def fake_authenticate_account(
        db,
        account_type,
        identifier,
        password,
    ):
        return account

    async def fail_if_mfa_setup_is_started(
        db,
        account,
        account_type,
    ):
        raise AssertionError(
            "MFA setup must not be required when account.mfa_required is false."
        )

    def fake_build_auth_token_response(
        account,
        account_type,
    ):
        return {
            "access_token": "fake-token",
            "token_type": "bearer",
            "account_type": account_type,
            "account_id": account.id,
            "full_name": account.full_name,
            "email": account.email,
            "role": None,
        }

    monkeypatch.setattr(
        auth_service,
        "authenticate_account",
        fake_authenticate_account,
    )
    monkeypatch.setattr(
        auth_service,
        "build_mfa_setup_response",
        fail_if_mfa_setup_is_started,
    )
    monkeypatch.setattr(
        auth_service,
        "build_auth_token_response",
        fake_build_auth_token_response,
    )

    response_data, raw_email_code = await auth_service.start_login(
        db=None,
        account_type="app_user",
        identifier="user@example.com",
        password="correct-password",
    )

    assert raw_email_code is None
    assert response_data["access_token"] == "fake-token"
    assert response_data["account_type"] == "app_user"
    assert response_data["account_id"] == account.id
