from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_secure_token, hash_token
from app.models.account_invitation import AccountInvitation
from app.models.admin import Admin
from app.schemas.isp_admin import (
    AppUserInvitationCreateRequest,
    AppUserInvitationStatus,
)


async def get_pending_app_user_invitation(
    db: AsyncSession,
    email: str,
    isp_id: UUID,
) -> AccountInvitation | None:
    normalized_email = email.strip().lower()
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(AccountInvitation).where(
            func.lower(AccountInvitation.email) == normalized_email,
            AccountInvitation.account_type == "app_user",
            AccountInvitation.isp_id == isp_id,
            AccountInvitation.accepted_at.is_(None),
            AccountInvitation.revoked_at.is_(None),
            AccountInvitation.expires_at > now,
        )
    )

    return result.scalar_one_or_none()


async def get_app_user_invitation_by_id(
    db: AsyncSession,
    isp_id: UUID,
    invitation_id: UUID,
) -> AccountInvitation | None:
    result = await db.execute(
        select(AccountInvitation).where(
            AccountInvitation.id == invitation_id,
            AccountInvitation.isp_id == isp_id,
            AccountInvitation.account_type == "app_user",
        )
    )

    return result.scalar_one_or_none()


async def list_app_user_invitations(
    db: AsyncSession,
    isp_id: UUID,
    invitation_status: AppUserInvitationStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AccountInvitation]:
    now = datetime.now(timezone.utc)

    stmt = (
        select(AccountInvitation)
        .where(
            AccountInvitation.isp_id == isp_id,
            AccountInvitation.account_type == "app_user",
        )
        .order_by(AccountInvitation.created_at.desc())
    )

    if invitation_status == "pending":
        stmt = stmt.where(
            AccountInvitation.accepted_at.is_(None),
            AccountInvitation.revoked_at.is_(None),
            AccountInvitation.expires_at > now,
        )

    elif invitation_status == "accepted":
        stmt = stmt.where(AccountInvitation.accepted_at.is_not(None))

    elif invitation_status == "revoked":
        stmt = stmt.where(AccountInvitation.revoked_at.is_not(None))

    elif invitation_status == "expired":
        stmt = stmt.where(
            AccountInvitation.accepted_at.is_(None),
            AccountInvitation.revoked_at.is_(None),
            AccountInvitation.expires_at <= now,
        )

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_app_user_invitation(
    db: AsyncSession,
    request: AppUserInvitationCreateRequest,
    current_admin: Admin,
) -> tuple[AccountInvitation, str]:
    if current_admin.isp_id is None:
        raise ValueError("ISP Admin must belong to an ISP")

    raw_token = generate_secure_token()
    now = datetime.now(timezone.utc)

    invitation = AccountInvitation(
        email=str(request.email).strip().lower(),
        full_name=request.full_name.strip() if request.full_name else None,
        account_type="app_user",
        admin_role=None,
        isp_id=current_admin.isp_id,
        invited_by_admin_id=current_admin.id,
        token_hash=hash_token(raw_token),
        expires_at=now + timedelta(days=request.expires_in_days),
    )

    db.add(invitation)
    await db.flush()
    await db.refresh(invitation)

    return invitation, raw_token


def can_revoke_app_user_invitation(
    invitation: AccountInvitation,
) -> tuple[bool, str | None]:
    now = datetime.now(timezone.utc)

    if invitation.accepted_at is not None:
        return False, "Accepted invitations cannot be revoked"

    if invitation.revoked_at is not None:
        return False, "Invitation is already revoked"

    if invitation.expires_at <= now:
        return False, "Expired invitations cannot be revoked"

    return True, None


async def revoke_app_user_invitation(
    db: AsyncSession,
    invitation: AccountInvitation,
) -> AccountInvitation:
    invitation.revoked_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(invitation)

    return invitation
