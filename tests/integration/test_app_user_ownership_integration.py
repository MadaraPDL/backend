from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.security import hash_password
from app.models.alert import Alert
from app.models.app_user import AppUser
from app.models.isp import ISP
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.services.app_user.alert_service import get_my_alert
from app.services.app_user.prediction_service import get_my_prediction
from app.services.app_user.recommendation_service import get_my_recommendation


@pytest.mark.asyncio
async def test_app_user_cannot_read_other_users_alert_prediction_or_recommendation(
    integration_db,
):
    suffix = uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    today = date.today()

    isp = ISP(
        name=f"App User Ownership ISP {suffix}",
        contact_email=f"ownership-isp-{suffix}@example.com",
        status="active",
    )

    integration_db.add(isp)
    await integration_db.flush()

    user_a = AppUser(
        isp_id=isp.id,
        full_name="User A",
        email=f"user-a-{suffix}@example.com",
        username=f"user_a_{suffix}",
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
        full_name="User B",
        email=f"user-b-{suffix}@example.com",
        username=f"user_b_{suffix}",
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
        plan_name=f"Ownership Plan {suffix}",
        monthly_price=Decimal("30.00"),
        data_limit_gb=150,
        speed_limit_mbps=80,
        description="Shared test plan",
        is_active=True,
        created_by_admin_id=None,
    )

    integration_db.add_all([user_a, user_b, plan])
    await integration_db.flush()

    subscription_b = UserSubscription(
        user_id=user_b.id,
        plan_id=plan.id,
        subscription_label="User B Subscription",
        assigned_by_admin_id=None,
        start_date=today,
        end_date=None,
        status="active",
        auto_renew=True,
    )

    integration_db.add(subscription_b)
    await integration_db.flush()

    prediction_b = Prediction(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        plan_id=plan.id,
        prediction_date=today,
        period_start=today,
        period_end=today,
        predicted_usage_gb=Decimal("75.5"),
        confidence_score=Decimal("0.85"),
        risk_level="low",
        model_version="integration-test",
    )

    integration_db.add(prediction_b)
    await integration_db.flush()

    alert_b = Alert(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        prediction_id=prediction_b.id,
        alert_type="high_usage",
        severity="low",
        title="User B Alert",
        message="This alert belongs to User B.",
        status="unread",
    )

    recommendation_b = Recommendation(
        user_id=user_b.id,
        user_subscription_id=subscription_b.id,
        current_plan_id=plan.id,
        recommendation_plan_id=plan.id,
        prediction_id=prediction_b.id,
        recommendation_type="upgrade_plan",
        recommendation_text="This recommendation belongs to User B.",
        reason="Integration ownership test",
        confidence_score=Decimal("0.90"),
        status="new",
    )

    integration_db.add_all([alert_b, recommendation_b])
    await integration_db.flush()

    assert await get_my_alert(
        db=integration_db,
        current_user=user_a,
        alert_id=alert_b.id,
    ) is None

    assert await get_my_prediction(
        db=integration_db,
        current_user=user_a,
        prediction_id=prediction_b.id,
    ) is None

    assert await get_my_recommendation(
        db=integration_db,
        current_user=user_a,
        recommendation_id=recommendation_b.id,
    ) is None
