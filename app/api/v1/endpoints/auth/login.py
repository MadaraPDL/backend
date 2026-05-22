from __future__ import annotations

from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.api.dependencies import rate_limit
from app.db.session import get_db
from app.schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    MFARequiredResponse,
    MFASetupRequiredResponse,
)
from app.services.auth_service import (
    EmailDeliveryRequiredError,
    MFAMethodNotAvailableError,
    start_login,
)

router = APIRouter()

@router.post(
    "/login",
    response_model=Union[
        AuthTokenResponse,
        MFARequiredResponse,
        MFASetupRequiredResponse,
    ],
    dependencies=[
        Depends(
            rate_limit(
                "auth_login",
                max_attempts=5,
                window_seconds=900,
            )
        ),
    ],
)

async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
): 
    try:
        result = await start_login(
            db=db,
            account_type=request.account_type,
            identifier=request.identifier,
            password=request.password,
        )
    except EmailDeliveryRequiredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Email delivery is not configured. Configure email delivery before "
                "using email-based MFA in production."
            ),
        )
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    response_data, raw_email_code = result


    # Development-only helper until real email sending is added.
    # Never return OTP codes in production.
    if settings.DEBUG and raw_email_code is not None:
        response_data["dev_email_code"] = raw_email_code

    await db.commit()
    return response_data



