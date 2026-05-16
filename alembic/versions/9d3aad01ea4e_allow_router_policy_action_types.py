"""allow router policy action types

Revision ID: 9d3aad01ea4e
Revises: 82b48d002f46
Create Date: 2026-05-16

"""
from typing import Sequence, Union

from alembic import op


revision: str = "9d3aad01ea4e"
down_revision: Union[str, Sequence[str], None] = "82b48d002f46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROUTER_ACTION_TYPES = (
    "bandwidth_limit",
    "device_priority",
)


def _router_action_type_check_sql() -> str:
    allowed_values = ", ".join(f"'{action_type}'" for action_type in ROUTER_ACTION_TYPES)
    return f"action_type IN ({allowed_values})"


def upgrade() -> None:
    op.drop_constraint(
        "chk_router_action_type",
        "router_action_logs",
        type_="check",
    )

    op.create_check_constraint(
        "chk_router_action_type",
        "router_action_logs",
        _router_action_type_check_sql(),
    )


def downgrade() -> None:
    op.drop_constraint(
        "chk_router_action_type",
        "router_action_logs",
        type_="check",
    )

    op.create_check_constraint(
        "chk_router_action_type",
        "router_action_logs",
        "action_type IN ('restart_router', 'limit_device', 'prioritize_device')",
    )
