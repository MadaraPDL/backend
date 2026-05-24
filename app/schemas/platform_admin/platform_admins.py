from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class PlatformAdminResponse(BaseModel):
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
