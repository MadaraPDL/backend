from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status


def build_error_response(
    *,
    status_code: int,
    error: str,
    message: str,
    details: Any | None = None,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "error": error,
        "message": message,
    }

    if details is not None:
        response["details"] = details

    return response


def _error_code_for_status(status_code: int) -> str:
    if status_code == status.HTTP_400_BAD_REQUEST:
        return "bad_request"
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return "unauthorized"
    if status_code == status.HTTP_403_FORBIDDEN:
        return "forbidden"
    if status_code == status.HTTP_404_NOT_FOUND:
        return "not_found"
    if status_code == status.HTTP_409_CONFLICT:
        return "conflict"
    if status_code == 422:
        return "validation_error"
    if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return "rate_limited"
    if status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        return "service_unavailable"

    if 400 <= status_code < 500:
        return "client_error"

    return "server_error"


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"

    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(
            status_code=exc.status_code,
            error=_error_code_for_status(exc.status_code),
            message=message,
            details=exc.detail if not isinstance(exc.detail, str) else None,
        ),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=build_error_response(
            status_code=422,
            error="validation_error",
            message="Request validation failed",
            details=exc.errors(),
        ),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="server_error",
            message="Internal server error",
        ),
    )

