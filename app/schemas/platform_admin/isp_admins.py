from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


ISPAdminStatus = Literal["active", "inactive", "suspended"]


class ISPAdminUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone_number: str | None = Field(default=None, max_length=50)
    status: ISPAdminStatus | None = None


class ISPAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    isp_id: UUID | None
    full_name: str
    email: EmailStr
    username: str | None
    phone_number: str | None
    role: str
    status: str
    created_by_admin_id: UUID | None
    email_verified_at: datetime | None
    mfa_enabled: bool
    mfa_required: bool
    preferred_mfa_method: str | None
    created_at: datetime
    updated_at: datetime