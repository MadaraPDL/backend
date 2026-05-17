from fastapi import HTTPException

import app.api.v1.endpoints.auth.login as login_endpoint


def valid_login_payload():
    return {
        "account_type": "admin",
        "identifier": "admin@test.com",
        "password": "password123",
    }


def test_login_endpoint_rate_limits_after_too_many_attempts(api_client, monkeypatch):
    async def fake_start_login(*args, **kwargs):
        return None

    monkeypatch.setattr(login_endpoint, "start_login", fake_start_login)

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
    assert "Too many attempts" in blocked_response.json()["message"]


