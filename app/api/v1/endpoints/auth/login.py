from __future__ import annotations

from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import AuthTokenResponse, LoginRequest, MFARequiredResponse
from app.services.auth_service import start_login

router = APIRouter()

@router.post(
    "/login",
    response_model=Union[AuthTokenResponse, MFARequiredResponse],
)

async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
): 
    result = await start_login(
        db=db, 
        account_type=request.account_type,
        identifier=request.identifier,
        password=request.password,
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