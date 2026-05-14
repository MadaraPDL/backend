from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MySubscriptionPlanSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_name: str
    monthly_price: Decimal
    data_limit_gb: Decimal
    speed_limit_mbps: Decimal | None
    description: str | None
    is_active: bool


class MySubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_id: UUID
    subscription_label: str | None
    start_date: date
    end_date: date | None
    status: str
    auto_renew: bool
    created_at: datetime
    updated_at: datetime
    plan: MySubscriptionPlanSummary
