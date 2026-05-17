import json

import pytest
from fastapi import APIRouter, HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.core.api_errors import unhandled_exception_handler
from app.main import create_application


def test_http_exception_returns_standard_error_shape() -> None:
    app = create_application()
    router = APIRouter()

    @router.get("/test/not-found")
    async def not_found_route():
        raise HTTPException(status_code=404, detail="Test item not found")

    app.include_router(router)
    client = TestClient(app)

    response = client.get("/test/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": "not_found",
        "message": "Test item not found",
    }


def test_validation_error_returns_standard_error_shape() -> None:
    app = create_application()
    router = APIRouter()

    @router.get("/test/items/{item_id}")
    async def item_route(item_id: int):
        return {"item_id": item_id}

    app.include_router(router)
    client = TestClient(app)

    response = client.get("/test/items/not-an-int")
    body = response.json()

    assert response.status_code == 422
    assert body["error"] == "validation_error"
    assert body["message"] == "Request validation failed"
    assert "details" in body
    assert isinstance(body["details"], list)


@pytest.mark.asyncio
async def test_unhandled_exception_handler_hides_internal_details() -> None:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test/crash",
            "headers": [],
        }
    )

    response = await unhandled_exception_handler(
        request,
        RuntimeError("Sensitive internal crash detail"),
    )

    body = json.loads(response.body.decode())

    assert response.status_code == 500
    assert body == {
        "error": "server_error",
        "message": "Internal server error",
    }
