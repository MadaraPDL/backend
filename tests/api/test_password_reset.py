import app.api.v1.endpoints.auth.password_reset as password_reset_endpoint


def valid_forgot_password_payload():
    return {
        "account_type": "admin",
        "identifier": "admin@test.com",
    }


def test_forgot_password_returns_dev_token_in_debug(api_client, monkeypatch):
    def fake_email_guard():
        return None

    async def fake_create_password_reset_token(*args, **kwargs):
        return "fake-reset-token"

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
    assert body["dev_reset_token"] == "fake-reset-token"


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
    assert "Email delivery is not configured" in response.json()["detail"]
