from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class MyRouterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    isp_id: UUID
    user_subscription_id: UUID | None
    router_name: str | None
    router_model: str | None
    router_ip: IPvAnyAddress | None
    mac_address: str | None
    api_endpoint: str | None
    username: str | None
    status: str
    created_at: datetime
    updated_at: datetime
