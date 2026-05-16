from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ISPAdminAnalyticsSummaryResponse(BaseModel):
    isp_id: UUID
    generated_at: datetime
    period_start: datetime | None
    period_end: datetime | None

    total_users: int
    active_users: int

    total_subscriptions: int
    active_subscriptions: int

    total_routers: int
    active_routers: int

    pending_plan_change_requests: int
    approved_plan_change_requests: int
    rejected_plan_change_requests: int

    total_alerts: int
    unread_alerts: int
    critical_alerts: int

    total_recommendations: int
    new_recommendations: int
    accepted_recommendations: int

    total_usage_mb: Decimal
    total_usage_gb: Decimal
