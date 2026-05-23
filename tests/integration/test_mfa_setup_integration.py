from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pyotp
import pytest

from app.core.encryption import decrypt_text
from app.core.security import hash_password
from app.models.admin import Admin
from app.models.isp import ISP
from app.services.mfa_setup_service import (
    build_mfa_setup_response,
    complete_mfa_setup,
    get_mfa_setup_challenge_by_token,
)
from app.services.auth_service import start_login


@pytest.mark.asyncio
async def test_mfa_setup_confirm_enables_mfa_with_real_db_rows(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Setup ISP {suffix}",
        contact_email=f"mfa-setup-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Setup Admin",
        email=f"mfa-setup-admin-{suffix}@example.com",
        username=f"mfasetup_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=True,
        preferred_mfa_method="authenticator",
    )

    integration_db.add(admin)
    await integration_db.flush()

    setup_response = await build_mfa_setup_response(
        db=integration_db,
        account=admin,
        account_type="admin",
    )

    setup_token = setup_response["mfa_setup_token"]
    authenticator_secret = setup_response["authenticator_secret"]
    correct_code = pyotp.TOTP(authenticator_secret).now()

    setup_result = await complete_mfa_setup(
        db=integration_db,
        mfa_setup_token=setup_token,
        code=correct_code,
    )

    assert setup_result is not None

    account, account_type = setup_result

    assert account_type == "admin"
    assert account.id == admin.id
    assert account.authenticator_mfa_enabled is True
    assert account.mfa_enabled is True
    assert account.preferred_mfa_method == "authenticator"
    assert account.mfa_secret is not None
    assert account.mfa_secret != authenticator_secret
    assert decrypt_text(account.mfa_secret) == authenticator_secret

    challenge = await get_mfa_setup_challenge_by_token(
        db=integration_db,
        raw_setup_token=setup_token,
    )

    assert challenge is not None
    assert challenge.used_at is not None
    assert challenge.authenticator_secret == ""

    next_login_result = await start_login(
        db=integration_db,
        account_type="admin",
        identifier=admin.email,
        password="CorrectHorseBatteryStaple123!",
    )

    assert next_login_result is not None

    next_login_response, next_raw_email_code = next_login_result

    assert next_raw_email_code is None
    assert next_login_response["mfa_required"] is True
    assert next_login_response["method"] == "authenticator"
    assert "mfa_setup_required" not in next_login_response


@pytest.mark.asyncio
async def test_mfa_setup_confirm_rejects_invalid_code_and_increments_attempts(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Invalid ISP {suffix}",
        contact_email=f"mfa-invalid-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Invalid Admin",
        email=f"mfa-invalid-admin-{suffix}@example.com",
        username=f"mfainvalid_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=True,
        preferred_mfa_method="authenticator",
    )

    integration_db.add(admin)
    await integration_db.flush()

    setup_response = await build_mfa_setup_response(
        db=integration_db,
        account=admin,
        account_type="admin",
    )

    setup_token = setup_response["mfa_setup_token"]
    authenticator_secret = setup_response["authenticator_secret"]
    correct_code = pyotp.TOTP(authenticator_secret).now()
    wrong_code = "000000" if correct_code != "000000" else "111111"

    setup_result = await complete_mfa_setup(
        db=integration_db,
        mfa_setup_token=setup_token,
        code=wrong_code,
    )

    assert setup_result is None
    assert admin.mfa_enabled is False
    assert admin.mfa_secret is None

    challenge = await get_mfa_setup_challenge_by_token(
        db=integration_db,
        raw_setup_token=setup_token,
    )

    assert challenge is not None
    assert challenge.used_at is None
    assert challenge.attempt_count == 1
    assert challenge.authenticator_secret != ""
