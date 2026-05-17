from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException, status

import app.api.v1.endpoints.isp_admin.user_invitations as user_invitation_endpoint
import app.api.v1.endpoints.platform_admin.admin_invitations as admin_invitation_endpoint
from app.api.dependencies import get_current_admin, get_current_isp_admin
from app.main import app


async def override_platform_admin():
    return SimpleNamespace(
        id=uuid4(),
        role="platform_admin",
        isp_id=None,
    )


async def override_isp_admin():
    return SimpleNamespace(
        id=uuid4(),
        role="isp_admin",
        isp_id=uuid4(),
    )


def invitation_payload():
    return {
        "email": "newuser@test.com",
        "full_name": "New User",
        "expires_in_days": 7,
    }


def raise_email_delivery_error():
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Email delivery is not configured.",
    )


def test_platform_admin_invitation_blocks_without_email_delivery(api_client, monkeypatch):
    isp_id = uuid4()

    app.dependency_overrides[get_current_admin] = override_platform_admin

    async def fake_get_isp_by_id(*args, **kwargs):
        return SimpleNamespace(
            id=isp_id,
            status="active",
        )

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    async def fake_create_invitation(*args, **kwargs):
        raise AssertionError("Invitation token should not be created when email delivery is blocked.")

    monkeypatch.setattr(
        admin_invitation_endpoint,
        "get_isp_by_id",
        fake_get_isp_by_id,
    )

    monkeypatch.setattr(
        admin_invitation_endpoint,
        "get_account_by_identifier",
        fake_get_account_by_identifier,
    )

    monkeypatch.setattr(
        admin_invitation_endpoint,
        "get_pending_isp_admin_invitation",
        fake_get_pending_invitation,
    )

    monkeypatch.setattr(
        admin_invitation_endpoint,
        "require_email_delivery_for_production",
        raise_email_delivery_error,
    )

    monkeypatch.setattr(
        admin_invitation_endpoint,
        "create_isp_admin_invitation",
        fake_create_invitation,
    )

    response = api_client.post(
        f"/api/v1/platform-admin/isps/{isp_id}/admin-invitations",
        json=invitation_payload(),
    )

    assert response.status_code == 503
    assert "Email delivery is not configured" in response.json()["message"]


def test_isp_admin_user_invitation_blocks_without_email_delivery(api_client, monkeypatch):
    app.dependency_overrides[get_current_isp_admin] = override_isp_admin

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    async def fake_create_invitation(*args, **kwargs):
        raise AssertionError("Invitation token should not be created when email delivery is blocked.")

    monkeypatch.setattr(
        user_invitation_endpoint,
        "get_account_by_identifier",
        fake_get_account_by_identifier,
    )

    monkeypatch.setattr(
        user_invitation_endpoint,
        "get_pending_app_user_invitation",
        fake_get_pending_invitation,
    )

    monkeypatch.setattr(
        user_invitation_endpoint,
        "require_email_delivery_for_production",
        raise_email_delivery_error,
    )

    monkeypatch.setattr(
        user_invitation_endpoint,
        "create_app_user_invitation",
        fake_create_invitation,
    )

    response = api_client.post(
        "/api/v1/isp-admin/user-invitations",
        json=invitation_payload(),
    )

    assert response.status_code == 503
    assert "Email delivery is not configured" in response.json()["message"]

