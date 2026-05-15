from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.device import Device
from app.models.device_network_policy import DeviceNetworkPolicy
from app.schemas.app_user import MyDevicePolicyCreate


async def list_my_device_policies(
    *,
    db: AsyncSession,
    current_user: AppUser,
    device_id: UUID | None = None,
    status: str | None = None,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[DeviceNetworkPolicy]:
    stmt = (
        select(DeviceNetworkPolicy)
        .where(DeviceNetworkPolicy.requested_by_user_id == current_user.id)
        .order_by(DeviceNetworkPolicy.requested_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if device_id is not None:
        stmt = stmt.where(DeviceNetworkPolicy.device_id == device_id)

    if status is not None:
        stmt = stmt.where(DeviceNetworkPolicy.status == status)

    if is_active is not None:
        stmt = stmt.where(DeviceNetworkPolicy.is_active == is_active)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_my_device_policy(
    *,
    db: AsyncSession,
    current_user: AppUser,
    policy_id: UUID,
) -> DeviceNetworkPolicy | None:
    stmt = select(DeviceNetworkPolicy).where(
        DeviceNetworkPolicy.id == policy_id,
        DeviceNetworkPolicy.requested_by_user_id == current_user.id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_my_device_policy(
    *,
    db: AsyncSession,
    current_user: AppUser,
    data: MyDevicePolicyCreate,
) -> DeviceNetworkPolicy | None:
    device_stmt = select(Device).where(
        Device.id == data.device_id,
        Device.user_id == current_user.id,
    )
    device_result = await db.execute(device_stmt)
    device = device_result.scalar_one_or_none()

    if device is None:
        return None

    policy = DeviceNetworkPolicy(
        device_id=device.id,
        router_id=device.router_id,
        requested_by_user_id=current_user.id,
        policy_type=data.policy_type,
        bandwidth_limit_mbps=data.bandwidth_limit_mbps,
        priority_level=data.priority_level,
    )

    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    return policy