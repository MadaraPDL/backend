from datetime import datetime, timedelta, timezone
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


def fake_invitation(
    *,
    email="newuser@test.com",
    full_name="New User",
    account_type="app_user",
    admin_role=None,
    isp_id=None,
    invited_by_admin_id=None,
    expires_in_days=7,
):
    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        id=uuid4(),
        email=email,
        full_name=full_name,
        account_type=account_type,
        admin_role=admin_role,
        isp_id=isp_id,
        invited_by_admin_id=invited_by_admin_id,
        expires_at=now + timedelta(days=expires_in_days),
        accepted_at=None,
        revoked_at=None,
        created_at=now,
    )


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
        raise AssertionError(
            "Invitation token should not be created when email delivery is blocked."
        )

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
        raise AssertionError(
            "Invitation token should not be created when email delivery is blocked."
        )

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


def test_platform_admin_invitation_sends_email_without_returning_token_in_production(
    api_client,
    monkeypatch,
):
    isp_id = uuid4()
    platform_admin_id = uuid4()
    sent_email = {}

    async def override_admin():
        return SimpleNamespace(
            id=platform_admin_id,
            role="platform_admin",
            isp_id=None,
        )

    async def fake_get_isp_by_id(*args, **kwargs):
        return SimpleNamespace(
            id=isp_id,
            name="Demo ISP",
            status="active",
        )

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    def fake_require_email_delivery():
        return None

    async def fake_create_invitation(*args, **kwargs):
        return (
            fake_invitation(
                account_type="admin",
                admin_role="isp_admin",
                isp_id=isp_id,
                invited_by_admin_id=platform_admin_id,
            ),
            "raw-platform-token",
        )

    async def fake_send_isp_admin_invitation_email(**kwargs):
        sent_email.update(kwargs)

    app.dependency_overrides[get_current_admin] = override_admin
    monkeypatch.setattr(admin_invitation_endpoint, "settings", SimpleNamespace(DEBUG=False))
    monkeypatch.setattr(admin_invitation_endpoint, "get_isp_by_id", fake_get_isp_by_id)
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
        fake_require_email_delivery,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "create_isp_admin_invitation",
        fake_create_invitation,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "send_isp_admin_invitation_email",
        fake_send_isp_admin_invitation_email,
    )

    response = api_client.post(
        f"/api/v1/platform-admin/isps/{isp_id}/admin-invitations",
        json=invitation_payload(),
    )

    assert response.status_code == 201
    assert sent_email == {
        "to_email": "newuser@test.com",
        "full_name": "New User",
        "isp_name": "Demo ISP",
        "raw_token": "raw-platform-token",
        "expires_in_days": 7,
    }
    assert "dev_invitation_token" not in response.json()


def test_platform_admin_invitation_uses_debug_origin_for_email_link(
    api_client,
    monkeypatch,
):
    isp_id = uuid4()
    platform_admin_id = uuid4()
    sent_email = {}

    async def override_admin():
        return SimpleNamespace(
            id=platform_admin_id,
            role="platform_admin",
            isp_id=None,
        )

    async def fake_get_isp_by_id(*args, **kwargs):
        return SimpleNamespace(
            id=isp_id,
            name="Demo ISP",
            status="active",
        )

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    def fake_require_email_delivery():
        return None

    async def fake_create_invitation(*args, **kwargs):
        return (
            fake_invitation(
                account_type="admin",
                admin_role="isp_admin",
                isp_id=isp_id,
                invited_by_admin_id=platform_admin_id,
            ),
            "raw-platform-token",
        )

    async def fake_send_isp_admin_invitation_email(**kwargs):
        sent_email.update(kwargs)

    app.dependency_overrides[get_current_admin] = override_admin
    monkeypatch.setattr(admin_invitation_endpoint, "settings", SimpleNamespace(DEBUG=True))
    monkeypatch.setattr(admin_invitation_endpoint, "get_isp_by_id", fake_get_isp_by_id)
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
        fake_require_email_delivery,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "create_isp_admin_invitation",
        fake_create_invitation,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "send_isp_admin_invitation_email",
        fake_send_isp_admin_invitation_email,
    )

    response = api_client.post(
        f"/api/v1/platform-admin/isps/{isp_id}/admin-invitations",
        json=invitation_payload(),
        headers={"Origin": "http://192.168.1.10:5173"},
    )

    assert response.status_code == 201
    assert sent_email["frontend_base_url"] == "http://192.168.1.10:5173"


def test_platform_admin_invitation_does_not_pass_frontend_base_without_origin(
    api_client,
    monkeypatch,
):
    isp_id = uuid4()
    platform_admin_id = uuid4()
    sent_email = {}

    async def override_admin():
        return SimpleNamespace(
            id=platform_admin_id,
            role="platform_admin",
            isp_id=None,
        )

    async def fake_get_isp_by_id(*args, **kwargs):
        return SimpleNamespace(
            id=isp_id,
            name="Demo ISP",
            status="active",
        )

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    def fake_require_email_delivery():
        return None

    async def fake_create_invitation(*args, **kwargs):
        return (
            fake_invitation(
                account_type="admin",
                admin_role="isp_admin",
                isp_id=isp_id,
                invited_by_admin_id=platform_admin_id,
            ),
            "raw-platform-token",
        )

    async def fake_send_isp_admin_invitation_email(**kwargs):
        sent_email.update(kwargs)

    app.dependency_overrides[get_current_admin] = override_admin
    monkeypatch.setattr(admin_invitation_endpoint, "settings", SimpleNamespace(DEBUG=True))
    monkeypatch.setattr(admin_invitation_endpoint, "get_isp_by_id", fake_get_isp_by_id)
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
        fake_require_email_delivery,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "create_isp_admin_invitation",
        fake_create_invitation,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "send_isp_admin_invitation_email",
        fake_send_isp_admin_invitation_email,
    )

    response = api_client.post(
        f"/api/v1/platform-admin/isps/{isp_id}/admin-invitations",
        json=invitation_payload(),
    )

    assert response.status_code == 201
    assert "frontend_base_url" not in sent_email


