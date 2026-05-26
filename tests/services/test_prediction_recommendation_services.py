from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.services.app_user.prediction_service import get_my_prediction
from app.services.app_user.recommendation_service import get_my_recommendation
from app.services.predictions import generate_usage_prediction_for_subscription
from app.services.recommendations import (
    PredictionNotFoundForRecommendationError,
    generate_recommendation_for_prediction,
)


class FakeScalarResult:
    def __init__(self, value=None):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeOneResult:
    def __init__(self, value):
        self.value = value

    def one(self):
        return self.value


class FakeDb:
    def __init__(self, execute_values):
        self.execute_values = list(execute_values)
        self.statements = []
        self.added = []
        self.flush_called = False
        self.refreshed = []

    async def execute(self, stmt):
        self.statements.append(stmt)

        if not self.execute_values:
            raise AssertionError("Unexpected db.execute call")

        return self.execute_values.pop(0)

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        self.flush_called = True

    async def refresh(self, item):
        self.refreshed.append(item)


def _compiled_sql(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": False}))


def _compiled_params(stmt) -> set:
    compiled = stmt.compile(compile_kwargs={"literal_binds": False})
    return set(compiled.params.values())


@pytest.mark.asyncio
async def test_prediction_generation_calculates_full_cycle_usage():
    user_id = uuid4()
    subscription_id = uuid4()
    plan_id = uuid4()

    start_date = date.today() - timedelta(days=4)
    end_date = start_date + timedelta(days=9)
    prediction_date = date.today()

    subscription = SimpleNamespace(
        id=subscription_id,
        user_id=user_id,
        plan_id=plan_id,
        status="active",
        start_date=start_date,
        end_date=end_date,
        plan=SimpleNamespace(
            data_limit_gb=Decimal("50"),
        ),
    )

    usage_row = SimpleNamespace(
        total_mb=Decimal("10240"),
        record_count=5,
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(subscription),
            FakeOneResult(usage_row),
        ]
    )

    result = await generate_usage_prediction_for_subscription(
        db=db,
        user_subscription_id=subscription_id,
        prediction_date=prediction_date,
    )

    assert result.days_elapsed == 5
    assert result.total_cycle_days == 10
    assert result.observed_usage_gb == Decimal("10.00")
    assert result.average_daily_usage_gb == Decimal("2.00")

    prediction = result.prediction

    assert isinstance(prediction, Prediction)
    assert prediction.user_id == user_id
    assert prediction.user_subscription_id == subscription_id
    assert prediction.plan_id == plan_id
    assert prediction.predicted_usage_gb == Decimal("20.00")
    assert prediction.risk_level == "low"
    assert prediction.confidence_score == Decimal("0.68")
    assert prediction.model_version == "rule_based_v1"

    assert db.flush_called is True
    assert prediction in db.added
    assert prediction in db.refreshed


@pytest.mark.asyncio
async def test_recommendation_generation_stay_current_path():
    prediction_id = uuid4()
    user_id = uuid4()
    subscription_id = uuid4()
    current_plan_id = uuid4()

    current_plan = SimpleNamespace(
        id=current_plan_id,
        isp_id=uuid4(),
        plan_name="Current Plan",
        data_limit_gb=Decimal("100"),
    )

    prediction = SimpleNamespace(
        id=prediction_id,
        user_id=user_id,
        user_subscription_id=subscription_id,
        plan_id=current_plan_id,
        predicted_usage_gb=Decimal("70"),
        confidence_score=Decimal("0.80"),
        plan=current_plan,
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(prediction),
            FakeScalarResult(None),
        ]
    )

    result = await generate_recommendation_for_prediction(
        db=db,
        prediction_id=prediction_id,
    )

    assert result.created is True
    assert result.predicted_usage_gb == Decimal("70")
    assert result.current_plan_limit_gb == Decimal("100")
    assert result.recommended_plan_limit_gb is None

    recommendation = result.recommendation

    assert isinstance(recommendation, Recommendation)
    assert recommendation.user_id == user_id
    assert recommendation.user_subscription_id == subscription_id
    assert recommendation.current_plan_id == current_plan_id
    assert recommendation.recommendation_plan_id is None
    assert recommendation.prediction_id == prediction_id
    assert recommendation.recommendation_type == "stay_current"
    assert recommendation.confidence_score == Decimal("0.80")
    assert recommendation.status == "new"

    assert db.flush_called is True
    assert recommendation in db.added
    assert recommendation in db.refreshed


