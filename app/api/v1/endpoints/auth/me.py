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
    MFABackupCodesRegenerateRequest,
    MFABackupCodesRegenerateResponse,
    MFABackupCodeStatusResponse,
    MFASettingsActionRequest,
    MFASettingsChallengeRequest,
    MFASettingsChallengeResponse,
    MFAStatusResponse,
    PreferredMFAMethodRequest,
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
from app.services.mfa_settings_service import (
    CannotDisableLastMFAMethodError,
    InvalidMFASettingsChallengeError,
    MFAMethodNotActiveError,
    apply_verified_mfa_settings_action,
    build_mfa_status,
    disable_authenticator_mfa,
    disable_email_mfa,
    enable_email_mfa,
    set_preferred_mfa_method,
)
from app.services.account_service import is_authenticator_mfa_active
from app.services.mfa_service import create_mfa_challenge
from app.services.mfa_backup_code_service import (
    build_backup_code_status,
    regenerate_backup_codes,
)

router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    current: CurrentAccount = Depends(get_current_account),
) -> CurrentUserResponse:
    return _build_current_user_response(current)

@router.get("/me/mfa/status", response_model=MFAStatusResponse)
async def get_my_mfa_status(
    current: CurrentAccount = Depends(get_current_account),
) -> MFAStatusResponse:
    return MFAStatusResponse(
        **build_mfa_status(
            account=current.account,
            account_type=current.account_type,
        )
    )


@router.get(
    "/me/mfa/backup-codes/status",
    response_model=MFABackupCodeStatusResponse,
)
async def get_my_mfa_backup_code_status(
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFABackupCodeStatusResponse:
    return MFABackupCodeStatusResponse(
        **await build_backup_code_status(
            db=db,
            account=current.account,
            account_type=current.account_type,
        )
    )


@router.patch(
    "/me/mfa/backup-codes/regenerate",
    response_model=MFABackupCodesRegenerateResponse,
    dependencies=[
        Depends(rate_limit("auth_mfa_backup_codes_regenerate", max_attempts=5, window_seconds=900))
    ],
)
async def regenerate_my_mfa_backup_codes(
    request: MFABackupCodesRegenerateRequest,
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFABackupCodesRegenerateResponse:
    try:
        backup_codes = await regenerate_backup_codes(
            db=db,
            account=current.account,
            account_type=current.account_type,
            challenge_token=request.challenge_token,
            code=request.code,
        )
        await db.commit()
    except InvalidMFASettingsChallengeError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    return MFABackupCodesRegenerateResponse(
        account_type=current.account_type,
        backup_codes_available=True,
        available_backup_code_count=len(backup_codes),
        backup_codes=backup_codes,
    )


@router.post(
    "/me/mfa/settings-challenge",
    response_model=MFASettingsChallengeResponse,
    dependencies=[
        Depends(rate_limit("auth_mfa_settings_challenge", max_attempts=5, window_seconds=900))
    ],
)
async def create_my_mfa_settings_challenge(
    request: MFASettingsChallengeRequest,
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFASettingsChallengeResponse:
    if request.method == "email":
        require_email_delivery_for_production()

    if request.method == "authenticator" and not is_authenticator_mfa_active(
        current.account
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticator MFA is not active for this account.",
        )

    challenge, raw_challenge_token, raw_email_code = await create_mfa_challenge(
        db=db,
        account=current.account,
        account_type=current.account_type,
        method=request.method,
    )

    if request.method == "email" and raw_email_code is not None:
        await send_profile_update_mfa_email(
            to_email=current.account.email,
            full_name=current.account.full_name,
            code=raw_email_code,
            expires_in_minutes=10,
        )

    await db.commit()

    response = MFASettingsChallengeResponse(
        challenge_token=raw_challenge_token,
        method=request.method,
        expires_at=challenge.expires_at,
        message=(
            "Enter the code from your authenticator app to continue."
            if request.method == "authenticator"
            else "Enter the verification code sent to your email to continue."
        ),
    )

    if settings.DEBUG and raw_email_code is not None:
        response.dev_email_code = raw_email_code

    return response


@router.patch(
    "/me/mfa/settings-action",
    response_model=MFAStatusResponse,
    dependencies=[
        Depends(rate_limit("auth_mfa_settings_action", max_attempts=5, window_seconds=900))
    ],
)
async def apply_my_mfa_settings_action(
    request: MFASettingsActionRequest,
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    try:
        await apply_verified_mfa_settings_action(
            db=db,
            account=current.account,
            account_type=current.account_type,
            action=request.action,
            challenge_token=request.challenge_token,
            code=request.code,
        )
        await db.commit()
    except InvalidMFASettingsChallengeError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )
    except (CannotDisableLastMFAMethodError, MFAMethodNotActiveError) as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return MFAStatusResponse(
        **build_mfa_status(
            account=current.account,
            account_type=current.account_type,
        )
    )


@router.post("/me/mfa/email/enable", response_model=MFAStatusResponse)
async def enable_my_email_mfa(
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    require_email_delivery_for_production()

    enable_email_mfa(current.account)

    await db.commit()

    return MFAStatusResponse(
        **build_mfa_status(
            account=current.account,
            account_type=current.account_type,
        )
    )


@router.patch("/me/mfa/email/disable", response_model=MFAStatusResponse)
async def disable_my_email_mfa(
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    try:
        disable_email_mfa(current.account)
        await db.commit()
    except CannotDisableLastMFAMethodError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return MFAStatusResponse(
        **build_mfa_status(
            account=current.account,
            account_type=current.account_type,
        )
    )


@router.patch("/me/mfa/authenticator/disable", response_model=MFAStatusResponse)
async def disable_my_authenticator_mfa(
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    try:
        disable_authenticator_mfa(current.account)
        await db.commit()
    except CannotDisableLastMFAMethodError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return MFAStatusResponse(
        **build_mfa_status(
            account=current.account,
            account_type=current.account_type,
        )
    )


@router.patch("/me/mfa/preferred-method", response_model=MFAStatusResponse)
async def update_my_preferred_mfa_method(
    request: PreferredMFAMethodRequest,
    current: CurrentAccount = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    try:
        set_preferred_mfa_method(
            account=current.account,
            method=request.method,
        )
        await db.commit()
    except MFAMethodNotActiveError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return MFAStatusResponse(
        **build_mfa_status(
            account=current.account,
            account_type=current.account_type,
        )
    )


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
