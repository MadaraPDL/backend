from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import MyDeviceResponse
from app.services.app_user import (
    get_my_device,
    list_my_devices,
)


router = APIRouter(prefix="/me/devices", tags=["App User"])


@router.get(
    "",
    response_model=list[MyDeviceResponse],
)
async def list_my_devices_endpoint(
    router_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyDeviceResponse]:
    devices = await list_my_devices(
        db=db,
        current_user=current_user,
        router_id=router_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [MyDeviceResponse.model_validate(device) for device in devices]


@router.get(
    "/{device_id}",
    response_model=MyDeviceResponse,
)
async def get_my_device_endpoint(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyDeviceResponse:
    device = await get_my_device(
        db=db,
        current_user=current_user,
        device_id=device_id,
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return MyDeviceResponse.model_validate(device)
