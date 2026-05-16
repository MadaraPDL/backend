"""allow step 20 alert types

Revision ID: 82b48d002f46
Revises: 68eea2a5b4d2
Create Date: 2026-05-16

"""
from typing import Sequence, Union

from alembic import op


revision: str = "82b48d002f46"
down_revision: Union[str, Sequence[str], None] = "68eea2a5b4d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ALERT_TYPES = (
    "high_usage",
    "plan_exceed_risk",
    "unusual_consumption",
    "new_device_connected",
    "policy_failed",
)


def _alert_type_check_sql() -> str:
    allowed_values = ", ".join(f"'{alert_type}'" for alert_type in ALERT_TYPES)
    return f"alert_type IN ({allowed_values})"


def upgrade() -> None:
    op.drop_constraint(
        "chk_alert_type",
        "alerts",
        type_="check",
    )

    op.create_check_constraint(
        "chk_alert_type",
        "alerts",
        _alert_type_check_sql(),
    )


def downgrade() -> None:
    op.drop_constraint(
        "chk_alert_type",
        "alerts",
        type_="check",
    )

    op.create_check_constraint(
        "chk_alert_type",
        "alerts",
        "alert_type IN ('high_usage', 'new_device_connected', 'policy_failed')",
    )
