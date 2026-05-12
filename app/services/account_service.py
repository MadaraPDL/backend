from __future__ import annotations

from typing import TypeAlias

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import AccountType, MFAMethod


Account: TypeAlias = Admin | AppUser


def normalize_identifier(identifier: str) -> str:
    return identifier.strip().lower()


async def get_account_by_identifier(
    db: AsyncSession,
    account_type: AccountType,
    identifier: str,
) -> Account | None:
    normalized_identifier = normalize_identifier(identifier)

    model = Admin if account_type == "admin" else AppUser

    stmt = select(model).where(
        or_(
            func.lower(model.email) == normalized_identifier,
            func.lower(model.username) == normalized_identifier,
        )
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def authenticate_account(
    db: AsyncSession,
    account_type: AccountType,
    identifier: str,
    password: str,
) -> Account | None:
    account = await get_account_by_identifier(
        db=db,
        account_type=account_type,
        identifier=identifier,
    )

    if account is None:
        return None

    if not verify_password(password, account.password_hash):
        return None

    if account.status != "active":
        return None

    return account


def get_default_mfa_method(account_type: AccountType) -> MFAMethod:
    return "authenticator" if account_type == "admin" else "email"


def get_account_mfa_method(
    account: Account,
    account_type: AccountType,
) -> MFAMethod:
    if account.preferred_mfa_method in ("email", "authenticator"):
        return account.preferred_mfa_method

    return get_default_mfa_method(account_type)