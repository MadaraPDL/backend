from __future__ import annotations

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_app_user
from app.db.session import get_db
from app.models.app_user import AppUser
from app.schemas.app_user import MyRouterResponse
from app.services.app_user import (
    get_my_router,
    list_my_routers,
)


RouterStatusFilter = Literal[
    "active",
    "inactive",
    "maintenance",
]


router = APIRouter(prefix="/me/routers", tags=["App User"])


@router.get(
    "",
    response_model=list[MyRouterResponse],
)
async def list_my_routers_endpoint(
    status_filter: RouterStatusFilter | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> list[MyRouterResponse]:
    routers = await list_my_routers(
        db=db,
        current_user=current_user,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [MyRouterResponse.model_validate(router) for router in routers]


@router.get(
    "/{router_id}",
    response_model=MyRouterResponse,
)
async def get_my_router_endpoint(
    router_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: AppUser = Depends(get_current_app_user),
) -> MyRouterResponse:
    router = await get_my_router(
        db=db,
        current_user=current_user,
        router_id=router_id,
    )

    if router is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router not found",
        )

    return MyRouterResponse.model_validate(router)
