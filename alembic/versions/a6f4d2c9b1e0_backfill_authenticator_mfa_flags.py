"""backfill authenticator mfa flags

Revision ID: a6f4d2c9b1e0
Revises: 8930a37f7add
Create Date: 2026-05-23

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "a6f4d2c9b1e0"
down_revision: Union[str, Sequence[str], None] = "8930a37f7add"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Repair accounts that completed authenticator setup before the new flag was synced."""
    op.execute(
        """
        UPDATE admins
        SET
            authenticator_mfa_enabled = true,
            preferred_mfa_method = 'authenticator'
        WHERE mfa_secret IS NOT NULL
          AND mfa_secret <> ''
          AND mfa_enabled = true
          AND COALESCE(authenticator_mfa_enabled, false) = false
        """
    )

    op.execute(
        """
        UPDATE app_users
        SET
            authenticator_mfa_enabled = true,
            preferred_mfa_method = 'authenticator'
        WHERE mfa_secret IS NOT NULL
          AND mfa_secret <> ''
          AND mfa_enabled = true
          AND COALESCE(authenticator_mfa_enabled, false) = false
        """
    )


def downgrade() -> None:
    """Data-only repair; do not unset MFA methods on downgrade."""
    pass
