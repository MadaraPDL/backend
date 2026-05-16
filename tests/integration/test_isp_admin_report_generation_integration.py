from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.models.report import Report
from app.models.router import Router
from app.models.subscription_plan import SubscriptionPlan
from app.models.usage_record import UsageRecord
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import ISPAdminReportCreateRequest
from app.services.isp_admin import (
    generate_report_for_isp,
    get_report_for_isp,
    list_reports_for_isp,
)


@pytest.mark.asyncio
async def test_isp_admin_can_generate_usage_report_for_own_isp(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"Report ISP {suffix}",
        contact_email=f"report-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="Report Admin",
        email=f"report-admin-{suffix}@example.com",
        username=f"report_admin_{suffix}",
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
        full_name="Report User",
        email=f"report-user-{suffix}@example.com",
        username=f"report_user_{suffix}",
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
        plan_name=f"Report Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Report plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([admin, user, plan])
    await integration_db.flush()

    subscription = UserSubscription(
        user_id=user.id,
        plan_id=plan.id,
        subscription_label="Report Subscription",
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
        router_name="Report Router",
        router_model="Simulator Router",
        router_ip="192.168.130.1",
        mac_address=f"AA:13:13:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}",
        api_endpoint=None,
        username=None,
        status="active",
    )

    integration_db.add(router)
    await integration_db.flush()

    usage = UsageRecord(
        user_id=user.id,
        user_subscription_id=subscription.id,
        router_id=router.id,
        device_id=None,
        upload_mb=Decimal("124.00"),
        download_mb=Decimal("900.00"),
        record_start=now - timedelta(hours=2),
        record_end=now - timedelta(hours=1),
        source="integration-test",
    )

    integration_db.add(usage)
    await integration_db.flush()

    report = await generate_report_for_isp(
        db=integration_db,
        current_admin=admin,
        request=ISPAdminReportCreateRequest(
            report_type="usage_report",
            title="Custom Usage Report",
            period_start=today,
            period_end=today,
        ),
    )

    assert report.id is not None
    assert report.isp_id == isp.id
    assert report.generated_by_admin_id == admin.id
    assert report.report_type == "usage_report"
    assert report.title == "Custom Usage Report"
    assert report.period_start == today
    assert report.period_end == today
    assert report.file_url is None
    assert report.report_data is not None
    assert report.report_data["summary_type"] == "usage_analytics_summary"
    assert report.report_data["summary"]["isp_id"] == str(isp.id)
    assert report.report_data["summary"]["total_users"] == 1
    assert report.report_data["summary"]["total_subscriptions"] == 1
    assert report.report_data["summary"]["total_routers"] == 1
    assert report.report_data["summary"]["total_usage_mb"] == "1024.00"
    assert report.report_data["summary"]["total_usage_gb"] == "1.00"

    listed_reports = await list_reports_for_isp(
        db=integration_db,
        isp_id=isp.id,
        report_type="usage_report",
    )

    assert [listed_report.id for listed_report in listed_reports] == [report.id]

    fetched_report = await get_report_for_isp(
        db=integration_db,
        isp_id=isp.id,
        report_id=report.id,
    )

    assert fetched_report is not None
    assert fetched_report.id == report.id


@pytest.mark.asyncio
async def test_isp_admin_report_queries_are_scoped_by_isp(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)

    isp_a = ISP(
        name=f"Report ISP A {suffix}",
        contact_email=f"report-isp-a-{suffix}@example.com",
        status="active",
    )
    isp_b = ISP(
        name=f"Report ISP B {suffix}",
        contact_email=f"report-isp-b-{suffix}@example.com",
        status="active",
    )

    integration_db.add_all([isp_a, isp_b])
    await integration_db.flush()

    admin_b = Admin(
        isp_id=isp_b.id,
        full_name="Report Admin B",
        email=f"report-admin-b-{suffix}@example.com",
        username=f"report_admin_b_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    report_b = Report(
        isp_id=isp_b.id,
        generated_by_admin_id=None,
        report_type="usage_report",
        title="ISP B Report",
        period_start=None,
        period_end=None,
        report_data={
            "summary_type": "usage_analytics_summary",
            "summary": {
                "isp_id": str(isp_b.id),
                "total_users": 0,
            },
        },
        file_url=None,
    )

    integration_db.add_all([admin_b, report_b])
    await integration_db.flush()

    invisible_report = await get_report_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
        report_id=report_b.id,
    )

    assert invisible_report is None

    listed_reports_for_a = await list_reports_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
    )

    assert report_b.id not in [report.id for report in listed_reports_for_a]
