# PulseFi Deployment Readiness Checklist

This checklist is for moving PulseFi from local development/demo mode toward a safer production-style deployment.

## Current checkpoint

- Step 41B hardened production email configuration validation.
- Step 41C hides dev verification-code UI by default.
- Step 41D adds this deployment checklist and a safe `.env.example`.

## Local development mode

Use local mode while developing:

```env
DEBUG=True
EMAIL_DELIVERY_ENABLED=False
FRONTEND_ADMIN_URL=http://localhost:5173
```

Local behavior:

- Backend may return development-only `dev_email_code` values when `DEBUG=True`.
- Admin web hides those codes by default.
- Admin web shows dev-code boxes only if local frontend env includes `VITE_SHOW_DEV_CODES=true`.
- `.env` and frontend env files must stay uncommitted.

## Production-style requirements

When `DEBUG=False`, backend validation requires:

- `EMAIL_DELIVERY_ENABLED=True`
- non-local `FRONTEND_ADMIN_URL`
- strong non-placeholder `SECRET_KEY`
- no wildcard CORS origin
- configured `DATA_ENCRYPTION_KEY`
- valid email settings: `SMTP_HOST`, `SMTP_FROM_EMAIL`, and `FRONTEND_ADMIN_URL`
- `SMTP_USE_TLS` and `SMTP_USE_SSL` cannot both be enabled

## Required production environment values

```env
DEBUG=False
EMAIL_DELIVERY_ENABLED=True
FRONTEND_ADMIN_URL=https://admin.pulsefi.example
BACKEND_CORS_ORIGINS=["https://admin.pulsefi.example"]
SECRET_KEY=<long-random-secret>
DATA_ENCRYPTION_KEY=<separate-long-random-secret>
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_FROM_EMAIL=noreply@pulsefi.example
SMTP_FROM_NAME=PulseFi
SMTP_USE_TLS=True
SMTP_USE_SSL=False
```

## Email flow checklist

- Invitation email links open the admin web invite acceptance page.
- Password reset emails open `/reset-password?token=...`.
- MFA email codes are delivered to the expected account email.
- Email verification codes are delivered.
- Production does not expose `dev_email_code`.
- Admin web does not show dev-code UI unless `VITE_SHOW_DEV_CODES=true`.

## CORS checklist

For local LAN testing, include the admin web network URL:

```env
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://192.168.1.10:5173"]
```

For production, do not use wildcard CORS:

```env
BACKEND_CORS_ORIGINS=["https://admin.pulsefi.example"]
```

## Secrets checklist

Never commit:

- `.env`
- SMTP password
- JWT secret
- encryption key
- database password
- router credentials
- ISP API keys
- production tokens

Use `.env.example` only for placeholders.

## Commands before deployment/demo

Backend:

```powershell
cd C:\PulseFi\backend
.\venv\Scripts\python.exe -m compileall app tests
.\venv\Scripts\python.exe -m pytest
git diff --check
```

Admin web:

```powershell
cd C:\PulseFi\pulsefi-admin-web
npm.cmd run lint
npm.cmd run build
git diff --check
```

## Still not production-complete

Before real public production, PulseFi still needs:

- Redis/shared-store rate limiting for multi-worker deployments.
- Real deployment secrets management.
- HTTPS.
- Database backup plan.
- Observability/logging strategy.
- Encrypted router credential storage before accepting real router credentials.
