from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.core.security import hash_password
from app.models.admin import Admin
from app.models.isp import ISP
from app.models.mfa_backup_code import MFABackupCode
from app.services.mfa_backup_code_service import (
    build_backup_code_status,
    regenerate_backup_codes,
)
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


@pytest.mark.asyncio
async def test_backup_code_status_reports_no_codes(integration_db):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Backup Empty ISP {suffix}",
        contact_email=f"mfa-backup-empty-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Backup Empty Admin",
        email=f"mfa-backup-empty-admin-{suffix}@example.com",
        username=f"mfabackupempty_{suffix}",
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

    status = await build_backup_code_status(
        db=integration_db,
        account=admin,
        account_type="admin",
    )

    assert status["backup_codes_available"] is False
    assert status["available_backup_code_count"] == 0


@pytest.mark.asyncio
async def test_regenerate_backup_codes_revokes_old_unused_codes_and_stores_hashes(
    integration_db,
    monkeypatch,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"MFA Backup Regen ISP {suffix}",
        contact_email=f"mfa-backup-regen-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="MFA Backup Regen Admin",
        email=f"mfa-backup-regen-admin-{suffix}@example.com",
        username=f"mfabackupregen_{suffix}",
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

    old_unused_code = MFABackupCode(
        account_type="admin",
        admin_id=admin.id,
        code_hash=hash_password("OLD-UNUSED-CODE"),
    )
    old_used_code = MFABackupCode(
        account_type="admin",
        admin_id=admin.id,
        code_hash=hash_password("OLD-USED-CODE"),
        used_at=now,
    )
    old_revoked_code = MFABackupCode(
        account_type="admin",
        admin_id=admin.id,
        code_hash=hash_password("OLD-REVOKED-CODE"),
        revoked_at=now,
    )
    integration_db.add_all([old_unused_code, old_used_code, old_revoked_code])
    await integration_db.flush()

    async def fake_verify_mfa_settings_challenge(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.services.mfa_backup_code_service.verify_mfa_settings_challenge",
        fake_verify_mfa_settings_challenge,
    )

    raw_codes = await regenerate_backup_codes(
        db=integration_db,
        account=admin,
        account_type="admin",
        challenge_token="x" * 20,
        code="123456",
    )

    assert len(raw_codes) == 10
    assert len(set(raw_codes)) == 10
    assert all(len(raw_code.split("-")) == 3 for raw_code in raw_codes)

    await integration_db.flush()

    result = await integration_db.execute(
        select(MFABackupCode).where(MFABackupCode.admin_id == admin.id)
    )
    backup_code_rows = result.scalars().all()

    active_rows = [
        row
        for row in backup_code_rows
        if row.used_at is None and row.revoked_at is None
    ]

    assert old_unused_code.revoked_at is not None
    assert old_used_code.used_at is not None
    assert old_revoked_code.revoked_at is not None
    assert len(active_rows) == 10

    stored_hashes = {row.code_hash for row in active_rows}
    assert not any(raw_code in stored_hashes for raw_code in raw_codes)

    status = await build_backup_code_status(
        db=integration_db,
        account=admin,
        account_type="admin",
    )

    assert status["backup_codes_available"] is True
    assert status["available_backup_code_count"] == 10
