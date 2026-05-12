from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth.common import AccountType, MFAMethod


class AcceptInvitationRequest(BaseModel):
    token: str = Field(..., min_length=20)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    preferred_mfa_method: MFAMethod | None = None


class AcceptInvitationResponse(BaseModel):
    message: str
    account_type: AccountType
    account_id: UUID
    email: EmailStr