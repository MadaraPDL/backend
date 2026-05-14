from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    AppUserResponse,
    AppUserStatus,
    AppUserUpdateRequest,
)
from app.services.isp_admin import (
    get_app_user_for_isp,
    list_app_users_for_isp,
    update_app_user_for_isp,
)


router = APIRouter(prefix="/users")


@router.get(
    "",
    response_model=list[AppUserResponse],
)
async def list_app_users_endpoint(
    status_filter: AppUserStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[AppUserResponse]:
    users = await list_app_users_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [AppUserResponse.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=AppUserResponse,
)
async def get_app_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> AppUserResponse:
    app_user = await get_app_user_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        user_id=user_id,
    )

    if app_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App User not found",
        )

    return AppUserResponse.model_validate(app_user)


@router.patch(
    "/{user_id}",
    response_model=AppUserResponse,
)
async def update_app_user_endpoint(
    user_id: UUID,
    request: AppUserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> AppUserResponse:
    app_user = await get_app_user_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        user_id=user_id,
    )

    if app_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App User not found",
        )

    updated_user = await update_app_user_for_isp(
        db=db,
        app_user=app_user,
        request=request,
    )

    await db.commit()

    return AppUserResponse.model_validate(updated_user)
