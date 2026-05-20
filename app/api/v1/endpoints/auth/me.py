from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    CurrentAccount,
    get_current_account,
    rate_limit,
    require_email_delivery_for_production,
)
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    CurrentUserResponse,
    ProfileUpdateChallengeResponse,
    UpdateCurrentUserIdentityRequest,
)
from app.services.account_settings_service import (
    InvalidProfileUpdateChallengeError,
    ProfileUpdateConflictError,
    ProfileUpdateMFANotEnabledError,
    create_profile_update_challenge,
    get_profile_update_mfa_method,
    update_current_account_identity,
)
from app.services.email.email_service import send_profile_update_mfa_email

router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    current: CurrentAccount = Depends(get_current_account),
) -> CurrentUserResponse:
    return _build_current_user_response(current)


@router.post(
    "/me/profile-update-challenge",
    response_model=ProfileUpdateChallengeResponse,
    dependencies=[
        Depends(rate_limit("auth_profile_update_challenge", max_attempts=5, window_seconds=900))
    ],
)
async def create_profile_update_mfa_challenge(
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> ProfileUpdateChallengeResponse:
    try:
        method = get_profile_update_mfa_method(
            account=current.account,
            account_type=current.account_type,
        )
    except ProfileUpdateMFANotEnabledError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA must be enabled before changing login identity.",
        )

    if method == "email":
        require_email_delivery_for_production()

    challenge, raw_challenge_token, raw_email_code = await create_profile_update_challenge(
        db=db,
        account=current.account,
        account_type=current.account_type,
        method=method,
    )

    if method == "email" and raw_email_code is not None:
        await send_profile_update_mfa_email(
            to_email=current.account.email,
            full_name=current.account.full_name,
            code=raw_email_code,
            expires_in_minutes=10,
        )

    await db.commit()

    response = ProfileUpdateChallengeResponse(
        challenge_token=raw_challenge_token,
        method=method,
        expires_at=challenge.expires_at,
        message=(
            "Enter the code from your authenticator app."
            if method == "authenticator"
            else "Enter the verification code sent to your current email."
        ),
    )

    if settings.DEBUG and raw_email_code is not None:
        response.dev_email_code = raw_email_code

    return response


@router.patch(
    "/me/identity",
    response_model=CurrentUserResponse,
    dependencies=[
        Depends(rate_limit("auth_profile_update_confirm", max_attempts=5, window_seconds=900))
    ],
)
async def update_me_identity(
    request: UpdateCurrentUserIdentityRequest,
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> CurrentUserResponse:
    try:
        await update_current_account_identity(
            db=db,
            account=current.account,
            account_type=current.account_type,
            email=str(request.email) if request.email is not None else None,
            username=request.username,
            mfa_challenge_token=request.mfa_challenge_token,
            mfa_code=request.mfa_code,
        )
        await db.commit()
    except InvalidProfileUpdateChallengeError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA verification.",
        )
    except ProfileUpdateConflictError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username is already in use.",
        )

    return _build_current_user_response(current)


def _build_current_user_response(current: CurrentAccount) -> CurrentUserResponse:
    account = current.account

    return CurrentUserResponse(
        account_type=current.account_type,
        account_id=account.id,
        full_name=account.full_name,
        email=account.email,
        username=account.username,
        role=account.role if current.account_type == "admin" else None,
        status=account.status,
        email_verified_at=account.email_verified_at,
        mfa_enabled=account.mfa_enabled,
        mfa_required=account.mfa_required,
        preferred_mfa_method=account.preferred_mfa_method,
    )
