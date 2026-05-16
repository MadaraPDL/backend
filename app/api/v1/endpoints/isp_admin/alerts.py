from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import ISPAdminAlertResponse
from app.services.isp_admin import (
    get_alert_for_isp,
    list_alerts_for_isp,
)


router = APIRouter(prefix="/alerts")


@router.get(
    "",
    response_model=list[ISPAdminAlertResponse],
)
async def list_alerts_endpoint(
    user_id: UUID | None = Query(default=None),
    user_subscription_id: UUID | None = Query(default=None),
    device_id: UUID | None = Query(default=None),
    alert_type: str | None = Query(default=None, min_length=1, max_length=50),
    severity: str | None = Query(default=None, min_length=1, max_length=50),
    status_filter: str | None = Query(default=None, alias="status", min_length=1, max_length=50),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminAlertResponse]:
    alerts = await list_alerts_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        user_id=user_id,
        user_subscription_id=user_subscription_id,
        device_id=device_id,
        alert_type=alert_type,
        severity=severity,
        status=status_filter,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
        offset=offset,
    )

    return [
        ISPAdminAlertResponse.model_validate(alert)
        for alert in alerts
    ]


@router.get(
    "/{alert_id}",
    response_model=ISPAdminAlertResponse,
)
async def get_alert_endpoint(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminAlertResponse:
    alert = await get_alert_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        alert_id=alert_id,
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return ISPAdminAlertResponse.model_validate(alert)
