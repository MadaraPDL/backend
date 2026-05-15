from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import rate_limit
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.auth import AcceptInvitationRequest, AcceptInvitationResponse, AccountType
from app.services.invitation_service import accept_invitation


router = APIRouter(prefix="/invitations")

@router.post(
    "/accept",
    response_model=AcceptInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)

async def accept_account_invitation(
    request: AcceptInvitationRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        account = await accept_invitation(
            db=db,
            raw_token=request.token,
            username=request.username,
            password=request.password,
            preferred_mfa_method=request.preferred_mfa_method,
        )

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists, please choose a different one.",
        )
    
    if account is None:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation token.",
        )
    
    account_type: AccountType = "admin" if isinstance(account, Admin) else "app_user"
    
    await db.commit()

    return {
        "message": "Invitation accepted successfully. You can now log in with your credentials.",
        "account_type": account_type,
        "account_id": account.id,
        "email": account.email,
    }