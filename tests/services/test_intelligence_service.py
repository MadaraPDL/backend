from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

import app.services.isp_admin.intelligence_service as intelligence_service
from app.services.isp_admin.intelligence_service import run_intelligence_for_isp


@pytest.mark.asyncio
async def test_run_intelligence_for_isp_generates_prediction_recommendation_and_alerts(
    monkeypatch,
):
    isp_id = uuid4()
    subscription_id = uuid4()
    router_id = uuid4()
    prediction_id = uuid4()
    recommendation_id = uuid4()
    seen_prediction_isp_ids: list[object] = []
    seen_recommendation_isp_ids: list[object] = []

    async def fake_list_active_subscription_ids_for_isp(db, isp_id):
        return [subscription_id]

    async def fake_get_latest_usage_window_for_subscription(db, subscription_id):
        return (
            datetime(2026, 5, 26, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 5, 26, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 5, 26, 10, 1, tzinfo=timezone.utc),
        )

    async def fake_generate_usage_alerts_for_subscription(**kwargs):
        assert kwargs["user_subscription_id"] == subscription_id
        return SimpleNamespace(alerts_created=1)

    async def fake_list_router_ids_for_subscription(db, subscription_id, isp_id):
        assert subscription_id is not None
        assert isp_id is not None
        return [router_id]

    async def fake_generate_new_device_alerts_for_router(**kwargs):
        assert kwargs["router_id"] == router_id
        return SimpleNamespace(new_device_alerts_created=1)

    async def fake_get_existing_prediction_for_today(db, subscription_id):
        return None

    async def fake_generate_usage_prediction_for_subscription(**kwargs):
        seen_prediction_isp_ids.append(kwargs["isp_id"])
        return SimpleNamespace(prediction=SimpleNamespace(id=prediction_id))

    async def fake_get_existing_recommendation_for_prediction(db, prediction_id):
        return None

    async def fake_generate_recommendation_for_prediction(**kwargs):
        seen_recommendation_isp_ids.append(kwargs["isp_id"])
        return SimpleNamespace(
            recommendation=SimpleNamespace(id=recommendation_id),
            created=True,
        )

    monkeypatch.setattr(
        intelligence_service,
        "list_active_subscription_ids_for_isp",
        fake_list_active_subscription_ids_for_isp,
    )
    monkeypatch.setattr(
        intelligence_service,
        "get_latest_usage_window_for_subscription",
        fake_get_latest_usage_window_for_subscription,
    )
    monkeypatch.setattr(
        intelligence_service,
        "generate_usage_alerts_for_subscription",
        fake_generate_usage_alerts_for_subscription,
    )
    monkeypatch.setattr(
        intelligence_service,
        "list_router_ids_for_subscription",
        fake_list_router_ids_for_subscription,
    )
    monkeypatch.setattr(
        intelligence_service,
        "generate_new_device_alerts_for_router",
        fake_generate_new_device_alerts_for_router,
    )
    monkeypatch.setattr(
        intelligence_service,
        "get_existing_prediction_for_today",
        fake_get_existing_prediction_for_today,
    )
    monkeypatch.setattr(
        intelligence_service,
        "generate_usage_prediction_for_subscription",
        fake_generate_usage_prediction_for_subscription,
    )
    monkeypatch.setattr(
        intelligence_service,
        "get_existing_recommendation_for_prediction",
        fake_get_existing_recommendation_for_prediction,
    )
    monkeypatch.setattr(
        intelligence_service,
        "generate_recommendation_for_prediction",
        fake_generate_recommendation_for_prediction,
    )

    result = await run_intelligence_for_isp(db=SimpleNamespace(), isp_id=isp_id)

    assert result.subscriptions_checked == 1
    assert result.predictions_created == 1
    assert result.recommendations_created == 1
    assert result.alerts_created == 2
    assert result.items[0].alerts_created == 2
    assert seen_prediction_isp_ids == [isp_id]
    assert seen_recommendation_isp_ids == [isp_id]
