# PulseFi Deployment Readiness Checklist

This checklist is for moving PulseFi from local development/demo mode toward a safer production-style deployment.

## Current checkpoint

- Step 41B hardened production email configuration validation.
- Step 41C hides dev verification-code UI by default.
- Step 41D adds this deployment checklist and a safe `.env.example`.
- Step 41E uses valid request `Origin` values for local DEBUG email links only,
  keeps production email links on `FRONTEND_ADMIN_URL`, removes visible admin-web
  debug/token helper UI, and repairs authenticator MFA setup persistence.

## Local development mode

Use local mode while developing:

```env
DEBUG=True
EMAIL_DELIVERY_ENABLED=False
FRONTEND_ADMIN_URL=http://localhost:5173
```

Local behavior:

- Backend may return development-only helper fields such as `dev_email_code`,
  `dev_invitation_token`, or `dev_reset_url` when `DEBUG=True`.
- The real admin web must not render local DEBUG helper fields, token boxes, or
  reset URLs.
- `VITE_SHOW_DEV_CODES` is no longer used by the real admin web.
- While `DEBUG=True`, invitation and password-reset emails may use the request
  `Origin` as the admin-web base URL only when it is a valid `http` or `https`
  origin with a host. Without a valid Origin, local links fall back to
  `FRONTEND_ADMIN_URL`.
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
- Local LAN invitation/password reset emails should use the LAN admin web URL
  when requests come from that valid LAN Origin.
- Production invitation/password reset emails ignore request Origin and use
  `FRONTEND_ADMIN_URL`.
- Password reset emails open `/reset-password?token=...`.
- MFA email codes are delivered to the expected account email.
- Email verification codes are delivered.
- Production does not expose `dev_email_code`.
- Admin web does not show dev-code, token, reset-URL, local DEBUG, or manual
  token helper UI.

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

<!-- PULSEFI_STEP_41F_41G_START -->
## Step 41F/41G Admin Lifecycle + UI Smoke Checkpoint - 2026-05-23

Status:
- Step 41E auth hardening was completed before this checkpoint.
- Step 41F admin lifecycle UI polish is complete in the admin web repo.
- Step 41G admin web smoke-test cleanup/polish is in progress/completed depending on final manual verification.
- Mobile feature work remains paused until Step 42A.

Admin web updates completed:
- Removed fake global/topbar search controls from Platform Admin and ISP Admin dashboards.
- Added authenticator QR code support to the admin MFA setup screen.
- Improved MFA setup instructions:
  - scan QR code first,
  - use secret key manually if QR scan is unavailable,
  - choose Time-based/TOTP if the authenticator app asks,
  - delete the old PulseFi authenticator entry if re-setting up.
- Added clear lifecycle action buttons instead of relying only on status dropdowns.
- No hard-delete actions were added.

Platform Admin lifecycle UI:
- ISP lifecycle buttons:
  - Reactivate ISP,
  - Set inactive,
  - Suspend ISP.
- ISP Admin lifecycle buttons:
  - Reactivate Admin,
  - Set inactive,
  - Suspend Admin.
- Platform ISP Management scroll trap was fixed so scrolling can continue to ISP Admin invitation sections.
- Platform/Admin overview and dashboard spacing were polished.

ISP Admin lifecycle UI:
- App User lifecycle buttons:
  - Reactivate User,
  - Set inactive,
  - Suspend User.
- Plan lifecycle buttons:
  - Reactivate Plan,
  - Archive Plan.
- Router lifecycle buttons:
  - Set active,
  - Set inactive,
  - Maintenance.
- Subscription lifecycle buttons:
  - Reactivate,
  - Suspend,
  - Cancel.
- ISP Overview spacing/layout was polished for KPI cards, action center, needs-attention panel, and recent activity panels.

Design/security decisions:
- Lifecycle actions use existing backend status/update fields.
- Plans use is_active as archive/reactivate behavior.
- Invitations continue to use revoke, not delete.
- No unsafe hard delete was added because historical subscriptions, usage, alerts, recommendations, reports, and ownership history must remain intact.
- No visible local DEBUG token/reset URL/MFA dev-code UI should appear in admin web.
- Mobile app was not changed in this checkpoint.

Checks expected after this checkpoint:
- Admin web:
  - npm.cmd run lint
  - npm.cmd run build
  - git diff --check
- Backend docs:
  - git diff --check

Next planned phase:
- Step 41H: final admin/backend bug cleanup and demo-readiness verification.
- Step 42A: mobile app source-of-truth check and missing-feature inventory.
<!-- PULSEFI_STEP_41F_41G_END -->

<!-- PULSEFI_STEP_42A_SERVICE_REQUESTS_START -->
## Step 42A App User Service Requests Checkpoint - 2026-05-23

Status:
- Mobile phase started after Step 41 admin/auth/lifecycle polish.
- Existing subscription change request system was extended instead of creating a duplicate request table.
- App Users still do not directly change account/subscription status.
- App Users submit requests; ISP Admin reviews and approves/rejects.

Backend behavior:
- Existing `/api/v1/me/plan-change-requests` flow now supports these request types:
  - `upgrade`
  - `downgrade`
  - `suspend_subscription`
  - `suspend_account`
- `confirmation_text` is required to prevent accidental dangerous actions.
- Confirmation phrases:
  - `CHANGE PLAN`
  - `SUSPEND SUBSCRIPTION`
  - `SUSPEND ACCOUNT`
