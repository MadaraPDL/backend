"""add step 26 quality check constraints

Revision ID: 7b1a4d8e2c6f
Revises: 25a9f4c8d1e2
Create Date: 2026-05-17

"""
from typing import Sequence, Union

from alembic import op


revision: str = "7b1a4d8e2c6f"
down_revision: Union[str, Sequence[str], None] = "25a9f4c8d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CHECK_CONSTRAINTS = (
    (
        "device_network_policies",
        "chk_device_network_policy_type",
        "policy_type IN ('bandwidth_limit', 'device_priority')",
    ),
    (
        "device_network_policies",
        "chk_device_network_policy_status",
        "status IN ('pending', 'applied', 'failed')",
    ),
    (
        "recommendations",
        "chk_recommendation_type",
        (
            "recommendation_type IN ("
            "'upgrade_plan', "
            "'downgrade_plan', "
            "'stay_current', "
            "'monitor_usage'"
            ")"
        ),
    ),
    (
        "recommendations",
        "chk_recommendation_status",
        "status IN ('new', 'accepted')",
    ),
    (
        "reports",
        "chk_report_type",
        (
            "report_type IN ("
            "'usage_report', "
            "'device_report', "
            "'alert_report', "
            "'recommendation_report', "
            "'network_performance_report'"
            ")"
        ),
    ),
    (
        "user_subscriptions",
        "chk_user_subscription_status",
        "status IN ('pending', 'active', 'suspended', 'expired', 'cancelled')",
    ),
)


def upgrade() -> None:
    for table_name, constraint_name, condition in CHECK_CONSTRAINTS:
        op.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}")
        op.create_check_constraint(
            constraint_name,
            table_name,
            condition,
        )


def downgrade() -> None:
    for table_name, constraint_name, _condition in reversed(CHECK_CONSTRAINTS):
        op.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}")
