from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.auth_service import start_login


@pytest.mark.asyncio
async def test_login_requires_mfa_setup(monkeypatch):
    fake_account = SimpleNamespace(
        id=uuid4(),
        full_name="Test Admin",
        email="admin@test.com",
        role="isp_admin",
        mfa_required=True,
        mfa_enabled=False,
    )

    async def fake_authenticate_account(*args, **kwargs):
        return fake_account

    monkeypatch.setattr(
        "app.services.auth_service.authenticate_account",
        fake_authenticate_account,
    )

    result = await start_login(
        db=None,
        account_type="admin",
        identifier="admin@test.com",
        password="password123",
    )

    assert result is not None

    response_data, raw_email_code = result

    assert raw_email_code is None
    assert response_data["mfa_setup_required"] is True
    assert response_data["account_id"] == fake_account.id