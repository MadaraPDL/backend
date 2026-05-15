from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import app.api.v1.endpoints.auth.login as login_endpoint
from app.db.session import get_db
from app.main import app
from app.services.auth_service import EmailDeliveryRequiredError


class FakeDB:
    async def commit(self):
        return None

    async def rollback(self):
        return None


async def override_get_db():
    yield FakeDB()


@pytest.fixture(autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def valid_login_payload():
    return {
        "account_type": "admin",
        "identifier": "admin@test.com",
        "password": "password123",
    }


def test_login_returns_401_for_invalid_credentials(monkeypatch):
    async def fake_start_login(*args, **kwargs):
        return None

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)

    response = client.post("/api/v1/auth/login", json=valid_login_payload())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_returns_mfa_setup_required_response(monkeypatch):
    account_id = uuid4()

    async def fake_start_login(*args, **kwargs):
        return (
            {
                "mfa_setup_required": True,
                "message": "MFA setup is required before this account can complete login.",
                "account_type": "admin",
                "account_id": account_id,
            },
            None,
        )

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)

    response = client.post("/api/v1/auth/login", json=valid_login_payload())

    assert response.status_code == 200

    body = response.json()

    assert body["mfa_setup_required"] is True
    assert body["account_type"] == "admin"
    assert body["account_id"] == str(account_id)
    assert "access_token" not in body


def test_login_returns_503_when_email_mfa_needs_email_delivery(monkeypatch):
    async def fake_start_login(*args, **kwargs):
        raise EmailDeliveryRequiredError

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)

    response = client.post("/api/v1/auth/login", json=valid_login_payload())

    assert response.status_code == 503
    assert "Email delivery is not configured" in response.json()["detail"]
