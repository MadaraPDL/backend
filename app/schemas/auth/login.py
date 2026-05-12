from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth.common import AccountType


class LoginRequest(BaseModel):
    account_type: AccountType
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Email or username",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    account_type: AccountType
    account_id: UUID
    full_name: str
    email: EmailStr
    role: str | None = None