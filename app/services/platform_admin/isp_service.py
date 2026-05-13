from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.isp import ISP
from app.schemas.platform_admin import ISPCreateRequest, ISPUpdateRequest


async def get_isp_by_id(
    db: AsyncSession,
    isp_id: UUID,
) -> ISP | None:
    result = await db.execute(
        select(ISP).where(ISP.id == isp_id)
    )
    return result.scalar_one_or_none()


async def get_isp_by_name(
    db: AsyncSession,
    name: str,
) -> ISP | None:
    normalized_name = name.strip().lower()

    result = await db.execute(
        select(ISP).where(func.lower(ISP.name) == normalized_name)
    )
    return result.scalar_one_or_none()


async def list_isps(
    db: AsyncSession,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ISP]:
    stmt = select(ISP).order_by(ISP.created_at.desc())

    if status is not None:
        stmt = stmt.where(ISP.status == status)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_isp(
    db: AsyncSession,
    request: ISPCreateRequest,
    platform_admin: Admin,
) -> ISP:
    isp = ISP(
        name=request.name.strip(),
        contact_email=str(request.contact_email) if request.contact_email else None,
        phone_number=request.phone_number,
        address=request.address,
        created_by_admin_id=platform_admin.id,
    )

    db.add(isp)
    await db.flush()
    await db.refresh(isp)

    return isp


async def update_isp(
    db: AsyncSession,
    isp: ISP,
    request: ISPUpdateRequest,
) -> ISP:
    update_data = request.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] is not None:
        isp.name = update_data["name"].strip()

    if "contact_email" in update_data:
        isp.contact_email = (
            str(update_data["contact_email"])
            if update_data["contact_email"] is not None
            else None
        )

    if "phone_number" in update_data:
        isp.phone_number = update_data["phone_number"]

    if "address" in update_data:
        isp.address = update_data["address"]

    if "status" in update_data and update_data["status"] is not None:
        isp.status = update_data["status"]

    await db.flush()
    await db.refresh(isp)

    return isp