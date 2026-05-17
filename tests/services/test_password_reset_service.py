from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.services.password_reset_service as service
from app.models.admin import Admin
from app.models.password_reset_token import PasswordResetToken


class FakeScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeDB:
    def __init__(self):
        self.executed = []
        self.added = []
        self.flushed = False
        self.account = None
        self.reset_token = None

    async def execute(self, stmt):
        self.executed.append(stmt)
        return FakeScalarResult(self.reset_token)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def get(self, model, object_id):
        return self.account


def _admin_account():
    return SimpleNamespace(
        id=uuid4(),
        password_hash="old-hash",
        password_changed_at=None,
    )


@pytest.mark.asyncio
async def test_create_password_reset_token_invalidates_existing_active_tokens(monkeypatch) -> None:
    db = FakeDB()
    account = _admin_account()

    async def fake_get_account_by_identifier(*args, **kwargs):
        return account

    monkeypatch.setattr(service, "get_account_by_identifier", fake_get_account_by_identifier)
    monkeypatch.setattr(service, "generate_secure_token", lambda: "raw-token")
    monkeypatch.setattr(service, "hash_token", lambda raw_token: f"hashed-{raw_token}")

    raw_token = await service.create_password_reset_token(
        db=db,
        account_type="admin",
        identifier="admin@test.com",
    )

    assert raw_token == "raw-token"
    assert len(db.executed) == 1
    assert len(db.added) == 1
    assert isinstance(db.added[0], PasswordResetToken)
    assert db.added[0].admin_id == account.id
    assert db.added[0].token_hash == "hashed-raw-token"
    assert db.flushed is True


@pytest.mark.asyncio
async def test_reset_password_with_token_invalidates_all_active_account_tokens(monkeypatch) -> None:
    db = FakeDB()
    account = _admin_account()
    db.account = account
    db.reset_token = SimpleNamespace(
        account_type="admin",
        admin_id=account.id,
        app_user_id=None,
        used_at=None,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    monkeypatch.setattr(service, "hash_token", lambda raw_token: f"hashed-{raw_token}")
    monkeypatch.setattr(service, "hash_password", lambda password: f"hashed-password-{password}")

    result = await service.reset_password_with_token(
        db=db,
        raw_token="raw-token",
        new_password="NewPassword123!",
    )

    assert result is account
    assert account.password_hash == "hashed-password-NewPassword123!"
    assert account.password_changed_at is not None
    assert db.reset_token.used_at is not None
    assert db.flushed is True
    assert len(db.executed) == 2
