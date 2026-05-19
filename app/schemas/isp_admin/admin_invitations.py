from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


ISPAdminInvitationStatus = Literal[
    "pending",
    "accepted",
    "revoked",
    "expired",
]


class ISPAdminInvitationCreateRequest(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    expires_in_days: int = Field(default=7, ge=1, le=30)


class ISPAdminInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str | None
    account_type: str
    admin_role: str | None
    isp_id: UUID | None
    invited_by_admin_id: UUID | None
    expires_at: datetime
    accepted_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    dev_invitation_token: str | None = None


class RevokeISPAdminInvitationResponse(BaseModel):
    message: str
    invitation: ISPAdminInvitationResponse
