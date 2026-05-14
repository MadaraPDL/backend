from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class MyDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    router_id: UUID
    device_name: str | None
    mac_address: str
    ip_address: IPvAnyAddress | None
    device_type: str | None
    is_trusted: bool
    status: str
    first_seen: datetime
    last_seen: datetime | None
    updated_at: datetime
