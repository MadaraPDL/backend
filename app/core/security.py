from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from uuid import UUID

import jwt
import hashlib
import hmac
import secrets
from pwdlib import PasswordHash

from app.core.config import settings

AccountType = Literal["admin","app_user"]

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(
        subject: str | UUID,
        account_type: AccountType,
        expires_delta: timedelta | None = None
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(subject),
        "account_type": account_type,
        "iat": now,
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={
            "require": ["sub","account_type","iat","exp"],
        }
    )

def generate_secure_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def generate_numeric_code(length: int =6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


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
        "purpose": "mfa_setup",
        "authenticator_secret": authenticator_secret,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_mfa_setup_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={
            "require": [
                "sub",
                "setup_account_type",
                "purpose",
                "authenticator_secret",
                "iat",
                "exp",
            ],
        },
    )

    if payload.get("purpose") != "mfa_setup":
        raise jwt.InvalidTokenError("Invalid MFA setup token purpose.")

    return payload
