from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.models.router import Router
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.services.isp_admin import (
    get_app_user_for_isp,
    get_router_for_isp,
    get_subscription_plan_for_isp,
    get_user_subscription_for_isp,
)


@pytest.mark.asyncio
async def test_isp_admin_cannot_access_other_isp_core_resources(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp_a = ISP(
        name=f"Isolation ISP A {suffix}",
        contact_email=f"isolation-a-{suffix}@example.com",
        status="active",
    )
    isp_b = ISP(
        name=f"Isolation ISP B {suffix}",
        contact_email=f"isolation-b-{suffix}@example.com",
        status="active",
    )

    integration_db.add_all([isp_a, isp_b])
    await integration_db.flush()

    admin_a = Admin(
        isp_id=isp_a.id,
        full_name="ISP A Admin",
        email=f"isp-a-admin-{suffix}@example.com",
        username=f"isp_a_admin_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=True,
        preferred_mfa_method="authenticator",
    )

    user_b = AppUser(
        isp_id=isp_b.id,
        full_name="ISP B User",
        email=f"isp-b-user-{suffix}@example.com",
        username=f"isp_b_user_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    plan_b = SubscriptionPlan(
        isp_id=isp_b.id,
        plan_name=f"ISP B Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Plan owned by ISP B",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([admin_a, user_b, plan_b])
    await integration_db.flush()

    subscription_b = UserSubscription(
        user_id=user_b.id,
        plan_id=plan_b.id,
        subscription_label="ISP B Subscription",
        assigned_by_admin_id=None,
        start_date=date.today(),
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add(subscription_b)
    await integration_db.flush()

    router_b = Router(
        isp_id=isp_b.id,
        user_subscription_id=subscription_b.id,
        assigned_by_admin_id=None,
        router_name="ISP B Router",
        router_model="Test Router",
        router_ip="192.168.50.1",
        mac_address=f"AA:BB:CC:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )

    integration_db.add(router_b)
    await integration_db.flush()

    assert admin_a.isp_id == isp_a.id

    assert await get_app_user_for_isp(
        db=integration_db,
        isp_id=admin_a.isp_id,
        user_id=user_b.id,
    ) is None

    assert await get_subscription_plan_for_isp(
        db=integration_db,
        isp_id=admin_a.isp_id,
        plan_id=plan_b.id,
    ) is None

    assert await get_user_subscription_for_isp(
        db=integration_db,
        isp_id=admin_a.isp_id,
        subscription_id=subscription_b.id,
    ) is None

    assert await get_router_for_isp(
        db=integration_db,
        isp_id=admin_a.isp_id,
        router_id=router_b.id,
    ) is None
