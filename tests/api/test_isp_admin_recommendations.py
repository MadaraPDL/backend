from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.api.dependencies import get_current_isp_admin
from app.api.dependencies.current_account import CurrentAccount, get_current_account
import app.api.v1.endpoints.isp_admin.recommendations as recommendations_endpoint
from app.main import app


def _fake_recommendation(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "user_subscription_id": uuid4(),
        "current_plan_id": uuid4(),
        "recommendation_plan_id": uuid4(),
        "prediction_id": uuid4(),
        "recommendation_type": "upgrade_plan",
        "recommendation_text": "Upgrade recommended.",
        "reason": "Predicted usage is over the current plan.",
        "confidence_score": Decimal("0.90"),
        "status": "new",
        "created_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_isp_admin_recommendation_list_uses_current_isp_scope(
    api_client,
    monkeypatch,
):
    admin = SimpleNamespace(id=uuid4(), role="isp_admin", isp_id=uuid4())
    user_id = uuid4()
    subscription_id = uuid4()
    recommendation = _fake_recommendation(
        user_id=user_id,
        user_subscription_id=subscription_id,
    )
    seen = {}

    async def override_current_admin():
        return admin

    async def fake_list_recommendations_for_isp(
        *,
        db,
        isp_id,
        status,
        user_id,
        subscription_id,
        limit,
        offset,
    ):
        seen.update(
            {
                "isp_id": isp_id,
                "status": status,
                "user_id": user_id,
                "subscription_id": subscription_id,
                "limit": limit,
                "offset": offset,
            }
        )
        return [recommendation]

    app.dependency_overrides[get_current_isp_admin] = override_current_admin
    monkeypatch.setattr(
        recommendations_endpoint,
        "list_recommendations_for_isp",
        fake_list_recommendations_for_isp,
    )

    response = api_client.get(
        "/api/v1/isp-admin/recommendations",
        params={
            "status": "new",
            "user_id": str(user_id),
            "subscription_id": str(subscription_id),
            "limit": 25,
            "offset": 5,
        },
    )

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(recommendation.id)
    assert seen == {
        "isp_id": admin.isp_id,
        "status": "new",
        "user_id": user_id,
        "subscription_id": subscription_id,
        "limit": 25,
        "offset": 5,
    }


def test_isp_admin_recommendation_detail_returns_404_for_non_owned_recommendation(
    api_client,
    monkeypatch,
):
    admin = SimpleNamespace(id=uuid4(), role="isp_admin", isp_id=uuid4())
    requested_recommendation_id = uuid4()
    seen = {}

    async def override_current_admin():
        return admin

    async def fake_get_recommendation_for_isp(*, db, isp_id, recommendation_id):
        seen["isp_id"] = isp_id
        seen["recommendation_id"] = recommendation_id
        return None

    app.dependency_overrides[get_current_isp_admin] = override_current_admin
    monkeypatch.setattr(
        recommendations_endpoint,
        "get_recommendation_for_isp",
        fake_get_recommendation_for_isp,
    )

    response = api_client.get(
        f"/api/v1/isp-admin/recommendations/{requested_recommendation_id}"
    )

    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "not_found"
    assert body["message"] == "Recommendation not found"
    assert seen == {
        "isp_id": admin.isp_id,
        "recommendation_id": requested_recommendation_id,
    }


def test_platform_admin_cannot_access_isp_admin_recommendations(api_client):
    async def override_current_platform_admin():
        return CurrentAccount(
            account_type="admin",
            account=SimpleNamespace(
                id=uuid4(),
                role="platform_admin",
                isp_id=None,
                status="active",
            ),
        )

    app.dependency_overrides[get_current_account] = override_current_platform_admin

    response = api_client.get("/api/v1/isp-admin/recommendations")

    assert response.status_code == 403
    assert response.json()["error"] == "forbidden"


def test_app_user_cannot_access_isp_admin_recommendations(api_client):
    async def override_current_app_user():
        return CurrentAccount(
            account_type="app_user",
            account=SimpleNamespace(
                id=uuid4(),
                role=None,
                isp_id=uuid4(),
                status="active",
            ),
        )

    app.dependency_overrides[get_current_account] = override_current_app_user

    response = api_client.get("/api/v1/isp-admin/recommendations")

    assert response.status_code == 403
    assert response.json()["error"] == "forbidden"
