from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MyDevicePolicyCreate(BaseModel):
    device_id: UUID
    policy_type: str = Field(min_length=1, max_length=50)
    bandwidth_limit_mbps: Decimal | None = None
    priority_level: int | None = Field(default=None, ge=1, le=10)


class MyDevicePolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    router_id: UUID
    policy_type: str
    bandwidth_limit_mbps: Decimal | None
    priority_level: int | None
    status: str
    requested_at: datetime
    applied_at: datetime | None
    failure_reason: str | None
    is_active: bool
    updated_at: datetime