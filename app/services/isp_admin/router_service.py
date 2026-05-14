from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.router import Router
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import RouterCreateRequest, RouterUpdateRequest


async def get_subscription_for_router_assignment(
    db: AsyncSession,
    isp_id: UUID,
    user_subscription_id: UUID,
) -> UserSubscription | None:
    result = await db.execute(
        select(UserSubscription)
        .join(AppUser, UserSubscription.user_id == AppUser.id)
        .where(
            UserSubscription.id == user_subscription_id,
            AppUser.isp_id == isp_id,
        )
    )

    return result.scalar_one_or_none()


async def create_router_for_isp(
    db: AsyncSession,
    request: RouterCreateRequest,
    current_admin: Admin,
) -> Router:
    router = Router(
        isp_id=current_admin.isp_id,
        user_subscription_id=request.user_subscription_id,
        assigned_by_admin_id=current_admin.id,
        router_name=request.router_name.strip() if request.router_name else None,
        router_model=request.router_model.strip() if request.router_model else None,
        router_ip=request.router_ip,
        mac_address=request.mac_address.strip() if request.mac_address else None,
        api_endpoint=request.api_endpoint.strip() if request.api_endpoint else None,
        username=request.username.strip() if request.username else None,
        status=request.status,
    )

    db.add(router)
    await db.flush()
    await db.refresh(router)

    return router


async def list_routers_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    user_subscription_id: UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Router]:
    stmt = (
        select(Router)
        .where(Router.isp_id == isp_id)
        .order_by(Router.created_at.desc())
    )

    if user_subscription_id is not None:
        stmt = stmt.where(Router.user_subscription_id == user_subscription_id)

    if status is not None:
        stmt = stmt.where(Router.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_router_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    router_id: UUID,
) -> Router | None:
    result = await db.execute(
        select(Router).where(
            Router.id == router_id,
            Router.isp_id == isp_id,
        )
    )

    return result.scalar_one_or_none()


async def update_router_for_isp(
    db: AsyncSession,
    router: Router,
    request: RouterUpdateRequest,
) -> Router:
    update_data = request.model_dump(exclude_unset=True)

    for field in ("router_name", "router_model", "mac_address", "api_endpoint", "username"):
        if field in update_data and update_data[field] is not None:
            update_data[field] = update_data[field].strip()

    for field, value in update_data.items():
        setattr(router, field, value)

    router.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(router)

    return router
