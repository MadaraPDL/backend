from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings


HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
}


def _api_error_response(description: str) -> dict[str, Any]:
    return {
        "description": description,
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIErrorResponse",
                },
            },
        },
    }


def _api_validation_error_response() -> dict[str, Any]:
    return {
        "description": "Request validation failed",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIValidationErrorResponse",
                },
            },
        },
    }


def _add_error_schemas(openapi_schema: dict[str, Any]) -> None:
    schemas = openapi_schema.setdefault("components", {}).setdefault("schemas", {})

    schemas["APIErrorResponse"] = {
        "type": "object",
        "required": ["error", "message"],
        "properties": {
            "error": {
                "type": "string",
                "description": "Stable error code for frontend handling.",
                "examples": ["not_found"],
            },
            "message": {
                "type": "string",
                "description": "Human-readable error message.",
                "examples": ["Resource not found"],
            },
            "details": {
                "description": "Optional additional error details.",
            },
        },
    }

    schemas["APIValidationErrorResponse"] = {
        "type": "object",
        "required": ["error", "message", "details"],
        "properties": {
            "error": {
                "type": "string",
                "examples": ["validation_error"],
            },
            "message": {
                "type": "string",
                "examples": ["Request validation failed"],
            },
            "details": {
                "type": "array",
                "items": {
                    "type": "object",
                },
            },
        },
    }


def _is_protected_path(path: str) -> bool:
    api_prefix = settings.API_V1_PREFIX

    protected_prefixes = (
        f"{api_prefix}/me",
        f"{api_prefix}/isp-admin",
        f"{api_prefix}/platform-admin",
    )

    return path.startswith(protected_prefixes) or path == f"{api_prefix}/auth/me"


def _is_auth_rate_limited_path(path: str) -> bool:
    api_prefix = settings.API_V1_PREFIX

    return path in {
        f"{api_prefix}/auth/login",
        f"{api_prefix}/auth/email/verify",
        f"{api_prefix}/auth/mfa/verify",
        f"{api_prefix}/auth/mfa/setup/confirm",
        f"{api_prefix}/auth/password/forgot",
        f"{api_prefix}/auth/password/reset",
        f"{api_prefix}/auth/invitations/accept",
    }


def _standardize_error_responses(openapi_schema: dict[str, Any]) -> None:
    for path, path_item in openapi_schema.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue

        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue

            responses = operation.setdefault("responses", {})

            if "422" in responses:
                responses["422"] = _api_validation_error_response()

            if _is_auth_rate_limited_path(path):
                responses.setdefault("429", _api_error_response("Too many requests"))

            if _is_protected_path(path):
                responses.setdefault("401", _api_error_response("Unauthorized"))
                responses.setdefault("403", _api_error_response("Forbidden"))

            if "{" in path:
                responses.setdefault("404", _api_error_response("Resource not found"))

            responses.setdefault("500", _api_error_response("Internal server error"))


def configure_openapi(app: FastAPI) -> None:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.APP_NAME,
            version=settings.APP_VERSION,
            routes=app.routes,
        )

        _add_error_schemas(openapi_schema)
        _standardize_error_responses(openapi_schema)

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
