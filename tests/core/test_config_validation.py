from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def build_settings(**overrides):
    values = {
        "APP_VERSION": "test",
        "DEBUG": True,
        "API_V1_PREFIX": "/api/v1",
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/pulsefi",
        "TEST_DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/pulsefi_test",
        "SECRET_KEY": "x" * 48,
        "ALGORITHM": "HS256",
        "BACKEND_CORS_ORIGINS": ["http://localhost:5173"],
    }
    values.update(overrides)

    return Settings(**values)


def test_debug_allows_email_delivery_disabled():
    settings = build_settings(DEBUG=True, EMAIL_DELIVERY_ENABLED=False)

    assert settings.DEBUG is True
    assert settings.EMAIL_DELIVERY_ENABLED is False


def test_email_delivery_rejects_tls_and_ssl_together():
    with pytest.raises(ValidationError, match="SMTP_USE_TLS and SMTP_USE_SSL"):
        build_settings(
            EMAIL_DELIVERY_ENABLED=True,
            SMTP_HOST="smtp.example.com",
            SMTP_FROM_EMAIL="noreply@example.com",
            SMTP_USE_TLS=True,
            SMTP_USE_SSL=True,
        )


def test_email_delivery_requires_frontend_admin_url():
    with pytest.raises(ValidationError, match="FRONTEND_ADMIN_URL"):
        build_settings(
            EMAIL_DELIVERY_ENABLED=True,
            SMTP_HOST="smtp.example.com",
            SMTP_FROM_EMAIL="noreply@example.com",
            FRONTEND_ADMIN_URL="",
        )


def test_production_requires_email_delivery_enabled():
    with pytest.raises(ValidationError, match="EMAIL_DELIVERY_ENABLED"):
        build_settings(
            DEBUG=False,
            EMAIL_DELIVERY_ENABLED=False,
            BACKEND_CORS_ORIGINS=["https://admin.pulsefi.example"],
            DATA_ENCRYPTION_KEY="encryption-key-placeholder",
            FRONTEND_ADMIN_URL="https://admin.pulsefi.example",
        )


def test_production_rejects_localhost_frontend_admin_url():
    with pytest.raises(ValidationError, match="FRONTEND_ADMIN_URL"):
        build_settings(
            DEBUG=False,
            EMAIL_DELIVERY_ENABLED=True,
            SMTP_HOST="smtp.example.com",
            SMTP_FROM_EMAIL="noreply@example.com",
            BACKEND_CORS_ORIGINS=["https://admin.pulsefi.example"],
            DATA_ENCRYPTION_KEY="encryption-key-placeholder",
            FRONTEND_ADMIN_URL="http://localhost:5173",
        )


def test_production_accepts_complete_email_settings():
    settings = build_settings(
        DEBUG=False,
        EMAIL_DELIVERY_ENABLED=True,
        SMTP_HOST="smtp.example.com",
        SMTP_FROM_EMAIL="noreply@example.com",
        BACKEND_CORS_ORIGINS=["https://admin.pulsefi.example"],
        DATA_ENCRYPTION_KEY="encryption-key-placeholder",
        FRONTEND_ADMIN_URL="https://admin.pulsefi.example",
    )

    assert settings.DEBUG is False
    assert settings.EMAIL_DELIVERY_ENABLED is True
    assert settings.FRONTEND_ADMIN_URL == "https://admin.pulsefi.example"
