from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import CurrentAccount, get_current_account
from app.schemas.auth import CurrentUserResponse

router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    current: CurrentAccount = Depends(get_current_account),
) -> CurrentUserResponse:
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