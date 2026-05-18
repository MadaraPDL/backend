from types import SimpleNamespace

import app.api.v1.endpoints.auth.rate_limits as rate_limits_endpoint
import app.api.v1.endpoints.auth.login as login_endpoint


def valid_login_payload():
    return {
        "account_type": "admin",
        "identifier": "admin@test.com",
        "password": "password123",
    }


def test_debug_rate_limit_reset_clears_login_bucket(api_client, monkeypatch):
    async def fake_start_login(*args, **kwargs):
        return None

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)
    monkeypatch.setattr(rate_limits_endpoint, "settings", SimpleNamespace(DEBUG=True))

    for _ in range(5):
        response = api_client.post(
            "/api/v1/auth/login",
            json=valid_login_payload(),
        )

        assert response.status_code == 401

    blocked_response = api_client.post(
        "/api/v1/auth/login",
        json=valid_login_payload(),
    )

    assert blocked_response.status_code == 429

    reset_response = api_client.post("/api/v1/auth/rate-limit/reset")

    assert reset_response.status_code == 200
    assert reset_response.json()["message"] == (
        "Local development auth rate limit state reset."
    )

    after_reset_response = api_client.post(
        "/api/v1/auth/login",
        json=valid_login_payload(),
    )

    assert after_reset_response.status_code == 401


def test_rate_limit_reset_is_not_available_when_debug_is_disabled(
    api_client,
    monkeypatch,
):
    monkeypatch.setattr(rate_limits_endpoint, "settings", SimpleNamespace(DEBUG=False))

    response = api_client.post("/api/v1/auth/rate-limit/reset")

    assert response.status_code == 404
