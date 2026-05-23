from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.core.security import hash_password
from app.models.app_user import AppUser
from app.models.device import Device
from app.models.device_network_policy import DeviceNetworkPolicy
from app.models.isp import ISP
from app.models.recommendation import Recommendation
from app.models.router import Router
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.app_user import MyDevicePolicyCreate, MyPlanChangeRequestCreate
from app.services.app_user.device_policy_service import create_my_device_policy
from app.services.app_user.plan_change_request_service import (
    create_my_plan_change_request,
)


@pytest.mark.asyncio
async def test_app_user_cannot_create_actions_using_other_users_resources(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"App User Action Ownership ISP {suffix}",
        contact_email=f"action-ownership-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    user_a = AppUser(
        isp_id=isp.id,
        full_name="Action User A",
        email=f"action-user-a-{suffix}@example.com",
        username=f"action_user_a_{suffix}",
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
        full_name="Action User B",
        email=f"action-user-b-{suffix}@example.com",
        username=f"action_user_b_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    current_plan = SubscriptionPlan(
        isp_id=isp.id,
        plan_name=f"Current Action Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan",
        is_active=True,
        created_by_admin_id=None,
    )

    requested_plan = SubscriptionPlan(
        isp_id=isp.id,
        plan_name=f"Requested Action Plan {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=200,
        speed_limit_mbps=100,
        description="Requested plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([user_a, user_b, current_plan, requested_plan])
    await integration_db.flush()

    subscription_a = UserSubscription(
        user_id=user_a.id,
        plan_id=current_plan.id,
        subscription_label="User A Subscription",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    subscription_b = UserSubscription(
        user_id=user_b.id,
        plan_id=current_plan.id,
        subscription_label="User B Subscription",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add_all([subscription_a, subscription_b])
    await integration_db.flush()

    router_b = Router(
        isp_id=isp.id,
        user_subscription_id=subscription_b.id,
        assigned_by_admin_id=None,
        router_name="User B Router",
        router_model="Test Router",
        router_ip="192.168.60.1",
        mac_address=f"BB:CC:DD:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )

    integration_db.add(router_b)
    await integration_db.flush()

    device_b = Device(
        router_id=router_b.id,
        user_id=user_b.id,
        device_name="User B Device",
        mac_address=f"CC:DD:EE:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        ip_address="192.168.60.20",
        device_type="phone",
        is_trusted=True,
        status="connected",
        last_seen=now,
    )

    recommendation_b = Recommendation(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        current_plan_id=current_plan.id,
        recommendation_plan_id=requested_plan.id,
        prediction_id=None,
        recommendation_type="upgrade_plan",
        recommendation_text="This recommendation belongs to User B.",
        reason="Action ownership integration test",
        confidence_score=Decimal("0.90"),
        status="new",
    )

    integration_db.add_all([device_b, recommendation_b])
    await integration_db.flush()

    policy_result = await create_my_device_policy(
        db=integration_db,
        current_user=user_a,
        data=MyDevicePolicyCreate(
            device_id=device_b.id,
            policy_type="bandwidth_limit",
            bandwidth_limit_mbps=Decimal("5.0"),
            priority_level=None,
        ),
    )

    assert policy_result is None

    other_subscription_request = await create_my_plan_change_request(
        db=integration_db,
        current_user=user_a,
        data=MyPlanChangeRequestCreate(
            user_subscription_id=subscription_b.id,
            requested_plan_id=requested_plan.id,
            recommendation_id=None,
            request_type="upgrade",
            confirmation_text="CHANGE PLAN",
            reason="Trying to use another user's subscription.",
        ),
    )

    assert other_subscription_request is None

    other_recommendation_request = await create_my_plan_change_request(
        db=integration_db,
        current_user=user_a,
        data=MyPlanChangeRequestCreate(
            user_subscription_id=subscription_a.id,
            requested_plan_id=requested_plan.id,
            recommendation_id=recommendation_b.id,
            request_type="upgrade",
            confirmation_text="CHANGE PLAN",
            reason="Trying to use another user's recommendation.",
        ),
    )

    assert other_recommendation_request is None

    policy_rows = await integration_db.execute(
        select(DeviceNetworkPolicy).where(
            DeviceNetworkPolicy.requested_by_user_id == user_a.id,
        )
    )
    assert list(policy_rows.scalars().all()) == []

    request_rows = await integration_db.execute(
        select(SubscriptionChangeRequest).where(
            SubscriptionChangeRequest.user_id == user_a.id,
        )
    )
    assert list(request_rows.scalars().all()) == []
