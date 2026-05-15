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
