from fastapi import HTTPException

from app.api.dependencies.rate_limit import (
    check_rate_limit,
    reset_rate_limit_state,
)


class FakeClient:
    host = "127.0.0.1"


class FakeRequest:
    headers = {}
    client = FakeClient()


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
