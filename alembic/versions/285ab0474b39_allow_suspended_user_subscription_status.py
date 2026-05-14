"""allow suspended user subscription status

Revision ID: 285ab0474b39
Revises: c384b4d102bc
Create Date: 2026-05-14

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "285ab0474b39"
down_revision: Union[str, Sequence[str], None] = "c384b4d102bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow suspended user subscriptions."""
    op.drop_constraint(
        "chk_subscription_status",
        "user_subscriptions",
        type_="check",
    )

    op.create_check_constraint(
        "chk_subscription_status",
        "user_subscriptions",
        "status IN ('active', 'expired', 'cancelled', 'pending', 'suspended')",
    )


def downgrade() -> None:
    """Remove suspended user subscription status."""
    op.drop_constraint(
        "chk_subscription_status",
        "user_subscriptions",
        type_="check",
    )

    op.create_check_constraint(
        "chk_subscription_status",
        "user_subscriptions",
        "status IN ('active', 'expired', 'cancelled', 'pending')",
    )
