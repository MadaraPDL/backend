from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.admin import Admin
from app.models.isp import ISP
from app.services.mfa_settings_service import (
    CannotDisableLastMFAMethodError,
    MFAMethodNotActiveError,
    build_mfa_status,
    disable_authenticator_mfa,
    disable_email_mfa,
    enable_email_mfa,
    set_preferred_mfa_method,
)


@pytest.mark.asyncio
async def test_mfa_status_reports_both_active_methods(integration_db):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Settings ISP {suffix}",
        contact_email=f"mfa-settings-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Settings Admin",
        email=f"mfa-settings-admin-{suffix}@example.com",
        username=f"mfasettings_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=True,
        mfa_required=True,
        email_mfa_enabled=True,
        authenticator_mfa_enabled=True,
        preferred_mfa_method="email",
    )

    integration_db.add(admin)
    await integration_db.flush()

    status = build_mfa_status(account=admin, account_type="admin")

    assert status["mfa_enabled"] is True
    assert status["email_mfa_enabled"] is True
    assert status["authenticator_mfa_enabled"] is True
    assert status["preferred_mfa_method"] == "email"
    assert status["active_methods"] == ["email", "authenticator"]
    assert status["can_disable_email_mfa"] is True
    assert status["can_disable_authenticator_mfa"] is True


@pytest.mark.asyncio
async def test_cannot_disable_last_required_mfa_method(integration_db):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Last Method ISP {suffix}",
        contact_email=f"mfa-last-method-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Last Method Admin",
        email=f"mfa-last-method-admin-{suffix}@example.com",
        username=f"mfalast_{suffix}",
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

    with pytest.raises(CannotDisableLastMFAMethodError):
        disable_email_mfa(admin)

    assert admin.email_mfa_enabled is True
    assert admin.mfa_enabled is True


@pytest.mark.asyncio
async def test_mfa_settings_can_enable_email_and_switch_preferred_method(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Switch ISP {suffix}",
        contact_email=f"mfa-switch-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Switch Admin",
        email=f"mfa-switch-admin-{suffix}@example.com",
        username=f"mfaswitch_{suffix}",
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

    enable_email_mfa(admin)
    set_preferred_mfa_method(account=admin, method="email")

    assert admin.email_mfa_enabled is True
    assert admin.authenticator_mfa_enabled is True
    assert admin.mfa_enabled is True
    assert admin.preferred_mfa_method == "email"


@pytest.mark.asyncio
async def test_cannot_prefer_inactive_mfa_method(integration_db):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Inactive ISP {suffix}",
        contact_email=f"mfa-inactive-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Inactive Admin",
        email=f"mfa-inactive-admin-{suffix}@example.com",
        username=f"mfainactive_{suffix}",
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

    with pytest.raises(MFAMethodNotActiveError):
        set_preferred_mfa_method(account=admin, method="authenticator")


@pytest.mark.asyncio
async def test_disabling_authenticator_keeps_email_mfa_active(integration_db):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Disable Auth ISP {suffix}",
        contact_email=f"mfa-disable-auth-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Disable Auth Admin",
        email=f"mfa-disable-auth-admin-{suffix}@example.com",
        username=f"mfadisableauth_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=True,
        mfa_required=True,
        email_mfa_enabled=True,
        authenticator_mfa_enabled=True,
        preferred_mfa_method="authenticator",
        mfa_secret="encrypted-secret-placeholder",
    )

    integration_db.add(admin)
    await integration_db.flush()

    disable_authenticator_mfa(admin)

    assert admin.email_mfa_enabled is True
    assert admin.authenticator_mfa_enabled is False
    assert admin.mfa_enabled is True
    assert admin.preferred_mfa_method == "email"
    assert admin.mfa_secret is None
