from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_scheme import oauth2_scheme
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import AccountType


@dataclass(frozen=True)
class CurrentAccount:
    account_type: AccountType
    account: Admin | AppUser


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def jwt_numeric_date_to_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        token_datetime = value
    elif isinstance(value, (int, float)):
        token_datetime = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        raise ValueError("Invalid JWT issued-at value")

    if token_datetime.tzinfo is None:
        return token_datetime.replace(tzinfo=timezone.utc)

    return token_datetime.astimezone(timezone.utc)


async def get_current_account(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentAccount:
    try:
        payload = decode_access_token(token)

        subject = payload.get("sub")
        account_type = payload.get("account_type")

        if subject is None or account_type not in ("admin", "app_user"):
            raise credentials_exception()

        account_id = UUID(str(subject))
        issued_at = jwt_numeric_date_to_datetime(payload.get("iat"))

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception()

    model = Admin if account_type == "admin" else AppUser

    result = await db.execute(
        select(model).where(model.id == account_id)
    )
    account = result.scalar_one_or_none()

    if account is None:
        raise credentials_exception()

    if account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )

    if account.password_changed_at is not None:
        password_changed_at = account.password_changed_at

        if password_changed_at.tzinfo is None:
            password_changed_at = password_changed_at.replace(tzinfo=timezone.utc)
        else:
            password_changed_at = password_changed_at.astimezone(timezone.utc)

        if issued_at + timedelta(seconds=1) < password_changed_at:
            raise credentials_exception()

    return CurrentAccount(
        account_type=account_type,
        account=account,
    )
