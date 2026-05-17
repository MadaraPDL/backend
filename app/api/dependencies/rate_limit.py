from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status

from app.core.config import settings


_attempts: dict[tuple[str, str], deque[datetime]] = defaultdict(deque)


def _get_direct_client_host(request: Request) -> str:
    if request.client is None:
        return "unknown-client"

    return request.client.host


def _is_trusted_proxy_host(client_host: str) -> bool:
    return client_host in settings.TRUSTED_PROXY_IPS


def get_client_identifier(request: Request) -> str:
    direct_client_host = _get_direct_client_host(request)
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for and _is_trusted_proxy_host(direct_client_host):
        forwarded_client = forwarded_for.split(",")[0].strip()

        if forwarded_client:
            return forwarded_client

    return direct_client_host


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
