from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.core.security import hash_token
from app.models.account_invitation import AccountInvitation
from app.models.isp import ISP
from app.services.auth_service import start_login
from app.services.invitation_service import accept_invitation


@pytest.mark.asyncio
async def test_admin_invitation_accept_then_login_requires_mfa_setup(
    integration_db,
):
    suffix = uuid4().hex[:12]

    raw_invitation_token = f"integration-invite-{suffix}"
    email = f"isp-admin-{suffix}@example.com"
    username = f"ispadmin_{suffix}"
    password = "CorrectHorseBatteryStaple123!"

    isp = ISP(
        name=f"Integration ISP {suffix}",
        contact_email=f"isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    invitation = AccountInvitation(
        email=email,
        full_name="Integration ISP Admin",
        account_type="admin",
        admin_role="isp_admin",
        isp_id=isp.id,
        token_hash=hash_token(raw_invitation_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    integration_db.add(invitation)
    await integration_db.flush()

    account = await accept_invitation(
        db=integration_db,
        raw_token=raw_invitation_token,
        username=username,
        password=password,
        preferred_mfa_method="authenticator",
    )

    assert account is not None
    assert account.email == email
    assert account.username == username
    assert account.role == "isp_admin"
    assert account.isp_id == isp.id
    assert account.mfa_required is True
    assert account.mfa_enabled is False
    assert invitation.accepted_at is not None

    login_result = await start_login(
        db=integration_db,
        account_type="admin",
        identifier=email,
        password=password,
    )

    assert login_result is not None

    response_data, raw_email_code = login_result

    assert raw_email_code is None
    assert response_data["mfa_setup_required"] is True
    assert response_data["account_type"] == "admin"
    assert response_data["account_id"] == account.id
    assert "access_token" not in response_data

@pytest.mark.asyncio
async def test_admin_invitation_accept_rejects_existing_email(
    integration_db,
):
    suffix = uuid4().hex[:12]

    email = f"duplicate-email-{suffix}@example.com"
    first_username = f"first_email_{suffix}"
    second_username = f"second_email_{suffix}"
    password = "CorrectHorseBatteryStaple123!"

    isp = ISP(
        name=f"Duplicate Email ISP {suffix}",
        contact_email=f"duplicate-email-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    first_token = f"first-email-token-{suffix}"
    first_invitation = AccountInvitation(
        email=email,
        full_name="First ISP Admin",
        account_type="admin",
        admin_role="isp_admin",
        isp_id=isp.id,
        token_hash=hash_token(first_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    integration_db.add(first_invitation)
    await integration_db.flush()

    first_account = await accept_invitation(
        db=integration_db,
        raw_token=first_token,
        username=first_username,
        password=password,
        preferred_mfa_method="authenticator",
    )

    assert first_account is not None
    assert first_account.email == email
    assert first_invitation.accepted_at is not None

    second_token = f"second-email-token-{suffix}"
    second_invitation = AccountInvitation(
        email=email,
        full_name="Second ISP Admin",
        account_type="admin",
        admin_role="isp_admin",
        isp_id=isp.id,
        token_hash=hash_token(second_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    integration_db.add(second_invitation)
    await integration_db.flush()

    second_account = await accept_invitation(
        db=integration_db,
        raw_token=second_token,
        username=second_username,
        password=password,
        preferred_mfa_method="authenticator",
    )

    assert second_account is None
    assert second_invitation.accepted_at is None


@pytest.mark.asyncio
async def test_admin_invitation_accept_rejects_existing_username(
    integration_db,
):
    suffix = uuid4().hex[:12]

    first_email = f"first-username-{suffix}@example.com"
    second_email = f"second-username-{suffix}@example.com"
    username = f"duplicate_username_{suffix}"
    password = "CorrectHorseBatteryStaple123!"

    isp = ISP(
        name=f"Duplicate Username ISP {suffix}",
        contact_email=f"duplicate-username-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    first_token = f"first-username-token-{suffix}"
    first_invitation = AccountInvitation(
        email=first_email,
        full_name="First ISP Admin",
        account_type="admin",
        admin_role="isp_admin",
        isp_id=isp.id,
        token_hash=hash_token(first_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    integration_db.add(first_invitation)
    await integration_db.flush()

    first_account = await accept_invitation(
        db=integration_db,
        raw_token=first_token,
        username=username,
        password=password,
        preferred_mfa_method="authenticator",
    )

    assert first_account is not None
    assert first_account.username == username
    assert first_invitation.accepted_at is not None

    second_token = f"second-username-token-{suffix}"
    second_invitation = AccountInvitation(
        email=second_email,
        full_name="Second ISP Admin",
        account_type="admin",
        admin_role="isp_admin",
        isp_id=isp.id,
        token_hash=hash_token(second_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    integration_db.add(second_invitation)
    await integration_db.flush()

    second_account = await accept_invitation(
        db=integration_db,
        raw_token=second_token,
        username=username,
        password=password,
        preferred_mfa_method="authenticator",
    )

    assert second_account is None
    assert second_invitation.accepted_at is None