- Plan change approval updates the subscription plan.
- Suspend subscription approval sets the selected subscription status to `suspended`.
- Suspend account approval sets the App User status to `suspended`.
- ISP Admin review remains scoped by `current_admin.isp_id`.

Mobile behavior:
- The previous Manual Plan Change Request screen is now a broader Service Request screen.
- Mobile App User can choose:
  - Change plan,
  - Suspend subscription,
  - Suspend account.
- Mobile requires a reason and exact confirmation phrase before submit.
- Request is sent to the existing `/me/plan-change-requests` endpoint.
- Mobile does not directly suspend the account or subscription.

Safety/product decisions:
- No direct user-side suspend action was added.
- No hard delete was added.
- All lifecycle-changing requests remain pending until ISP Admin approval.
- This supports users who may want to change ISPs or temporarily suspend a subscription without accidental one-tap actions.

Checks expected:
- Backend:
  - compileall app tests
  - full pytest
  - git diff --check
- Mobile:
  - npx.cmd tsc --noEmit
  - npx.cmd expo-doctor
  - git diff --check

Next:
- Step 42B: mobile auth/session/MFA gap check.
- Step 42C: mobile service request manual smoke test with backend + mobile over LAN.
<!-- PULSEFI_STEP_42A_SERVICE_REQUESTS_END -->

<!-- PULSEFI_STEP_42B_MOBILE_MFA_START -->
## Step 42B Mobile MFA + Service Request UI Checkpoint - 2026-05-23

Status:
- Step 42A App User service request backend/mobile flow was completed before this checkpoint.
- Mobile auth/session cleanup continued with App User MFA improvements.
- Mobile App User service request screen was stabilized after display separator cleanup issues.

Mobile updates:
- Mobile App User login supports:
  - normal credential login,
  - MFA challenge verification,
  - switching MFA method when the backend allows it,
  - backup-code entry mode when available.
- Mobile App User first-login authenticator setup now supports confirming MFA setup from the mobile app.
- Mobile no longer renders local DEBUG email MFA codes.
- Mobile service request screen supports:
  - Change plan,
  - Suspend subscription,
  - Suspend account.
- Mobile requires a reason and exact confirmation phrase before request submission.
- Mobile plan/subscription display separators were normalized to plain ASCII separators.
- Avoid global replacement of `?` characters in TSX files because it corrupts TypeScript ternary operators.

Checks expected:
- Mobile:
  - npx.cmd tsc --noEmit
  - npx.cmd expo-doctor
  - git diff --check
- Backend docs:
  - git diff --check

Next:
- Step 42C: run backend + admin web + mobile over LAN and manually smoke-test:
  - App User login,
  - MFA challenge,
  - MFA setup,
  - service request creation,
  - ISP Admin request review approval/rejection.
<!-- PULSEFI_STEP_42B_MOBILE_MFA_END -->

<!-- PULSEFI_STEP_42C_ROUTER_SERVICE_LINE_START -->
## Step 42C Router/Service-Line LAN Smoke Checkpoint - 2026-05-23

Status:
- LAN smoke test completed for backend, admin web, and mobile.
- Router/service-line behavior was corrected for demo readiness.

Verified behavior:
- Multiple routers under the same App User can use the same package/plan.
- Independent routers use separate `user_subscriptions` service-line rows.
- Usage, devices, policies, and service requests remain independent per router/service line.
- Mobile Plan Request stays locked to the selected router from the Routers screen.
- ISP Admin can see service request reasons.
- Admin web can create a new service line for a router using the same package.

Demo data note:
- Hussien Olliek test account was repaired so Home, work, and office routers are on independent service lines.
- Old demo/test routers remain in the database and may affect total router counts unless filtered or removed before final presentation.

Checks completed before checkpoint:
- Backend compile/tests.
- Admin web lint/build.
- Mobile TypeScript/Expo checks.
<!-- PULSEFI_STEP_42C_ROUTER_SERVICE_LINE_END -->

<!-- PULSEFI_STEP_42D_OPERATIONS_REPORTS_START -->
## Step 42D Operations Context and Useful Reports Checkpoint - 2026-05-23

Status:
- ISP Admin Operations request context and report usefulness polish completed.

Verified behavior:
- Service request review now shows readable user/router/service/package context.
- Request reasons are visible in the request table and detail panel.
- Technical IDs are hidden behind technical details.
- Generated reports are viewable from the admin web UI.
- Usage reports include actionable insights and useful tables:
  - top service lines by usage,
  - top routers by usage,
  - recent usage records.
- Alert reports include actionable insights and useful alert rows.
- Raw report JSON is no longer the primary admin-facing view.

Checks required before commit:
- Backend compileall and pytest.
- Admin web lint/build.
- `git diff --check` in changed repositories.
<!-- PULSEFI_STEP_42D_OPERATIONS_REPORTS_END -->

<!-- PULSEFI_STEP_42D_ACTIONABLE_REPORTS_START -->
## Step 42D Actionable Reports Checkpoint - 2026-05-23

Status:
- ISP Admin generated reports were upgraded from basic counters/raw JSON into actionable report data.

Verified backend report behavior:
- Usage reports include summary metrics, insights, top service lines by usage, top routers by usage, and recent usage records.
- Alert reports include summary metrics, insights, breakdowns, and recent alert rows.
- Report data remains stored in `reports.report_data`.
- No database migration was required.

Admin-facing rule:
- Raw report JSON should be hidden under technical details.
- The primary report view should show readable summary cards, insights, and tables.
<!-- PULSEFI_STEP_42D_ACTIONABLE_REPORTS_END -->

