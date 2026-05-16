from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.admin import Admin
from app.models.alert import Alert
from app.models.app_user import AppUser
from app.models.device import Device
from app.models.isp import ISP
from app.models.recommendation import Recommendation
from app.models.router import Router
from app.models.router_action_log import RouterActionLog
from app.models.subscription_plan import SubscriptionPlan
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import ISPAdminReportCreateRequest
from app.services.isp_admin import generate_report_for_isp


@pytest.mark.asyncio
async def test_isp_admin_can_generate_expanded_report_types(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"Expanded Reports ISP {suffix}",
        contact_email=f"expanded-reports-isp-{suffix}@example.com",
        status="active",
    )
    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="Expanded Reports Admin",
        email=f"expanded-reports-admin-{suffix}@example.com",
        username=f"expanded_reports_admin_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    user = AppUser(
        isp_id=isp.id,
        full_name="Expanded Reports User",
        email=f"expanded-reports-user-{suffix}@example.com",
        username=f"expanded_reports_user_{suffix}",
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
        plan_name=f"Expanded Reports Current Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan",
        is_active=True,
        created_by_admin_id=None,
    )

    recommended_plan = SubscriptionPlan(
        isp_id=isp.id,
        plan_name=f"Expanded Reports Recommended Plan {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=250,
        speed_limit_mbps=100,
        description="Recommended plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([admin, user, current_plan, recommended_plan])
    await integration_db.flush()

    subscription = UserSubscription(
        user_id=user.id,
        plan_id=current_plan.id,
        subscription_label="Expanded Reports Subscription",
        assigned_by_admin_id=None,
        start_date=today,
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
        router_name="Expanded Reports Router",
        router_model="Simulator Router",
        router_ip="192.168.140.1",
        mac_address=f"AA:14:14:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )

    integration_db.add(router)
    await integration_db.flush()

    trusted_device = Device(
        router_id=router.id,
        user_id=user.id,
        device_name="Trusted Laptop",
        mac_address=f"AA:DD:14:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        ip_address="192.168.140.20",
        device_type="laptop",
        is_trusted=True,
        status="connected",
        last_seen=now,
    )

    untrusted_device = Device(
        router_id=router.id,
        user_id=user.id,
        device_name="Untrusted Phone",
        mac_address=f"BB:DD:14:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        ip_address="192.168.140.21",
        device_type="phone",
        is_trusted=False,
        status="disconnected",
        last_seen=now,
    )

    usage = UsageRecord(
        user_id=user.id,
        user_subscription_id=subscription.id,
        router_id=router.id,
        device_id=None,
        upload_mb=Decimal("100.00"),
        download_mb=Decimal("924.00"),
        record_start=now - timedelta(hours=1),
        record_end=now,
        source="expanded-report-test",
    )

    alert = Alert(
        user_id=user.id,
        user_subscription_id=subscription.id,
        alert_type="high_usage",
        severity="critical",
        title="High usage",
        message="High usage alert.",
        status="unread",
    )

    recommendation = Recommendation(
        user_id=user.id,
        user_subscription_id=subscription.id,
        current_plan_id=current_plan.id,
        recommendation_plan_id=recommended_plan.id,
        prediction_id=None,
        recommendation_type="upgrade_plan",
        recommendation_text="Upgrade recommended.",
        reason="Predicted high usage.",
        confidence_score=Decimal("90.00"),
        status="new",
    )

    router_action_log = RouterActionLog(
        router_id=router.id,
        policy_id=None,
        action_type="bandwidth_limit",
        command_payload={"source": "expanded-report-test"},
        response_payload={"adapter": "simulator"},
        status="success",
        error_message=None,
        executed_at=now,
    )

    integration_db.add_all(
        [
            trusted_device,
            untrusted_device,
            usage,
            alert,
            recommendation,
            router_action_log,
        ]
    )
    await integration_db.flush()

    alert_report = await generate_report_for_isp(
        db=integration_db,
        current_admin=admin,
        request=ISPAdminReportCreateRequest(report_type="alert_report"),
    )

    assert alert_report.report_type == "alert_report"
    assert alert_report.report_data["summary_type"] == "alert_summary"
    assert alert_report.report_data["total_alerts"] == 1
    assert alert_report.report_data["unread_alerts"] == 1
    assert alert_report.report_data["critical_alerts"] == 1
    assert alert_report.report_data["counts_by_type"]["high_usage"] == 1
    assert alert_report.report_data["counts_by_severity"]["critical"] == 1

    recommendation_report = await generate_report_for_isp(
        db=integration_db,
        current_admin=admin,
        request=ISPAdminReportCreateRequest(report_type="recommendation_report"),
    )

    assert recommendation_report.report_type == "recommendation_report"
    assert recommendation_report.report_data["summary_type"] == "recommendation_summary"
    assert recommendation_report.report_data["total_recommendations"] == 1
    assert recommendation_report.report_data["counts_by_status"]["new"] == 1
    assert recommendation_report.report_data["counts_by_type"]["upgrade_plan"] == 1

    device_report = await generate_report_for_isp(
        db=integration_db,
        current_admin=admin,
        request=ISPAdminReportCreateRequest(report_type="device_report"),
    )

    assert device_report.report_type == "device_report"
    assert device_report.report_data["summary_type"] == "device_summary"
    assert device_report.report_data["total_devices"] == 2
    assert device_report.report_data["connected_devices"] == 1
    assert device_report.report_data["trusted_devices"] == 1
    assert device_report.report_data["untrusted_devices"] == 1
    assert device_report.report_data["counts_by_status"]["connected"] == 1
    assert device_report.report_data["counts_by_status"]["disconnected"] == 1
    assert device_report.report_data["counts_by_type"]["laptop"] == 1
    assert device_report.report_data["counts_by_type"]["phone"] == 1

    network_report = await generate_report_for_isp(
        db=integration_db,
        current_admin=admin,
        request=ISPAdminReportCreateRequest(
            report_type="network_performance_report"
        ),
    )

    assert network_report.report_type == "network_performance_report"
    assert network_report.report_data["summary_type"] == "network_performance_summary"
    assert network_report.report_data["total_routers"] == 1
    assert network_report.report_data["active_routers"] == 1
    assert network_report.report_data["inactive_routers"] == 0
    assert network_report.report_data["total_usage_mb"] == "1024.00"
    assert network_report.report_data["total_usage_gb"] == "1.00"
    assert network_report.report_data["router_action_counts_by_status"]["success"] == 1
    assert network_report.report_data["router_action_counts_by_type"]["bandwidth_limit"] == 1
