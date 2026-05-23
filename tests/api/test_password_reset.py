import app.api.v1.endpoints.auth.password_reset as password_reset_endpoint
from app.services.password_reset_service import PasswordResetTokenResult


def valid_forgot_password_payload():
    return {
        "account_type": "admin",
        "identifier": "admin@test.com",
    }


def test_forgot_password_sends_reset_link_and_returns_dev_url_in_debug(
    api_client,
    monkeypatch,
):
    sent_messages = []

    def fake_email_guard():
        return None

    async def fake_create_password_reset_token(*args, **kwargs):
        return PasswordResetTokenResult(
            raw_token="fake-reset-token",
            email="admin@test.com",
            full_name="Admin User",
        )

    async def fake_send_password_reset_email(**kwargs):
        sent_messages.append(kwargs)

    monkeypatch.setattr(
        password_reset_endpoint,
        "require_email_delivery_for_production",
        fake_email_guard,
    )

    monkeypatch.setattr(
        password_reset_endpoint,
        "create_password_reset_token",
        fake_create_password_reset_token,
    )

    monkeypatch.setattr(
        password_reset_endpoint,
        "send_password_reset_email",
        fake_send_password_reset_email,
    )

    monkeypatch.setattr(
        password_reset_endpoint.settings,
        "DEBUG",
        True,
    )

    response = api_client.post(
        "/api/v1/auth/password/forgot",
        json=valid_forgot_password_payload(),
    )

    assert response.status_code == 200

    body = response.json()

    assert "password reset link will be sent" in body["message"]
    assert body["dev_reset_url"].endswith("/reset-password?token=fake-reset-token")
    assert sent_messages == [
        {
            "to_email": "admin@test.com",
            "full_name": "Admin User",
            "raw_token": "fake-reset-token",
            "expires_in_minutes": 30,
        }
    ]


def test_forgot_password_uses_debug_origin_for_reset_link(
    api_client,
    monkeypatch,
):
    sent_messages = []

    def fake_email_guard():
        return None

    async def fake_create_password_reset_token(*args, **kwargs):
        return PasswordResetTokenResult(
            raw_token="fake-reset-token",
            email="admin@test.com",
            full_name="Admin User",
        )

    async def fake_send_password_reset_email(**kwargs):
        sent_messages.append(kwargs)

    monkeypatch.setattr(
        password_reset_endpoint,
        "require_email_delivery_for_production",
        fake_email_guard,
    )
    monkeypatch.setattr(
        password_reset_endpoint,
        "create_password_reset_token",
        fake_create_password_reset_token,
    )
    monkeypatch.setattr(
        password_reset_endpoint,
        "send_password_reset_email",
        fake_send_password_reset_email,
    )
    monkeypatch.setattr(
        password_reset_endpoint.settings,
        "DEBUG",
        True,
    )

    response = api_client.post(
        "/api/v1/auth/password/forgot",
        json=valid_forgot_password_payload(),
        headers={"Origin": "http://192.168.1.10:5173"},
    )

    assert response.status_code == 200
    assert response.json()["dev_reset_url"].startswith(
        "http://192.168.1.10:5173/reset-password"
    )
    assert sent_messages[0]["frontend_base_url"] == "http://192.168.1.10:5173"


def test_forgot_password_ignores_origin_in_production(
    api_client,
    monkeypatch,
):
    sent_messages = []

    def fake_email_guard():
        return None

    async def fake_create_password_reset_token(*args, **kwargs):
        return PasswordResetTokenResult(
            raw_token="fake-reset-token",
            email="admin@test.com",
            full_name="Admin User",
        )

    async def fake_send_password_reset_email(**kwargs):
        sent_messages.append(kwargs)

    monkeypatch.setattr(
        password_reset_endpoint,
        "require_email_delivery_for_production",
        fake_email_guard,
    )
    monkeypatch.setattr(
        password_reset_endpoint,
        "create_password_reset_token",
        fake_create_password_reset_token,
    )
    monkeypatch.setattr(
        password_reset_endpoint,
        "send_password_reset_email",
        fake_send_password_reset_email,
    )
    monkeypatch.setattr(
        password_reset_endpoint.settings,
        "DEBUG",
        False,
    )

    response = api_client.post(
        "/api/v1/auth/password/forgot",
        json=valid_forgot_password_payload(),
        headers={"Origin": "http://192.168.1.10:5173"},
    )

    assert response.status_code == 200
    assert "dev_reset_url" not in response.json()
    assert "frontend_base_url" not in sent_messages[0]


def test_forgot_password_blocks_when_email_delivery_guard_blocks(api_client, monkeypatch):
    def fake_email_guard():
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email delivery is not configured.",
        )

    async def fake_create_password_reset_token(*args, **kwargs):
        raise AssertionError("Reset token should not be created when email delivery is blocked.")

    monkeypatch.setattr(
        password_reset_endpoint,
        "require_email_delivery_for_production",
        fake_email_guard,
    )

    monkeypatch.setattr(
        password_reset_endpoint,
        "create_password_reset_token",
        fake_create_password_reset_token,
    )

    response = api_client.post(
        "/api/v1/auth/password/forgot",
        json=valid_forgot_password_payload(),
    )

    assert response.status_code == 503
    assert "Email delivery is not configured" in response.json()["message"]
