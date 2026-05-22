from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.admin import Admin
from app.models.isp import ISP
from app.services.mfa_service import create_mfa_challenge
from app.services.mfa_settings_service import (
    InvalidMFASettingsChallengeError,
    apply_verified_mfa_settings_action,
)


@pytest.mark.asyncio
async def test_verified_mfa_settings_action_enables_email_mfa(integration_db):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Verified Settings ISP {suffix}",
        contact_email=f"mfa-verified-settings-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Verified Settings Admin",
        email=f"mfa-verified-settings-admin-{suffix}@example.com",
        username=f"mfaverified_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=True,
        mfa_required=True,
        email_mfa_enabled=False,
        authenticator_mfa_enabled=True,
        preferred_mfa_method="authenticator",
    )

    integration_db.add(admin)
    await integration_db.flush()

    _, challenge_token, email_code = await create_mfa_challenge(
        db=integration_db,
        account=admin,
        account_type="admin",
        method="email",
    )

    assert email_code is not None

    await apply_verified_mfa_settings_action(
        db=integration_db,
        account=admin,
        account_type="admin",
        action="enable_email",
        challenge_token=challenge_token,
        code=email_code,
    )

    assert admin.email_mfa_enabled is True
    assert admin.authenticator_mfa_enabled is True
    assert admin.mfa_enabled is True


@pytest.mark.asyncio
async def test_verified_mfa_settings_action_rejects_wrong_code(integration_db):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Wrong Settings ISP {suffix}",
        contact_email=f"mfa-wrong-settings-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Wrong Settings Admin",
        email=f"mfa-wrong-settings-admin-{suffix}@example.com",
        username=f"mfawrong_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=True,
        mfa_required=True,
        email_mfa_enabled=True,
        authenticator_mfa_enabled=False,
        preferred_mfa_method="email",
    )

    integration_db.add(admin)
    await integration_db.flush()

    _, challenge_token, email_code = await create_mfa_challenge(
        db=integration_db,
        account=admin,
        account_type="admin",
        method="email",
    )

    assert email_code is not None
    wrong_code = "000000" if email_code != "000000" else "111111"

    with pytest.raises(InvalidMFASettingsChallengeError):
        await apply_verified_mfa_settings_action(
            db=integration_db,
            account=admin,
            account_type="admin",
            action="prefer_email",
            challenge_token=challenge_token,
            code=wrong_code,
        )
