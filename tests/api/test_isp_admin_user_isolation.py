from types import SimpleNamespace
from uuid import uuid4

from app.api.dependencies import get_current_isp_admin
import app.api.v1.endpoints.isp_admin.users as users_endpoint
from app.main import app


def _fake_admin():
    return SimpleNamespace(id=uuid4(), isp_id=uuid4())


def test_isp_admin_user_list_passes_current_isp_scope(api_client, monkeypatch):
    admin = _fake_admin()
    seen = {}

    async def override_current_admin():
        return admin

    async def fake_list_app_users_for_isp(*, db, isp_id, status, limit, offset):
        seen["isp_id"] = isp_id
        seen["status"] = status
        seen["limit"] = limit
        seen["offset"] = offset
        return []

    app.dependency_overrides[get_current_isp_admin] = override_current_admin
    monkeypatch.setattr(
        users_endpoint,
        "list_app_users_for_isp",
        fake_list_app_users_for_isp,
    )

    response = api_client.get("/api/v1/isp-admin/users?status=active")

    assert response.status_code == 200
    assert response.json() == []
    assert seen == {
        "isp_id": admin.isp_id,
        "status": "active",
        "limit": 50,
        "offset": 0,
    }


def test_isp_admin_user_detail_returns_404_for_non_owned_user(api_client, monkeypatch):
    admin = _fake_admin()
    requested_user_id = uuid4()
    seen = {}

    async def override_current_admin():
        return admin

    async def fake_get_app_user_for_isp(*, db, isp_id, user_id):
        seen["isp_id"] = isp_id
        seen["user_id"] = user_id
        return None

    app.dependency_overrides[get_current_isp_admin] = override_current_admin
    monkeypatch.setattr(
        users_endpoint,
        "get_app_user_for_isp",
        fake_get_app_user_for_isp,
    )

    response = api_client.get(f"/api/v1/isp-admin/users/{requested_user_id}")

    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "not_found"
    assert body["message"] == "App User not found"
    assert seen == {
        "isp_id": admin.isp_id,
        "user_id": requested_user_id,
    }
