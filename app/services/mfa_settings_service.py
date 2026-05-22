from __future__ import annotations

from datetime import datetime, timezone

from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import AccountType, MFAMethod
from app.services.account_service import (
    Account,
    get_account_mfa_method,
    get_active_mfa_methods,
    is_authenticator_mfa_active,
    is_email_mfa_active,
    sync_legacy_mfa_enabled,
)


class CannotDisableLastMFAMethodError(RuntimeError):
    """Raised when an account would be left without MFA while MFA is required."""


class MFAMethodNotActiveError(RuntimeError):
    """Raised when a requested preferred MFA method is not active."""


def build_mfa_status(
    *,
    account: Account,
    account_type: AccountType,
) -> dict:
    email_active = is_email_mfa_active(account)
    authenticator_active = is_authenticator_mfa_active(account)
    active_methods = get_active_mfa_methods(account)

    sync_legacy_mfa_enabled(account)

    preferred_method: MFAMethod | None = None

    if active_methods:
        preferred_method = get_account_mfa_method(
            account=account,
            account_type=account_type,
        )

    return {
        "account_type": account_type,
        "mfa_required": account.mfa_required,
        "mfa_enabled": account.mfa_enabled,
        "email_mfa_enabled": email_active,
        "authenticator_mfa_enabled": authenticator_active,
        "preferred_mfa_method": preferred_method,
        "active_methods": active_methods,
        "can_disable_email_mfa": not (
            account.mfa_required and email_active and not authenticator_active
        ),
        "can_disable_authenticator_mfa": not (
            account.mfa_required and authenticator_active and not email_active
        ),
    }


def _touch_account(account: Admin | AppUser) -> None:
    account.updated_at = datetime.now(timezone.utc)


def enable_email_mfa(account: Account) -> None:
    had_active_method = bool(get_active_mfa_methods(account))

    account.email_mfa_enabled = True

    if not had_active_method:
        account.preferred_mfa_method = "email"

    sync_legacy_mfa_enabled(account)
    _touch_account(account)


def disable_email_mfa(account: Account) -> None:
    email_active = is_email_mfa_active(account)
    authenticator_active = is_authenticator_mfa_active(account)

    if not email_active:
        return

    if account.mfa_required and not authenticator_active:
        raise CannotDisableLastMFAMethodError(
            "Cannot disable the last active MFA method while MFA is required."
        )

    account.email_mfa_enabled = False

    if account.preferred_mfa_method == "email":
        account.preferred_mfa_method = "authenticator" if authenticator_active else None

    sync_legacy_mfa_enabled(account)
    _touch_account(account)


def disable_authenticator_mfa(account: Account) -> None:
    email_active = is_email_mfa_active(account)
    authenticator_active = is_authenticator_mfa_active(account)

    if not authenticator_active:
        return

    if account.mfa_required and not email_active:
        raise CannotDisableLastMFAMethodError(
            "Cannot disable the last active MFA method while MFA is required."
        )

    account.authenticator_mfa_enabled = False
    account.mfa_secret = None

    if account.preferred_mfa_method == "authenticator":
        account.preferred_mfa_method = "email" if email_active else None

    sync_legacy_mfa_enabled(account)
    _touch_account(account)


def set_preferred_mfa_method(
    *,
    account: Account,
    method: MFAMethod,
) -> None:
    if method == "email" and not is_email_mfa_active(account):
        raise MFAMethodNotActiveError("Email MFA is not active for this account.")

    if method == "authenticator" and not is_authenticator_mfa_active(account):
        raise MFAMethodNotActiveError(
            "Authenticator MFA is not active for this account."
        )

    account.preferred_mfa_method = method
    sync_legacy_mfa_enabled(account)
    _touch_account(account)
