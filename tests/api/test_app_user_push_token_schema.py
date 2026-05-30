import pytest
from pydantic import ValidationError

from app.schemas.app_user.push_tokens import PushTokenRegisterRequest


def test_push_token_register_request_accepts_expo_tokens() -> None:
    payload = PushTokenRegisterRequest(
        expo_push_token="ExpoPushToken[demo-token-123]",
        platform="ANDROID",
        device_id="demo-device",
        permission_status="GRANTED",
    )

    assert payload.expo_push_token == "ExpoPushToken[demo-token-123]"
    assert payload.platform == "android"
    assert payload.permission_status == "granted"


def test_push_token_register_request_rejects_non_expo_tokens() -> None:
    with pytest.raises(ValidationError):
        PushTokenRegisterRequest(
            expo_push_token="not-a-valid-token",
            platform="android",
            permission_status="granted",
        )
