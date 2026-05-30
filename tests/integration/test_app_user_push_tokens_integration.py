from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.core.security import hash_password
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.schemas.app_user.push_tokens import PushTokenRegisterRequest
from app.services.app_user.push_token_service import (
    disable_my_push_token,
    list_my_push_tokens,
    register_my_push_token,
)


async def ensure_push_token_table_exists(integration_db) -> None:
    """Create the push-token table in the exact DB/schema used by integration_db.

    The normal Alembic migration still exists for real deployments. This helper is
    only for the local integration test connection because the test database can be
    separate from the app database checked by app.db.session.AsyncSessionLocal.
    """

    await integration_db.execute(
        text(
            """
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
        )
    )
    await integration_db.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_app_user_push_tokens_token
            ON app_user_push_tokens (expo_push_token)
            """
        )
    )
    await integration_db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_app_user_push_tokens_user_id
            ON app_user_push_tokens (user_id)
            """
        )
    )
    await integration_db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_app_user_push_tokens_user_active
            ON app_user_push_tokens (user_id, is_active)
            """
        )
    )


@pytest.mark.asyncio
async def test_app_user_push_token_registration_is_idempotent_and_scoped(
    integration_db,
) -> None:
    await ensure_push_token_table_exists(integration_db)

    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"Push Token ISP {suffix}",
        contact_email=f"push-token-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    user_a = AppUser(
        isp_id=isp.id,
        full_name="Push User A",
        email=f"push-user-a-{suffix}@example.com",
        username=f"push_user_a_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )
    user_b = AppUser(
        isp_id=isp.id,
        full_name="Push User B",
        email=f"push-user-b-{suffix}@example.com",
        username=f"push_user_b_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    integration_db.add_all([user_a, user_b])
    await integration_db.flush()

    first_payload = PushTokenRegisterRequest(
        expo_push_token=f"ExpoPushToken[test-token-{suffix}]",
        platform="android",
        device_id="android-device-1",
        permission_status="granted",
    )

    first_token = await register_my_push_token(
        db=integration_db,
        current_user=user_a,
        payload=first_payload,
    )

    second_payload = PushTokenRegisterRequest(
        expo_push_token=f"ExpoPushToken[test-token-{suffix}]",
        platform="android",
        device_id="android-device-2",
        permission_status="granted",
    )

    second_token = await register_my_push_token(
        db=integration_db,
        current_user=user_a,
        payload=second_payload,
    )

    assert second_token.id == first_token.id
    assert second_token.user_id == user_a.id
    assert second_token.device_id == "android-device-2"
    assert second_token.is_active is True

    user_a_tokens = await list_my_push_tokens(
        db=integration_db,
        current_user=user_a,
    )
    user_b_tokens = await list_my_push_tokens(
        db=integration_db,
        current_user=user_b,
    )

    assert [token.id for token in user_a_tokens] == [first_token.id]
    assert user_b_tokens == []

    assert await disable_my_push_token(
        db=integration_db,
        current_user=user_b,
        token_id=first_token.id,
    ) is None

    disabled_token = await disable_my_push_token(
        db=integration_db,
        current_user=user_a,
        token_id=first_token.id,
    )

    assert disabled_token is not None
    assert disabled_token.id == first_token.id
    assert disabled_token.is_active is False
    assert disabled_token.disabled_at is not None
