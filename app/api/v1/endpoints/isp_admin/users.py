from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.isp_admin import (
    AppUserResponse,
    AppUserStatus,
    AppUserUpdateRequest,
)
from app.services.usage_summary_service import (
    build_latest_active_usage_summary_for_user,
    build_usage_summaries_for_user,
)
from app.services.isp_admin import (
    get_app_user_for_isp,
    list_app_users_for_isp,
    update_app_user_for_isp,
)


router = APIRouter(prefix="/users")



async def _build_app_user_response_with_usage(
    *,
    db: AsyncSession,
    app_user: AppUser,
    isp_id: UUID,
) -> AppUserResponse:
    usage_summary = await build_latest_active_usage_summary_for_user(
        db=db,
        user_id=app_user.id,
        isp_id=isp_id,
    )
    usage_summaries = await build_usage_summaries_for_user(
        db=db,
        user_id=app_user.id,
        isp_id=isp_id,
    )

    return AppUserResponse.model_validate(app_user).model_copy(
        update={
            "usage_summary": usage_summary,
            "usage_summaries": usage_summaries,
        }
    )


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

    return [
        await _build_app_user_response_with_usage(
            db=db,
            app_user=user,
            isp_id=current_admin.isp_id,
        )
        for user in users
    ]


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

    return await _build_app_user_response_with_usage(
        db=db,
        app_user=app_user,
        isp_id=current_admin.isp_id,
    )


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

    return await _build_app_user_response_with_usage(
        db=db,
        app_user=updated_user,
        isp_id=current_admin.isp_id,
    )
