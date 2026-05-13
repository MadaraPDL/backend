from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin_role
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.platform_admin import ISPCreateRequest, ISPResponse, ISPUpdateRequest
from app.services.platform_admin import (
    create_isp,
    get_isp_by_id,
    get_isp_by_name,
    list_isps,
    update_isp,
)

router = APIRouter(prefix="/isps")


@router.post(
    "",
    response_model=ISPResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_isp_endpoint(
    request: ISPCreateRequest,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> ISPResponse:
    existing_isp = await get_isp_by_name(
        db=db,
        name=request.name,
    )

    if existing_isp is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An ISP with this name already exists",
        )

    isp = await create_isp(
        db=db,
        request=request,
        platform_admin=platform_admin,
    )

    await db.commit()

    return ISPResponse.model_validate(isp)


@router.get(
    "",
    response_model=list[ISPResponse],
)
async def list_isps_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> list[ISPResponse]:
    isps = await list_isps(
        db=db,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [ISPResponse.model_validate(isp) for isp in isps]


@router.get(
    "/{isp_id}",
    response_model=ISPResponse,
)
async def get_isp_endpoint(
    isp_id: UUID,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> ISPResponse:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )

    return ISPResponse.model_validate(isp)


@router.patch(
    "/{isp_id}",
    response_model=ISPResponse,
)
async def update_isp_endpoint(
    isp_id: UUID,
    request: ISPUpdateRequest,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> ISPResponse:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )

    if request.name is not None:
        existing_isp = await get_isp_by_name(
            db=db,
            name=request.name,
        )

        if existing_isp is not None and existing_isp.id != isp.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An ISP with this name already exists",
            )

    updated_isp = await update_isp(
        db=db,
        isp=isp,
        request=request,
    )

    await db.commit()

    return ISPResponse.model_validate(updated_isp)