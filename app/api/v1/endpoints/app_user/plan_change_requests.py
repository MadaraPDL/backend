from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import (
    MyPlanChangeRequestCreate,
    MyPlanChangeRequestResponse,
)
from app.services.app_user import (
    create_my_plan_change_request,
    get_my_plan_change_request,
    list_my_plan_change_requests,
)
from app.services.app_user.plan_change_request_service import (
    PlanChangeRequestValidationError,
)


router = APIRouter(prefix="/me/plan-change-requests", tags=["App User"])


@router.post(
    "",
    response_model=MyPlanChangeRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_plan_change_request_endpoint(
    data: MyPlanChangeRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyPlanChangeRequestResponse:
    try:
        change_request = await create_my_plan_change_request(
            db=db,
            current_user=current_user,
            data=data,
        )
    except PlanChangeRequestValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if change_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan change request could not be created",
        )

    return change_request


@router.get("", response_model=list[MyPlanChangeRequestResponse])
async def list_my_plan_change_requests_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyPlanChangeRequestResponse]:
    return await list_my_plan_change_requests(
        db=db,
        current_user=current_user,
        status=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get("/{request_id}", response_model=MyPlanChangeRequestResponse)
async def get_my_plan_change_request_endpoint(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyPlanChangeRequestResponse:
    change_request = await get_my_plan_change_request(
        db=db,
        current_user=current_user,
        request_id=request_id,
    )

    if change_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan change request not found",
        )

    return change_request
