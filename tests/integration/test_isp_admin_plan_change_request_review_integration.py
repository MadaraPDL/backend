from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.isp_admin import ISPAdminPlanChangeRequestReviewRequest
from app.services.isp_admin import (
    get_plan_change_request_for_isp,
    list_plan_change_requests_for_isp,
    review_plan_change_request_for_isp,
)


@pytest.mark.asyncio
async def test_isp_admin_can_approve_plan_change_request_for_own_isp(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"Plan Review ISP {suffix}",
        contact_email=f"plan-review-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="Plan Review Admin",
        email=f"plan-review-admin-{suffix}@example.com",
        username=f"plan_review_admin_{suffix}",
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
        full_name="Plan Review User",
        email=f"plan-review-user-{suffix}@example.com",
        username=f"plan_review_user_{suffix}",
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
        plan_name=f"Current Review Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan",
        is_active=True,
        created_by_admin_id=None,
    )

    requested_plan = SubscriptionPlan(
        isp_id=isp.id,
        plan_name=f"Requested Review Plan {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=250,
        speed_limit_mbps=100,
        description="Requested plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([admin, user, current_plan, requested_plan])
    await integration_db.flush()

    subscription = UserSubscription(
        user_id=user.id,
        plan_id=current_plan.id,
        subscription_label="Home Subscription",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add(subscription)
    await integration_db.flush()

    change_request = SubscriptionChangeRequest(
        user_id=user.id,
        user_subscription_id=subscription.id,
        current_plan_id=current_plan.id,
        requested_plan_id=requested_plan.id,
        recommendation_id=None,
        request_type="upgrade",
        reason="I need more data.",
        status="pending",
    )

    integration_db.add(change_request)
    await integration_db.flush()

    listed_requests = await list_plan_change_requests_for_isp(
        db=integration_db,
        isp_id=isp.id,
        status="pending",
    )

    assert [request.id for request in listed_requests] == [change_request.id]

    owned_request = await get_plan_change_request_for_isp(
        db=integration_db,
        isp_id=isp.id,
        request_id=change_request.id,
    )

    assert owned_request is not None
    assert owned_request.id == change_request.id

    reviewed_request = await review_plan_change_request_for_isp(
        db=integration_db,
        change_request=owned_request,
        current_admin=admin,
        request=ISPAdminPlanChangeRequestReviewRequest(
            decision="approve",
            admin_response="Approved for upgrade.",
        ),
    )

    assert reviewed_request is not None
    assert reviewed_request.status == "approved"
    assert reviewed_request.reviewed_by_admin_id == admin.id
    assert reviewed_request.reviewed_at is not None
    assert reviewed_request.admin_response == "Approved for upgrade."
    assert subscription.plan_id == requested_plan.id

    second_review = await review_plan_change_request_for_isp(
        db=integration_db,
        change_request=reviewed_request,
        current_admin=admin,
        request=ISPAdminPlanChangeRequestReviewRequest(
            decision="reject",
            admin_response="Trying to review twice.",
        ),
    )

    assert second_review is None


@pytest.mark.asyncio
async def test_isp_admin_cannot_access_other_isp_plan_change_request(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp_a = ISP(
        name=f"Plan Review ISP A {suffix}",
        contact_email=f"plan-review-isp-a-{suffix}@example.com",
        status="active",
    )
    isp_b = ISP(
        name=f"Plan Review ISP B {suffix}",
        contact_email=f"plan-review-isp-b-{suffix}@example.com",
        status="active",
    )

    integration_db.add_all([isp_a, isp_b])
    await integration_db.flush()

    admin_a = Admin(
        isp_id=isp_a.id,
        full_name="Plan Review Admin A",
        email=f"plan-review-admin-a-{suffix}@example.com",
        username=f"plan_review_admin_a_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        role="isp_admin",
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    user_b = AppUser(
        isp_id=isp_b.id,
        full_name="Plan Review User B",
        email=f"plan-review-user-b-{suffix}@example.com",
        username=f"plan_review_user_b_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )

    current_plan_b = SubscriptionPlan(
        isp_id=isp_b.id,
        plan_name=f"Current ISP B Review Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan",
        is_active=True,
        created_by_admin_id=None,
    )

    requested_plan_b = SubscriptionPlan(
        isp_id=isp_b.id,
        plan_name=f"Requested ISP B Review Plan {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=250,
        speed_limit_mbps=100,
        description="Requested plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([admin_a, user_b, current_plan_b, requested_plan_b])
    await integration_db.flush()

    subscription_b = UserSubscription(
        user_id=user_b.id,
        plan_id=current_plan_b.id,
        subscription_label="ISP B Subscription",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add(subscription_b)
    await integration_db.flush()

    change_request_b = SubscriptionChangeRequest(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        current_plan_id=current_plan_b.id,
        requested_plan_id=requested_plan_b.id,
        recommendation_id=None,
        request_type="upgrade",
        reason="ISP B user request.",
        status="pending",
    )

    integration_db.add(change_request_b)
    await integration_db.flush()

    invisible_request = await get_plan_change_request_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
        request_id=change_request_b.id,
    )

    assert invisible_request is None

    listed_requests = await list_plan_change_requests_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
    )

    assert change_request_b.id not in [request.id for request in listed_requests]
    assert subscription_b.plan_id == current_plan_b.id


@pytest.mark.asyncio
async def test_isp_admin_can_reject_plan_change_request_for_own_isp(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"Plan Reject ISP {suffix}",
        contact_email=f"plan-reject-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    admin = Admin(
        isp_id=isp.id,
        full_name="Plan Reject Admin",
        email=f"plan-reject-admin-{suffix}@example.com",
        username=f"plan_reject_admin_{suffix}",
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
        full_name="Plan Reject User",
        email=f"plan-reject-user-{suffix}@example.com",
        username=f"plan_reject_user_{suffix}",
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
        plan_name=f"Current Reject Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan",
        is_active=True,
        created_by_admin_id=None,
    )

    requested_plan = SubscriptionPlan(
        isp_id=isp.id,
        plan_name=f"Requested Reject Plan {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=250,
        speed_limit_mbps=100,
        description="Requested plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([admin, user, current_plan, requested_plan])
    await integration_db.flush()

    subscription = UserSubscription(
        user_id=user.id,
        plan_id=current_plan.id,
        subscription_label="Reject Subscription",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add(subscription)
    await integration_db.flush()

    change_request = SubscriptionChangeRequest(
        user_id=user.id,
        user_subscription_id=subscription.id,
        current_plan_id=current_plan.id,
        requested_plan_id=requested_plan.id,
        recommendation_id=None,
        request_type="upgrade",
        reason="Please upgrade me.",
        status="pending",
    )

    integration_db.add(change_request)
    await integration_db.flush()

    reviewed_request = await review_plan_change_request_for_isp(
        db=integration_db,
        change_request=change_request,
        current_admin=admin,
        request=ISPAdminPlanChangeRequestReviewRequest(
            decision="reject",
            admin_response="Rejected for now.",
        ),
    )

    assert reviewed_request is not None
    assert reviewed_request.status == "rejected"
    assert reviewed_request.reviewed_by_admin_id == admin.id
    assert reviewed_request.reviewed_at is not None
    assert reviewed_request.admin_response == "Rejected for now."
    assert subscription.plan_id == current_plan.id
