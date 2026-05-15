from __future__ import annotations

import argparse
import asyncio

from app.db.session import AsyncSessionLocal
from app.services.mfa_setup_cleanup_service import (
    DEFAULT_MFA_SETUP_CLEANUP_RETENTION_DAYS,
    cleanup_inactive_mfa_setup_challenges,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean old inactive MFA setup challenges.",
    )

    parser.add_argument(
        "--retention-days",
        type=int,
        default=DEFAULT_MFA_SETUP_CLEANUP_RETENTION_DAYS,
        help=(
            "Delete inactive MFA setup challenges older than this many days. "
            "Default: %(default)s"
        ),
    )

    return parser


async def run_cleanup(retention_days: int) -> int:
    async with AsyncSessionLocal() as db:
        deleted_count = await cleanup_inactive_mfa_setup_challenges(
            db=db,
            retention_days=retention_days,
        )

        await db.commit()

    return deleted_count


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    deleted_count = asyncio.run(
        run_cleanup(retention_days=args.retention_days)
    )

    print(f"Deleted {deleted_count} inactive MFA setup challenge(s).")


if __name__ == "__main__":
    main()
