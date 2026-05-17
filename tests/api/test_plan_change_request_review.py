from types import SimpleNamespace
from uuid import uuid4

from app.api.dependencies import get_current_isp_admin
import app.api.v1.endpoints.isp_admin.plan_change_requests as endpoint
from app.main import app
from app.services.isp_admin import StalePlanChangeRequestApprovalError


def test_stale_plan_change_request_review_returns_conflict(api_client, monkeypatch):
    admin = SimpleNamespace(id=uuid4(), isp_id=uuid4())

    async def override_current_admin():
        return admin

    async def fake_get_plan_change_request_for_isp(*args, **kwargs):
        return SimpleNamespace(status="pending")

    async def fake_review_plan_change_request_for_isp(*args, **kwargs):
        raise StalePlanChangeRequestApprovalError(
            "Subscription plan changed after this request was created."
        )

    app.dependency_overrides[get_current_isp_admin] = override_current_admin
    monkeypatch.setattr(
        endpoint,
        "get_plan_change_request_for_isp",
        fake_get_plan_change_request_for_isp,
    )
    monkeypatch.setattr(
        endpoint,
        "review_plan_change_request_for_isp",
        fake_review_plan_change_request_for_isp,
    )

    response = api_client.patch(
        f"/api/v1/isp-admin/plan-change-requests/{uuid4()}/review",
        json={"decision": "approve"},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["error"] == "conflict"
    assert "Subscription plan changed" in body["message"]
