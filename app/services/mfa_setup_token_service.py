from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.core.config import settings
from app.core.security import AccountType, generate_secure_token


MFA_SETUP_TOKEN_AUDIENCE = "pulsefi:mfa_setup"
MFA_SETUP_TOKEN_TYPE = "mfa_setup"


@dataclass(frozen=True)
class MFASetupTokenPayload:
    account_id: UUID
    account_type: AccountType
    authenticator_secret: str


def create_mfa_setup_token(
    subject: str | UUID,
    setup_account_type: AccountType,
    authenticator_secret: str,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=10)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(subject),
        "setup_account_type": setup_account_type,
        "purpose": MFA_SETUP_TOKEN_TYPE,
        "token_type": MFA_SETUP_TOKEN_TYPE,
        "authenticator_secret": authenticator_secret,
        "aud": MFA_SETUP_TOKEN_AUDIENCE,
        "iss": settings.APP_NAME,
        "jti": generate_secure_token(),
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_mfa_setup_token(token: str) -> MFASetupTokenPayload | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=MFA_SETUP_TOKEN_AUDIENCE,
            issuer=settings.APP_NAME,
            options={
                "require": [
                    "sub",
                    "setup_account_type",
                    "purpose",
                    "token_type",
                    "authenticator_secret",
                    "aud",
                    "iss",
                    "jti",
                    "iat",
                    "exp",
                ],
            },
        )
    except jwt.PyJWTError:
        return None

    if payload.get("purpose") != MFA_SETUP_TOKEN_TYPE:
        return None

    if payload.get("token_type") != MFA_SETUP_TOKEN_TYPE:
        return None

    account_type = payload.get("setup_account_type")
    if account_type not in ("admin", "app_user"):
        return None

    authenticator_secret = payload.get("authenticator_secret")
    if not isinstance(authenticator_secret, str) or not authenticator_secret:
        return None

    try:
        account_id = UUID(str(payload.get("sub")))
    except ValueError:
        return None

    return MFASetupTokenPayload(
        account_id=account_id,
        account_type=account_type,
        authenticator_secret=authenticator_secret,
    )
