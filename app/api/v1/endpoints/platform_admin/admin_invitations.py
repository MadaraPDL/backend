from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    require_admin_role,
    require_email_delivery_for_production,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.platform_admin import (
    ISPAdminInvitationCreateRequest,
    ISPAdminInvitationResponse,
    ISPAdminInvitationStatus,
    ISPAdminResponse,
    RevokeISPAdminInvitationResponse,
)
from app.services.account_service import get_account_by_identifier
from app.services.platform_admin import (
    can_revoke_invitation,
    create_isp_admin_invitation,
    get_isp_admin_invitation_by_id,
    get_isp_by_id,
    get_pending_isp_admin_invitation,
    list_isp_admin_invitations,
    list_isp_admins,
    revoke_isp_admin_invitation,
)

router = APIRouter(prefix="/isps/{isp_id}")


@router.post(
    "/admin-invitations",
    response_model=ISPAdminInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_isp_admin_invitation_endpoint(
    isp_id: UUID,
    request: ISPAdminInvitationCreateRequest,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> ISPAdminInvitationResponse:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )

    if isp.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot invite an ISP Admin for an inactive or suspended ISP",
        )

    existing_admin = await get_account_by_identifier(
        db=db,
        account_type="admin",
        identifier=str(request.email),
    )

    if existing_admin is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An admin account with this email already exists",
        )

    pending_invitation = await get_pending_isp_admin_invitation(
        db=db,
        email=str(request.email),
        isp_id=isp_id,
    )

    if pending_invitation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a pending invitation for this ISP Admin",
        )

    require_email_delivery_for_production()

    invitation, raw_token = await create_isp_admin_invitation(
        db=db,
        request=request,
        isp=isp,
        platform_admin=platform_admin,
    )

    await db.commit()

    response_data = ISPAdminInvitationResponse.model_validate(invitation).model_dump()

    # Development-only helper until real email sending is added.
    # Never return invitation tokens in production.
    if settings.DEBUG:
        response_data["dev_invitation_token"] = raw_token

    return ISPAdminInvitationResponse.model_validate(response_data)


@router.get(
    "/admin-invitations",
    response_model=list[ISPAdminInvitationResponse],
)
async def list_isp_admin_invitations_endpoint(
    isp_id: UUID,
    invitation_status: ISPAdminInvitationStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> list[ISPAdminInvitationResponse]:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )

    invitations = await list_isp_admin_invitations(
        db=db,
        isp_id=isp_id,
        invitation_status=invitation_status,
        limit=limit,
        offset=offset,
    )

    return [
        ISPAdminInvitationResponse.model_validate(invitation)
        for invitation in invitations
    ]


@router.patch(
    "/admin-invitations/{invitation_id}/revoke",
    response_model=RevokeISPAdminInvitationResponse,
)
async def revoke_isp_admin_invitation_endpoint(
    isp_id: UUID,
    invitation_id: UUID,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> RevokeISPAdminInvitationResponse:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )

    invitation = await get_isp_admin_invitation_by_id(
        db=db,
        isp_id=isp_id,
        invitation_id=invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP Admin invitation not found",
        )

    can_revoke, reason = can_revoke_invitation(invitation)

    if not can_revoke:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    revoked_invitation = await revoke_isp_admin_invitation(
        db=db,
        invitation=invitation,
    )

    await db.commit()

    return RevokeISPAdminInvitationResponse(
        message="ISP Admin invitation revoked successfully",
        invitation=ISPAdminInvitationResponse.model_validate(revoked_invitation),
    )


@router.get(
    "/admins",
    response_model=list[ISPAdminResponse],
)
async def list_isp_admins_endpoint(
    isp_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> list[ISPAdminResponse]:
    isp = await get_isp_by_id(
        db=db,
        isp_id=isp_id,
    )

    if isp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP not found",
        )

    admins = await list_isp_admins(
        db=db,
        isp_id=isp_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [ISPAdminResponse.model_validate(admin) for admin in admins]