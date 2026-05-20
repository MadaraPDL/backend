"""add directional bandwidth limits

Revision ID: 846df2ca470d
Revises: 75c40bfe2d00
Create Date: 2026-05-20 12:14:52.200483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '846df2ca470d'
down_revision: Union[str, Sequence[str], None] = '75c40bfe2d00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "device_network_policies",
        sa.Column("download_limit_mbps", sa.Numeric(), nullable=True),
    )
    op.add_column(
        "device_network_policies",
        sa.Column("upload_limit_mbps", sa.Numeric(), nullable=True),
    )

    op.execute(
        """
        UPDATE device_network_policies
        SET
            download_limit_mbps = bandwidth_limit_mbps,
            upload_limit_mbps = bandwidth_limit_mbps
        WHERE policy_type = 'bandwidth_limit'
          AND bandwidth_limit_mbps IS NOT NULL
          AND download_limit_mbps IS NULL
          AND upload_limit_mbps IS NULL
        """
    )

    op.create_check_constraint(
        "chk_device_network_policy_download_limit_positive",
        "device_network_policies",
        "download_limit_mbps IS NULL OR download_limit_mbps > 0",
    )
    op.create_check_constraint(
        "chk_device_network_policy_upload_limit_positive",
        "device_network_policies",
        "upload_limit_mbps IS NULL OR upload_limit_mbps > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "chk_device_network_policy_upload_limit_positive",
        "device_network_policies",
        type_="check",
    )
    op.drop_constraint(
        "chk_device_network_policy_download_limit_positive",
        "device_network_policies",
        type_="check",
    )
    op.drop_column("device_network_policies", "upload_limit_mbps")
    op.drop_column("device_network_policies", "download_limit_mbps")
