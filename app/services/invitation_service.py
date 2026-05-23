from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, hash_token
from app.models.account_invitation import AccountInvitation
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import MFAMethod
from app.services.account_service import (
    Account,
    get_account_by_identifier,
    get_default_mfa_method,
)


async def get_invitation_by_token(
    db: AsyncSession,
    raw_token: str,
) -> AccountInvitation | None:
    token_hash = hash_token(raw_token)

    stmt = select(AccountInvitation).where(
        AccountInvitation.token_hash == token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def is_invitation_active(invitation: AccountInvitation) -> bool:
    now = datetime.now(timezone.utc)

    if invitation.accepted_at is not None:
        return False

    if invitation.revoked_at is not None:
        return False

    if invitation.expires_at <= now:
        return False

    return True


async def accept_invitation(
    db: AsyncSession,
    raw_token: str,
    username: str,
    password: str,
    preferred_mfa_method: MFAMethod | None = None,
) -> Account | None:
    invitation = await get_invitation_by_token(
        db=db,
        raw_token=raw_token,
    )

    if invitation is None:
        return None

    if not is_invitation_active(invitation):
        return None

    existing_email_account = await get_account_by_identifier(
        db=db,
        account_type=invitation.account_type,
        identifier=invitation.email,
    )

    if existing_email_account is not None:
        return None

    existing_username_account = await get_account_by_identifier(
        db=db,
        account_type=invitation.account_type,
        identifier=username,
    )

    if existing_username_account is not None:
        return None

    now = datetime.now(timezone.utc)

    if invitation.account_type == "admin":
        # Admin invitations require MFA setup after first login.
        # Do not mark Email MFA as preferred before the email method is verified/enabled.
        selected_mfa_method = get_default_mfa_method("admin")
    else:
        selected_mfa_method = (
            preferred_mfa_method
            if preferred_mfa_method in ("email", "authenticator")
            else get_default_mfa_method(invitation.account_type)
        )

    password_hash = hash_password(password)

    if invitation.account_type == "admin":
        account = Admin(
            isp_id=invitation.isp_id,
            full_name=invitation.full_name or invitation.email,
            email=invitation.email,
            username=username,
            password_hash=password_hash,
            role=invitation.admin_role or "isp_admin",
            status="active",
            created_by_admin_id=invitation.invited_by_admin_id,
            email_verified_at=now,
            password_changed_at=now,
            mfa_enabled=False,
            mfa_required=True,
            email_mfa_enabled=False,
            authenticator_mfa_enabled=False,
            preferred_mfa_method=selected_mfa_method,
        )
    else:
        if invitation.isp_id is None:
            return None

        account = AppUser(
            isp_id=invitation.isp_id,
            full_name=invitation.full_name or invitation.email,
            email=invitation.email,
            username=username,
            password_hash=password_hash,
            status="active",
            created_by_admin_id=invitation.invited_by_admin_id,
            email_verified_at=now,
            password_changed_at=now,
            mfa_enabled=False,
            mfa_required=False,
            email_mfa_enabled=False,
            authenticator_mfa_enabled=False,
            preferred_mfa_method=selected_mfa_method,
        )

    invitation.accepted_at = now

    db.add(account)
    await db.flush()

    return account
