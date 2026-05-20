from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.schemas.auth.common import AccountType, MFAMethod


class CurrentUserResponse(BaseModel):
    account_type: AccountType
    account_id: UUID
    full_name: str
    email: EmailStr
    username: str | None = None
    role: str | None = None
    status: str
    email_verified_at: datetime | None = None
    mfa_enabled: bool
    mfa_required: bool
    preferred_mfa_method: MFAMethod | None = None


class ProfileUpdateChallengeResponse(BaseModel):
    challenge_token: str
    method: MFAMethod
    expires_at: datetime
    message: str
    dev_email_code: str | None = None


class UpdateCurrentUserIdentityRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_.-]+$",
    )
    mfa_challenge_token: str = Field(..., min_length=20)
    mfa_code: str = Field(..., min_length=6, max_length=32)

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: str | None) -> str | None:
        if value is None:
            return None

        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def require_identity_change(self) -> "UpdateCurrentUserIdentityRequest":
        if self.email is None and self.username is None:
            raise ValueError("Email or username is required.")

        return self
