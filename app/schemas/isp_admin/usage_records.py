from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict



class ISPAdminUsageTotalsResponse(BaseModel):
    upload_mb: Decimal
    download_mb: Decimal
    total_mb: Decimal
    record_count: int
    first_record_start: datetime | None
    last_record_end: datetime | None


class ISPAdminDailyUsageResponse(BaseModel):
    usage_date: date
    totals: ISPAdminUsageTotalsResponse


class ISPAdminDailyUsageByUserResponse(BaseModel):
    usage_date: date
    user_id: UUID
    user_full_name: str
    user_email: str
    user_subscription_id: UUID
    subscription_label: str | None
    router_id: UUID
    router_name: str | None
    usage_kind: str
    usage_note: str
    totals: ISPAdminUsageTotalsResponse


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
