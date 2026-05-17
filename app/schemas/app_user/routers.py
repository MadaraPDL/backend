from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MyRouterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_subscription_id: UUID | None
    router_name: str | None
    router_model: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class MyRouterCapabilitiesResponse(BaseModel):
    router_id: UUID
    adapter_name: str
    integration_mode: str
    is_simulator: bool
    can_read_total_usage: bool
    can_read_connected_devices: bool
    can_read_device_usage: bool
    can_apply_bandwidth_limit: bool
    can_apply_device_priority: bool
