from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.auth.common import MFAMethod


class MFARequiredResponse(BaseModel):
    mfa_required: bool = True
    challenge_token: str
    method: MFAMethod
    expires_at: datetime
    message: str = "MFA verification is required to complete login."

    # Development-only helper until real email sending is added.
    # Do not return this in production.
    dev_email_code: str | None = None


class MFAVerifyRequest(BaseModel):
    challenge_token: str = Field(..., min_length=20)
    code: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Email OTP, authenticator code, or backup code",
    )