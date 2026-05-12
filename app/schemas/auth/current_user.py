from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

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