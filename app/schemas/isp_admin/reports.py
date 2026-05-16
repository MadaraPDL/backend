from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


ISPAdminReportType = Literal[
    "usage_report",
    "device_report",
    "alert_report",
    "recommendation_report",
    "network_performance_report",
]


class ISPAdminReportCreateRequest(BaseModel):
    report_type: ISPAdminReportType = "usage_report"
    title: str | None = Field(default=None, max_length=200)
    period_start: date | None = None
    period_end: date | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "ISPAdminReportCreateRequest":
        if (
            self.period_start is not None
            and self.period_end is not None
            and self.period_end < self.period_start
        ):
            raise ValueError("period_end cannot be before period_start")

        return self


class ISPAdminReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    isp_id: UUID
    generated_by_admin_id: UUID | None
    report_type: str
    title: str
    period_start: date | None
    period_end: date | None
    report_data: dict[str, Any] | None
    file_url: str | None
    created_at: datetime
