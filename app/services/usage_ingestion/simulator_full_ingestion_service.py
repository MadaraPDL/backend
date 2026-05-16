from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.usage_ingestion.simulator_device_service import (
    SimulatorDeviceIngestionResult,
    run_simulator_device_ingestion_for_router,
)
from app.services.usage_ingestion.simulator_usage_service import (
    SimulatorUsageIngestionResult,
    run_simulator_usage_ingestion_for_router,
)


@dataclass(frozen=True)
class SimulatorFullIngestionResult:
    device_ingestion: SimulatorDeviceIngestionResult
    usage_ingestion: SimulatorUsageIngestionResult


async def run_full_simulator_ingestion_for_router(
    db: AsyncSession,
    router_id: UUID,
    isp_id: UUID | None = None,
    record_start: datetime | None = None,
    record_end: datetime | None = None,
) -> SimulatorFullIngestionResult:
    device_result = await run_simulator_device_ingestion_for_router(
        db=db,
        router_id=router_id,
        isp_id=isp_id,
    )

    usage_result = await run_simulator_usage_ingestion_for_router(
        db=db,
        router_id=router_id,
        isp_id=isp_id,
        record_start=record_start,
        record_end=record_end,
    )

    return SimulatorFullIngestionResult(
        device_ingestion=device_result,
        usage_ingestion=usage_result,
    )
