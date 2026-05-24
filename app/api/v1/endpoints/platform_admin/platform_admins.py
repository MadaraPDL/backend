from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin_role
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.platform_admin import PlatformAdminResponse
from app.services.platform_admin import list_platform_admins

router = APIRouter(prefix="/platform-admins")


@router.get(
    "",
    response_model=list[PlatformAdminResponse],
)
async def list_platform_admins_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> list[PlatformAdminResponse]:
    admins = await list_platform_admins(
        db=db,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [PlatformAdminResponse.model_validate(admin) for admin in admins]
