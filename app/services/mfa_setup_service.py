from __future__ import annotations

from datetime import datetime, timezone

import pyotp
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth.common import AccountType
from app.services.account_service import Account
from app.services.mfa_service import generate_authenticator_secret, verify_authenticator_code
from app.services.mfa_setup_token_service import (
    create_mfa_setup_token,
    decode_mfa_setup_token,
)


def build_mfa_setup_response(
    account: Account,
    account_type: AccountType,
) -> dict:
    authenticator_secret = generate_authenticator_secret()

    mfa_setup_token = create_mfa_setup_token(
        subject=account.id,
        setup_account_type=account_type,
        authenticator_secret=authenticator_secret,
    )

    authenticator_uri = pyotp.TOTP(authenticator_secret).provisioning_uri(
        name=account.email,
        issuer_name=settings.APP_NAME,
    )

    return {
        "mfa_setup_required": True,
        "message": "MFA setup is required before this account can complete login.",
        "account_type": account_type,
        "account_id": account.id,
        "method": "authenticator",
        "mfa_setup_token": mfa_setup_token,
        "authenticator_secret": authenticator_secret,
        "authenticator_uri": authenticator_uri,
    }


async def complete_mfa_setup(
    db: AsyncSession,
    mfa_setup_token: str,
    code: str,
) -> tuple[Account, AccountType] | None:
    payload = decode_mfa_setup_token(mfa_setup_token)

    if payload is None:
        return None

    if not verify_authenticator_code(payload.authenticator_secret, code):
        return None

    model = Admin if payload.account_type == "admin" else AppUser
    account = await db.get(model, payload.account_id)

    if account is None:
        return None

    if account.status != "active":
        return None

    if not account.mfa_required:
        return None

    if account.mfa_enabled:
        return None

    account.mfa_secret = payload.authenticator_secret
    account.mfa_enabled = True
    account.preferred_mfa_method = "authenticator"
    account.updated_at = datetime.now(timezone.utc)

    await db.flush()

    return account, payload.account_type
