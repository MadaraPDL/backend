from __future__ import annotations

from datetime import datetime, timezone
import secrets

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.mfa_backup_code import MFABackupCode
from app.schemas.auth import AccountType
from app.services.account_service import Account
from app.services.mfa_settings_service import verify_mfa_settings_challenge


BACKUP_CODE_COUNT = 10
_BACKUP_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_backup_code() -> str:
    groups = [
        "".join(secrets.choice(_BACKUP_CODE_ALPHABET) for _ in range(4))
        for _ in range(3)
    ]

    return "-".join(groups)


def _owner_filter(account: Account, account_type: AccountType):
    if account_type == "admin":
        return MFABackupCode.admin_id == account.id

    return MFABackupCode.app_user_id == account.id


async def count_available_backup_codes(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> int:
    stmt = select(func.count(MFABackupCode.id)).where(
        MFABackupCode.account_type == account_type,
        MFABackupCode.used_at.is_(None),
        MFABackupCode.revoked_at.is_(None),
        _owner_filter(account, account_type),
    )

    result = await db.execute(stmt)
    return int(result.scalar_one())


async def build_backup_code_status(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> dict:
    available_count = await count_available_backup_codes(
        db=db,
        account=account,
        account_type=account_type,
    )

    return {
        "account_type": account_type,
        "backup_codes_available": available_count > 0,
        "available_backup_code_count": available_count,
    }


async def revoke_unused_backup_codes(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> None:
    stmt = select(MFABackupCode).where(
        MFABackupCode.account_type == account_type,
        MFABackupCode.used_at.is_(None),
        MFABackupCode.revoked_at.is_(None),
        _owner_filter(account, account_type),
    )

    result = await db.execute(stmt)
    active_backup_codes = result.scalars().all()
    now = datetime.now(timezone.utc)

    for backup_code in active_backup_codes:
        backup_code.revoked_at = now


async def regenerate_backup_codes(
    *,
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
    challenge_token: str,
    code: str,
) -> list[str]:
    await verify_mfa_settings_challenge(
        db=db,
        account=account,
        account_type=account_type,
        challenge_token=challenge_token,
        code=code,
    )

    await revoke_unused_backup_codes(
        db=db,
        account=account,
        account_type=account_type,
    )

    raw_codes = [generate_backup_code() for _ in range(BACKUP_CODE_COUNT)]

    for raw_code in raw_codes:
        db.add(
            MFABackupCode(
                account_type=account_type,
                admin_id=account.id if account_type == "admin" else None,
                app_user_id=account.id if account_type == "app_user" else None,
                code_hash=hash_password(raw_code),
            )
        )

    await db.flush()

    return raw_codes
