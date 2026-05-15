from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.mfa_setup_challenge import MFASetupChallenge
from app.schemas.auth.common import AccountType
from app.services.account_service import Account
from app.services.mfa_service import (
    generate_authenticator_secret,
    verify_authenticator_code,
)
from app.services.mfa_setup_token_service import (
    generate_mfa_setup_token,
    hash_mfa_setup_token,
)

MAX_MFA_SETUP_ATTEMPTS = 10


def is_mfa_setup_challenge_active(challenge: MFASetupChallenge) -> bool:
    now = datetime.now(timezone.utc)

    if challenge.used_at is not None:
        return False

    if challenge.expires_at <= now:
        return False

    if challenge.attempt_count >= MAX_MFA_SETUP_ATTEMPTS:
        return False

    return True


async def build_mfa_setup_response(
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> dict:
    authenticator_secret = generate_authenticator_secret()
    raw_setup_token, setup_token_hash = generate_mfa_setup_token()

    setup_challenge = MFASetupChallenge(
        account_type=account_type,
        admin_id=account.id if account_type == "admin" else None,
        app_user_id=account.id if account_type == "app_user" else None,
        setup_token_hash=setup_token_hash,
        authenticator_secret=authenticator_secret,
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

    if not verify_authenticator_code(challenge.authenticator_secret, code):
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

    account.mfa_secret = challenge.authenticator_secret
    account.mfa_enabled = True
    account.preferred_mfa_method = "authenticator"
    account.updated_at = datetime.now(timezone.utc)

    challenge.used_at = datetime.now(timezone.utc)

    await db.flush()

    return account, challenge.account_type
