from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.router import Router
from app.models.router_action_log import RouterActionLog


async def list_router_action_logs_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    router_id: UUID | None = None,
    policy_id: UUID | None = None,
    status: str | None = None,
    action_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[RouterActionLog]:
    stmt = (
        select(RouterActionLog)
        .join(Router, RouterActionLog.router_id == Router.id)
        .where(Router.isp_id == isp_id)
        .order_by(RouterActionLog.executed_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if router_id is not None:
        stmt = stmt.where(RouterActionLog.router_id == router_id)

    if policy_id is not None:
        stmt = stmt.where(RouterActionLog.policy_id == policy_id)

    if status is not None:
        stmt = stmt.where(RouterActionLog.status == status)

    if action_type is not None:
        stmt = stmt.where(RouterActionLog.action_type == action_type)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_router_action_log_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    action_log_id: UUID,
) -> RouterActionLog | None:
    stmt = (
        select(RouterActionLog)
        .join(Router, RouterActionLog.router_id == Router.id)
        .where(
            RouterActionLog.id == action_log_id,
            Router.isp_id == isp_id,
        )
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
