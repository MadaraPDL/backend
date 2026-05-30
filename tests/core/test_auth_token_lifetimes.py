from types import SimpleNamespace
from uuid import uuid4

from app.core.config import settings
from app.core.security import decode_access_token
from app.services.auth_service import build_auth_token_response


def _fake_account():
    return SimpleNamespace(
        id=uuid4(),
        full_name="PulseFi Test User",
        email="test@example.com",
        username="pulsefi_test",
        role="isp_admin",
    )


def _token_lifetime_seconds(token: str) -> int:
    payload = decode_access_token(token)

    return int(payload["exp"]) - int(payload["iat"])


def test_admin_access_token_uses_short_admin_session_window():
    response = build_auth_token_response(_fake_account(), "admin")

    assert response["account_type"] == "admin"
    assert _token_lifetime_seconds(response["access_token"]) == (
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def test_app_user_access_token_uses_long_mobile_session_window():
    response = build_auth_token_response(_fake_account(), "app_user")

    assert response["account_type"] == "app_user"
    assert _token_lifetime_seconds(response["access_token"]) == (
        settings.APP_USER_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    assert settings.APP_USER_ACCESS_TOKEN_EXPIRE_MINUTES >= 60 * 24 * 7
