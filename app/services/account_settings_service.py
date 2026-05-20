from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import AccountType, MFAMethod
from app.services.account_service import Account, get_account_mfa_method
from app.services.mfa_service import (
    create_mfa_challenge,
    get_mfa_challenge_by_token,
    verify_mfa_challenge_code,
)


class ProfileUpdateMFANotEnabledError(RuntimeError):
    pass


class ProfileUpdateConflictError(RuntimeError):
    pass


class InvalidProfileUpdateChallengeError(RuntimeError):
    pass


def get_profile_update_mfa_method(
    *,
    account: Account,
    account_type: AccountType,
) -> MFAMethod:
    if not account.mfa_enabled:
        raise ProfileUpdateMFANotEnabledError

    return get_account_mfa_method(
        account=account,
        account_type=account_type,
    )


async def create_profile_update_challenge(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    method: MFAMethod,
):
    return await create_mfa_challenge(
        db=db,
        account=account,
        account_type=account_type,
        method=method,
    )


async def update_current_account_identity(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    email: str | None,
    username: str | None,
    mfa_challenge_token: str,
    mfa_code: str,
) -> Account:
    challenge = await get_mfa_challenge_by_token(
        db=db,
        raw_challenge_token=mfa_challenge_token,
    )

    if challenge is None or challenge.account_type != account_type:
        raise InvalidProfileUpdateChallengeError

    verified_account = await verify_mfa_challenge_code(
        db=db,
        challenge=challenge,
        code=mfa_code,
    )

    if verified_account is None or verified_account.id != account.id:
        raise InvalidProfileUpdateChallengeError

    model = Admin if account_type == "admin" else AppUser
    updated_email = email.strip().lower() if email is not None else account.email
    updated_username = username.strip() if username is not None else account.username

    await _ensure_unique_email(
        db=db,
        model=model,
        account=account,
        email=updated_email,
    )

    if updated_username:
        await _ensure_unique_username(
            db=db,
            model=model,
            account=account,
            username=updated_username,
        )

    now = datetime.now(timezone.utc)
    account.email = updated_email
    account.username = updated_username or None
    account.updated_at = now

    await db.flush()
    return account


async def _ensure_unique_email(
    *,
    db: AsyncSession,
    model: type[Admin] | type[AppUser],
    account: Account,
    email: str,
) -> None:
    stmt = select(model.id).where(
        func.lower(model.email) == email.lower(),
        model.id != account.id,
    )

    result = await db.execute(stmt)

    if result.scalar_one_or_none() is not None:
        raise ProfileUpdateConflictError("Email is already in use.")


async def _ensure_unique_username(
    *,
    db: AsyncSession,
    model: type[Admin] | type[AppUser],
    account: Account,
    username: str,
) -> None:
    stmt = select(model.id).where(
        func.lower(model.username) == username.lower(),
        model.id != account.id,
    )

    result = await db.execute(stmt)

    if result.scalar_one_or_none() is not None:
        raise ProfileUpdateConflictError("Username is already in use.")
