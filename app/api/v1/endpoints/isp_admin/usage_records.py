from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import ISPAdminDailyUsageByUserResponse, ISPAdminDailyUsageResponse, ISPAdminUsageRecordResponse
from app.services.isp_admin import (
    get_usage_record_for_isp,
    list_daily_usage_by_user_for_isp,
    list_daily_usage_for_isp,
    list_usage_records_for_isp,
)


router = APIRouter(prefix="/usage-records")


@router.get(
    "",
    response_model=list[ISPAdminUsageRecordResponse],
)
async def list_usage_records_endpoint(
    router_id: UUID | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    user_subscription_id: UUID | None = Query(default=None),
    device_id: UUID | None = Query(default=None),
    source: str | None = Query(default=None, min_length=1, max_length=50),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminUsageRecordResponse]:
    records = await list_usage_records_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        router_id=router_id,
        user_id=user_id,
        user_subscription_id=user_subscription_id,
        device_id=device_id,
        source=source,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
        offset=offset,
    )

    return [ISPAdminUsageRecordResponse.model_validate(record) for record in records]


@router.get(
    "/daily-by-user",
    response_model=list[ISPAdminDailyUsageByUserResponse],
)
async def list_daily_usage_by_user_endpoint(
    router_id: UUID | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    user_subscription_id: UUID | None = Query(default=None),
    source: str | None = Query(default=None, min_length=1, max_length=50),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminDailyUsageByUserResponse]:
    return await list_daily_usage_by_user_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        router_id=router_id,
        user_id=user_id,
        user_subscription_id=user_subscription_id,
        source=source,
        start_at=start_at,
        end_at=end_at,
        days=days,
    )


@router.get(
    "/daily",
    response_model=list[ISPAdminDailyUsageResponse],
)
async def list_daily_usage_endpoint(
    router_id: UUID | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    user_subscription_id: UUID | None = Query(default=None),
    device_id: UUID | None = Query(default=None),
    source: str | None = Query(default=None, min_length=1, max_length=50),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminDailyUsageResponse]:
    return await list_daily_usage_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        router_id=router_id,
        user_id=user_id,
        user_subscription_id=user_subscription_id,
        device_id=device_id,
        source=source,
        start_at=start_at,
        end_at=end_at,
        days=days,
    )


@router.get(
    "/{usage_record_id}",
    response_model=ISPAdminUsageRecordResponse,
)
async def get_usage_record_endpoint(
    usage_record_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminUsageRecordResponse:
    record = await get_usage_record_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        usage_record_id=usage_record_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage record not found",
        )

    return ISPAdminUsageRecordResponse.model_validate(record)
