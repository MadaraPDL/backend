from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_secure_token, hash_password, hash_token
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.password_reset_token import PasswordResetToken
from app.schemas.auth import AccountType
from app.services.account_service import Account, get_account_by_identifier


async def create_password_reset_token(
    db: AsyncSession,
    account_type: AccountType,
    identifier: str,
) -> str | None:
    account = await get_account_by_identifier(
        db=db,
        account_type=account_type,
        identifier=identifier,
    )

    if account is None:
        return None

    raw_token = generate_secure_token()
    token_hash = hash_token(raw_token)

    if account_type == "admin":
        reset_token = PasswordResetToken(
            account_type=account_type,
            admin_id=account.id,
            app_user_id=None,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
    else:
        reset_token = PasswordResetToken(
            account_type=account_type,
            admin_id=None,
            app_user_id=account.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )

    db.add(reset_token)
    await db.flush()

    return raw_token


async def get_password_reset_token(
    db: AsyncSession,
    raw_token: str,
) -> PasswordResetToken | None:
    token_hash = hash_token(raw_token)

    stmt = select(PasswordResetToken).where(
        PasswordResetToken.token_hash == token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def is_password_reset_token_active(reset_token: PasswordResetToken) -> bool:
    now = datetime.now(timezone.utc)

    if reset_token.used_at is not None:
        return False

    if reset_token.expires_at <= now:
        return False

    return True


async def reset_password_with_token(
    db: AsyncSession,
    raw_token: str,
    new_password: str,
) -> Account | None:
    reset_token = await get_password_reset_token(
        db=db,
        raw_token=raw_token,
    )

    if reset_token is None:
        return None

    if not is_password_reset_token_active(reset_token):
        return None

    if reset_token.account_type == "admin":
        if reset_token.admin_id is None:
            return None

        account = await db.get(Admin, reset_token.admin_id)
    else:
        if reset_token.app_user_id is None:
            return None

        account = await db.get(AppUser, reset_token.app_user_id)

    if account is None:
        return None

    now = datetime.now(timezone.utc)

    account.password_hash = hash_password(new_password)
    account.password_changed_at = now
    reset_token.used_at = now

    await db.flush()

    return account