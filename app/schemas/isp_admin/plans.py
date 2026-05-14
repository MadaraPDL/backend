from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionPlanCreateRequest(BaseModel):
    plan_name: str = Field(..., min_length=2, max_length=120)
    monthly_price: Decimal = Field(..., ge=0)
    data_limit_gb: Decimal = Field(..., gt=0)
    speed_limit_mbps: Decimal | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True


class SubscriptionPlanUpdateRequest(BaseModel):
    plan_name: str | None = Field(default=None, min_length=2, max_length=120)
    monthly_price: Decimal | None = Field(default=None, ge=0)
    data_limit_gb: Decimal | None = Field(default=None, gt=0)
    speed_limit_mbps: Decimal | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None


class SubscriptionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    isp_id: UUID
    plan_name: str
    monthly_price: Decimal
    data_limit_gb: Decimal
    speed_limit_mbps: Decimal | None
    description: str | None
    is_active: bool
    created_by_admin_id: UUID | None
    created_at: datetime
    updated_at: datetime
