from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ISPAdminUsageRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_subscription_id: UUID
    router_id: UUID
    device_id: UUID | None
    upload_mb: Decimal
    download_mb: Decimal
    total_mb: Decimal | None
    record_start: datetime
    record_end: datetime
    source: str | None
    created_at: datetime
