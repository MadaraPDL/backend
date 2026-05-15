from types import SimpleNamespace

import pytest
from cryptography.fernet import Fernet

import app.core.encryption as encryption


def reset_encryption_cache():
    encryption.get_fernet.cache_clear()


def test_encrypt_text_round_trip(monkeypatch):
    key = Fernet.generate_key().decode("utf-8")

    monkeypatch.setattr(
        encryption,
        "settings",
        SimpleNamespace(DATA_ENCRYPTION_KEY=key),
    )
    reset_encryption_cache()

    encrypted = encryption.encrypt_text("secret-value")

    assert encrypted != "secret-value"
    assert encryption.decrypt_text(encrypted) == "secret-value"


def test_encrypt_text_requires_key(monkeypatch):
    monkeypatch.setattr(
        encryption,
        "settings",
        SimpleNamespace(DATA_ENCRYPTION_KEY=""),
    )
    reset_encryption_cache()

    with pytest.raises(encryption.EncryptionNotConfiguredError):
        encryption.encrypt_text("secret-value")
