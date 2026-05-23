from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_isp_admin,
    require_email_delivery_for_production,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin.admin_invitations import (
    ISPAdminInvitationCreateRequest,
    ISPAdminInvitationResponse,
    ISPAdminInvitationStatus,
    RevokeISPAdminInvitationResponse,
)
from app.services.account_service import get_account_by_identifier
from app.services.email import EmailDeliveryError, send_isp_admin_invitation_email
from app.services.email.email_service import resolve_debug_frontend_base_url
from app.services.isp_admin.admin_invitation_service import (
    can_revoke_isp_admin_invitation_for_isp,
    create_isp_admin_invitation_for_isp,
    get_isp_admin_invitation_for_isp,
    get_pending_isp_admin_invitation_for_isp,
    list_isp_admin_invitations_for_isp,
    revoke_isp_admin_invitation_for_isp,
)

router = APIRouter(prefix="/admin-invitations")


@router.post(
    "",
    response_model=ISPAdminInvitationResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_isp_admin_invitation_endpoint(
    request: ISPAdminInvitationCreateRequest,
    fastapi_request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminInvitationResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account required",
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

    pending_invitation = await get_pending_isp_admin_invitation_for_isp(
        db=db,
        email=str(request.email),
        isp_id=current_admin.isp_id,
    )

    if pending_invitation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a pending invitation for this ISP Admin",
        )

    require_email_delivery_for_production()

    invitation, raw_token = await create_isp_admin_invitation_for_isp(
        db=db,
        request=request,
        current_admin=current_admin,
    )

    try:
        invitation_email_kwargs = {
            "to_email": invitation.email,
            "full_name": invitation.full_name,
            "isp_name": "your ISP",
            "raw_token": raw_token,
            "expires_in_days": request.expires_in_days,
        }

        invitation_origin = resolve_debug_frontend_base_url(
            fastapi_request.headers.get("origin"),
            debug=getattr(settings, "DEBUG", False),
        )

        if invitation_origin:
            invitation_email_kwargs["frontend_base_url"] = invitation_origin

        await send_isp_admin_invitation_email(**invitation_email_kwargs)
    except EmailDeliveryError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Invitation email delivery failed. Check SMTP settings.",
        ) from exc

    await db.commit()

    response_data = ISPAdminInvitationResponse.model_validate(invitation).model_dump()

    if settings.DEBUG:
        response_data["dev_invitation_token"] = raw_token

    return ISPAdminInvitationResponse.model_validate(response_data)


@router.get(
    "",
    response_model=list[ISPAdminInvitationResponse],
    response_model_exclude_none=True,
)
async def list_isp_admin_invitations_endpoint(
    invitation_status: ISPAdminInvitationStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminInvitationResponse]:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account required",
        )

    invitations = await list_isp_admin_invitations_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        invitation_status=invitation_status,
        limit=limit,
        offset=offset,
    )

    return [
        ISPAdminInvitationResponse.model_validate(invitation)
        for invitation in invitations
    ]


@router.patch(
    "/{invitation_id}/revoke",
    response_model=RevokeISPAdminInvitationResponse,
    response_model_exclude_none=True,
)
async def revoke_isp_admin_invitation_endpoint(
    invitation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> RevokeISPAdminInvitationResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account required",
        )

    invitation = await get_isp_admin_invitation_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        invitation_id=invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISP Admin invitation not found",
        )

    can_revoke, reason = can_revoke_isp_admin_invitation_for_isp(invitation)

    if not can_revoke:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    revoked_invitation = await revoke_isp_admin_invitation_for_isp(
        db=db,
        invitation=invitation,
    )

    await db.commit()

    return RevokeISPAdminInvitationResponse(
        message="ISP Admin invitation revoked successfully",
        invitation=ISPAdminInvitationResponse.model_validate(revoked_invitation),
    )
