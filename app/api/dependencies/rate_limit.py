from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status


_attempts: dict[tuple[str, str], deque[datetime]] = defaultdict(deque)


def get_client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client is None:
        return "unknown-client"

    return request.client.host


def check_rate_limit(
    request: Request,
    bucket: str,
    max_attempts: int,
    window_seconds: int,
) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=window_seconds)

    client_identifier = get_client_identifier(request)
    key = (bucket, client_identifier)

    attempts = _attempts[key]

    while attempts and attempts[0] <= window_start:
        attempts.popleft()

    if len(attempts) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please try again later.",
        )

    attempts.append(now)


def rate_limit(
    bucket: str,
    max_attempts: int,
    window_seconds: int,
) -> Callable[[Request], None]:
    def dependency(request: Request) -> None:
        check_rate_limit(
            request=request,
            bucket=bucket,
            max_attempts=max_attempts,
            window_seconds=window_seconds,
        )

    return dependency


def reset_rate_limit_state() -> None:
    _attempts.clear()
