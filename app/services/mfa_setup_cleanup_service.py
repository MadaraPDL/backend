from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mfa_setup_challenge import MFASetupChallenge


DEFAULT_MFA_SETUP_CLEANUP_RETENTION_DAYS = 7


async def cleanup_inactive_mfa_setup_challenges(
    db: AsyncSession,
    retention_days: int = DEFAULT_MFA_SETUP_CLEANUP_RETENTION_DAYS,
) -> int:
    if retention_days < 0:
        raise ValueError("retention_days must be greater than or equal to 0.")

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=retention_days)

    stmt = delete(MFASetupChallenge).where(
        MFASetupChallenge.created_at <= cutoff,
        or_(
            MFASetupChallenge.used_at.is_not(None),
            MFASetupChallenge.revoked_at.is_not(None),
            MFASetupChallenge.expires_at <= now,
        ),
    )

    result = await db.execute(stmt)

    return result.rowcount or 0
