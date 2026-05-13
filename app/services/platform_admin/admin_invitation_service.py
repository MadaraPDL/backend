from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_secure_token, hash_token
from app.models.account_invitation import AccountInvitation
from app.models.admin import Admin
from app.models.isp import ISP
from app.schemas.platform_admin import (
    ISPAdminInvitationCreateRequest,
    ISPAdminInvitationStatus,
)


async def get_pending_isp_admin_invitation(
    db: AsyncSession,
    email: str,
    isp_id: UUID,
) -> AccountInvitation | None:
    normalized_email = email.strip().lower()
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(AccountInvitation).where(
            func.lower(AccountInvitation.email) == normalized_email,
            AccountInvitation.account_type == "admin",
            AccountInvitation.admin_role == "isp_admin",
            AccountInvitation.isp_id == isp_id,
            AccountInvitation.accepted_at.is_(None),
            AccountInvitation.revoked_at.is_(None),
            AccountInvitation.expires_at > now,
        )
    )

    return result.scalar_one_or_none()


async def get_isp_admin_invitation_by_id(
    db: AsyncSession,
    isp_id: UUID,
    invitation_id: UUID,
) -> AccountInvitation | None:
    result = await db.execute(
        select(AccountInvitation).where(
            AccountInvitation.id == invitation_id,
            AccountInvitation.isp_id == isp_id,
            AccountInvitation.account_type == "admin",
            AccountInvitation.admin_role == "isp_admin",
        )
    )

    return result.scalar_one_or_none()


async def list_isp_admin_invitations(
    db: AsyncSession,
    isp_id: UUID,
    invitation_status: ISPAdminInvitationStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AccountInvitation]:
    now = datetime.now(timezone.utc)

    stmt = (
        select(AccountInvitation)
        .where(
            AccountInvitation.isp_id == isp_id,
            AccountInvitation.account_type == "admin",
            AccountInvitation.admin_role == "isp_admin",
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


async def create_isp_admin_invitation(
    db: AsyncSession,
    request: ISPAdminInvitationCreateRequest,
    isp: ISP,
    platform_admin: Admin,
) -> tuple[AccountInvitation, str]:
    raw_token = generate_secure_token()
    now = datetime.now(timezone.utc)

    invitation = AccountInvitation(
        email=str(request.email).strip().lower(),
        full_name=request.full_name.strip() if request.full_name else None,
        account_type="admin",
        admin_role="isp_admin",
        isp_id=isp.id,
        invited_by_admin_id=platform_admin.id,
        token_hash=hash_token(raw_token),
        expires_at=now + timedelta(days=request.expires_in_days),
    )

    db.add(invitation)
    await db.flush()
    await db.refresh(invitation)

    return invitation, raw_token


def can_revoke_invitation(invitation: AccountInvitation) -> tuple[bool, str | None]:
    now = datetime.now(timezone.utc)

    if invitation.accepted_at is not None:
        return False, "Accepted invitations cannot be revoked"

    if invitation.revoked_at is not None:
        return False, "Invitation is already revoked"

    if invitation.expires_at <= now:
        return False, "Expired invitations cannot be revoked"

    return True, None


async def revoke_isp_admin_invitation(
    db: AsyncSession,
    invitation: AccountInvitation,
) -> AccountInvitation:
    invitation.revoked_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(invitation)

    return invitation
