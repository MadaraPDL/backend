from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


UserSubscriptionStatus = Literal[
    "pending",
    "active",
    "suspended",
    "expired",
    "cancelled",
]


class UserSubscriptionCreateRequest(BaseModel):
    user_id: UUID
    plan_id: UUID
    subscription_label: str | None = Field(default=None, max_length=120)
    start_date: date
    end_date: date | None = None
    status: UserSubscriptionStatus = "active"
    auto_renew: bool = False

    @model_validator(mode="after")
    def validate_dates(self) -> "UserSubscriptionCreateRequest":
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")

        return self


class UserSubscriptionUpdateRequest(BaseModel):
    plan_id: UUID | None = None
    subscription_label: str | None = Field(default=None, max_length=120)
    start_date: date | None = None
    end_date: date | None = None
    status: UserSubscriptionStatus | None = None
    auto_renew: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "UserSubscriptionUpdateRequest":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date cannot be before start_date")

        return self


class UserSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    plan_id: UUID
    subscription_label: str | None
    assigned_by_admin_id: UUID | None
    start_date: date
    end_date: date | None
    status: str
    auto_renew: bool
    created_at: datetime
    updated_at: datetime
