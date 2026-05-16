from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.core.security import hash_password
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.models.recommendation import Recommendation
from app.models.subscription_change_request import SubscriptionChangeRequest
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.schemas.app_user import MyRecommendationPlanChangeRequestCreate
from app.services.app_user.plan_change_request_service import (
    create_my_plan_change_request_from_recommendation,
)


@pytest.mark.asyncio
async def test_app_user_can_create_plan_change_request_from_upgrade_recommendation(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"Recommendation Request ISP {suffix}",
        contact_email=f"recommendation-request-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    user = AppUser(
        isp_id=isp.id,
        full_name="Recommendation Request User",
        email=f"recommendation-request-user-{suffix}@example.com",
        username=f"recommendation_request_user_{suffix}",
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
        plan_name=f"Current Recommendation Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan",
        is_active=True,
        created_by_admin_id=None,
    )

    recommended_plan = SubscriptionPlan(
        isp_id=isp.id,
        plan_name=f"Recommended Upgrade Plan {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=250,
        speed_limit_mbps=100,
        description="Recommended upgrade plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([user, current_plan, recommended_plan])
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

    recommendation = Recommendation(
        user_id=user.id,
        user_subscription_id=subscription.id,
        current_plan_id=current_plan.id,
        recommendation_plan_id=recommended_plan.id,
        prediction_id=None,
        recommendation_type="upgrade_plan",
        recommendation_text="Upgrade to avoid exceeding your current plan.",
        reason="Predicted usage is higher than the current plan limit.",
        confidence_score=Decimal("90.00"),
        status="new",
    )

    integration_db.add(recommendation)
    await integration_db.flush()

    change_request = await create_my_plan_change_request_from_recommendation(
        db=integration_db,
        current_user=user,
        recommendation_id=recommendation.id,
        data=MyRecommendationPlanChangeRequestCreate(
            reason="I want to request the recommended upgrade.",
        ),
    )

    assert change_request is not None
    assert change_request.user_id == user.id
    assert change_request.user_subscription_id == subscription.id
    assert change_request.current_plan_id == current_plan.id
    assert change_request.requested_plan_id == recommended_plan.id
    assert change_request.recommendation_id == recommendation.id
    assert change_request.request_type == "upgrade"
    assert change_request.status == "pending"
    assert recommendation.status == "accepted"

    duplicate_request = await create_my_plan_change_request_from_recommendation(
        db=integration_db,
        current_user=user,
        recommendation_id=recommendation.id,
        data=MyRecommendationPlanChangeRequestCreate(
            reason="Trying to request the same recommendation again.",
        ),
    )

    assert duplicate_request is None

    request_rows = await integration_db.execute(
        select(SubscriptionChangeRequest).where(
            SubscriptionChangeRequest.recommendation_id == recommendation.id,
        )
    )

    assert len(list(request_rows.scalars().all())) == 1


@pytest.mark.asyncio
async def test_app_user_cannot_create_plan_change_request_from_non_plan_recommendation(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"Non Plan Recommendation ISP {suffix}",
        contact_email=f"non-plan-recommendation-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    user = AppUser(
        isp_id=isp.id,
        full_name="Non Plan Recommendation User",
        email=f"non-plan-recommendation-user-{suffix}@example.com",
        username=f"non_plan_recommendation_user_{suffix}",
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
        plan_name=f"Non Plan Current Plan {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=100,
        speed_limit_mbps=50,
        description="Current plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([user, current_plan])
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

    recommendation = Recommendation(
        user_id=user.id,
        user_subscription_id=subscription.id,
        current_plan_id=current_plan.id,
        recommendation_plan_id=None,
        prediction_id=None,
        recommendation_type="monitor_usage",
        recommendation_text="Monitor your usage for now.",
        reason="No plan change is needed.",
        confidence_score=Decimal("80.00"),
        status="new",
    )

    integration_db.add(recommendation)
    await integration_db.flush()

    change_request = await create_my_plan_change_request_from_recommendation(
        db=integration_db,
        current_user=user,
        recommendation_id=recommendation.id,
        data=MyRecommendationPlanChangeRequestCreate(reason=None),
    )

    assert change_request is None
    assert recommendation.status == "new"
