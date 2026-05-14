from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class MyUsageTotalsResponse(BaseModel):
    upload_mb: Decimal
    download_mb: Decimal
    total_mb: Decimal
    record_count: int
    first_record_start: datetime | None
    last_record_end: datetime | None


class MyUsageSummaryResponse(BaseModel):
    user_id: UUID
    totals: MyUsageTotalsResponse


class MyDeviceUsageResponse(BaseModel):
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
    usage: MyUsageTotalsResponse


class MyUsageRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_subscription_id: UUID
    router_id: UUID
    device_id: UUID | None
    upload_mb: Decimal
    download_mb: Decimal
    total_mb: Decimal
    record_start: datetime
    record_end: datetime
    source: str | None
    created_at: datetime
