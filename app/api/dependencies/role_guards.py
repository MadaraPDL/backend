from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status

from app.api.dependencies.current_account import CurrentAccount, get_current_account
from app.models.admin import Admin
from app.models.app_user import AppUser


async def get_current_admin(
    current: CurrentAccount = Depends(get_current_account),
) -> Admin:
    if current.account_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account required",
        )

    return current.account


async def get_current_app_user(
    current: CurrentAccount = Depends(get_current_account),
) -> AppUser:
    if current.account_type != "app_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="App user account required",
        )

    return current.account


def require_admin_role(*allowed_roles: str) -> Callable:
    async def dependency(
        admin: Admin = Depends(get_current_admin),
    ) -> Admin:
        if admin.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return admin

    return dependency