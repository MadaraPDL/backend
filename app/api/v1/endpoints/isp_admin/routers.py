from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    RouterCreateRequest,
    RouterResponse,
    RouterStatus,
    RouterUpdateRequest,
)
from app.services.isp_admin import (
    create_router_for_isp,
    get_router_for_isp,
    get_subscription_for_router_assignment,
    list_routers_for_isp,
    update_router_for_isp,
)


router = APIRouter(prefix="/routers")


@router.post(
    "",
    response_model=RouterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_router_endpoint(
    request: RouterCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> RouterResponse:
    subscription = await get_subscription_for_router_assignment(
        db=db,
        isp_id=current_admin.isp_id,
        user_subscription_id=request.user_subscription_id,
    )

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User subscription not found",
        )

    router = await create_router_for_isp(
        db=db,
        request=request,
        current_admin=current_admin,
    )

    await db.commit()

    return RouterResponse.model_validate(router)


@router.get(
    "",
    response_model=list[RouterResponse],
)
async def list_routers_endpoint(
    user_subscription_id: UUID | None = Query(default=None),
    status_filter: RouterStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[RouterResponse]:
    if user_subscription_id is not None:
        subscription = await get_subscription_for_router_assignment(
            db=db,
            isp_id=current_admin.isp_id,
            user_subscription_id=user_subscription_id,
        )

        if subscription is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User subscription not found",
            )

    routers = await list_routers_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        user_subscription_id=user_subscription_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [RouterResponse.model_validate(router) for router in routers]


@router.get(
    "/{router_id}",
    response_model=RouterResponse,
)
async def get_router_endpoint(
    router_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> RouterResponse:
    router = await get_router_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        router_id=router_id,
    )

    if router is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router not found",
        )

    return RouterResponse.model_validate(router)


@router.patch(
    "/{router_id}",
    response_model=RouterResponse,
)
async def update_router_endpoint(
    router_id: UUID,
    request: RouterUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> RouterResponse:
    router = await get_router_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        router_id=router_id,
    )

    if router is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router not found",
        )

    if request.user_subscription_id is not None:
        subscription = await get_subscription_for_router_assignment(
            db=db,
            isp_id=current_admin.isp_id,
            user_subscription_id=request.user_subscription_id,
        )

        if subscription is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User subscription not found",
            )

    updated_router = await update_router_for_isp(
        db=db,
        router=router,
        request=request,
    )

    await db.commit()

    return RouterResponse.model_validate(updated_router)
