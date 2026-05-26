from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class UsageConsumptionSummary(BaseModel):
    user_id: UUID
    subscription_id: UUID | None = None
    plan_id: UUID | None = None
    plan_name: str | None = None
    subscription_label: str | None = None
    subscription_status: str | None = None

    plan_limit_gb: Decimal | None = None
    today_usage_gb: Decimal
    monthly_usage_gb: Decimal
    current_cycle_usage_gb: Decimal
    total_usage_gb: Decimal
    remaining_gb: Decimal | None = None
    usage_percent: Decimal | None = None
    is_unlimited: bool = False

    cycle_start: date | None = None
    cycle_end: date | None = None
    last_record_end: datetime | None = None
