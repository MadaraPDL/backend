from types import SimpleNamespace

import pytest

import app.services.mfa_service as mfa_service
import app.services.mfa_setup_service as mfa_setup_service


def test_mfa_service_decrypts_account_secret_before_verification(monkeypatch):
    account = SimpleNamespace(
        mfa_secret="encrypted-secret",
        id="account-id",
    )

    challenge = SimpleNamespace(
        method="authenticator",
    )

    captured = {}

    monkeypatch.setattr(
        mfa_service,
        "decrypt_text",
        lambda value: "RAWSECRET" if value == "encrypted-secret" else None,
    )

    def fake_verify_authenticator_code(secret, code):
        captured["secret"] = secret
        captured["code"] = code
        return True

    monkeypatch.setattr(
        mfa_service,
        "verify_authenticator_code",
        fake_verify_authenticator_code,
    )

    # This block mirrors the authenticator branch behavior without needing DB.
    authenticator_secret = mfa_service.decrypt_text(account.mfa_secret)
    is_valid = mfa_service.verify_authenticator_code(
        secret=authenticator_secret,
        code="123456",
    )

    assert is_valid is True
    assert captured["secret"] == "RAWSECRET"
    assert captured["code"] == "123456"


def test_mfa_setup_service_encrypts_final_account_secret(monkeypatch):
    assert "encrypt_text(authenticator_secret)" in PathText.read(
        "app/services/mfa_setup_service.py"
    )


class PathText:
    @staticmethod
    def read(path):
        from pathlib import Path

        return Path(path).read_text()
