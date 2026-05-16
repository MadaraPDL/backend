from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ISPAdminPredictionGenerateRequest(BaseModel):
    prediction_date: date | None = None


class ISPAdminPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_subscription_id: UUID
    plan_id: UUID | None
    prediction_date: date
    period_start: date
    period_end: date
    predicted_usage_gb: Decimal
    confidence_score: Decimal | None
    risk_level: str
    model_version: str | None
    created_at: datetime


class ISPAdminPredictionGenerationResponse(BaseModel):
    prediction: ISPAdminPredictionResponse
    days_elapsed: int
    total_cycle_days: int
    observed_usage_gb: Decimal
    average_daily_usage_gb: Decimal
