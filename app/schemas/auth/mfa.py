from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.auth.common import AccountType, MFAMethod


class MFARequiredResponse(BaseModel):
    mfa_required: bool = True
    challenge_token: str
    method: MFAMethod
    active_methods: list[MFAMethod] = Field(default_factory=list)
    backup_codes_available: bool = False
    expires_at: datetime
    message: str = "MFA verification is required to complete login."

    # Development-only helper until real email sending is added.
    # Do not return this in production.
    dev_email_code: str | None = None


class MFASetupRequiredResponse(BaseModel):
    mfa_setup_required: bool = True
    message: str = "MFA setup is required before this account can complete login."
    account_type: AccountType
    account_id: UUID
    method: MFAMethod = "authenticator"
    mfa_setup_token: str
    authenticator_secret: str
    authenticator_uri: str


class MFAVerifyRequest(BaseModel):
    challenge_token: str = Field(..., min_length=20)
    code: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Email OTP, authenticator code, or backup code",
    )


class MFASetupConfirmRequest(BaseModel):
    mfa_setup_token: str = Field(..., min_length=20)
    code: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Authenticator app code from the newly configured MFA secret.",
    )

class MFAChallengeMethodRequest(BaseModel):
    challenge_token: str = Field(..., min_length=20)
    method: MFAMethod
