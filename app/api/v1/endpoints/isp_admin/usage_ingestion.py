from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    SimulatorDeviceIngestionResponse,
    SimulatorFullIngestionResponse,
    SimulatorUsageIngestionRequest,
    SimulatorUsageIngestionResponse,
)
from app.services.alerts import generate_alerts_after_router_ingestion
from app.services.isp_admin.intelligence_service import run_intelligence_for_isp
from app.services.usage_ingestion import (
    RouterNotFoundForIngestionError,
    RouterNotReadyForIngestionError,
    run_full_simulator_ingestion_for_router,
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
            scenario=request_data.scenario,
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

    alert_result = await generate_alerts_after_router_ingestion(
        db=db,
        router_id=router_id,
        latest_record_start=result.record_start,
        latest_record_end=result.record_end,
    )

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
        alerts_created=alert_result.usage_alerts_created + result.policy_alerts_created,
        blocked_devices=result.blocked_devices,
        policy_alerts_created=result.policy_alerts_created,
        scenario=request_data.scenario,
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

    device_event_start = datetime.now(timezone.utc)

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

    alert_result = await generate_alerts_after_router_ingestion(
        db=db,
        router_id=router_id,
        device_event_start=device_event_start,
        include_new_device_alerts=True,
    )

    await db.commit()

    return SimulatorDeviceIngestionResponse(
        router_id=result.router_id,
        user_id=result.user_id,
        user_subscription_id=result.user_subscription_id,
        devices_seen=result.devices_seen,
        devices_created=result.devices_created,
        devices_updated=result.devices_updated,
        connection_logs_created=result.connection_logs_created,
        alerts_created=alert_result.new_device_alerts_created,
    )


@router.post(
    "/routers/{router_id}/simulator/run",
    response_model=SimulatorFullIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_full_simulator_ingestion_endpoint(
    router_id: UUID,
    request: SimulatorUsageIngestionRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> SimulatorFullIngestionResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    request_data = request or SimulatorUsageIngestionRequest()
    device_event_start = datetime.now(timezone.utc)

    try:
        result = await run_full_simulator_ingestion_for_router(
            db=db,
            router_id=router_id,
            isp_id=current_admin.isp_id,
            record_start=request_data.record_start,
            record_end=request_data.record_end,
            scenario=request_data.scenario,
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

    device_result = result.device_ingestion
    usage_result = result.usage_ingestion

    alert_result = await generate_alerts_after_router_ingestion(
        db=db,
        router_id=router_id,
        latest_record_start=usage_result.record_start,
        latest_record_end=usage_result.record_end,
        device_event_start=device_event_start,
        include_new_device_alerts=True,
    )

    await db.flush()

    intelligence_result = await run_intelligence_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        include_alert_generation=False,
    )

    await db.commit()

    device_response = SimulatorDeviceIngestionResponse(
        router_id=device_result.router_id,
        user_id=device_result.user_id,
        user_subscription_id=device_result.user_subscription_id,
        devices_seen=device_result.devices_seen,
        devices_created=device_result.devices_created,
        devices_updated=device_result.devices_updated,
        connection_logs_created=device_result.connection_logs_created,
        alerts_created=alert_result.new_device_alerts_created,
        scenario=result.scenario,
    )

    usage_response = SimulatorUsageIngestionResponse(
        router_id=usage_result.router_id,
        user_id=usage_result.user_id,
        user_subscription_id=usage_result.user_subscription_id,
        record_start=usage_result.record_start,
        record_end=usage_result.record_end,
        records_created=usage_result.records_created,
        upload_mb=usage_result.upload_mb,
        download_mb=usage_result.download_mb,
        total_mb=usage_result.total_mb,
        alerts_created=alert_result.usage_alerts_created + usage_result.policy_alerts_created,
        blocked_devices=usage_result.blocked_devices,
        policy_alerts_created=usage_result.policy_alerts_created,
        scenario=result.scenario,
    )

    return SimulatorFullIngestionResponse(
        router_id=usage_result.router_id,
        user_id=usage_result.user_id,
        user_subscription_id=usage_result.user_subscription_id,
        device_ingestion=device_response,
        usage_ingestion=usage_response,
        alerts_created=(
            alert_result.alerts_created
            + int(result.policy_failure_alert_created)
            + usage_result.policy_alerts_created
        ),
        scenario=result.scenario,
        policy_failure_alert_created=result.policy_failure_alert_created,
        intelligence_alerts_created=intelligence_result.alerts_created,
        predictions_created=intelligence_result.predictions_created,
        recommendations_created=intelligence_result.recommendations_created,
    )
