"""add app user push tokens

Revision ID: e3b7c6a9d4f1
Revises: a6f4d2c9b1e0
Create Date: 2026-05-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e3b7c6a9d4f1"
down_revision: Union[str, None] = "a6f4d2c9b1e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_user_push_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expo_push_token", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("device_id", sa.String(length=128), nullable=True),
        sa.Column("permission_status", sa.String(length=32), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "last_registered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_app_user_push_tokens_user_id",
        "app_user_push_tokens",
        ["user_id"],
    )
    op.create_index(
        "idx_app_user_push_tokens_user_active",
        "app_user_push_tokens",
        ["user_id", "is_active"],
    )
    op.create_index(
        "ux_app_user_push_tokens_token",
        "app_user_push_tokens",
        ["expo_push_token"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ux_app_user_push_tokens_token",
        table_name="app_user_push_tokens",
    )
    op.drop_index(
        "idx_app_user_push_tokens_user_active",
        table_name="app_user_push_tokens",
    )
    op.drop_index(
        "idx_app_user_push_tokens_user_id",
        table_name="app_user_push_tokens",
    )
    op.drop_table("app_user_push_tokens")
