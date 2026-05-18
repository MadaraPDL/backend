from types import SimpleNamespace

import pytest

import app.services.email.email_service as email_service


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.login_args = None
        self.messages = []
        self.quit_called = False
        FakeSMTP.instances.append(self)

    def starttls(self):
        self.started_tls = True

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        self.messages.append(message)

    def quit(self):
        self.quit_called = True


@pytest.mark.asyncio
async def test_app_user_invitation_email_uses_enabled_smtp_with_password(monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(
        email_service,
        "settings",
        SimpleNamespace(
            EMAIL_DELIVERY_ENABLED=True,
            SMTP_HOST="smtp.test",
            SMTP_PORT=587,
            SMTP_USERNAME="smtp-user",
            SMTP_PASSWORD="smtp-pass",
            SMTP_FROM_EMAIL="no-reply@pulsefi.test",
            SMTP_FROM_NAME="PulseFi",
            SMTP_USE_TLS=True,
            SMTP_USE_SSL=False,
            FRONTEND_ADMIN_URL="https://admin.pulsefi.test",
        ),
    )
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    await email_service.send_app_user_invitation_email(
        to_email="user@example.com",
        full_name="User Example",
        raw_token="raw token with spaces",
        expires_in_days=7,
    )

    smtp = FakeSMTP.instances[0]
    message = smtp.messages[0]

    assert smtp.host == "smtp.test"
    assert smtp.port == 587
    assert smtp.started_tls is True
    assert smtp.login_args == ("smtp-user", "smtp-pass")
    assert smtp.quit_called is True
    assert message["To"] == "user@example.com"
    assert "token=raw+token+with+spaces" in message.get_body().get_content()


@pytest.mark.asyncio
async def test_isp_admin_invitation_email_does_not_send_when_delivery_disabled(
    monkeypatch,
):
    FakeSMTP.instances = []
    monkeypatch.setattr(
        email_service,
        "settings",
        SimpleNamespace(
            EMAIL_DELIVERY_ENABLED=False,
            SMTP_HOST="smtp.test",
            SMTP_PORT=587,
            SMTP_USERNAME="smtp-user",
            SMTP_PASSWORD="smtp-pass",
            SMTP_FROM_EMAIL="no-reply@pulsefi.test",
            SMTP_FROM_NAME="PulseFi",
            SMTP_USE_TLS=True,
            SMTP_USE_SSL=False,
            FRONTEND_ADMIN_URL="https://admin.pulsefi.test",
        ),
    )
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    await email_service.send_isp_admin_invitation_email(
        to_email="admin@example.com",
        full_name="Admin Example",
        isp_name="Demo ISP",
        raw_token="raw-token",
        expires_in_days=7,
    )

    assert FakeSMTP.instances == []
