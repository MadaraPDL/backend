"""add multi method mfa flags

Revision ID: 8930a37f7add
Revises: 846df2ca470d
Create Date: 2026-05-22

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8930a37f7add"
down_revision: Union[str, Sequence[str], None] = "846df2ca470d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "admins",
        sa.Column(
            "email_mfa_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "admins",
        sa.Column(
            "authenticator_mfa_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "app_users",
        sa.Column(
            "email_mfa_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "app_users",
        sa.Column(
            "authenticator_mfa_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Backfill admins from the legacy single-method MFA fields.
    # Admin default MFA method was authenticator.
    op.execute(
        """
        UPDATE admins
        SET
            email_mfa_enabled =
                CASE
                    WHEN mfa_enabled = true
                         AND preferred_mfa_method = 'email'
                    THEN true
                    ELSE false
                END,
            authenticator_mfa_enabled =
                CASE
                    WHEN mfa_secret IS NOT NULL
                         OR (
                            mfa_enabled = true
                            AND COALESCE(preferred_mfa_method, 'authenticator') = 'authenticator'
                         )
                    THEN true
                    ELSE false
                END
        """
    )

    # Backfill app users from the legacy single-method MFA fields.
    # App User default MFA method was email.
    op.execute(
        """
        UPDATE app_users
        SET
            email_mfa_enabled =
                CASE
                    WHEN mfa_enabled = true
                         AND COALESCE(preferred_mfa_method, 'email') = 'email'
                    THEN true
                    ELSE false
                END,
            authenticator_mfa_enabled =
                CASE
                    WHEN mfa_secret IS NOT NULL
                         OR (
                            mfa_enabled = true
                            AND preferred_mfa_method = 'authenticator'
                         )
                    THEN true
                    ELSE false
                END
        """
    )

    # Keep legacy compatibility flag aligned.
    op.execute(
        """
        UPDATE admins
        SET mfa_enabled = email_mfa_enabled OR authenticator_mfa_enabled
        """
    )
    op.execute(
        """
        UPDATE app_users
        SET mfa_enabled = email_mfa_enabled OR authenticator_mfa_enabled
        """
    )


def downgrade() -> None:
    op.drop_column("app_users", "authenticator_mfa_enabled")
    op.drop_column("app_users", "email_mfa_enabled")
    op.drop_column("admins", "authenticator_mfa_enabled")
    op.drop_column("admins", "email_mfa_enabled")
