from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import require_email_delivery_for_production
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services.password_reset_service import (
    create_password_reset_token,
    reset_password_with_token,
)

router = APIRouter(prefix="/password")

@router.post("/forgot", response_model=ForgotPasswordResponse)

async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
): 
    require_email_delivery_for_production()

    raw_token = await create_password_reset_token(
        db=db,
        account_type=request.account_type,
        identifier=request.identifier,
    )

    if raw_token is not None:
        await db.commit()

    else:
        await db.rollback()

    response = {
        "message": (

        "if an account exists for the provided identifier," 
        "a password reset link will be sent to the associated email address."
        )
    }
    
    # Development-only helper until real email sending is added.
    # Never return reset tokens in production.
    if settings.DEBUG and raw_token is not None:
        response["dev_reset_token"] = raw_token

    return response


@router.post("/reset", response_model=ResetPasswordResponse)

async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    account = await reset_password_with_token(
        db=db,
        raw_token=request.token,
        new_password=request.new_password,
    )

    if account is None:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    
    await db.commit()

    return {
        "message": "Password has been reset successfully. You can now log in with your new password.",
    }
