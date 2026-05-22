from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import rate_limit
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    AuthTokenResponse,
    MFAChallengeMethodRequest,
    MFARequiredResponse,
    MFASetupConfirmRequest,
    MFAVerifyRequest,
)
from app.services.auth_service import (
    EmailDeliveryRequiredError,
    MFAMethodNotAvailableError,
    build_auth_token_response,
    complete_mfa_login,
    switch_mfa_challenge_method,
)
from app.services.mfa_setup_service import complete_mfa_setup

router = APIRouter(prefix="/mfa")


@router.patch(
    "/challenge-method",
    response_model=MFARequiredResponse,
    dependencies=[
        Depends(
            rate_limit(
                "auth_mfa_challenge_method",
                max_attempts=5,
                window_seconds=900,
            )
        )
    ],
)
async def change_mfa_challenge_method(
    request: MFAChallengeMethodRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await switch_mfa_challenge_method(
            db=db,
            challenge_token=request.challenge_token,
            method=request.method,
        )
    except EmailDeliveryRequiredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Email delivery is not configured. Configure email delivery before "
                "using email-based MFA in production."
            ),
        )
    except MFAMethodNotAvailableError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested MFA method is not active for this account.",
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA challenge.",
        )

    response_data, raw_email_code = result

    if settings.DEBUG and raw_email_code is not None:
        response_data["dev_email_code"] = raw_email_code

    await db.commit()
    return response_data


@router.post(
    "/verify",
    response_model=AuthTokenResponse,
    dependencies=[
        Depends(rate_limit("auth_mfa_verify", max_attempts=5, window_seconds=900))
    ],
)
async def verify_mfa(
    request: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    response_data = await complete_mfa_login(
        db=db,
        challenge_token=request.challenge_token,
        code=request.code,
    )

    if response_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA code.",
        )

    await db.commit()
    return response_data


@router.post(
    "/setup/confirm",
    response_model=AuthTokenResponse,
    dependencies=[
        Depends(
            rate_limit(
                "auth_mfa_setup_confirm",
                max_attempts=5,
                window_seconds=900,
            )
        )
    ],
)
async def confirm_mfa_setup(
    request: MFASetupConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    setup_result = await complete_mfa_setup(
        db=db,
        mfa_setup_token=request.mfa_setup_token,
        code=request.code,
    )

    if setup_result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired MFA setup token or code.",
        )

    account, account_type = setup_result

    response_data = build_auth_token_response(
        account=account,
        account_type=account_type,
    )

    await db.commit()
    return response_data
