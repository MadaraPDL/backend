from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import AccountType, MFAMethod
from app.services.account_service import (
    Account,
    authenticate_account,
    get_account_mfa_method,
    is_any_mfa_method_active,
    is_mfa_method_active,
    sync_legacy_mfa_enabled,
)
from app.services.email.email_service import send_login_mfa_email
from app.services.mfa_service import (
    create_mfa_challenge,
    get_mfa_challenge_by_token,
    verify_mfa_challenge_code,
)
from app.services.mfa_setup_service import build_mfa_setup_response


class EmailDeliveryRequiredError(RuntimeError):
    """Raised when an email-based auth flow is requested without email delivery."""


class MFAMethodNotAvailableError(RuntimeError):
    """Raised when the requested MFA login method is not active for the account."""


def build_auth_token_response(
    account: Account,
    account_type: AccountType,
) -> dict:
    access_token = create_access_token(
        subject=account.id,
        account_type=account_type,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "account_type": account_type,
        "account_id": account.id,
        "full_name": account.full_name,
        "email": account.email,
        "username": account.username,
        "role": getattr(account, "role", None) if account_type == "admin" else None,
    }


async def start_login(
    db: AsyncSession,
    account_type: AccountType,
    identifier: str,
    password: str,
    requested_mfa_method: MFAMethod | None = None,
) -> tuple[dict, str | None] | None:
    account = await authenticate_account(
        db=db,
        account_type=account_type,
        identifier=identifier,
        password=password,
    )

    if account is None:
        return None

    sync_legacy_mfa_enabled(account)

    if account.mfa_required and not is_any_mfa_method_active(account):
        return await build_mfa_setup_response(
            db=db,
            account=account,
            account_type=account_type,
        ), None

    if not is_any_mfa_method_active(account):
        return build_auth_token_response(
            account=account,
            account_type=account_type,
        ), None

    if requested_mfa_method is not None:
        if not is_mfa_method_active(account, requested_mfa_method):
            raise MFAMethodNotAvailableError

        method = requested_mfa_method
    else:
        method = get_account_mfa_method(
            account=account,
            account_type=account_type,
        )

    if method == "email" and not settings.DEBUG and not settings.EMAIL_DELIVERY_ENABLED:
        raise EmailDeliveryRequiredError

    challenge, raw_challenge_token, raw_email_code = await create_mfa_challenge(
        db=db,
        account=account,
        account_type=account_type,
        method=method,
    )

    if method == "email" and raw_email_code is not None:
        await send_login_mfa_email(
            to_email=account.email,
            full_name=account.full_name,
            code=raw_email_code,
            expires_in_minutes=10,
        )

    return {
        "mfa_required": True,
        "challenge_token": raw_challenge_token,
        "method": method,
        "expires_at": challenge.expires_at,
        "message": "MFA verification is required to complete login.",
    }, raw_email_code


async def complete_mfa_login(
    db: AsyncSession,
    challenge_token: str,
    code: str,
) -> dict | None:
    challenge = await get_mfa_challenge_by_token(
        db=db,
        raw_challenge_token=challenge_token,
    )

    if challenge is None:
        return None

    account = await verify_mfa_challenge_code(
        db=db,
        challenge=challenge,
        code=code,
    )

    if account is None:
        return None

    return build_auth_token_response(
        account=account,
        account_type=challenge.account_type,
    )
