from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin_role
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.platform_admin import ISPAdminResponse, ISPAdminUpdateRequest
from app.services.platform_admin import (
    get_isp_admin_by_id,
    get_isp_by_id,
    update_isp_admin,
)

router = APIRouter(prefix="/isps/{isp_id}/admins")

@router.get(
    "/{admin_id}",
    response_model=ISPAdminResponse,
)

async def get_isp_admin_endpoint(
    isp_id: UUID,
    admin_id: UUID,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> ISPAdminResponse:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )
    
    admin = await get_isp_admin_by_id(
        db=db,
        isp_id=isp_id,
        admin_id=admin_id,
    )

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP Admin not found",
        )
    
    return ISPAdminResponse.model_validate(admin)

@router.patch(
    "/{admin_id}",
    response_model=ISPAdminResponse,
)

async def update_isp_admin_endpoint(
    isp_id: UUID,
    admin_id: UUID,
    request: ISPAdminUpdateRequest,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),

) -> ISPAdminResponse:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )
    
    admin = await get_isp_admin_by_id(
        db=db,
        isp_id=isp_id,
        admin_id=admin_id,  
    )

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP Admin not found",
        )
    
    updated_admin = await update_isp_admin(
        db=db,
        admin=admin,
        request=request,
    )

    await db.commit()

    return ISPAdminResponse.model_validate(updated_admin)
