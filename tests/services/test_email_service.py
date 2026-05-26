from types import SimpleNamespace

import pytest

import app.services.email.email_service as email_service


def test_resolve_frontend_base_url_uses_valid_debug_origin(monkeypatch):
    monkeypatch.setattr(
        email_service,
        "settings",
        SimpleNamespace(
            DEBUG=True,
            FRONTEND_ADMIN_URL="http://localhost:5173",
        ),
    )

    assert (
        email_service.resolve_frontend_base_url("http://192.168.1.10:5173/some/path")
        == "http://192.168.1.10:5173"
    )


def test_resolve_frontend_base_url_falls_back_without_origin(monkeypatch):
    monkeypatch.setattr(
        email_service,
        "settings",
        SimpleNamespace(
            DEBUG=True,
            FRONTEND_ADMIN_URL="http://localhost:5173",
        ),
    )

    assert email_service.resolve_frontend_base_url(None) == "http://localhost:5173"


def test_resolve_frontend_base_url_ignores_origin_in_production(monkeypatch):
    monkeypatch.setattr(
        email_service,
        "settings",
        SimpleNamespace(
            DEBUG=False,
            FRONTEND_ADMIN_URL="https://admin.pulsefi.example",
        ),
    )

    assert (
        email_service.resolve_frontend_base_url("http://192.168.1.10:5173")
        == "https://admin.pulsefi.example"
    )


def test_resolve_frontend_base_url_rejects_invalid_origin(monkeypatch):
    monkeypatch.setattr(
        email_service,
        "settings",
        SimpleNamespace(
            DEBUG=True,
            FRONTEND_ADMIN_URL="http://localhost:5173",
        ),
    )

    assert (
        email_service.resolve_frontend_base_url("javascript:alert(1)")
        == "http://localhost:5173"
    )


class FakeAsyncEmailResponse:
    def __init__(self, status_code=201, text="ok"):
        self.status_code = status_code
        self.text = text


class FakeBrevoAsyncClient:
    posts = []
    status_code = 201
    text = "ok"

    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url, *, headers, json):
        self.__class__.posts.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": self.timeout,
            }
        )
        return FakeAsyncEmailResponse(
            status_code=self.__class__.status_code,
            text=self.__class__.text,
        )


def patch_brevo_settings(monkeypatch, *, enabled=True):
    monkeypatch.setattr(
        email_service,
        "settings",
        SimpleNamespace(
            DEBUG=True,
            EMAIL_DELIVERY_ENABLED=enabled,
            EMAIL_DELIVERY_PROVIDER="brevo",
            BREVO_API_KEY="brevo-test-key",
            BREVO_API_URL="https://api.brevo.com/v3/smtp/email",
            SMTP_FROM_EMAIL="no-reply@pulsefi.test",
            SMTP_FROM_NAME="PulseFi",
            FRONTEND_ADMIN_URL="https://admin.pulsefi.test",
        ),
    )


@pytest.mark.asyncio
async def test_send_email_uses_brevo_provider(monkeypatch):
    FakeBrevoAsyncClient.posts = []
    FakeBrevoAsyncClient.status_code = 201
    FakeBrevoAsyncClient.text = "ok"
    patch_brevo_settings(monkeypatch)
    monkeypatch.setattr(email_service.httpx, "AsyncClient", FakeBrevoAsyncClient)

    await email_service.send_email(
        to_email="user@example.com",
        subject="PulseFi test",
        text_body="Plain text body",
        html_body="<p>HTML body</p>",
    )

    post = FakeBrevoAsyncClient.posts[0]

    assert post["url"] == "https://api.brevo.com/v3/smtp/email"
    assert post["headers"]["api-key"] == "brevo-test-key"
    assert post["json"]["sender"] == {
        "email": "no-reply@pulsefi.test",
        "name": "PulseFi",
    }
    assert post["json"]["to"] == [{"email": "user@example.com"}]
    assert post["json"]["subject"] == "PulseFi test"
    assert post["json"]["textContent"] == "Plain text body"
    assert post["json"]["htmlContent"] == "<p>HTML body</p>"


@pytest.mark.asyncio
async def test_app_user_invitation_email_uses_brevo(monkeypatch):
    FakeBrevoAsyncClient.posts = []
    FakeBrevoAsyncClient.status_code = 201
    FakeBrevoAsyncClient.text = "ok"
    patch_brevo_settings(monkeypatch)
    monkeypatch.setattr(email_service.httpx, "AsyncClient", FakeBrevoAsyncClient)

    await email_service.send_app_user_invitation_email(
        to_email="user@example.com",
        full_name="User Example",
        raw_token="raw token with spaces",
        expires_in_days=7,
    )

    post = FakeBrevoAsyncClient.posts[0]

    assert post["json"]["to"] == [{"email": "user@example.com"}]
    assert post["json"]["subject"] == "PulseFi App User invitation"
    assert "token=raw+token+with+spaces" in post["json"]["textContent"]
    assert "token=raw+token+with+spaces" in post["json"]["htmlContent"]


@pytest.mark.asyncio
async def test_isp_admin_invitation_email_does_not_send_when_delivery_disabled(
    monkeypatch,
):
    FakeBrevoAsyncClient.posts = []
    patch_brevo_settings(monkeypatch, enabled=False)
    monkeypatch.setattr(email_service.httpx, "AsyncClient", FakeBrevoAsyncClient)

    await email_service.send_isp_admin_invitation_email(
        to_email="admin@example.com",
        full_name="Admin Example",
        isp_name="Demo ISP",
        raw_token="raw-token",
        expires_in_days=7,
    )

    assert FakeBrevoAsyncClient.posts == []


@pytest.mark.asyncio
async def test_brevo_failure_raises_clean_email_error(monkeypatch):
    FakeBrevoAsyncClient.posts = []
    FakeBrevoAsyncClient.status_code = 401
    FakeBrevoAsyncClient.text = "invalid api key"
    patch_brevo_settings(monkeypatch)
    monkeypatch.setattr(email_service.httpx, "AsyncClient", FakeBrevoAsyncClient)

    with pytest.raises(email_service.EmailDeliveryError, match="Brevo HTTP email delivery failed"):
        await email_service.send_email(
            to_email="user@example.com",
            subject="PulseFi test",
            text_body="Plain text body",
        )
