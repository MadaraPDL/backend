from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.schemas.platform_admin import ISPAdminUpdateRequest


async def list_isp_admins(
    db: AsyncSession,
    isp_id: UUID,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Admin]:
    stmt = (
        select(Admin)
        .where(
            Admin.isp_id == isp_id,
            Admin.role == "isp_admin",
        )
        .order_by(Admin.created_at.desc())
    )

    if status is not None:
        stmt = stmt.where(Admin.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_isp_admin_by_id(
    db: AsyncSession,
    isp_id: UUID,
    admin_id: UUID,
) -> Admin | None:
    result = await db.execute(
        select(Admin).where(
            Admin.id == admin_id,
            Admin.isp_id == isp_id,
            Admin.role == "isp_admin",
        )
    )

    return result.scalar_one_or_none()


async def update_isp_admin(
    db: AsyncSession,
    admin: Admin,
    request: ISPAdminUpdateRequest,
) -> Admin:
    update_data = request.model_dump(exclude_unset=True)

    if "full_name" in update_data and update_data["full_name"] is not None:
        admin.full_name = update_data["full_name"].strip()

    if "phone_number" in update_data:
        admin.phone_number = update_data["phone_number"]

    if "status" in update_data and update_data["status"] is not None:
        admin.status = update_data["status"]

    await db.flush()
    await db.refresh(admin)

    return admin