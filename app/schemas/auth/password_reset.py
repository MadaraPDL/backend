from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.auth.common import AccountType


class ForgotPasswordRequest(BaseModel):
    account_type: AccountType
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Email or username",
    )


class ForgotPasswordResponse(BaseModel):
    message: str = (
        "If an account exists for the provided identifier, "
        "a password reset link will be sent."
    )

    # Development-only helper until real email sending is added.
    # Do not return this in production.
    dev_reset_token: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8, max_length=128)


class ResetPasswordResponse(BaseModel):
    message: str = "Password has been reset successfully."