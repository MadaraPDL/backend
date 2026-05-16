from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.alert import Alert
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.models.recommendation import Recommendation
from app.models.router import Router
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription
from app.services.isp_admin import get_isp_admin_analytics_summary


@pytest.mark.asyncio
async def test_isp_admin_analytics_summary_counts_only_current_isp_data(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()
    period_start = now - timedelta(days=1)
    period_end = now + timedelta(days=1)

    isp_a = ISP(
        name=f"Analytics ISP A {suffix}",
        contact_email=f"analytics-isp-a-{suffix}@example.com",
        status="active",
    )
    isp_b = ISP(
        name=f"Analytics ISP B {suffix}",
        contact_email=f"analytics-isp-b-{suffix}@example.com",
        status="active",
    )

    integration_db.add_all([isp_a, isp_b])
    await integration_db.flush()

    user_a_active = AppUser(
        isp_id=isp_a.id,
        full_name="Analytics Active User A",
        email=f"analytics-active-user-a-{suffix}@example.com",
        username=f"analytics_active_user_a_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )
    user_a_inactive = AppUser(
        isp_id=isp_a.id,
        full_name="Analytics Inactive User A",
        email=f"analytics-inactive-user-a-{suffix}@example.com",
        username=f"analytics_inactive_user_a_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="inactive",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )
    user_b = AppUser(
        isp_id=isp_b.id,
        full_name="Analytics User B",
        email=f"analytics-user-b-{suffix}@example.com",
        username=f"analytics_user_b_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    integration_db.add_all([user_a_active, user_a_inactive, user_b])
    await integration_db.flush()

    plan_a_current = SubscriptionPlan(
        isp_id=isp_a.id,
        plan_name=f"Analytics Current Plan A {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan A",
        is_active=True,
        created_by_admin_id=None,
    )
    plan_a_requested = SubscriptionPlan(
        isp_id=isp_a.id,
        plan_name=f"Analytics Requested Plan A {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=250,
        speed_limit_mbps=100,
        description="Requested plan A",
        is_active=True,
        created_by_admin_id=None,
    )
    plan_b = SubscriptionPlan(
        isp_id=isp_b.id,
        plan_name=f"Analytics Plan B {suffix}",
        monthly_price=Decimal("30.00"),
        data_limit_gb=150,
        speed_limit_mbps=70,
        description="Plan B",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([plan_a_current, plan_a_requested, plan_b])
    await integration_db.flush()

    subscription_a_active = UserSubscription(
        user_id=user_a_active.id,
        plan_id=plan_a_current.id,
        subscription_label="Analytics Active Subscription A",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )
    subscription_a_suspended = UserSubscription(
        user_id=user_a_inactive.id,
        plan_id=plan_a_current.id,
        subscription_label="Analytics Suspended Subscription A",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="suspended",
        auto_renew=False,
    )
    subscription_b = UserSubscription(
        user_id=user_b.id,
        plan_id=plan_b.id,
        subscription_label="Analytics Subscription B",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add_all(
        [subscription_a_active, subscription_a_suspended, subscription_b]
    )
    await integration_db.flush()

    router_a_active = Router(
        isp_id=isp_a.id,
        user_subscription_id=subscription_a_active.id,
        assigned_by_admin_id=None,
        router_name="Analytics Active Router A",
        router_model="Simulator Router",
        router_ip="192.168.90.1",
        mac_address=f"AA:90:90:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )
    router_a_inactive = Router(
        isp_id=isp_a.id,
        user_subscription_id=subscription_a_suspended.id,
        assigned_by_admin_id=None,
        router_name="Analytics Inactive Router A",
        router_model="Simulator Router",
        router_ip="192.168.91.1",
        mac_address=f"AB:91:91:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="inactive",
    )
    router_b = Router(
        isp_id=isp_b.id,
        user_subscription_id=subscription_b.id,
        assigned_by_admin_id=None,
        router_name="Analytics Router B",
        router_model="Simulator Router",
        router_ip="192.168.92.1",
        mac_address=f"AC:92:92:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )

    integration_db.add_all([router_a_active, router_a_inactive, router_b])
    await integration_db.flush()

    usage_a_inside_period = UsageRecord(
        user_id=user_a_active.id,
        user_subscription_id=subscription_a_active.id,
        router_id=router_a_active.id,
        device_id=None,
        upload_mb=Decimal("100.00"),
        download_mb=Decimal("900.00"),
        record_start=now - timedelta(hours=1),
        record_end=now,
        source="integration-test",
    )
    usage_a_outside_period = UsageRecord(
        user_id=user_a_active.id,
        user_subscription_id=subscription_a_active.id,
        router_id=router_a_active.id,
        device_id=None,
        upload_mb=Decimal("50.00"),
        download_mb=Decimal("50.00"),
        record_start=now - timedelta(days=10),
        record_end=now - timedelta(days=9),
        source="integration-test",
    )
    usage_b_inside_period = UsageRecord(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        router_id=router_b.id,
        device_id=None,
        upload_mb=Decimal("500.00"),
        download_mb=Decimal("500.00"),
        record_start=now - timedelta(hours=1),
        record_end=now,
        source="integration-test",
    )

    integration_db.add_all(
        [usage_a_inside_period, usage_a_outside_period, usage_b_inside_period]
    )

    alerts = [
        Alert(
            user_id=user_a_active.id,
            user_subscription_id=subscription_a_active.id,
            alert_type="high_usage",
            severity="critical",
            title="Critical usage",
            message="Critical usage alert.",
            status="unread",
        ),
        Alert(
            user_id=user_a_active.id,
            user_subscription_id=subscription_a_active.id,
            alert_type="new_device",
            severity="medium",
            title="New device",
            message="New device alert.",
            status="read",
        ),
        Alert(
            user_id=user_b.id,
            user_subscription_id=subscription_b.id,
            alert_type="high_usage",
            severity="critical",
            title="Other ISP critical usage",
            message="Should not count for ISP A.",
            status="unread",
        ),
    ]

    recommendations = [
        Recommendation(
            user_id=user_a_active.id,
            user_subscription_id=subscription_a_active.id,
            current_plan_id=plan_a_current.id,
            recommendation_plan_id=plan_a_requested.id,
            prediction_id=None,
            recommendation_type="upgrade_plan",
            recommendation_text="Upgrade recommended.",
            reason="Higher predicted usage.",
            confidence_score=Decimal("90.00"),
            status="new",
        ),
        Recommendation(
            user_id=user_a_active.id,
            user_subscription_id=subscription_a_active.id,
            current_plan_id=plan_a_current.id,
            recommendation_plan_id=plan_a_requested.id,
            prediction_id=None,
            recommendation_type="upgrade_plan",
            recommendation_text="Accepted upgrade.",
            reason="User accepted.",
            confidence_score=Decimal("95.00"),
            status="accepted",
        ),
        Recommendation(
            user_id=user_b.id,
            user_subscription_id=subscription_b.id,
            current_plan_id=plan_b.id,
            recommendation_plan_id=None,
            prediction_id=None,
            recommendation_type="monitor_usage",
            recommendation_text="Other ISP recommendation.",
            reason="Should not count for ISP A.",
            confidence_score=Decimal("80.00"),
            status="new",
        ),
    ]

    change_requests = [
        SubscriptionChangeRequest(
            user_id=user_a_active.id,
            user_subscription_id=subscription_a_active.id,
            current_plan_id=plan_a_current.id,
            requested_plan_id=plan_a_requested.id,
            recommendation_id=None,
            request_type="upgrade",
            reason="Pending request.",
            status="pending",
        ),
        SubscriptionChangeRequest(
            user_id=user_a_active.id,
            user_subscription_id=subscription_a_active.id,
            current_plan_id=plan_a_current.id,
            requested_plan_id=plan_a_requested.id,
            recommendation_id=None,
            request_type="upgrade",
            reason="Approved request.",
            status="approved",
        ),
        SubscriptionChangeRequest(
            user_id=user_a_active.id,
            user_subscription_id=subscription_a_active.id,
            current_plan_id=plan_a_current.id,
            requested_plan_id=plan_a_requested.id,
            recommendation_id=None,
            request_type="upgrade",
            reason="Rejected request.",
            status="rejected",
        ),
        SubscriptionChangeRequest(
            user_id=user_b.id,
            user_subscription_id=subscription_b.id,
            current_plan_id=plan_b.id,
            requested_plan_id=plan_b.id,
            recommendation_id=None,
            request_type="upgrade",
            reason="Other ISP request.",
            status="pending",
        ),
    ]

    integration_db.add_all(alerts + recommendations + change_requests)
    await integration_db.flush()

    summary = await get_isp_admin_analytics_summary(
        db=integration_db,
        isp_id=isp_a.id,
        period_start=period_start,
        period_end=period_end,
    )

    assert summary.isp_id == isp_a.id
    assert summary.period_start == period_start
    assert summary.period_end == period_end

    assert summary.total_users == 2
    assert summary.active_users == 1

    assert summary.total_subscriptions == 2
    assert summary.active_subscriptions == 1

    assert summary.total_routers == 2
    assert summary.active_routers == 1

    assert summary.pending_plan_change_requests == 1
    assert summary.approved_plan_change_requests == 1
    assert summary.rejected_plan_change_requests == 1

    assert summary.total_alerts == 2
    assert summary.unread_alerts == 1
    assert summary.critical_alerts == 1

    assert summary.total_recommendations == 2
    assert summary.new_recommendations == 1
    assert summary.accepted_recommendations == 1

    assert summary.total_usage_mb == Decimal("1000.00")
    assert summary.total_usage_gb == Decimal("0.9765625")
