from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import DecryptionError, decrypt_text
from app.core.security import (
    generate_numeric_code,
    generate_secure_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.mfa_backup_code import MFABackupCode
from app.models.mfa_challenge import MFAChallenge
from app.schemas.auth import AccountType, MFAMethod

Account = Admin | AppUser
MAX_MFA_ATTEMPTS = 10


def generate_authenticator_secret() -> str:
    return pyotp.random_base32()


def verify_authenticator_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


async def create_mfa_challenge(
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    method: MFAMethod,
) -> tuple[MFAChallenge, str, str | None]:
    raw_challenge_token = generate_secure_token()
    challenge_token_hash = hash_token(raw_challenge_token)

    raw_email_code: str | None = None
    code_hash: str | None = None

    if method == "email":
        raw_email_code = generate_numeric_code()
        code_hash = hash_password(raw_email_code)

    challenge = MFAChallenge(
        account_type=account_type,
        admin_id=account.id if account_type == "admin" else None,
        app_user_id=account.id if account_type == "app_user" else None,
        method=method,
        challenge_token_hash=challenge_token_hash,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(challenge)
    await db.flush()

    return challenge, raw_challenge_token, raw_email_code


async def get_mfa_challenge_by_token(
    db: AsyncSession,
    raw_challenge_token: str,
) -> MFAChallenge | None:
    challenge_token_hash = hash_token(raw_challenge_token)

    stmt = select(MFAChallenge).where(
        MFAChallenge.challenge_token_hash == challenge_token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def is_mfa_challenge_active(challenge: MFAChallenge) -> bool:
    now = datetime.now(timezone.utc)

    if challenge.used_at is not None:
        return False

    if challenge.expires_at <= now:
        return False

    if challenge.attempt_count >= MAX_MFA_ATTEMPTS:
        return False

    return True


async def get_account_from_challenge(
    db: AsyncSession,
    challenge: MFAChallenge,
) -> Account | None:
    if challenge.account_type == "admin":
        if challenge.admin_id is None:
            return None

        return await db.get(Admin, challenge.admin_id)

    if challenge.app_user_id is None:
        return None

    return await db.get(AppUser, challenge.app_user_id)


async def verify_backup_code(
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    code: str,
) -> bool:
    owner_filter = (
        MFABackupCode.admin_id == account.id
        if account_type == "admin"
        else MFABackupCode.app_user_id == account.id
    )

    stmt = select(MFABackupCode).where(
        MFABackupCode.account_type == account_type,
        MFABackupCode.used_at.is_(None),
        MFABackupCode.revoked_at.is_(None),
        owner_filter,
    )

    result = await db.execute(stmt)
    active_backup_codes = result.scalars().all()

    for backup_code in active_backup_codes:
        if verify_password(code, backup_code.code_hash):
            backup_code.used_at = datetime.now(timezone.utc)
            await db.flush()
            return True

    return False


async def verify_mfa_challenge_code(
    db: AsyncSession,
    challenge: MFAChallenge,
    code: str,
) -> Account | None:
    if not is_mfa_challenge_active(challenge):
        return None

    account = await get_account_from_challenge(db, challenge)

    if account is None:
        return None

    is_valid = False

    if challenge.method == "email":
        if challenge.code_hash is not None:
            is_valid = verify_password(code, challenge.code_hash)

    elif challenge.method == "authenticator":
        if account.mfa_secret is not None:
            try:
                authenticator_secret = decrypt_text(account.mfa_secret)
            except DecryptionError:
                authenticator_secret = None

            if authenticator_secret is not None:
                is_valid = verify_authenticator_code(
                    secret=authenticator_secret,
                    code=code,
                )

    if not is_valid:
        is_valid = await verify_backup_code(
            db=db,
            account=account,
            account_type=challenge.account_type,
            code=code,
        )

    if not is_valid:
        challenge.attempt_count += 1
        await db.flush()
        return None

    challenge.used_at = datetime.now(timezone.utc)
    await db.flush()

    return account
