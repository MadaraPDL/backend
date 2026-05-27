from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.app_user import AppUser
from app.models.router import Router
from app.models.user_subscription import UserSubscription


async def list_my_alerts(
        *,
        db: AsyncSession,
        current_user: AppUser,
        status: str | None = None,
        severity: str | None = None,
        alert_type: str | None = None,
        router_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
) -> list[Alert]:
    stmt= (
        select(Alert)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if status is not None:
        stmt = stmt.where(Alert.status == status)


    if severity is not None:
        stmt = stmt.where(Alert.severity == severity)


    if alert_type is not None:
        stmt = stmt.where(Alert.alert_type == alert_type)

    if router_id is not None:
        router_result = await db.execute(
            select(Router.user_subscription_id)
            .join(
                UserSubscription,
                UserSubscription.id == Router.user_subscription_id,
            )
            .where(
                Router.id == router_id,
                UserSubscription.user_id == current_user.id,
            )
        )
        user_subscription_id = router_result.scalar_one_or_none()

        if user_subscription_id is None:
            return []

        stmt = stmt.where(Alert.user_subscription_id == user_subscription_id)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_my_alert(
        *,
        db: AsyncSession,
        current_user: AppUser,
        alert_id: UUID,
) -> Alert | None:
    stmt = select(Alert).where(
        Alert.id == alert_id,
        Alert.user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_my_alert_as_read(
        *,
        db : AsyncSession,
        current_user: AppUser,
        alert_id: UUID,
) -> Alert | None:
    alert = await get_my_alert(
        db=db,
        current_user=current_user,
        alert_id=alert_id,
    )

    if alert is None:
        return None
    
    if alert.status != "read":
        alert.status = "read"
        alert.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(alert)


    return alert