from __future__ import annotations

from pydantic import BaseModel


class ISPAdminIntelligenceRunItem(BaseModel):
    subscription_id: str
    status: str
    prediction_id: str | None = None
    recommendation_id: str | None = None
    alerts_created: int = 0
    message: str | None = None


class ISPAdminIntelligenceRunResponse(BaseModel):
    subscriptions_checked: int
    predictions_created: int
    recommendations_created: int
    alerts_created: int = 0
    skipped: int
    failed: int
    items: list[ISPAdminIntelligenceRunItem]
