from __future__ import annotations

from datetime import datetime
from decimal import Decimal 
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class MyRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_subscription_id: UUID
    current_plan_id: UUID | None
    recommendation_plan_id: UUID | None
    prediction_id: UUID | None
    recommendation_type: str
    recommendation_text: str
    reason: str | None
    explanation: str = "PulseFi generated this recommendation from available plan data."
    confidence_score: Decimal | None
    status: str
    created_at: datetime
