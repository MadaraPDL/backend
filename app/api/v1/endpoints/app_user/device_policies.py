from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import (
    MyDevicePolicyCreate,
    MyDevicePolicyExecutionResponse,
    MyDevicePolicyResponse,
)
from app.services.app_user import (
    create_my_device_policy,
    get_my_device_policy,
    list_my_device_policies,
)
from app.services.router_actions import execute_device_network_policy


router = APIRouter(prefix="/me/device-policies", tags=["App User"])


@router.post(
    "",
    response_model=MyDevicePolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_device_policy_endpoint(
    data: MyDevicePolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyDevicePolicyResponse:
    policy = await create_my_device_policy(
        db=db,
        current_user=current_user,
        data=data,
    )

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return policy


@router.get("", response_model=list[MyDevicePolicyResponse])
async def list_my_device_policies_endpoint(
    device_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyDevicePolicyResponse]:
    return await list_my_device_policies(
        db=db,
        current_user=current_user,
        device_id=device_id,
        status=status_filter,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@router.get("/{policy_id}", response_model=MyDevicePolicyResponse)
async def get_my_device_policy_endpoint(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyDevicePolicyResponse:
    policy = await get_my_device_policy(
        db=db,
        current_user=current_user,
        policy_id=policy_id,
    )

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device policy not found",
        )

    return policy


@router.patch(
    "/{policy_id}/execute",
    response_model=MyDevicePolicyExecutionResponse,
)
async def execute_my_device_policy_endpoint(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyDevicePolicyExecutionResponse:
    policy = await get_my_device_policy(
        db=db,
        current_user=current_user,
        policy_id=policy_id,
    )

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device policy not found",
        )

    if policy.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending device policies can be executed",
        )

    executed_policy, action_log = await execute_device_network_policy(
        db=db,
        policy_id=policy_id,
    )

    if executed_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device policy not found",
        )

    if action_log is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device policy was not executed",
        )

    return MyDevicePolicyExecutionResponse(
        policy=executed_policy,
        action_log=action_log,
        message="Device policy execution completed",
    )
