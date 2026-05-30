from __future__ import annotations

import logging

from sqlalchemy import text

from app.db.session import engine

logger = logging.getLogger(__name__)


CREATE_PUSH_TOKEN_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_user_push_tokens (
    id UUID DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    user_id UUID NOT NULL,
    expo_push_token VARCHAR(255) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    device_id VARCHAR(128),
    permission_status VARCHAR(32) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    last_registered_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    disabled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
)
"""

CREATE_PUSH_TOKEN_INDEXES_SQL = [
    """
    CREATE INDEX IF NOT EXISTS idx_app_user_push_tokens_user_id
    ON app_user_push_tokens (user_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_app_user_push_tokens_user_active
    ON app_user_push_tokens (user_id, is_active)
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS ux_app_user_push_tokens_token
    ON app_user_push_tokens (expo_push_token)
    """,
]


async def ensure_app_user_push_token_table() -> None:
    """Ensure the optional push-token table exists.

    This is an idempotent deployment safety guard for hosted environments where
    an interactive shell is unavailable. It only creates the push-token table and
    indexes if missing; it does not alter existing core tables or expose secrets.
    """

    try:
        async with engine.begin() as connection:
            await connection.execute(text(CREATE_PUSH_TOKEN_TABLE_SQL))

            for index_sql in CREATE_PUSH_TOKEN_INDEXES_SQL:
                await connection.execute(text(index_sql))

    except Exception as exc:
        logger.warning("Push token table startup check failed: %s", exc)
