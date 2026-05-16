from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import ISPAdminDeviceConnectionLogResponse
from app.services.isp_admin import (
    get_device_connection_log_for_isp,
    list_device_connection_logs_for_isp,
)


router = APIRouter(prefix="/device-connection-logs")


@router.get(
    "",
    response_model=list[ISPAdminDeviceConnectionLogResponse],
)
async def list_device_connection_logs_endpoint(
    router_id: UUID | None = Query(default=None),
    device_id: UUID | None = Query(default=None),
    event_type: str | None = Query(default=None, min_length=1, max_length=50),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminDeviceConnectionLogResponse]:
    logs = await list_device_connection_logs_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        router_id=router_id,
        device_id=device_id,
        event_type=event_type,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
        offset=offset,
    )

    return [
        ISPAdminDeviceConnectionLogResponse.model_validate(log)
        for log in logs
    ]


@router.get(
    "/{connection_log_id}",
    response_model=ISPAdminDeviceConnectionLogResponse,
)
async def get_device_connection_log_endpoint(
    connection_log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminDeviceConnectionLogResponse:
    log = await get_device_connection_log_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        connection_log_id=connection_log_id,
    )

    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device connection log not found",
        )

    return ISPAdminDeviceConnectionLogResponse.model_validate(log)
