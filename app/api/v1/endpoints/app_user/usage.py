from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import (
    MyDeviceUsageResponse,
    MyUsageRecordResponse,
    MyUsageSummaryResponse,
)
from app.services.app_user import (
    get_my_device_usage,
    get_my_usage_summary,
    list_my_device_usage,
    list_my_usage_records,
)


router = APIRouter(prefix="/me/usage", tags=["App User"])


@router.get(
    "/summary",
    response_model=MyUsageSummaryResponse,
)
async def get_my_usage_summary_endpoint(
    user_subscription_id: UUID | None = Query(default=None),
    router_id: UUID | None = Query(default=None),
    device_id: UUID | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyUsageSummaryResponse:
    return await get_my_usage_summary(
        db=db,
        current_user=current_user,
        user_subscription_id=user_subscription_id,
        router_id=router_id,
        device_id=device_id,
        start_at=start_at,
        end_at=end_at,
    )


@router.get(
    "/devices",
    response_model=list[MyDeviceUsageResponse],
)
async def list_my_device_usage_endpoint(
    router_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyDeviceUsageResponse]:
    return await list_my_device_usage(
        db=db,
        current_user=current_user,
        router_id=router_id,
        status=status_filter,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/devices/{device_id}",
    response_model=MyDeviceUsageResponse,
)
async def get_my_device_usage_endpoint(
    device_id: UUID,
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyDeviceUsageResponse:
    device_usage = await get_my_device_usage(
        db=db,
        current_user=current_user,
        device_id=device_id,
        start_at=start_at,
        end_at=end_at,
    )

    if device_usage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device_usage


@router.get(
    "/records",
    response_model=list[MyUsageRecordResponse],
)
async def list_my_usage_records_endpoint(
    user_subscription_id: UUID | None = Query(default=None),
    router_id: UUID | None = Query(default=None),
    device_id: UUID | None = Query(default=None),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyUsageRecordResponse]:
    return await list_my_usage_records(
        db=db,
        current_user=current_user,
        user_subscription_id=user_subscription_id,
        router_id=router_id,
        device_id=device_id,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
        offset=offset,
    )
