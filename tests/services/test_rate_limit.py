from importlib import import_module

from fastapi import HTTPException

from app.api.dependencies.rate_limit import (
    check_rate_limit,
    reset_rate_limit_state,
)

rate_limit_module = import_module("app.api.dependencies.rate_limit")


class FakeClient:
    def __init__(self, host="127.0.0.1"):
        self.host = host


class FakeRequest:
    def __init__(self, headers=None, client_host="127.0.0.1"):
        self.headers = headers or {}
        self.client = FakeClient(client_host)


def test_rate_limit_allows_attempts_under_limit():
    reset_rate_limit_state()

    request = FakeRequest()

    check_rate_limit(
        request=request,
        bucket="test",
        max_attempts=2,
        window_seconds=60,
    )

    check_rate_limit(
        request=request,
        bucket="test",
        max_attempts=2,
        window_seconds=60,
    )


def test_rate_limit_blocks_attempts_over_limit():
    reset_rate_limit_state()

    request = FakeRequest()

    check_rate_limit(
        request=request,
        bucket="test",
        max_attempts=1,
        window_seconds=60,
    )

    try:
        check_rate_limit(
            request=request,
            bucket="test",
            max_attempts=1,
            window_seconds=60,
        )
    except HTTPException as exc:
        assert exc.status_code == 429
        assert "Too many attempts" in exc.detail
    else:
        raise AssertionError("Expected rate limit to block the second request.")


def test_rate_limit_ignores_forwarded_for_from_untrusted_clients():
    reset_rate_limit_state()

    first_request = FakeRequest(
        headers={"x-forwarded-for": "198.51.100.10"},
        client_host="127.0.0.1",
    )
    spoofed_request = FakeRequest(
        headers={"x-forwarded-for": "198.51.100.11"},
        client_host="127.0.0.1",
    )

    check_rate_limit(
        request=first_request,
        bucket="test-untrusted-forwarded-for",
        max_attempts=1,
        window_seconds=60,
    )

    try:
        check_rate_limit(
            request=spoofed_request,
            bucket="test-untrusted-forwarded-for",
            max_attempts=1,
            window_seconds=60,
        )
    except HTTPException as exc:
        assert exc.status_code == 429
    else:
        raise AssertionError("Expected untrusted X-Forwarded-For to be ignored.")


def test_rate_limit_uses_forwarded_for_from_trusted_proxy(monkeypatch):
    reset_rate_limit_state()
    monkeypatch.setattr(rate_limit_module.settings, "TRUSTED_PROXY_IPS", ["127.0.0.1"])

    first_client = FakeRequest(
        headers={"x-forwarded-for": "198.51.100.10"},
        client_host="127.0.0.1",
    )
    second_client = FakeRequest(
        headers={"x-forwarded-for": "198.51.100.11"},
        client_host="127.0.0.1",
    )

    check_rate_limit(
        request=first_client,
        bucket="test-trusted-forwarded-for",
        max_attempts=1,
        window_seconds=60,
    )

    check_rate_limit(
        request=second_client,
        bucket="test-trusted-forwarded-for",
        max_attempts=1,
        window_seconds=60,
    )

    try:
        check_rate_limit(
            request=first_client,
            bucket="test-trusted-forwarded-for",
            max_attempts=1,
            window_seconds=60,
        )
    except HTTPException as exc:
        assert exc.status_code == 429
    else:
        raise AssertionError("Expected trusted forwarded client to be rate limited.")
