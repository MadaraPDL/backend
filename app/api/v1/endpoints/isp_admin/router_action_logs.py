from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    RouterActionLogResponse,
    RouterActionLogStatus,
)
from app.services.isp_admin import (
    get_router_action_log_for_isp,
    list_router_action_logs_for_isp,
)


router = APIRouter(prefix="/router-action-logs")


@router.get(
    "",
    response_model=list[RouterActionLogResponse],
)
async def list_router_action_logs_endpoint(
    router_id: UUID | None = Query(default=None),
    policy_id: UUID | None = Query(default=None),
    status_filter: RouterActionLogStatus | None = Query(default=None, alias="status"),
    action_type: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[RouterActionLogResponse]:
    action_logs = await list_router_action_logs_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        router_id=router_id,
        policy_id=policy_id,
        status=status_filter,
        action_type=action_type,
        limit=limit,
        offset=offset,
    )

    return [
        RouterActionLogResponse.model_validate(action_log)
        for action_log in action_logs
    ]


@router.get(
    "/{action_log_id}",
    response_model=RouterActionLogResponse,
)
async def get_router_action_log_endpoint(
    action_log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> RouterActionLogResponse:
    action_log = await get_router_action_log_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        action_log_id=action_log_id,
    )

    if action_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Router action log not found",
        )

    return RouterActionLogResponse.model_validate(action_log)