def test_platform_admin_invitation_ignores_origin_in_production(
    api_client,
    monkeypatch,
):
    isp_id = uuid4()
    platform_admin_id = uuid4()
    sent_email = {}

    async def override_admin():
        return SimpleNamespace(
            id=platform_admin_id,
            role="platform_admin",
            isp_id=None,
        )

    async def fake_get_isp_by_id(*args, **kwargs):
        return SimpleNamespace(
            id=isp_id,
            name="Demo ISP",
            status="active",
        )

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    def fake_require_email_delivery():
        return None

    async def fake_create_invitation(*args, **kwargs):
        return (
            fake_invitation(
                account_type="admin",
                admin_role="isp_admin",
                isp_id=isp_id,
                invited_by_admin_id=platform_admin_id,
            ),
            "raw-platform-token",
        )

    async def fake_send_isp_admin_invitation_email(**kwargs):
        sent_email.update(kwargs)

    app.dependency_overrides[get_current_admin] = override_admin
    monkeypatch.setattr(admin_invitation_endpoint, "settings", SimpleNamespace(DEBUG=False))
    monkeypatch.setattr(admin_invitation_endpoint, "get_isp_by_id", fake_get_isp_by_id)
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
        fake_require_email_delivery,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "create_isp_admin_invitation",
        fake_create_invitation,
    )
    monkeypatch.setattr(
        admin_invitation_endpoint,
        "send_isp_admin_invitation_email",
        fake_send_isp_admin_invitation_email,
    )

    response = api_client.post(
        f"/api/v1/platform-admin/isps/{isp_id}/admin-invitations",
        json=invitation_payload(),
        headers={"Origin": "http://192.168.1.10:5173"},
    )

    assert response.status_code == 201
    assert "frontend_base_url" not in sent_email


def test_isp_admin_user_invitation_sends_email_without_returning_token_in_production(
    api_client,
    monkeypatch,
):
    isp_admin_id = uuid4()
    isp_id = uuid4()
    sent_email = {}

    async def override_admin():
        return SimpleNamespace(
            id=isp_admin_id,
            role="isp_admin",
            isp_id=isp_id,
        )

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    def fake_require_email_delivery():
        return None

    async def fake_create_invitation(*args, **kwargs):
        return (
            fake_invitation(
                isp_id=isp_id,
                invited_by_admin_id=isp_admin_id,
            ),
            "raw-app-user-token",
        )

    async def fake_send_app_user_invitation_email(**kwargs):
        sent_email.update(kwargs)

    app.dependency_overrides[get_current_isp_admin] = override_admin
    monkeypatch.setattr(user_invitation_endpoint, "settings", SimpleNamespace(DEBUG=False))
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
        fake_require_email_delivery,
    )
    monkeypatch.setattr(
        user_invitation_endpoint,
        "create_app_user_invitation",
        fake_create_invitation,
    )
    monkeypatch.setattr(
        user_invitation_endpoint,
        "send_app_user_invitation_email",
        fake_send_app_user_invitation_email,
    )

    response = api_client.post(
        "/api/v1/isp-admin/user-invitations",
        json=invitation_payload(),
    )

    assert response.status_code == 201
    assert sent_email == {
        "to_email": "newuser@test.com",
        "full_name": "New User",
        "raw_token": "raw-app-user-token",
        "expires_in_days": 7,
    }
    assert "dev_invitation_token" not in response.json()


def test_isp_admin_user_invitation_uses_debug_origin_for_email_link(
    api_client,
    monkeypatch,
):
    isp_admin_id = uuid4()
    isp_id = uuid4()
    sent_email = {}

    async def override_admin():
        return SimpleNamespace(
            id=isp_admin_id,
            role="isp_admin",
            isp_id=isp_id,
        )

    async def fake_get_account_by_identifier(*args, **kwargs):
        return None

    async def fake_get_pending_invitation(*args, **kwargs):
        return None

    def fake_require_email_delivery():
        return None

    async def fake_create_invitation(*args, **kwargs):
        return (
            fake_invitation(
                isp_id=isp_id,
                invited_by_admin_id=isp_admin_id,
            ),
            "raw-app-user-token",
        )

    async def fake_send_app_user_invitation_email(**kwargs):
        sent_email.update(kwargs)

    app.dependency_overrides[get_current_isp_admin] = override_admin
    monkeypatch.setattr(user_invitation_endpoint, "settings", SimpleNamespace(DEBUG=True))
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
        fake_require_email_delivery,
    )
    monkeypatch.setattr(
        user_invitation_endpoint,
        "create_app_user_invitation",
        fake_create_invitation,
    )
    monkeypatch.setattr(
        user_invitation_endpoint,
        "send_app_user_invitation_email",
        fake_send_app_user_invitation_email,
    )

    response = api_client.post(
        "/api/v1/isp-admin/user-invitations",
        json=invitation_payload(),
        headers={"Origin": "http://192.168.1.10:5173"},
    )

    assert response.status_code == 201
    assert sent_email["frontend_base_url"] == "http://192.168.1.10:5173"
