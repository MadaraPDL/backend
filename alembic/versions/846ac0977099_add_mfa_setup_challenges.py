"""add mfa setup challenges

Revision ID: 846ac0977099
Revises: 11d8754136bc
Create Date: 2026-05-15 14:35:53.849077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '846ac0977099'
down_revision: Union[str, Sequence[str], None] = '11d8754136bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add server-side pending MFA setup challenge storage."""
    op.create_table(
        "mfa_setup_challenges",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("account_type", sa.String(length=20), nullable=False),
        sa.Column("admin_id", sa.UUID(), nullable=True),
        sa.Column("app_user_id", sa.UUID(), nullable=True),
        sa.Column("setup_token_hash", sa.Text(), nullable=False),
        sa.Column("authenticator_secret", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "attempt_count >= 0",
            name="chk_mfa_setup_attempt_count_non_negative",
        ),
        sa.CheckConstraint(
            "("
            "account_type = 'admin' "
            "AND admin_id IS NOT NULL "
            "AND app_user_id IS NULL"
            ") OR ("
            "account_type = 'app_user' "
            "AND app_user_id IS NOT NULL "
            "AND admin_id IS NULL"
            ")",
            name="chk_mfa_setup_account_owner",
        ),
        sa.ForeignKeyConstraint(
            ["admin_id"],
            ["admins.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["app_user_id"],
            ["app_users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("setup_token_hash"),
    )

    op.create_index(
        "ix_mfa_setup_challenges_admin_id",
        "mfa_setup_challenges",
        ["admin_id"],
    )

    op.create_index(
        "ix_mfa_setup_challenges_app_user_id",
        "mfa_setup_challenges",
        ["app_user_id"],
    )

    op.create_index(
        "ix_mfa_setup_challenges_expires_at",
        "mfa_setup_challenges",
        ["expires_at"],
    )


def downgrade() -> None:
    """Remove server-side pending MFA setup challenge storage."""
    op.drop_index(
        "ix_mfa_setup_challenges_expires_at",
        table_name="mfa_setup_challenges",
    )
    op.drop_index(
        "ix_mfa_setup_challenges_app_user_id",
        table_name="mfa_setup_challenges",
    )
    op.drop_index(
        "ix_mfa_setup_challenges_admin_id",
        table_name="mfa_setup_challenges",
    )
    op.drop_table("mfa_setup_challenges")
