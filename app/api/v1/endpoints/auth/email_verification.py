from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import rate_limit
from app.db.session import get_db
from app.schemas.auth import VerifyEmailRequest, VerifyEmailResponse
from app.services.email_verification_service import verify_email_with_token

router = APIRouter(prefix="/email")

@router.post(
    "/verify",
    response_model=VerifyEmailResponse,
    dependencies=[
        Depends(
            rate_limit(
                "auth_email_verify",
                max_attempts=5,
                window_seconds=900,
            )
        ),
    ],
)
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    account = await verify_email_with_token(
        db=db,
        raw_token=request.token,
    )

    if account is None:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired email verification token.",
        )

    await db.commit()

    return {
        "message": "Email verified successfully. You can now log in.",
    }
