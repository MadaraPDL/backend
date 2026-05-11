from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

AccountType =Literal["admin","app_user"]
MFAMethod = Literal["email","authenticator"]

class LoginRequest(BaseModel):
    account_type: AccountType
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Email or username"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str= "bearer"
    account_type: AccountType
    account_id: UUID
    full_name: str
    email: EmailStr
    role: str | None = None

class MFARequiredResponse(BaseModel):
    mfa_required: bool = True
    challenge_token: str
    method: MFAMethod
    expires_at: datetime
    message: str = "MFA verification is required to complete login."

class MFAVerifyRequest(BaseModel):
    challenge_token: str = Field(..., min_length=20)
    code: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Email OTP, authenticator code, or backup code",
    )

class AcceptInvitationRequest(BaseModel):
    token: str = Field(..., min_length=20)
    username: str = Field(...,min_length=3,max_length=50)
    password: str = Field(...,min_length=8,max_length=128)
    preferred_mfa_method: MFAMethod | None = None

class AcceptInvitationResponse(BaseModel):
    message: str
    account_type: AccountType
    account_id : UUID
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Email or username",
    )

class ForgotPasswordResponse(BaseModel):
    message: str =(
        "If an account exists for the provided identifier, "
        "a password reset link will be sent."
    )

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20)
    new_password: str = Field(...,min_length=8,max_length=128)

class ResetPasswordResponse(BaseModel):
    message: str = "Password has been reset successfully."

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
