from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    require_admin_role,
    require_email_delivery_for_production,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.platform_admin import (
    PlatformAdminInvitationCreateRequest,
    PlatformAdminInvitationResponse,
    PlatformAdminInvitationStatus,
    RevokePlatformAdminInvitationResponse,
)
from app.services.account_service import get_account_by_identifier
from app.services.email import EmailDeliveryError, send_platform_admin_invitation_email
from app.services.email.email_service import resolve_debug_frontend_base_url
from app.services.platform_admin import (
    can_revoke_platform_admin_invitation,
    create_platform_admin_invitation,
    get_pending_platform_admin_invitation,
    get_platform_admin_invitation_by_id,
    list_platform_admin_invitations,
    revoke_platform_admin_invitation,
)

router = APIRouter(prefix="/platform-admin-invitations")


@router.post(
    "",
    response_model=PlatformAdminInvitationResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_platform_admin_invitation_endpoint(
    request: PlatformAdminInvitationCreateRequest,
    fastapi_request: Request,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> PlatformAdminInvitationResponse:
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

    pending_invitation = await get_pending_platform_admin_invitation(
        db=db,
        email=str(request.email),
    )

    if pending_invitation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a pending invitation for this Platform Admin",
        )

    require_email_delivery_for_production()

    invitation, raw_token = await create_platform_admin_invitation(
        db=db,
        request=request,
        platform_admin=platform_admin,
    )

    try:
        invitation_email_kwargs = {
            "to_email": invitation.email,
            "full_name": invitation.full_name,
            "raw_token": raw_token,
            "expires_in_days": request.expires_in_days,
        }

        invitation_origin = resolve_debug_frontend_base_url(
            fastapi_request.headers.get("origin"),
            debug=getattr(settings, "DEBUG", False),
        )

        if invitation_origin:
            invitation_email_kwargs["frontend_base_url"] = invitation_origin

        await send_platform_admin_invitation_email(**invitation_email_kwargs)
    except EmailDeliveryError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Invitation email delivery failed. Check email provider settings.",
        ) from exc

    await db.commit()

    response_data = PlatformAdminInvitationResponse.model_validate(
        invitation
    ).model_dump()

    if settings.DEBUG:
        response_data["dev_invitation_token"] = raw_token

    return PlatformAdminInvitationResponse.model_validate(response_data)


@router.get(
    "",
    response_model=list[PlatformAdminInvitationResponse],
    response_model_exclude_none=True,
)
async def list_platform_admin_invitations_endpoint(
    invitation_status: PlatformAdminInvitationStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> list[PlatformAdminInvitationResponse]:
    invitations = await list_platform_admin_invitations(
        db=db,
        invitation_status=invitation_status,
        limit=limit,
        offset=offset,
    )

    return [
        PlatformAdminInvitationResponse.model_validate(invitation)
        for invitation in invitations
    ]


@router.patch(
    "/{invitation_id}/revoke",
    response_model=RevokePlatformAdminInvitationResponse,
    response_model_exclude_none=True,
)
async def revoke_platform_admin_invitation_endpoint(
    invitation_id: UUID,
    db: AsyncSession = Depends(get_db),
    platform_admin: Admin = Depends(require_admin_role("platform_admin")),
) -> RevokePlatformAdminInvitationResponse:
    invitation = await get_platform_admin_invitation_by_id(
        db=db,
        invitation_id=invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform Admin invitation not found",
        )

    can_revoke, reason = can_revoke_platform_admin_invitation(invitation)

    if not can_revoke:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    revoked_invitation = await revoke_platform_admin_invitation(
        db=db,
        invitation=invitation,
    )

    await db.commit()

    return RevokePlatformAdminInvitationResponse(
        message="Platform Admin invitation revoked successfully",
        invitation=PlatformAdminInvitationResponse.model_validate(
            revoked_invitation
        ),
    )
