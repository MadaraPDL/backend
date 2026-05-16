from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class ISPAdminDeviceConnectionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    router_id: UUID
    event_type: str
    ip_address: IPvAnyAddress | None
    details: str | None
    event_time: datetime
