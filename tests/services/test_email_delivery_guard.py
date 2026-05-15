from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import app.api.dependencies.email_delivery as email_delivery


def test_email_delivery_guard_allows_debug_mode(monkeypatch):
    monkeypatch.setattr(
        email_delivery,
        "settings",
        SimpleNamespace(DEBUG=True, EMAIL_DELIVERY_ENABLED=False),
    )

    assert email_delivery.require_email_delivery_for_production() is None


def test_email_delivery_guard_allows_production_when_email_enabled(monkeypatch):
    monkeypatch.setattr(
        email_delivery,
        "settings",
        SimpleNamespace(DEBUG=False, EMAIL_DELIVERY_ENABLED=True),
    )

    assert email_delivery.require_email_delivery_for_production() is None


def test_email_delivery_guard_blocks_production_without_email(monkeypatch):
    monkeypatch.setattr(
        email_delivery,
        "settings",
        SimpleNamespace(DEBUG=False, EMAIL_DELIVERY_ENABLED=False),
    )

    with pytest.raises(HTTPException) as exc_info:
        email_delivery.require_email_delivery_for_production()

    assert exc_info.value.status_code == 503
