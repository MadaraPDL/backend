from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pyotp
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.encryption import DecryptionError, decrypt_text, encrypt_text
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.mfa_setup_challenge import MFASetupChallenge
from app.schemas.auth.common import AccountType
from app.services.account_service import Account, sync_legacy_mfa_enabled
from app.services.mfa_service import (
    generate_authenticator_secret,
    verify_authenticator_code,
)
from app.services.mfa_setup_token_service import (
    generate_mfa_setup_token,
    hash_mfa_setup_token,
)

MAX_MFA_SETUP_ATTEMPTS = 5


def is_mfa_setup_challenge_active(challenge: MFASetupChallenge) -> bool:
    now = datetime.now(timezone.utc)

    if challenge.used_at is not None:
        return False

    if challenge.revoked_at is not None:
        return False

    if challenge.expires_at <= now:
        return False

    if challenge.attempt_count >= MAX_MFA_SETUP_ATTEMPTS:
        return False

    if not challenge.authenticator_secret:
        return False

    return True




async def redact_inactive_mfa_setup_challenge_secrets(
    db: AsyncSession,
) -> None:
    now = datetime.now(timezone.utc)

    stmt = (
        update(MFASetupChallenge)
        .where(
            MFASetupChallenge.authenticator_secret != "",
            (
                MFASetupChallenge.used_at.is_not(None)
                | MFASetupChallenge.revoked_at.is_not(None)
                | (MFASetupChallenge.expires_at <= now)
            ),
        )
        .values(authenticator_secret="")
    )

    await db.execute(stmt)


async def revoke_active_mfa_setup_challenges(
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> None:
    now = datetime.now(timezone.utc)

    owner_filter = (
        MFASetupChallenge.admin_id == account.id
        if account_type == "admin"
        else MFASetupChallenge.app_user_id == account.id
    )

    stmt = (
        update(MFASetupChallenge)
        .where(
            MFASetupChallenge.account_type == account_type,
            owner_filter,
            MFASetupChallenge.used_at.is_(None),
            MFASetupChallenge.revoked_at.is_(None),
            MFASetupChallenge.expires_at > now,
        )
        .values(revoked_at=now, authenticator_secret="")
    )

    await db.execute(stmt)


async def build_mfa_setup_response(
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> dict:
    await redact_inactive_mfa_setup_challenge_secrets(db=db)

    await revoke_active_mfa_setup_challenges(
        db=db,
        account=account,
        account_type=account_type,
    )

    authenticator_secret = generate_authenticator_secret()
    raw_setup_token, setup_token_hash = generate_mfa_setup_token()

    setup_challenge = MFASetupChallenge(
        account_type=account_type,
        admin_id=account.id if account_type == "admin" else None,
        app_user_id=account.id if account_type == "app_user" else None,
        setup_token_hash=setup_token_hash,
        authenticator_secret=encrypt_text(authenticator_secret),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(setup_challenge)
    await db.flush()

    authenticator_uri = pyotp.TOTP(authenticator_secret).provisioning_uri(
        name=account.email,
        issuer_name=settings.APP_NAME,
    )

    return {
        "mfa_setup_required": True,
        "message": "MFA setup is required before this account can complete login.",
        "account_type": account_type,
        "account_id": account.id,
        "method": "authenticator",
        "mfa_setup_token": raw_setup_token,
        "authenticator_secret": authenticator_secret,
        "authenticator_uri": authenticator_uri,
    }


async def get_mfa_setup_challenge_by_token(
    db: AsyncSession,
    raw_setup_token: str,
) -> MFASetupChallenge | None:
    setup_token_hash = hash_mfa_setup_token(raw_setup_token)

    stmt = select(MFASetupChallenge).where(
        MFASetupChallenge.setup_token_hash == setup_token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_account_from_setup_challenge(
    db: AsyncSession,
    challenge: MFASetupChallenge,
) -> Account | None:
    if challenge.account_type == "admin":
        if challenge.admin_id is None:
            return None

        return await db.get(Admin, challenge.admin_id)

    if challenge.app_user_id is None:
        return None

    return await db.get(AppUser, challenge.app_user_id)


async def complete_mfa_setup(
    db: AsyncSession,
    mfa_setup_token: str,
    code: str,
) -> tuple[Account, AccountType] | None:
    challenge = await get_mfa_setup_challenge_by_token(
        db=db,
        raw_setup_token=mfa_setup_token,
    )

    if challenge is None:
        return None

    if not is_mfa_setup_challenge_active(challenge):
        return None

    try:
        authenticator_secret = decrypt_text(challenge.authenticator_secret)
    except DecryptionError:
        return None

    if not verify_authenticator_code(authenticator_secret, code):
        challenge.attempt_count += 1
        await db.flush()
        return None

    account = await get_account_from_setup_challenge(
        db=db,
        challenge=challenge,
    )

    if account is None:
        return None

    if account.status != "active":
        return None

    if not account.mfa_required:
        return None

    if account.mfa_enabled:
        return None

    account.mfa_secret = encrypt_text(authenticator_secret)
    account.authenticator_mfa_enabled = True
    account.preferred_mfa_method = "authenticator"
    sync_legacy_mfa_enabled(account)
    account.updated_at = datetime.now(timezone.utc)

    challenge.used_at = datetime.now(timezone.utc)
    challenge.authenticator_secret = ""

    await db.flush()

    return account, challenge.account_type

async def complete_current_account_authenticator_setup(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    mfa_setup_token: str,
    code: str,
) -> bool:
    challenge = await get_mfa_setup_challenge_by_token(
        db=db,
        raw_setup_token=mfa_setup_token,
    )

    if challenge is None:
        return False

    if not is_mfa_setup_challenge_active(challenge):
        return False

    if challenge.account_type != account_type:
        return False

    if account_type == "admin" and challenge.admin_id != account.id:
        return False

    if account_type == "app_user" and challenge.app_user_id != account.id:
        return False

    if account.status != "active":
        return False

    if account.authenticator_mfa_enabled:
        return False

    try:
        authenticator_secret = decrypt_text(challenge.authenticator_secret)
    except DecryptionError:
        return False

    if not verify_authenticator_code(authenticator_secret, code):
        challenge.attempt_count += 1
        await db.flush()
        return False

    account.mfa_secret = encrypt_text(authenticator_secret)
    account.authenticator_mfa_enabled = True
    account.preferred_mfa_method = "authenticator"
    sync_legacy_mfa_enabled(account)
    account.updated_at = datetime.now(timezone.utc)

    challenge.used_at = datetime.now(timezone.utc)
    challenge.authenticator_secret = ""

    await db.flush()
    return True
