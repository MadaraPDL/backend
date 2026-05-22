from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import AccountType, MFAMethod
from app.schemas.auth.mfa_settings import MFASettingsAction
from app.services.account_service import (
    Account,
    get_account_mfa_method,
    get_active_mfa_methods,
    is_authenticator_mfa_active,
    is_email_mfa_active,
    sync_legacy_mfa_enabled,
)
from app.services.mfa_service import (
    get_mfa_challenge_by_token,
    verify_mfa_challenge_code,
)


class CannotDisableLastMFAMethodError(RuntimeError):
    """Raised when an account would be left without MFA while MFA is required."""


class MFAMethodNotActiveError(RuntimeError):
    """Raised when a requested preferred MFA method is not active."""


class InvalidMFASettingsChallengeError(RuntimeError):
    """Raised when an MFA settings challenge is invalid for the current account."""


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


def _get_account_id(account: Account) -> UUID:
    return account.id


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


async def verify_mfa_settings_challenge(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    challenge_token: str,
    code: str,
) -> None:
    challenge = await get_mfa_challenge_by_token(
        db=db,
        raw_challenge_token=challenge_token,
    )

    if challenge is None:
        raise InvalidMFASettingsChallengeError("Invalid or expired MFA challenge.")

    if challenge.account_type != account_type:
        raise InvalidMFASettingsChallengeError("Invalid or expired MFA challenge.")

    if account_type == "admin":
        if challenge.admin_id != _get_account_id(account):
            raise InvalidMFASettingsChallengeError("Invalid or expired MFA challenge.")
    else:
        if challenge.app_user_id != _get_account_id(account):
            raise InvalidMFASettingsChallengeError("Invalid or expired MFA challenge.")

    verified_account = await verify_mfa_challenge_code(
        db=db,
        challenge=challenge,
        code=code,
    )

    if verified_account is None or verified_account.id != account.id:
        raise InvalidMFASettingsChallengeError("Invalid or expired MFA challenge.")


async def apply_verified_mfa_settings_action(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    action: MFASettingsAction,
    challenge_token: str,
    code: str,
) -> None:
    await verify_mfa_settings_challenge(
        db=db,
        account=account,
        account_type=account_type,
        challenge_token=challenge_token,
        code=code,
    )

    if action == "enable_email":
        enable_email_mfa(account)
        return

    if action == "disable_email":
        disable_email_mfa(account)
        return

    if action == "disable_authenticator":
        disable_authenticator_mfa(account)
        return

    if action == "prefer_email":
        set_preferred_mfa_method(account=account, method="email")
        return

    if action == "prefer_authenticator":
        set_preferred_mfa_method(account=account, method="authenticator")
        return
