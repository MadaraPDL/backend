from __future__ import annotations

from app.core.security import generate_secure_token, hash_token


def generate_mfa_setup_token() -> tuple[str, str]:
    raw_token = generate_secure_token()
    token_hash = hash_token(raw_token)

    return raw_token, token_hash


def hash_mfa_setup_token(raw_token: str) -> str:
    return hash_token(raw_token)
