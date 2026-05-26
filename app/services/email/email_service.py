from __future__ import annotations

import logging

import httpx
from html import escape
from urllib.parse import urlencode, urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


async def _send_brevo_email(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> None:
    payload: dict[str, object] = {
        "sender": {
            "email": settings.SMTP_FROM_EMAIL,
            "name": settings.SMTP_FROM_NAME,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_body,
    }

    if html_body:
        payload["htmlContent"] = html_body

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                settings.BREVO_API_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code < 200 or response.status_code >= 300:
            logger.warning(
                "Brevo HTTP email delivery failed with status %s: %s",
                response.status_code,
                response.text[:500],
            )
            raise EmailDeliveryError(
                f"Brevo HTTP email delivery failed with status {response.status_code}."
            )
    except httpx.HTTPError as exc:
        raise EmailDeliveryError("Brevo HTTP email delivery failed.") from exc


async def send_email(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> None:
    if not settings.EMAIL_DELIVERY_ENABLED:
        return

    email_provider = getattr(settings, "EMAIL_DELIVERY_PROVIDER", "brevo").strip().lower()

    if email_provider != "brevo":
        raise EmailDeliveryError("Unsupported email delivery provider. Use 'brevo'.")

    await _send_brevo_email(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def _normalize_frontend_base_url(value: str) -> str | None:
    parsed = urlparse(value.strip())

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def resolve_debug_frontend_base_url(
    frontend_base_url: str | None,
    *,
    debug: bool | None = None,
) -> str | None:
    debug_enabled = getattr(settings, "DEBUG", False) if debug is None else debug

    if not debug_enabled or not frontend_base_url:
        return None

    return _normalize_frontend_base_url(frontend_base_url)


def resolve_frontend_base_url(frontend_base_url: str | None = None) -> str:
    normalized_url = resolve_debug_frontend_base_url(frontend_base_url)

    if normalized_url:
        return normalized_url

    return settings.FRONTEND_ADMIN_URL.rstrip("/")


def _build_accept_invitation_url(
    *,
    raw_token: str,
    account_type: str,
    frontend_base_url: str | None = None,
) -> str:
    query = urlencode(
        {
            "token": raw_token,
            "account_type": account_type,
        }
    )
    return (
        f"{resolve_frontend_base_url(frontend_base_url)}/accept-invitation?{query}"
    )


def build_password_reset_url(
    *,
    raw_token: str,
    frontend_base_url: str | None = None,
) -> str:
    query = urlencode({"token": raw_token})
    return f"{resolve_frontend_base_url(frontend_base_url)}/reset-password?{query}"


async def send_password_reset_email(
    *,
    to_email: str,
    full_name: str | None,
    raw_token: str,
    expires_in_minutes: int,
    frontend_base_url: str | None = None,
) -> None:
    reset_url = build_password_reset_url(
        raw_token=raw_token,
        frontend_base_url=frontend_base_url,
    )
    display_name = full_name or to_email

    text_body = f"""
Hello {display_name},

Open this PulseFi link to reset your admin password:

{reset_url}

This link expires in {expires_in_minutes} minute(s).

If you did not request this password reset, you can ignore this email.

PulseFi
""".strip()

    html_body = f"""
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color: #102033;">
    <h2>PulseFi Password Reset</h2>
    <p>Hello {escape(display_name)},</p>
    <p>Open this PulseFi link to reset your admin password:</p>
    <p>
      <a href="{escape(reset_url)}"
         style="display:inline-block;padding:12px 16px;background:#2274a5;color:white;text-decoration:none;border-radius:10px;font-weight:bold;">
        Reset password
      </a>
    </p>
    <p>This link expires in {expires_in_minutes} minute(s).</p>
    <p>If you did not request this password reset, you can ignore this email.</p>
    <p>PulseFi</p>
  </body>
</html>
""".strip()

    await send_email(
        to_email=to_email,
        subject="PulseFi password reset",
        text_body=text_body,
        html_body=html_body,
    )


async def send_profile_update_mfa_email(
    *,
    to_email: str,
    full_name: str | None,
    code: str,
    expires_in_minutes: int,
) -> None:
    display_name = full_name or to_email

    text_body = f"""
Hello {display_name},

Use this PulseFi verification code to confirm your account settings change:

{code}

This code expires in {expires_in_minutes} minute(s).

If you did not request this change, secure your account immediately.

PulseFi
""".strip()

    html_body = f"""
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color: #102033;">
    <h2>PulseFi Settings Verification</h2>
    <p>Hello {escape(display_name)},</p>
    <p>Use this verification code to confirm your account settings change:</p>
    <p style="font-size:24px;font-weight:bold;letter-spacing:4px;">{escape(code)}</p>
    <p>This code expires in {expires_in_minutes} minute(s).</p>
    <p>If you did not request this change, secure your account immediately.</p>
    <p>PulseFi</p>
  </body>
</html>
""".strip()

    await send_email(
        to_email=to_email,
        subject="PulseFi settings verification code",
        text_body=text_body,
        html_body=html_body,
    )

async def send_login_mfa_email(
    *,
    to_email: str,
    full_name: str | None,
    code: str,
    expires_in_minutes: int,
) -> None:
    display_name = full_name or to_email

    text_body = f"""
Hello {display_name},

Use this PulseFi verification code to complete your login:

{code}

This code expires in {expires_in_minutes} minute(s).

If you did not try to log in, secure your account immediately.

PulseFi
""".strip()

    html_body = f"""
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color: #102033;">
    <h2>PulseFi Login Verification</h2>
    <p>Hello {escape(display_name)},</p>
    <p>Use this verification code to complete your login:</p>
    <p style="font-size:24px;font-weight:bold;letter-spacing:4px;">{escape(code)}</p>
    <p>This code expires in {expires_in_minutes} minute(s).</p>
    <p>If you did not try to log in, secure your account immediately.</p>
    <p>PulseFi</p>
  </body>
</html>
""".strip()

    await send_email(
        to_email=to_email,
        subject="PulseFi login verification code",
        text_body=text_body,
        html_body=html_body,
    )



async def send_platform_admin_invitation_email(
    *,
    to_email: str,
    full_name: str | None,
    raw_token: str,
    expires_in_days: int,
    frontend_base_url: str | None = None,
) -> None:
    accept_url = _build_accept_invitation_url(
        raw_token=raw_token,
        account_type="admin",
        frontend_base_url=frontend_base_url,
    )

    display_name = full_name or to_email

    text_body = f"""
Hello {display_name},

You have been invited to become a Platform Admin on PulseFi.

Open this link to accept the invitation and create your login information:

{accept_url}

This invitation expires in {expires_in_days} day(s).

If you did not expect this invitation, you can ignore this email.

PulseFi
""".strip()

    html_body = f"""
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color: #102033;">
    <h2>PulseFi Platform Admin Invitation</h2>
    <p>Hello {escape(display_name)},</p>
    <p>You have been invited to become a <strong>Platform Admin</strong> on PulseFi.</p>
    <p>
      <a href="{escape(accept_url)}"
         style="display:inline-block;padding:12px 16px;background:#2274a5;color:white;text-decoration:none;border-radius:10px;font-weight:bold;">
        Accept invitation
      </a>
    </p>
    <p>This invitation expires in {expires_in_days} day(s).</p>
    <p>If you did not expect this invitation, you can ignore this email.</p>
    <p>PulseFi</p>
  </body>
</html>
""".strip()

    await send_email(
        to_email=to_email,
        subject="PulseFi Platform Admin invitation",
        text_body=text_body,
        html_body=html_body,
    )


async def send_isp_admin_invitation_email(
    *,
    to_email: str,
    full_name: str | None,
    isp_name: str,
    raw_token: str,
    expires_in_days: int,
    frontend_base_url: str | None = None,
) -> None:
    accept_url = _build_accept_invitation_url(
        raw_token=raw_token,
        account_type="admin",
        frontend_base_url=frontend_base_url,
    )

    display_name = full_name or to_email

    text_body = f"""
Hello {display_name},

You have been invited to become an ISP Admin for {isp_name} on PulseFi.

Open this link to accept the invitation and create your login information:

{accept_url}

This invitation expires in {expires_in_days} day(s).

If you did not expect this invitation, you can ignore this email.

PulseFi
""".strip()

    html_body = f"""
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color: #102033;">
    <h2>PulseFi ISP Admin Invitation</h2>
    <p>Hello {escape(display_name)},</p>
    <p>
      You have been invited to become an ISP Admin for
      <strong>{escape(isp_name)}</strong> on PulseFi.
    </p>
    <p>
      <a href="{escape(accept_url)}"
         style="display:inline-block;padding:12px 16px;background:#2274a5;color:white;text-decoration:none;border-radius:10px;font-weight:bold;">
        Accept invitation
      </a>
    </p>
    <p>This invitation expires in {expires_in_days} day(s).</p>
    <p>If you did not expect this invitation, you can ignore this email.</p>
    <p>PulseFi</p>
  </body>
</html>
""".strip()

    await send_email(
        to_email=to_email,
        subject=f"PulseFi invitation for {isp_name}",
        text_body=text_body,
        html_body=html_body,
    )


async def send_app_user_invitation_email(
    *,
    to_email: str,
    full_name: str | None,
    raw_token: str,
    expires_in_days: int,
    frontend_base_url: str | None = None,
) -> None:
    accept_url = _build_accept_invitation_url(
        raw_token=raw_token,
        account_type="app_user",
        frontend_base_url=frontend_base_url,
    )

    display_name = full_name or to_email

    text_body = f"""
Hello {display_name},

You have been invited to create a PulseFi App User account.

Open this link to accept the invitation and create your login information:

{accept_url}

This invitation expires in {expires_in_days} day(s).

If you did not expect this invitation, you can ignore this email.

PulseFi
""".strip()

    html_body = f"""
<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color: #102033;">
    <h2>PulseFi App User Invitation</h2>
    <p>Hello {escape(display_name)},</p>
    <p>You have been invited to create a PulseFi App User account.</p>
    <p>
      <a href="{escape(accept_url)}"
         style="display:inline-block;padding:12px 16px;background:#2274a5;color:white;text-decoration:none;border-radius:10px;font-weight:bold;">
        Accept invitation
      </a>
    </p>
    <p>This invitation expires in {expires_in_days} day(s).</p>
    <p>If you did not expect this invitation, you can ignore this email.</p>
    <p>PulseFi</p>
  </body>
</html>
""".strip()

    await send_email(
        to_email=to_email,
        subject="PulseFi App User invitation",
        text_body=text_body,
        html_body=html_body,
    )