@pytest.mark.asyncio
async def test_recommendation_generation_upgrade_path():
    prediction_id = uuid4()
    user_id = uuid4()
    subscription_id = uuid4()
    current_plan_id = uuid4()
    recommended_plan_id = uuid4()
    isp_id = uuid4()

    current_plan = SimpleNamespace(
        id=current_plan_id,
        isp_id=isp_id,
        plan_name="Small Plan",
        data_limit_gb=Decimal("100"),
    )

    recommended_plan = SimpleNamespace(
        id=recommended_plan_id,
        isp_id=isp_id,
        plan_name="Bigger Plan",
        data_limit_gb=Decimal("150"),
        monthly_price=Decimal("20"),
    )

    prediction = SimpleNamespace(
        id=prediction_id,
        user_id=user_id,
        user_subscription_id=subscription_id,
        plan_id=current_plan_id,
        predicted_usage_gb=Decimal("120"),
        confidence_score=Decimal("0.75"),
        plan=current_plan,
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(prediction),
            FakeScalarResult(None),
            FakeScalarResult(recommended_plan),
        ]
    )

    result = await generate_recommendation_for_prediction(
        db=db,
        prediction_id=prediction_id,
    )

    assert result.created is True
    assert result.recommended_plan_limit_gb == Decimal("150")

    recommendation = result.recommendation

    assert recommendation.recommendation_type == "upgrade_plan"
    assert recommendation.recommendation_plan_id == recommended_plan_id
    assert "Upgrade to Bigger Plan." == recommendation.recommendation_text
    assert "recommends an upgrade" in recommendation.explanation


@pytest.mark.asyncio
async def test_recommendation_generation_returns_existing_new_recommendation():
    prediction_id = uuid4()
    existing_recommendation = SimpleNamespace(
        id=uuid4(),
        recommendation_plan_id=None,
    )

    current_plan = SimpleNamespace(
        id=uuid4(),
        isp_id=uuid4(),
        plan_name="Current Plan",
        data_limit_gb=Decimal("100"),
    )

    prediction = SimpleNamespace(
        id=prediction_id,
        user_id=uuid4(),
        user_subscription_id=uuid4(),
        plan_id=current_plan.id,
        predicted_usage_gb=Decimal("70"),
        confidence_score=Decimal("0.80"),
        plan=current_plan,
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(prediction),
            FakeScalarResult(existing_recommendation),
        ]
    )

    result = await generate_recommendation_for_prediction(
        db=db,
        prediction_id=prediction_id,
    )

    assert result.created is False
    assert result.recommendation == existing_recommendation
    assert db.added == []
    assert db.flush_called is False


@pytest.mark.asyncio
async def test_recommendation_generation_query_keeps_isp_scope():
    prediction_id = uuid4()
    isp_id = uuid4()

    db = FakeDb(
        execute_values=[
            FakeScalarResult(None),
        ]
    )

    with pytest.raises(PredictionNotFoundForRecommendationError):
        await generate_recommendation_for_prediction(
            db=db,
            prediction_id=prediction_id,
            isp_id=isp_id,
        )

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "JOIN app_users" in sql
    assert "predictions.user_id = app_users.id" in sql
    assert "app_users.isp_id" in sql
    assert prediction_id in params
    assert isp_id in params


@pytest.mark.asyncio
async def test_app_user_get_prediction_requires_current_user_id_and_prediction_id():
    user_id = uuid4()
    prediction_id = uuid4()
    current_user = SimpleNamespace(id=user_id)

    db = FakeDb(
        execute_values=[
            FakeScalarResult(None),
        ]
    )

    await get_my_prediction(
        db=db,
        current_user=current_user,
        prediction_id=prediction_id,
    )

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "predictions.id" in sql
    assert "predictions.user_id" in sql
    assert prediction_id in params
    assert user_id in params


