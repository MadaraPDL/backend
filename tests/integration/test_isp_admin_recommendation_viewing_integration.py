from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.services.isp_admin import (
    get_recommendation_for_isp,
    list_recommendations_for_isp,
)


@pytest.mark.asyncio
async def test_isp_admin_can_list_and_view_own_isp_recommendations(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp_a = ISP(
        name=f"Recommendation ISP A {suffix}",
        contact_email=f"recommendation-isp-a-{suffix}@example.com",
        status="active",
    )
    isp_b = ISP(
        name=f"Recommendation ISP B {suffix}",
        contact_email=f"recommendation-isp-b-{suffix}@example.com",
        status="active",
    )

    integration_db.add_all([isp_a, isp_b])
    await integration_db.flush()

    user_a = AppUser(
        isp_id=isp_a.id,
        full_name="Recommendation User A",
        email=f"recommendation-user-a-{suffix}@example.com",
        username=f"recommendation_user_a_{suffix}",
        password_hash=hash_password("CorrectHorseBatteryStaple123!"),
        status="active",
        email_verified_at=now,
        password_changed_at=now,
        mfa_enabled=False,
        mfa_required=False,
        preferred_mfa_method="email",
    )
    user_b = AppUser(
        isp_id=isp_b.id,
        full_name="Recommendation User B",
        email=f"recommendation-user-b-{suffix}@example.com",
        username=f"recommendation_user_b_{suffix}",
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

    plan_a_current = SubscriptionPlan(
        isp_id=isp_a.id,
        plan_name=f"Recommendation Current Plan A {suffix}",
        monthly_price=Decimal("25.00"),
        data_limit_gb=Decimal("100.00"),
        speed_limit_mbps=50,
        description="Current plan A",
        is_active=True,
        created_by_admin_id=None,
    )
    plan_a_recommended = SubscriptionPlan(
        isp_id=isp_a.id,
        plan_name=f"Recommendation Upgrade Plan A {suffix}",
        monthly_price=Decimal("40.00"),
        data_limit_gb=Decimal("250.00"),
        speed_limit_mbps=100,
        description="Recommended plan A",
        is_active=True,
        created_by_admin_id=None,
    )
    plan_b = SubscriptionPlan(
        isp_id=isp_b.id,
        plan_name=f"Recommendation Plan B {suffix}",
        monthly_price=Decimal("30.00"),
        data_limit_gb=Decimal("150.00"),
        speed_limit_mbps=75,
        description="Plan B",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([plan_a_current, plan_a_recommended, plan_b])
    await integration_db.flush()

    subscription_a = UserSubscription(
        user_id=user_a.id,
        plan_id=plan_a_current.id,
        subscription_label="Recommendation Subscription A",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )
    subscription_b = UserSubscription(
        user_id=user_b.id,
        plan_id=plan_b.id,
        subscription_label="Recommendation Subscription B",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add_all([subscription_a, subscription_b])
    await integration_db.flush()

    prediction_a = Prediction(
        user_id=user_a.id,
        user_subscription_id=subscription_a.id,
        plan_id=plan_a_current.id,
        prediction_date=today,
        period_start=today,
        period_end=today,
        predicted_usage_gb=Decimal("140.00"),
        confidence_score=Decimal("0.90"),
        risk_level="high",
        model_version="integration-test",
    )
    prediction_b = Prediction(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        plan_id=plan_b.id,
        prediction_date=today,
        period_start=today,
        period_end=today,
        predicted_usage_gb=Decimal("50.00"),
        confidence_score=Decimal("0.80"),
        risk_level="low",
        model_version="integration-test",
    )

    integration_db.add_all([prediction_a, prediction_b])
    await integration_db.flush()

    recommendation_a = Recommendation(
        user_id=user_a.id,
        user_subscription_id=subscription_a.id,
        current_plan_id=plan_a_current.id,
        recommendation_plan_id=plan_a_recommended.id,
        prediction_id=prediction_a.id,
        recommendation_type="upgrade_plan",
        recommendation_text="Upgrade recommended.",
        reason="Predicted usage is over the current plan.",
        confidence_score=Decimal("0.90"),
        status="new",
    )
    recommendation_b = Recommendation(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        current_plan_id=plan_b.id,
        recommendation_plan_id=None,
        prediction_id=prediction_b.id,
        recommendation_type="stay_current",
        recommendation_text="Stay current.",
        reason="Other ISP recommendation.",
        confidence_score=Decimal("0.80"),
        status="new",
    )

    integration_db.add_all([recommendation_a, recommendation_b])
    await integration_db.flush()

    recommendations = await list_recommendations_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
    )

    assert [recommendation.id for recommendation in recommendations] == [
        recommendation_a.id
    ]

    filtered_recommendations = await list_recommendations_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
        status="new",
        user_id=user_a.id,
        subscription_id=subscription_a.id,
    )

    assert [recommendation.id for recommendation in filtered_recommendations] == [
        recommendation_a.id
    ]

    fetched_recommendation = await get_recommendation_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
        recommendation_id=recommendation_a.id,
    )

    assert fetched_recommendation is not None
    assert fetched_recommendation.id == recommendation_a.id

    non_owned_recommendation = await get_recommendation_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
        recommendation_id=recommendation_b.id,
    )

    assert non_owned_recommendation is None

    fake_recommendation = await get_recommendation_for_isp(
        db=integration_db,
        isp_id=isp_a.id,
        recommendation_id=uuid4(),
    )

    assert fake_recommendation is None
