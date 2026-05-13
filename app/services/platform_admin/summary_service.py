from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.schemas.platform_admin import PlatformAdminSummaryResponse


async def count_rows(
    db: AsyncSession,
    model,
    *conditions,
) -> int:
    stmt = select(func.count()).select_from(model)

    for condition in conditions:
        stmt = stmt.where(condition)

    result = await db.execute(stmt)
    return int(result.scalar_one())


async def get_platform_admin_summary(
    db: AsyncSession,
) -> PlatformAdminSummaryResponse:
    total_isps = await count_rows(db, ISP)
    active_isps = await count_rows(db, ISP, ISP.status == "active")
    inactive_isps = await count_rows(db, ISP, ISP.status == "inactive")
    suspended_isps = await count_rows(db, ISP, ISP.status == "suspended")

    total_isp_admins = await count_rows(
        db,
        Admin,
        Admin.role == "isp_admin",
    )
    active_isp_admins = await count_rows(
        db,
        Admin,
        Admin.role == "isp_admin",
        Admin.status == "active",
    )
    inactive_isp_admins = await count_rows(
        db,
        Admin,
        Admin.role == "isp_admin",
        Admin.status == "inactive",
    )
    suspended_isp_admins = await count_rows(
        db,
        Admin,
        Admin.role == "isp_admin",
        Admin.status == "suspended",
    )

    total_app_users = await count_rows(db, AppUser)
    active_app_users = await count_rows(db, AppUser, AppUser.status == "active")
    inactive_app_users = await count_rows(db, AppUser, AppUser.status == "inactive")
    suspended_app_users = await count_rows(db, AppUser, AppUser.status == "suspended")

    return PlatformAdminSummaryResponse(
        total_isps=total_isps,
        active_isps=active_isps,
        inactive_isps=inactive_isps,
        suspended_isps=suspended_isps,
        total_isp_admins=total_isp_admins,
        active_isp_admins=active_isp_admins,
        inactive_isp_admins=inactive_isp_admins,
        suspended_isp_admins=suspended_isp_admins,
        total_app_users=total_app_users,
        active_app_users=active_app_users,
        inactive_app_users=inactive_app_users,
        suspended_app_users=suspended_app_users,
    )
