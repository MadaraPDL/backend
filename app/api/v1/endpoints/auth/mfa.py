from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import AuthTokenResponse, MFAVerifyRequest
from app.services.auth_service import complete_mfa_login

router = APIRouter(prefix="/mfa")

@router.post("/verify", response_model = AuthTokenResponse)
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
            detail="Invalid or Expired MFA code. ",
        )
    
    await db.commit()
    return response_data