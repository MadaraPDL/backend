from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from html import escape
from urllib.parse import urlencode

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


def _build_message(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email

    message.set_content(text_body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    return message


def _send_message_blocking(message: EmailMessage) -> None:
    if not settings.SMTP_HOST:
        raise EmailDeliveryError("SMTP_HOST is not configured.")

    if settings.SMTP_USE_SSL:
        smtp = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)
    else:
        smtp = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)

    try:
        if settings.SMTP_USE_TLS and not settings.SMTP_USE_SSL:
            smtp.starttls()

        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        smtp.send_message(message)
    except Exception as exc:
        raise EmailDeliveryError("Email delivery failed.") from exc
    finally:
        smtp.quit()


async def send_email(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> None:
    if not settings.EMAIL_DELIVERY_ENABLED:
        return

    message = _build_message(
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )

    await asyncio.to_thread(_send_message_blocking, message)


def _build_accept_invitation_url(*, raw_token: str, account_type: str) -> str:
    query = urlencode(
        {
            "token": raw_token,
            "account_type": account_type,
        }
    )
    return f"{settings.FRONTEND_ADMIN_URL.rstrip('/')}/accept-invitation?{query}"


def build_password_reset_url(*, raw_token: str) -> str:
    query = urlencode({"token": raw_token})
    return f"{settings.FRONTEND_ADMIN_URL.rstrip('/')}/reset-password?{query}"


async def send_password_reset_email(
    *,
    to_email: str,
    full_name: str | None,
    raw_token: str,
    expires_in_minutes: int,
) -> None:
    reset_url = build_password_reset_url(raw_token=raw_token)
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


async def send_isp_admin_invitation_email(
    *,
    to_email: str,
    full_name: str | None,
    isp_name: str,
    raw_token: str,
    expires_in_days: int,
) -> None:
    accept_url = _build_accept_invitation_url(
        raw_token=raw_token,
        account_type="admin",
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
) -> None:
    accept_url = _build_accept_invitation_url(
        raw_token=raw_token,
        account_type="app_user",
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

