from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_secure_token, hash_token
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.email_verification_token import EmailVerificationToken
from app.schemas.auth import AccountType
from app.services.account_service import Account


async def create_email_verification_token(
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> str:
    raw_token = generate_secure_token()
    token_hash = hash_token(raw_token)

    verification_token = EmailVerificationToken(
        account_type=account_type,
        admin_id=account.id if account_type == "admin" else None,
        app_user_id=account.id if account_type == "app_user" else None,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(verification_token)
    await db.flush()

    return raw_token


async def get_email_verification_token(
    db: AsyncSession,
    raw_token: str,
) -> EmailVerificationToken | None:
    token_hash = hash_token(raw_token)

    stmt = select(EmailVerificationToken).where(
        EmailVerificationToken.token_hash == token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def is_email_verification_token_active(
    verification_token: EmailVerificationToken,
) -> bool:
    now = datetime.now(timezone.utc)

    if verification_token.used_at is not None:
        return False

    if verification_token.expires_at <= now:
        return False

    return True


async def verify_email_with_token(
    db: AsyncSession,
    raw_token: str,
) -> Account | None:
    verification_token = await get_email_verification_token(
        db=db,
        raw_token=raw_token,
    )

    if verification_token is None:
        return None

    if not is_email_verification_token_active(verification_token):
        return None

    if verification_token.account_type == "admin":
        if verification_token.admin_id is None:
            return None

        account = await db.get(Admin, verification_token.admin_id)
    else:
        if verification_token.app_user_id is None:
            return None

        account = await db.get(AppUser, verification_token.app_user_id)

    if account is None:
        return None

    now = datetime.now(timezone.utc)

    account.email_verified_at = now
    verification_token.used_at = now

    await db.flush()

    return account