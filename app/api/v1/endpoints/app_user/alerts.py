from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends,  HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import MyAlertResponse
from app.services.app_user import (
    get_my_alert,
    list_my_alerts,
    mark_my_alert_as_read,
)

router = APIRouter(prefix="/me/alerts", tags=["App User"])

@router.get("", response_model=list[MyAlertResponse])

async def list_my_alerts_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = Query(default=None),
    alert_type: str | None = Query(default=None),
    router_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyAlertResponse]:
    return await list_my_alerts(
        db=db,
        current_user=current_user,
        status=status_filter,
        severity=severity,
        alert_type=alert_type,
        router_id=router_id,
        limit=limit,
        offset=offset,
    )

@router.get("/{alert_id}", response_model=MyAlertResponse)
async def get_my_alert_endpoint(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyAlertResponse:
    alert = await get_my_alert(
        db=db, 
        current_user=current_user,
        alert_id=alert_id,
)
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Alert not found")
    return alert

@router.patch("/{alert_id}/read", response_model=MyAlertResponse)

async def mark_my_alert_as_read_endpoint(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyAlertResponse:
    alert = await mark_my_alert_as_read(
        db=db,
        current_user=current_user,
        alert_id=alert_id,
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    return alert