@pytest.mark.asyncio
async def test_app_user_get_recommendation_requires_current_user_id_and_recommendation_id():
    user_id = uuid4()
    recommendation_id = uuid4()
    current_user = SimpleNamespace(id=user_id)

    db = FakeDb(
        execute_values=[
            FakeScalarResult(None),
        ]
    )

    await get_my_recommendation(
        db=db,
        current_user=current_user,
        recommendation_id=recommendation_id,
    )

    stmt = db.statements[0]
    sql = _compiled_sql(stmt)
    params = _compiled_params(stmt)

    assert "recommendations.id" in sql
    assert "recommendations.user_id" in sql
    assert recommendation_id in params
    assert user_id in params


@pytest.mark.asyncio
async def test_recommendation_generation_downgrade_path():
    prediction_id = uuid4()
    user_id = uuid4()
    subscription_id = uuid4()
    current_plan_id = uuid4()
    recommended_plan_id = uuid4()
    isp_id = uuid4()

    current_plan = SimpleNamespace(
        id=current_plan_id,
        isp_id=isp_id,
        plan_name="Large Plan",
        data_limit_gb=Decimal("100"),
    )

    recommended_plan = SimpleNamespace(
        id=recommended_plan_id,
        isp_id=isp_id,
        plan_name="Smaller Plan",
        data_limit_gb=Decimal("50"),
        monthly_price=Decimal("10"),
    )

    prediction = SimpleNamespace(
        id=prediction_id,
        user_id=user_id,
        user_subscription_id=subscription_id,
        plan_id=current_plan_id,
        predicted_usage_gb=Decimal("40"),
        confidence_score=Decimal("0.72"),
        plan=current_plan,
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(prediction),
            FakeScalarResult(None),
            FakeScalarResult(recommended_plan),
        ]
    )

    result = await generate_recommendation_for_prediction(
        db=db,
        prediction_id=prediction_id,
    )

    assert result.created is True
    assert result.recommended_plan_limit_gb == Decimal("50")

    recommendation = result.recommendation

    assert isinstance(recommendation, Recommendation)
    assert recommendation.user_id == user_id
    assert recommendation.user_subscription_id == subscription_id
    assert recommendation.current_plan_id == current_plan_id
    assert recommendation.recommendation_plan_id == recommended_plan_id
    assert recommendation.prediction_id == prediction_id
    assert recommendation.recommendation_type == "downgrade_plan"
    assert recommendation.recommendation_text == "Consider switching to Smaller Plan."
    assert recommendation.confidence_score == Decimal("0.72")
    assert recommendation.status == "new"


@pytest.mark.asyncio
async def test_recommendation_generation_monitor_usage_when_no_upgrade_plan_exists():
    prediction_id = uuid4()
    user_id = uuid4()
    subscription_id = uuid4()
    current_plan_id = uuid4()
    isp_id = uuid4()

    current_plan = SimpleNamespace(
        id=current_plan_id,
        isp_id=isp_id,
        plan_name="Current Plan",
        data_limit_gb=Decimal("100"),
    )

    prediction = SimpleNamespace(
        id=prediction_id,
        user_id=user_id,
        user_subscription_id=subscription_id,
        plan_id=current_plan_id,
        predicted_usage_gb=Decimal("130"),
        confidence_score=Decimal("0.81"),
        plan=current_plan,
    )

    db = FakeDb(
        execute_values=[
            FakeScalarResult(prediction),
            FakeScalarResult(None),
            FakeScalarResult(None),
        ]
    )

    result = await generate_recommendation_for_prediction(
        db=db,
        prediction_id=prediction_id,
    )

    assert result.created is True
    assert result.recommended_plan_limit_gb is None

    recommendation = result.recommendation

    assert isinstance(recommendation, Recommendation)
    assert recommendation.user_id == user_id
    assert recommendation.user_subscription_id == subscription_id
    assert recommendation.current_plan_id == current_plan_id
    assert recommendation.recommendation_plan_id is None
    assert recommendation.prediction_id == prediction_id
    assert recommendation.recommendation_type == "monitor_usage"
    assert recommendation.recommendation_text == "Monitor your usage closely."
    assert recommendation.confidence_score == Decimal("0.81")
    assert recommendation.status == "new"
