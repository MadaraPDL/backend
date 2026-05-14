from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    SubscriptionPlanCreateRequest,
    SubscriptionPlanResponse,
    SubscriptionPlanUpdateRequest,
)
from app.services.isp_admin import (
    create_subscription_plan_for_isp,
    get_subscription_plan_by_name_for_isp,
    get_subscription_plan_for_isp,
    list_subscription_plans_for_isp,
    update_subscription_plan_for_isp,
)


router = APIRouter(prefix="/plans")


@router.post(
    "",
    response_model=SubscriptionPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription_plan_endpoint(
    request: SubscriptionPlanCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> SubscriptionPlanResponse:
    existing_plan = await get_subscription_plan_by_name_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        plan_name=request.plan_name,
    )

    if existing_plan is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A subscription plan with this name already exists for this ISP",
        )

    plan = await create_subscription_plan_for_isp(
        db=db,
        request=request,
        current_admin=current_admin,
    )

    await db.commit()

    return SubscriptionPlanResponse.model_validate(plan)


@router.get(
    "",
    response_model=list[SubscriptionPlanResponse],
)
async def list_subscription_plans_endpoint(
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[SubscriptionPlanResponse]:
    plans = await list_subscription_plans_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )

    return [
        SubscriptionPlanResponse.model_validate(plan)
        for plan in plans
    ]


@router.get(
    "/{plan_id}",
    response_model=SubscriptionPlanResponse,
)
async def get_subscription_plan_endpoint(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> SubscriptionPlanResponse:
    plan = await get_subscription_plan_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        plan_id=plan_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    return SubscriptionPlanResponse.model_validate(plan)


@router.patch(
    "/{plan_id}",
    response_model=SubscriptionPlanResponse,
)
async def update_subscription_plan_endpoint(
    plan_id: UUID,
    request: SubscriptionPlanUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> SubscriptionPlanResponse:
    plan = await get_subscription_plan_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        plan_id=plan_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found",
        )

    if request.plan_name is not None:
        existing_plan = await get_subscription_plan_by_name_for_isp(
            db=db,
            isp_id=current_admin.isp_id,
            plan_name=request.plan_name,
        )

        if existing_plan is not None and existing_plan.id != plan.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A subscription plan with this name already exists for this ISP",
            )

    updated_plan = await update_subscription_plan_for_isp(
        db=db,
        plan=plan,
        request=request,
    )

    await db.commit()

    return SubscriptionPlanResponse.model_validate(updated_plan)
