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


def is_email_mfa_active(account: Account) -> bool:
    explicit_value = getattr(account, "email_mfa_enabled", None)

    if explicit_value is not None:
        return bool(explicit_value)

    return bool(
        getattr(account, "mfa_enabled", False)
        and getattr(account, "preferred_mfa_method", None) == "email"
    )


def is_authenticator_mfa_active(account: Account) -> bool:
    explicit_value = getattr(account, "authenticator_mfa_enabled", None)

    if explicit_value is not None:
        return bool(explicit_value)

    return bool(
        getattr(account, "mfa_enabled", False)
        and getattr(account, "preferred_mfa_method", None) == "authenticator"
    )


def is_any_mfa_method_active(account: Account) -> bool:
    return is_email_mfa_active(account) or is_authenticator_mfa_active(account)


def get_active_mfa_methods(account: Account) -> list[MFAMethod]:
    methods: list[MFAMethod] = []

    if is_email_mfa_active(account):
        methods.append("email")

    if is_authenticator_mfa_active(account):
        methods.append("authenticator")

    return methods


def sync_legacy_mfa_enabled(account: Account) -> None:
    account.mfa_enabled = is_any_mfa_method_active(account)


def get_account_mfa_method(
    account: Account,
    account_type: AccountType,
) -> MFAMethod:
    active_methods = get_active_mfa_methods(account)

    if not active_methods:
        return get_default_mfa_method(account_type)

    if account.preferred_mfa_method in active_methods:
        return account.preferred_mfa_method

    default_method = get_default_mfa_method(account_type)

    if default_method in active_methods:
        return default_method

    return active_methods[0]

def is_mfa_method_active(account: Account, method: MFAMethod) -> bool:
    if method == "email":
        return is_email_mfa_active(account)

    if method == "authenticator":
        return is_authenticator_mfa_active(account)

    return False

