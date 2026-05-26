from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class MyAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_subscription_id: UUID
    device_id: UUID | None
    connection_log_id: UUID | None
    usage_id: UUID | None
    prediction_id: UUID | None
    alert_type: str
    severity: str
    title: str
    message: str
    explanation: str = "PulseFi generated this alert from available account data."
    status: str
    read_at: datetime | None
    created_at: datetime
