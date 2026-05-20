from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_secure_token, hash_password, hash_token
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.password_reset_token import PasswordResetToken
from app.schemas.auth import AccountType
from app.services.account_service import Account, get_account_by_identifier

PASSWORD_RESET_EXPIRY_MINUTES = 30


@dataclass(frozen=True)
class PasswordResetTokenResult:
    raw_token: str
    email: str
    full_name: str | None
    expires_in_minutes: int = PASSWORD_RESET_EXPIRY_MINUTES


def _account_token_filter(
    *,
    account_type: AccountType,
    account: Account,
):
    if account_type == "admin":
        return PasswordResetToken.admin_id == account.id

    return PasswordResetToken.app_user_id == account.id


async def mark_active_password_reset_tokens_used_for_account(
    *,
    db: AsyncSession,
    account_type: AccountType,
    account: Account,
    used_at: datetime,
) -> None:
    stmt = (
        update(PasswordResetToken)
        .where(
            PasswordResetToken.account_type == account_type,
            _account_token_filter(
                account_type=account_type,
                account=account,
            ),
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > used_at,
        )
        .values(used_at=used_at)
    )

    await db.execute(stmt)


async def create_password_reset_token(
    db: AsyncSession,
    account_type: AccountType,
    identifier: str,
) -> PasswordResetTokenResult | None:
    account = await get_account_by_identifier(
        db=db,
        account_type=account_type,
        identifier=identifier,
    )

    if account is None:
        return None

    now = datetime.now(timezone.utc)

    await mark_active_password_reset_tokens_used_for_account(
        db=db,
        account_type=account_type,
        account=account,
        used_at=now,
    )

    raw_token = generate_secure_token()
    token_hash = hash_token(raw_token)

    if account_type == "admin":
        reset_token = PasswordResetToken(
            account_type=account_type,
            admin_id=account.id,
            app_user_id=None,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=PASSWORD_RESET_EXPIRY_MINUTES),
        )
    else:
        reset_token = PasswordResetToken(
            account_type=account_type,
            admin_id=None,
            app_user_id=account.id,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=PASSWORD_RESET_EXPIRY_MINUTES),
        )

    db.add(reset_token)
    await db.flush()

    return PasswordResetTokenResult(
        raw_token=raw_token,
        email=account.email,
        full_name=account.full_name,
    )


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

    await mark_active_password_reset_tokens_used_for_account(
        db=db,
        account_type=reset_token.account_type,
        account=account,
        used_at=now,
    )

    reset_token.used_at = now

    await db.flush()

    return account
