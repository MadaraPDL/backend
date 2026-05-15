from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_isp_admin,
    require_email_delivery_for_production,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    AppUserInvitationCreateRequest,
    AppUserInvitationResponse,
    AppUserInvitationStatus,
    RevokeAppUserInvitationResponse,
)
from app.services.account_service import get_account_by_identifier
from app.services.isp_admin import (
    can_revoke_app_user_invitation,
    create_app_user_invitation,
    get_app_user_invitation_by_id,
    get_pending_app_user_invitation,
    list_app_user_invitations,
    revoke_app_user_invitation,
)


router = APIRouter(prefix="/user-invitations")


@router.post(
    "",
    response_model=AppUserInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_app_user_invitation_endpoint(
    request: AppUserInvitationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> AppUserInvitationResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account required",
        )

    existing_user = await get_account_by_identifier(
        db=db,
        account_type="app_user",
        identifier=str(request.email),
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An app user account with this email already exists",
        )

    pending_invitation = await get_pending_app_user_invitation(
        db=db,
        email=str(request.email),
        isp_id=current_admin.isp_id,
    )

    if pending_invitation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a pending invitation for this app user",
        )

    require_email_delivery_for_production()

    invitation, raw_token = await create_app_user_invitation(
        db=db,
        request=request,
        current_admin=current_admin,
    )

    await db.commit()

    response_data = AppUserInvitationResponse.model_validate(invitation).model_dump()

    # Development-only helper until real email sending is added.
    # Never return invitation tokens in production.
    if settings.DEBUG:
        response_data["dev_invitation_token"] = raw_token

    return AppUserInvitationResponse.model_validate(response_data)


@router.get(
    "",
    response_model=list[AppUserInvitationResponse],
)
async def list_app_user_invitations_endpoint(
    invitation_status: AppUserInvitationStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[AppUserInvitationResponse]:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account required",
        )

    invitations = await list_app_user_invitations(
        db=db,
        isp_id=current_admin.isp_id,
        invitation_status=invitation_status,
        limit=limit,
        offset=offset,
    )

    return [
        AppUserInvitationResponse.model_validate(invitation)
        for invitation in invitations
    ]


@router.patch(
    "/{invitation_id}/revoke",
    response_model=RevokeAppUserInvitationResponse,
)
async def revoke_app_user_invitation_endpoint(
    invitation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> RevokeAppUserInvitationResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account required",
        )

    invitation = await get_app_user_invitation_by_id(
        db=db,
        isp_id=current_admin.isp_id,
        invitation_id=invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App User invitation not found",
        )

    can_revoke, reason = can_revoke_app_user_invitation(invitation)

    if not can_revoke:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    revoked_invitation = await revoke_app_user_invitation(
        db=db,
        invitation=invitation,
    )

    await db.commit()

    return RevokeAppUserInvitationResponse(
        message="App User invitation revoked successfully",
        invitation=AppUserInvitationResponse.model_validate(revoked_invitation),
    )
