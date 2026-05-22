from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies import rate_limit, require_email_delivery_for_production
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services.email.email_service import (
    build_password_reset_url,
    send_password_reset_email,
)
from app.services.password_reset_service import (
    create_password_reset_token,
    reset_password_with_token,
)

router = APIRouter(prefix="/password")


@router.post(
    "/forgot",
    response_model=ForgotPasswordResponse,
    dependencies=[
        Depends(rate_limit("auth_password_forgot", max_attempts=5, window_seconds=900))
    ],
)
async def forgot_password(
    request: ForgotPasswordRequest,
    fastapi_request: Request,
    db: AsyncSession = Depends(get_db),
):
    require_email_delivery_for_production()

    reset_result = await create_password_reset_token(
        db=db,
        account_type=request.account_type,
        identifier=request.identifier,
    )

    if reset_result is not None:
        reset_email_kwargs = {
            "to_email": reset_result.email,
            "full_name": reset_result.full_name,
            "raw_token": reset_result.raw_token,
            "expires_in_minutes": reset_result.expires_in_minutes,
        }

        reset_origin = fastapi_request.headers.get("origin")

        if reset_origin:
            reset_email_kwargs["frontend_base_url"] = reset_origin

        await send_password_reset_email(**reset_email_kwargs)
        await db.commit()

    else:
        await db.rollback()

    response: dict[str, str] = {
        "message": (
            "If an account exists for the provided identifier, "
            "a password reset link will be sent to the associated email address."
        )
    }

    # Development-only helper. Never return reset tokens or reset URLs in production.
    if settings.DEBUG and reset_result is not None:
        reset_url_kwargs = {"raw_token": reset_result.raw_token}
        reset_origin = fastapi_request.headers.get("origin")

        if reset_origin:
            reset_url_kwargs["frontend_base_url"] = reset_origin

        response["dev_reset_url"] = build_password_reset_url(**reset_url_kwargs)

    return response


@router.post(
    "/reset",
    response_model=ResetPasswordResponse,
    dependencies=[
        Depends(rate_limit("auth_password_reset", max_attempts=5, window_seconds=900))
    ],
)
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
