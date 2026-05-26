from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.usage_summary import UsageConsumptionSummary


class AppUserSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    isp_id: UUID
    full_name: str
    email: str
    username: str | None
    phone_number: str | None
    status: str
    email_verified_at: datetime | None
    created_at: datetime | None
    total_subscriptions: int
    active_subscriptions: int
    usage_summary: UsageConsumptionSummary | None = None
    usage_summaries: list[UsageConsumptionSummary] = Field(default_factory=list)
