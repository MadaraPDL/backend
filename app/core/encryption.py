from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class EncryptionNotConfiguredError(RuntimeError):
    """Raised when encryption is required but no encryption key is configured."""


class DecryptionError(RuntimeError):
    """Raised when encrypted data cannot be decrypted."""


@lru_cache(maxsize=1)
def get_fernet() -> Fernet:
    if not settings.DATA_ENCRYPTION_KEY:
        raise EncryptionNotConfiguredError(
            "DATA_ENCRYPTION_KEY is required for encrypting sensitive values."
        )

    return Fernet(settings.DATA_ENCRYPTION_KEY.encode("utf-8"))


def encrypt_text(value: str) -> str:
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(encrypted_value: str) -> str:
    try:
        return get_fernet().decrypt(
            encrypted_value.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken as exc:
        raise DecryptionError("Encrypted value could not be decrypted.") from exc
