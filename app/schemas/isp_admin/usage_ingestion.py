from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.core.simulator_scenarios import (
    DEFAULT_SIMULATOR_SCENARIO,
    SimulatorScenario,
)


class SimulatorUsageIngestionRequest(BaseModel):
    record_start: datetime | None = None
    record_end: datetime | None = None
    scenario: SimulatorScenario = DEFAULT_SIMULATOR_SCENARIO


class SimulatorUsageIngestionResponse(BaseModel):
    router_id: UUID
    user_id: UUID
    user_subscription_id: UUID
    record_start: datetime
    record_end: datetime
    records_created: int
    upload_mb: Decimal
    download_mb: Decimal
    total_mb: Decimal
    alerts_created: int = 0
    scenario: SimulatorScenario = DEFAULT_SIMULATOR_SCENARIO
    source: str = "simulator"


class SimulatorDeviceIngestionResponse(BaseModel):
    router_id: UUID
    user_id: UUID
    user_subscription_id: UUID
    devices_seen: int
    devices_created: int
    devices_updated: int
    connection_logs_created: int
    alerts_created: int = 0
    scenario: SimulatorScenario = DEFAULT_SIMULATOR_SCENARIO
    source: str = "simulator"


class SimulatorFullIngestionResponse(BaseModel):
    router_id: UUID
    user_id: UUID
    user_subscription_id: UUID
    device_ingestion: SimulatorDeviceIngestionResponse
    usage_ingestion: SimulatorUsageIngestionResponse
    alerts_created: int = 0
    scenario: SimulatorScenario = DEFAULT_SIMULATOR_SCENARIO
    policy_failure_alert_created: bool = False
    intelligence_alerts_created: int = 0
    predictions_created: int = 0
    recommendations_created: int = 0
    source: str = "simulator"
