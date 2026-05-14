from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.subscription_plan import SubscriptionPlan
from app.schemas.isp_admin import (
    SubscriptionPlanCreateRequest,
    SubscriptionPlanUpdateRequest,
)


async def get_subscription_plan_by_name_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    plan_name: str,
) -> SubscriptionPlan | None:
    normalized_name = plan_name.strip().lower()

    result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.isp_id == isp_id,
            func.lower(SubscriptionPlan.plan_name) == normalized_name,
        )
    )

    return result.scalar_one_or_none()


async def list_subscription_plans_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[SubscriptionPlan]:
    stmt = (
        select(SubscriptionPlan)
        .where(SubscriptionPlan.isp_id == isp_id)
        .order_by(SubscriptionPlan.created_at.desc())
    )

    if is_active is not None:
        stmt = stmt.where(SubscriptionPlan.is_active == is_active)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_subscription_plan_for_isp(
    db: AsyncSession,
    isp_id: UUID,
    plan_id: UUID,
) -> SubscriptionPlan | None:
    result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.id == plan_id,
            SubscriptionPlan.isp_id == isp_id,
        )
    )

    return result.scalar_one_or_none()


async def create_subscription_plan_for_isp(
    db: AsyncSession,
    request: SubscriptionPlanCreateRequest,
    current_admin: Admin,
) -> SubscriptionPlan:
    plan = SubscriptionPlan(
        isp_id=current_admin.isp_id,
        plan_name=request.plan_name.strip(),
        monthly_price=request.monthly_price,
        data_limit_gb=request.data_limit_gb,
        speed_limit_mbps=request.speed_limit_mbps,
        description=request.description.strip() if request.description else None,
        is_active=request.is_active,
        created_by_admin_id=current_admin.id,
    )

    db.add(plan)
    await db.flush()
    await db.refresh(plan)

    return plan


async def update_subscription_plan_for_isp(
    db: AsyncSession,
    plan: SubscriptionPlan,
    request: SubscriptionPlanUpdateRequest,
) -> SubscriptionPlan:
    update_data = request.model_dump(exclude_unset=True)

    if "plan_name" in update_data and update_data["plan_name"] is not None:
        update_data["plan_name"] = update_data["plan_name"].strip()

    if "description" in update_data and update_data["description"] is not None:
        update_data["description"] = update_data["description"].strip()

    for field, value in update_data.items():
        setattr(plan, field, value)

    plan.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(plan)

    return plan
