from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    ISPAdminPlanChangeRequestResponse,
    ISPAdminPlanChangeRequestReviewRequest,
    PlanChangeRequestStatus,
)
from app.services.isp_admin import (
    get_app_user_for_isp,
    get_plan_change_request_for_isp,
    list_plan_change_requests_for_isp,
    review_plan_change_request_for_isp,
)


router = APIRouter(prefix="/plan-change-requests")


@router.get(
    "",
    response_model=list[ISPAdminPlanChangeRequestResponse],
)
async def list_plan_change_requests_endpoint(
    user_id: UUID | None = Query(default=None),
    status_filter: PlanChangeRequestStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminPlanChangeRequestResponse]:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    if user_id is not None:
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

    requests = await list_plan_change_requests_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        user_id=user_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [
        ISPAdminPlanChangeRequestResponse.model_validate(change_request)
        for change_request in requests
    ]


@router.get(
    "/{request_id}",
    response_model=ISPAdminPlanChangeRequestResponse,
)
async def get_plan_change_request_endpoint(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminPlanChangeRequestResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    change_request = await get_plan_change_request_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        request_id=request_id,
    )

    if change_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan change request not found",
        )

    return ISPAdminPlanChangeRequestResponse.model_validate(change_request)


@router.patch(
    "/{request_id}/review",
    response_model=ISPAdminPlanChangeRequestResponse,
)
async def review_plan_change_request_endpoint(
    request_id: UUID,
    request: ISPAdminPlanChangeRequestReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminPlanChangeRequestResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    change_request = await get_plan_change_request_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        request_id=request_id,
    )

    if change_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan change request not found",
        )

    if change_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending plan change requests can be reviewed",
        )

    reviewed_request = await review_plan_change_request_for_isp(
        db=db,
        change_request=change_request,
        current_admin=current_admin,
        request=request,
    )

    if reviewed_request is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan change request could not be reviewed",
        )

    await db.commit()

    return ISPAdminPlanChangeRequestResponse.model_validate(reviewed_request)
