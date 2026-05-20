from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.subscription_plan import SubscriptionPlan


async def list_my_available_plans(
    *,
    db: AsyncSession,
    current_user: AppUser,
) -> list[SubscriptionPlan]:
    result = await db.execute(
        select(SubscriptionPlan)
        .where(
            SubscriptionPlan.isp_id == current_user.isp_id,
            SubscriptionPlan.is_active.is_(True),
        )
        .order_by(SubscriptionPlan.monthly_price.asc(), SubscriptionPlan.plan_name.asc())
    )

    return list(result.scalars().all())
