from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


PlanChangeRequestStatus = Literal[
    "pending",
    "approved",
    "rejected",
    "cancelled",
    "completed",
]

PlanChangeReviewDecision = Literal[
    "approve",
    "reject",
]


class ISPAdminPlanChangeRequestReviewRequest(BaseModel):
    decision: PlanChangeReviewDecision
    admin_response: str | None = Field(default=None, max_length=1000)


class ISPAdminPlanChangeRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
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
