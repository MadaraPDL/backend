"""allow medium alert severity

Revision ID: 75c40bfe2d00
Revises: 7b1a4d8e2c6f
Create Date: 2026-05-20 11:52:14.962223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75c40bfe2d00'
down_revision: Union[str, Sequence[str], None] = '7b1a4d8e2c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS chk_alert_severity")
    op.create_check_constraint(
        "chk_alert_severity",
        "alerts",
        "severity IN ('low', 'medium', 'high', 'critical')",
    )


def downgrade() -> None:
    op.execute("ALTER TABLE alerts DROP CONSTRAINT IF EXISTS chk_alert_severity")
    op.create_check_constraint(
        "chk_alert_severity",
        "alerts",
        "severity IN ('low', 'high', 'critical')",
    )
