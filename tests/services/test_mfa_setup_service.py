from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.services.mfa_setup_service as mfa_setup_service


class FakeDB:
    def __init__(self):
        self.added = None

    def add(self, value):
        self.added = value

    async def execute(self, stmt):
        return None

    async def flush(self):
        return None


@pytest.mark.asyncio
async def test_build_mfa_setup_response_stores_encrypted_pending_secret(monkeypatch):
    db = FakeDB()

    fake_account = SimpleNamespace(
        id=uuid4(),
        email="admin@test.com",
    )

    monkeypatch.setattr(
        mfa_setup_service,
        "generate_authenticator_secret",
        lambda: "RAWSECRET123",
    )

    monkeypatch.setattr(
        mfa_setup_service,
        "generate_mfa_setup_token",
        lambda: ("raw-setup-token", "hashed-setup-token"),
    )

    monkeypatch.setattr(
        mfa_setup_service,
        "encrypt_text",
        lambda value: f"encrypted::{value}",
    )

    response = await mfa_setup_service.build_mfa_setup_response(
        db=db,
        account=fake_account,
        account_type="admin",
    )

    assert response["mfa_setup_token"] == "raw-setup-token"
    assert response["authenticator_secret"] == "RAWSECRET123"

    assert db.added is not None
    assert db.added.setup_token_hash == "hashed-setup-token"
    assert db.added.authenticator_secret == "encrypted::RAWSECRET123"
    assert db.added.authenticator_secret != "RAWSECRET123"


def test_mfa_setup_challenge_is_inactive_after_five_attempts():
    challenge = SimpleNamespace(
        used_at=None,
        revoked_at=None,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        attempt_count=5,
        authenticator_secret="encrypted-secret",
    )

    assert mfa_setup_service.is_mfa_setup_challenge_active(challenge) is False
