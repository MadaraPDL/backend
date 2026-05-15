"""add revoked at to mfa setup challenges

Revision ID: 68eea2a5b4d2
Revises: 846ac0977099
Create Date: 2026-05-15 14:50:07.705634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68eea2a5b4d2'
down_revision: Union[str, Sequence[str], None] = '846ac0977099'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add revocation timestamp to MFA setup challenges."""
    op.add_column(
        "mfa_setup_challenges",
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_mfa_setup_challenges_revoked_at",
        "mfa_setup_challenges",
        ["revoked_at"],
    )


def downgrade() -> None:
    """Remove revocation timestamp from MFA setup challenges."""
    op.drop_index(
        "ix_mfa_setup_challenges_revoked_at",
        table_name="mfa_setup_challenges",
    )

    op.drop_column("mfa_setup_challenges", "revoked_at")
