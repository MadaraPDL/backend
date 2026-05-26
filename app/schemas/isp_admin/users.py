from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.usage_summary import UsageConsumptionSummary


AppUserStatus = Literal[
    "active",
    "inactive",
    "suspended",
]


class AppUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    isp_id: UUID
    full_name: str
    email: str
    username: str | None
    phone_number: str | None
    status: str
    created_by_admin_id: UUID | None
    created_at: datetime | None
    updated_at: datetime | None
    email_verified_at: datetime | None
    mfa_enabled: bool
    mfa_required: bool
    preferred_mfa_method: str | None
    usage_summary: UsageConsumptionSummary | None = None
    usage_summaries: list[UsageConsumptionSummary] = Field(default_factory=list)


class AppUserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone_number: str | None = Field(default=None, max_length=30)
    status: AppUserStatus | None = None
