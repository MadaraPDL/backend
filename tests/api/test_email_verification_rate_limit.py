import app.api.v1.endpoints.auth.email_verification as email_verification_endpoint


def test_email_verification_endpoint_rate_limits_after_too_many_attempts(
    api_client,
    monkeypatch,
):
    async def fake_verify_email_with_token(*args, **kwargs):
        return None

    monkeypatch.setattr(
        email_verification_endpoint,
        "verify_email_with_token",
        fake_verify_email_with_token,
    )

    payload = {"token": "invalid-email-token-value"}

    for _ in range(5):
        response = api_client.post("/api/v1/auth/email/verify", json=payload)
        assert response.status_code == 400

    blocked_response = api_client.post("/api/v1/auth/email/verify", json=payload)

    assert blocked_response.status_code == 429
    body = blocked_response.json()
    assert body["error"] == "rate_limited"
    assert "Too many attempts" in body["message"]
