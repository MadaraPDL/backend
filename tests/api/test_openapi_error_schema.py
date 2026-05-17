from app.main import app


def test_openapi_uses_standard_validation_error_schema() -> None:
    schema = app.openapi()

    responses = schema["paths"]["/api/v1/auth/login"]["post"]["responses"]

    assert responses["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/APIValidationErrorResponse"
    }


def test_openapi_documents_auth_rate_limit_response() -> None:
    schema = app.openapi()

    responses = schema["paths"]["/api/v1/auth/login"]["post"]["responses"]

    assert responses["429"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/APIErrorResponse"
    }

    email_verify_responses = schema["paths"]["/api/v1/auth/email/verify"]["post"][
        "responses"
    ]

    assert email_verify_responses["429"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/APIErrorResponse"
    }


def test_openapi_documents_protected_endpoint_auth_errors() -> None:
    schema = app.openapi()

    responses = schema["paths"]["/api/v1/me/summary"]["get"]["responses"]

    assert responses["401"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/APIErrorResponse"
    }
    assert responses["403"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/APIErrorResponse"
    }


def test_openapi_includes_standard_error_components() -> None:
    schema = app.openapi()
    schemas = schema["components"]["schemas"]

    assert "APIErrorResponse" in schemas
    assert "APIValidationErrorResponse" in schemas
    assert schemas["APIErrorResponse"]["required"] == ["error", "message"]
    assert schemas["APIValidationErrorResponse"]["required"] == [
        "error",
        "message",
        "details",
    ]
