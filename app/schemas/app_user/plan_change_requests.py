from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MyPlanChangeRequestCreate(BaseModel):
    user_subscription_id: UUID
    requested_plan_id: UUID
    recommendation_id: UUID | None = None
    request_type: Literal["upgrade", "downgrade"]
    reason: str | None = Field(default=None, max_length=1000)


class MyRecommendationPlanChangeRequestCreate(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class MyPlanChangeRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_subscription_id: UUID
    current_plan_id: UUID
    requested_plan_id: UUID
    recommendation_id: UUID | None
    request_type: str
    reason: str | None
    status: str
    requested_at: datetime
    reviewed_by_admin_id: UUID | None
    reviewed_at: datetime | None
    admin_response: str | None
    updated_at: datetime
