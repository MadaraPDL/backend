from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PushTokenRegisterRequest(BaseModel):
    expo_push_token: str = Field(min_length=10, max_length=255)
    platform: str = Field(default="unknown", max_length=20)
    device_id: str | None = Field(default=None, max_length=128)
    permission_status: str = Field(default="granted", max_length=32)

    @field_validator("expo_push_token")
    @classmethod
    def validate_expo_push_token(cls, value: str) -> str:
        token = value.strip()

        if not (
            token.startswith("ExpoPushToken[")
            or token.startswith("ExponentPushToken[")
        ):
            raise ValueError("Invalid Expo push token format.")

        return token

    @field_validator("platform")
    @classmethod
    def normalize_platform(cls, value: str) -> str:
        platform = value.strip().lower() or "unknown"
        allowed_platforms = {"android", "ios", "web", "unknown"}

        if platform not in allowed_platforms:
            return "unknown"

        return platform

    @field_validator("permission_status")
    @classmethod
    def normalize_permission_status(cls, value: str) -> str:
        permission_status = value.strip().lower() or "unknown"
        allowed_statuses = {"granted", "denied", "undetermined", "unknown"}

        if permission_status not in allowed_statuses:
            return "unknown"

        return permission_status


class PushTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    expo_push_token: str
    platform: str
    device_id: str | None
    permission_status: str
    is_active: bool
    last_registered_at: datetime
    disabled_at: datetime | None
    created_at: datetime
    updated_at: datetime
