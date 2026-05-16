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
from app.models.router import Router
from app.models.router_action_log import RouterActionLog
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.services.isp_admin import (
    get_router_action_log_for_isp,
    list_router_action_logs_for_isp,
)
from app.services.router_actions import execute_device_network_policy


@pytest.mark.asyncio
async def test_execute_device_network_policy_creates_router_action_log(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp = ISP(
        name=f"Router Execution ISP {suffix}",
        contact_email=f"router-execution-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    user = AppUser(
        isp_id=isp.id,
        full_name="Router Execution User",
        email=f"router-execution-user-{suffix}@example.com",
        username=f"router_execution_user_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    plan = SubscriptionPlan(
        isp_id=isp.id,
        plan_name=f"Router Execution Plan {suffix}",
        monthly_price=Decimal("30.00"),
        data_limit_gb=150,
        speed_limit_mbps=80,
        description="Plan for router execution test",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([user, plan])
    await integration_db.flush()

    subscription = UserSubscription(
        user_id=user.id,
        plan_id=plan.id,
        subscription_label="Router Execution Subscription",
        assigned_by_admin_id=None,
        start_date=date.today(),
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add(subscription)
    await integration_db.flush()

    router = Router(
        isp_id=isp.id,
        user_subscription_id=subscription.id,
        assigned_by_admin_id=None,
        router_name="Router Execution Demo Router",
        router_model="Simulator Router",
        router_ip="192.168.70.1",
        mac_address=f"AA:70:70:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )

    integration_db.add(router)
    await integration_db.flush()

    device = Device(
        router_id=router.id,
        user_id=user.id,
        device_name="Router Execution Device",
        mac_address=f"BB:70:70:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        ip_address="192.168.70.20",
        device_type="laptop",
        is_trusted=True,
        status="connected",
        last_seen=now,
    )

    integration_db.add(device)
    await integration_db.flush()

    policy = DeviceNetworkPolicy(
        device_id=device.id,
        router_id=router.id,
        requested_by_user_id=user.id,
        policy_type="bandwidth_limit",
        bandwidth_limit_mbps=Decimal("12.5"),
        priority_level=None,
        status="pending",
        is_active=True,
    )

    integration_db.add(policy)
    await integration_db.flush()

    executed_policy, action_log = await execute_device_network_policy(
        db=integration_db,
        policy_id=policy.id,
    )

    assert executed_policy is not None
    assert action_log is not None

    assert executed_policy.id == policy.id
    assert executed_policy.status == "applied"
    assert executed_policy.applied_at is not None
    assert executed_policy.failure_reason is None

    assert action_log.router_id == router.id
    assert action_log.policy_id == policy.id
    assert action_log.action_type == "bandwidth_limit"
    assert action_log.status == "success"
    assert action_log.error_message is None
    assert action_log.command_payload["policy_id"] == str(policy.id)
    assert action_log.command_payload["device_id"] == str(device.id)
    assert action_log.response_payload["adapter"] == "simulator"

    rows = await integration_db.execute(
        select(RouterActionLog).where(
            RouterActionLog.policy_id == policy.id,
        )
    )
    saved_logs = list(rows.scalars().all())

    assert len(saved_logs) == 1
    assert saved_logs[0].id == action_log.id


@pytest.mark.asyncio
async def test_isp_admin_router_action_log_access_is_scoped_by_isp(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp_a = ISP(
        name=f"Router Log ISP A {suffix}",
        contact_email=f"router-log-isp-a-{suffix}@example.com",
        status="active",
    )
    isp_b = ISP(
        name=f"Router Log ISP B {suffix}",
        contact_email=f"router-log-isp-b-{suffix}@example.com",
        status="active",
    )

    integration_db.add_all([isp_a, isp_b])
    await integration_db.flush()

    user_b = AppUser(
        isp_id=isp_b.id,
        full_name="Router Log User B",
        email=f"router-log-user-b-{suffix}@example.com",
        username=f"router_log_user_b_{suffix}",
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
        plan_name=f"Router Log Plan B {suffix}",
        monthly_price=Decimal("35.00"),
        data_limit_gb=200,
        speed_limit_mbps=100,
        description="Plan for ISP B router log test",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([user_b, plan_b])
    await integration_db.flush()

    subscription_b = UserSubscription(
        user_id=user_b.id,
        plan_id=plan_b.id,
        subscription_label="Router Log Subscription B",
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
        router_name="ISP B Router Log Router",
        router_model="Simulator Router",
        router_ip="192.168.80.1",
        mac_address=f"AA:80:80:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )

    integration_db.add(router_b)
    await integration_db.flush()

    action_log_b = RouterActionLog(
        router_id=router_b.id,
        policy_id=None,
        action_type="bandwidth_limit",
        command_payload={"source": "integration-test"},
        response_payload={"adapter": "simulator"},
        status="success",
        error_message=None,
        executed_at=now,
    )

    integration_db.add(action_log_b)
    await integration_db.flush()

    logs_visible_to_isp_a = await list_router_action_logs_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
    )

    assert logs_visible_to_isp_a == []

    direct_lookup_from_isp_a = await get_router_action_log_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
        action_log_id=action_log_b.id,
    )

    assert direct_lookup_from_isp_a is None

    logs_visible_to_isp_b = await list_router_action_logs_for_isp(
        db=integration_db,
        isp_id=isp_b.id,
    )

    assert len(logs_visible_to_isp_b) == 1
    assert logs_visible_to_isp_b[0].id == action_log_b.id

    direct_lookup_from_isp_b = await get_router_action_log_for_isp(
        db=integration_db,
        isp_id=isp_b.id,
        action_log_id=action_log_b.id,
    )

    assert direct_lookup_from_isp_b is not None
    assert direct_lookup_from_isp_b.id == action_log_b.id
