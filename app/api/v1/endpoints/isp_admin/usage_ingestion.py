from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    SimulatorDeviceIngestionResponse,
    SimulatorUsageIngestionRequest,
    SimulatorUsageIngestionResponse,
)
from app.services.usage_ingestion import (
    RouterNotFoundForIngestionError,
    RouterNotReadyForIngestionError,
    run_simulator_device_ingestion_for_router,
    run_simulator_usage_ingestion_for_router,
)


router = APIRouter(prefix="/usage-ingestion")


@router.post(
    "/routers/{router_id}/simulator",
    response_model=SimulatorUsageIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_simulator_usage_ingestion_endpoint(
    router_id: UUID,
    request: SimulatorUsageIngestionRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> SimulatorUsageIngestionResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    request_data = request or SimulatorUsageIngestionRequest()

    try:
        result = await run_simulator_usage_ingestion_for_router(
            db=db,
            router_id=router_id,
            isp_id=current_admin.isp_id,
            record_start=request_data.record_start,
            record_end=request_data.record_end,
        )
    except RouterNotFoundForIngestionError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router not found",
        ) from None
    except RouterNotReadyForIngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None

    await db.commit()

    return SimulatorUsageIngestionResponse(
        router_id=result.router_id,
        user_id=result.user_id,
        user_subscription_id=result.user_subscription_id,
        record_start=result.record_start,
        record_end=result.record_end,
        records_created=result.records_created,
        upload_mb=result.upload_mb,
        download_mb=result.download_mb,
        total_mb=result.total_mb,
    )


@router.post(
    "/routers/{router_id}/simulator/devices",
    response_model=SimulatorDeviceIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_simulator_device_ingestion_endpoint(
    router_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> SimulatorDeviceIngestionResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    try:
        result = await run_simulator_device_ingestion_for_router(
            db=db,
            router_id=router_id,
            isp_id=current_admin.isp_id,
        )
    except RouterNotFoundForIngestionError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router not found",
        ) from None
    except RouterNotReadyForIngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None

    await db.commit()

    return SimulatorDeviceIngestionResponse(
        router_id=result.router_id,
        user_id=result.user_id,
        user_subscription_id=result.user_subscription_id,
        devices_seen=result.devices_seen,
        devices_created=result.devices_created,
        devices_updated=result.devices_updated,
        connection_logs_created=result.connection_logs_created,
    )
