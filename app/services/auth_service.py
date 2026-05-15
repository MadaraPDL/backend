from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import AccountType
from app.services.account_service import (
    Account,
    authenticate_account,
    get_account_mfa_method,
)
from app.services.mfa_service import (
    create_mfa_challenge,
    get_mfa_challenge_by_token,
    verify_mfa_challenge_code,
)
from app.services.mfa_setup_service import build_mfa_setup_response

class EmailDeliveryRequiredError(RuntimeError):
    """Raised when an email-based auth flow is requested without email delivery."""


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
        "role": getattr(account, "role", None) if account_type == "admin" else None,
    }


async def start_login(
    db: AsyncSession,
    account_type: AccountType,
    identifier: str,
    password: str,
) -> tuple[dict, str | None] | None:
    account = await authenticate_account(
        db=db,
        account_type=account_type,
        identifier=identifier,
        password=password,
    )

    if account is None:
        return None

    if account.mfa_required and not account.mfa_enabled:
        return await build_mfa_setup_response(
            db=db,
            account=account,
            account_type=account_type,
        ), None

    if not account.mfa_enabled:
        return build_auth_token_response(
            account=account,
            account_type=account_type,
        ), None

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