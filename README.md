# PulseFi Backend

PulseFi is a Smart Network Monitoring and Optimization System built for internet users, ISP administrators, and platform administrators.

The backend is a FastAPI + PostgreSQL service designed for a deployable Final Year Project MVP. It supports secure authentication, role-based access, ISP/platform management, and will later support usage monitoring, alerts, predictions, recommendations, router integration, and reports.

---

## Current Backend Status

Current phase: **Step 22 in progress - Recommendation to plan change request integration**.

Recently completed and tested:

- Step 16: ISP Admin management endpoints.
- Step 17: App User/mobile MVP endpoints.
- Step 18A/18B: Router adapter interface and simulator adapter.
- Step 18C: Router policy execution service.
- Step 18D: App User device policy execution endpoint.
- Step 18E: ISP Admin router action log visibility.
- Step 18F: Router action integration tests.
- Step 18G: App User router capability visibility endpoint.

Current next backend work:`r`n`r`n- Step 20B: Generate policy failed alerts from failed router/device policy execution.

Step 18 added the router integration foundation without storing router passwords or credentials. Router execution currently uses the simulator adapter for safe demo/testing.

---

## Current Completed Platform Admin Endpoints

Protected by `platform_admin` role only:

- `POST /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps/{isp_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}`
- `POST /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `GET /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admin-invitations/{invitation_id}/revoke`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `GET /api/v1/platform-admin/summary`

---

## ISP Admin Isolation Rule

ISP Admin endpoints must be scoped to the authenticated ISP Admin's own `isp_id`.

ISP Admins:

- Can manage only their own ISP's users, plans, subscriptions, routers, reports, and analytics.
- Cannot create ISPs.
- Cannot invite or manage ISP Admin accounts.
- Cannot access another ISP's users, plans, subscriptions, routers, reports, or analytics.

---

## Project Idea

PulseFi connects users, ISP admins, subscriptions, routers, devices, usage data, alerts, predictions, recommendations, and reports into one smart system.

A regular user should be able to use a mobile app to:

- View total internet usage.
- View their subscription or subscriptions.
- View connected devices.
- View per-device consumption when supported by the router.
- Receive high-usage alerts.
- Receive new-device-connected alerts.
- View future usage predictions.
- View plan recommendations.
- Request a subscription upgrade or downgrade.
- Apply bandwidth limits or device priority to selected devices when supported.

An ISP Admin should be able to use a web dashboard to:

- Manage app users.
- Invite users.
- Manage subscription plans.
- Assign user subscriptions.
- Manage router information.
- View usage records.
- View device records.
- View alerts and policy status.
- View recommendations and network analytics.
- Generate reports.
- View router action logs.
- Handle user subscription change requests.

A Platform Admin should be able to use a web dashboard to:

- Manage ISPs.
- Invite ISP Admins.
- Manage ISP Admin accounts.
- View platform-level summary metrics.

---

## User Types

### Platform Admin

The Platform Admin manages the platform itself.

Main responsibilities:

- Manage ISPs.
- Invite ISP Admins.
- Manage ISP Admin accounts.
- View platform-level summary data.

### ISP Admin

The ISP Admin represents one internet service provider.

Main responsibilities:

- Manage users under their ISP.
- Manage plans under their ISP.
- Assign subscriptions.
- Manage routers.
- View usage, devices, alerts, recommendations, reports, analytics, and router action logs for their ISP.

### App User

The App User is the regular internet customer using the mobile app.

Main responsibilities:

- Monitor their internet usage.
- View connected devices.
- Receive alerts.
- View predictions and recommendations.
- Request subscription changes.
- Apply device optimization actions when router capabilities allow it.

---

## Router Integration Concept

PulseFi should not pretend to support every router from day one.

The backend should use a router adapter architecture:

- Start with a simulator adapter for reliable demo/testing.
- Add one first supported router integration family or protocol if possible.
- Use router capabilities to show, hide, enable, or disable features.

Router feature tiers:

### Full Mode

Supports most features:

- Total usage.
- Connected devices.
- Per-device usage.
- New-device detection.
- Bandwidth limiting.
- Device prioritization.

### Partial Mode

Supports only some features exposed by the router.

### Basic Mode

Supports subscription-level usage, predictions, recommendations, and ISP-side analytics, but does not provide reliable device-level monitoring or device optimization.

---

## Authentication and Security

PulseFi uses secure invitation-based onboarding.

Authentication design:

- Platform Admin invites ISP Admins.
- ISP Admins invite App Users.
- Invited accounts accept an expiring setup link.
- Invited accounts set their own password.
- Invited accounts choose a username.
- Login accepts email or username plus `account_type`.
- Passwords are hashed using Argon2 through `pwdlib[argon2]`.
- JWT access tokens include account ID, account type, issued-at time, and expiration time.
- Password reset tokens are expiring and single-use.
- Old tokens are rejected after `password_changed_at`.
- Email verification is included.
- MFA supports authenticator app, email OTP, and backup recovery codes.
- Backup codes are single-use and stored hashed.
- SMS verification is deferred for now because it adds recurring production cost.

---

## Backend Technology

- FastAPI
- Python
- PostgreSQL
- Async SQLAlchemy
- asyncpg
- Pydantic / pydantic-settings
- JWT with PyJWT
- Argon2 password hashing through `pwdlib[argon2]`
- pyotp for authenticator-app MFA

---

## Backend Structure

Main structure:

- `app/main.py`
- `app/core/config.py`
- `app/core/security.py`
- `app/db/session.py`
- `app/db/base.py`
- `app/api/dependencies/`
- `app/api/v1/router.py`
- `app/api/v1/endpoints/`
- `app/models/`
- `app/schemas/`
- `app/services/`

Architecture style:

- Clean modular monolith.
- Keep endpoint files thin.
- Put business logic in services.
- Keep schemas split by feature area.
- Avoid huge mixed-responsibility files.

---

## Development Commands

Run the backend from the project root:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Root endpoint:

```text
/
```

Health endpoint:

```text
/api/v1/health
```

Basic app import test:

```powershell
.\venv\Scripts\python.exe -c "from app.main import app; print('App imported successfully')"
```

API router import test:

```powershell
.\venv\Scripts\python.exe -c "from app.api.v1.router import api_router; print('API router imported successfully')"
```

Current Step 16 preparation import test:

```powershell
.\venv\Scripts\python.exe -c "from app.api.dependencies import get_current_isp_admin; from app.core.config import settings; print('Step 16 foundation imported successfully.')"
```

---

## Deployment Goal

PulseFi should be deployable by presentation time.

The MVP should prioritize:

- Reliable backend.
- Secure authentication.
- Clear Platform Admin, ISP Admin, and App User flows.
- Working database.
- Demo-friendly router simulator.
- Usage data flow.
- Alerts.
- Predictions and recommendations.
- Reports.
- Frontend integration.

Avoid claiming universal router support before it exists. Use simulator support and capability-based feature availability for a realistic MVP.

---

## Backend Quality Progress â€” 2026-05-14

The backend quality foundation was improved before continuing Step 16.

Completed on 2026-05-14:

- Created and tested a limited PostgreSQL application role: `pulsefi_app`.
- Updated local `.env` to connect with `pulsefi_app` instead of the `postgres` superuser.
- Confirmed the backend connects successfully as `pulsefi_app`.
- Initialized Alembic.
- Configured Alembic to use the same async PostgreSQL URL from `app/core/config.py`.
- Configured Alembic to read SQLAlchemy metadata from `Base.metadata`.
- Created an empty baseline migration for the existing database schema.
- Stamped the current database at Alembic head: `c384b4d102bc`.
- Confirmed Alembic current revision: `c384b4d102bc (head)`.

Important database note:

- Existing PulseFi tables and data were not recreated, deleted, or changed.
- Alembic created/uses the normal `alembic_version` tracking table.
- `pulsefi_app` was temporarily granted `CREATE` on schema `public` so Alembic could create `alembic_version`.

Future permission hardening:

- Before production deployment, revisit database permissions.
- The preferred production setup is to separate responsibilities:
  - an application role for normal backend runtime access
  - a migration/admin role for Alembic schema changes
- After migrations are properly managed, avoid giving the normal runtime app role unnecessary schema-creation power.

---

## Testing Progress â€” 2026-05-14

Completed:

- Installed testing dependencies: pytest, pytest-asyncio, and httpx.
- Created initial tests folder structure.
- Added first API test for the health endpoint.
- Confirmed the test suite runs successfully with pytest.
- First test result: 1 passed.

Current testing status:

- Testing foundation exists.
- Health endpoint is covered.
- Future tests should cover authentication, Platform Admin endpoints, invitation behavior, password reset, and Step 16 ISP Admin isolation.

Recommended test command:

.\venv\Scripts\python.exe -m pytest

---

## CI Progress â€” 2026-05-14

Completed:

- Added GitHub Actions workflow for backend checks.
- CI runs on push and pull request to `main`.
- CI installs backend dependencies from `requirements.txt`.
- CI imports the FastAPI app.
- CI imports the API router.
- CI compiles `app`, `alembic`, and `tests`.
- CI runs the pytest suite.

Current CI status:

- CI foundation exists.
- Current test suite includes the health endpoint test.
- Future CI can be expanded to include database-backed tests, linting, formatting checks, and security checks.

Important note:

- The first CI version does not run real database migrations or database-backed API tests.
- Future database tests should use a separate test database/service, not the local development database.

---

## Step 16 Progress â€” 2026-05-14

### Step 16A â€” ISP Admin Router Foundation

Completed:

- Created ISP Admin endpoint package under `app/api/v1/endpoints/isp_admin/`.
- Added ISP Admin router prefix: `/api/v1/isp-admin`.
- Added Swagger tag: `ISP Admin`.
- Added protected starter endpoint: `GET /api/v1/isp-admin/summary`.
- Connected ISP Admin router to the main API v1 router.
- Confirmed `get_current_isp_admin` is used by the starter summary endpoint.
- Import checks passed.
- Pytest passed.
- Compile check passed.

Current behavior:

- The starter summary endpoint is protected by the ISP Admin guard.
- It returns the authenticated ISP Admin ID and ISP ID.
- It does not change database data.

Next Step 16 work:

- Replace/expand the temporary summary endpoint with real ISP-scoped counts later.
- Continue with ISP Admin App User invitation and management endpoints.
- Every Step 16 query must filter by `current_admin.isp_id`.

---

## Step 16 Progress â€” 2026-05-14

### Step 16B â€” ISP Admin App User Invitation Endpoints

Completed:

- Added ISP Admin schemas under `app/schemas/isp_admin/`.
- Added App User invitation request/response schemas.
- Added ISP Admin services under `app/services/isp_admin/`.
- Added service logic for creating, listing, finding, and revoking App User invitations.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/user_invitations.py`.
- Added endpoints:
  - `POST /api/v1/isp-admin/user-invitations`
  - `GET /api/v1/isp-admin/user-invitations`
  - `PATCH /api/v1/isp-admin/user-invitations/{invitation_id}/revoke`
- Connected user invitation endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- All invitation queries are scoped by `current_admin.isp_id`.
- Development invitation token is returned only while `DEBUG=True`.
- Import checks passed.
- Pytest passed.
- Compile check passed.

Impact:

- Database schema: no change.
- Existing data: no change unless the new endpoints are called.
- SE diagrams: later update ISP Admin use cases/activity flow to include App User invitation flow.

Next Step 16 work:

- Test App User invitation endpoints through Swagger/Postman.
- Then add ISP Admin App User listing/detail/update endpoints.

---

## Step 16 Testing Progress â€” 2026-05-14

### Step 16B â€” App User Invitation Endpoints Tested

Tested successfully:

- ISP Admin login worked after password reset.
- `GET /api/v1/isp-admin/summary` confirmed the account is a valid ISP Admin.
- `POST /api/v1/isp-admin/user-invitations` created an App User invitation.
- Created invitation was correctly scoped to the ISP Admin's `isp_id`.
- Created invitation used `account_type = app_user`.
- Created invitation stored `invited_by_admin_id` as the logged-in ISP Admin.
- `GET /api/v1/isp-admin/user-invitations?status=pending` listed the pending invitation.
- Duplicate pending invitation test prevented duplicate active invitations.
- `PATCH /api/v1/isp-admin/user-invitations/{invitation_id}/revoke` revoked the invitation.
- Second revoke attempt was rejected.
- Pending list after revoke returned empty.
- Revoked list showed the revoked invitation.

Impact:

- Database schema: no change.
- Existing data: only local test invitation/reset data changed.
- SE diagrams: later update ISP Admin use cases/activity flow to include App User invitation management.
- Security: Step 16B confirmed ISP Admin invitation actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin App User listing/detail/update endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress â€” 2026-05-14

### Step 16C â€” ISP Admin App User Management Endpoints

Completed and tested:

- Added ISP Admin App User management schemas.
- Added ISP Admin App User management service logic.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/users.py`.
- Added endpoints:
  - `GET /api/v1/isp-admin/users`
  - `GET /api/v1/isp-admin/users/{user_id}`
  - `PATCH /api/v1/isp-admin/users/{user_id}`
- Connected App User management endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- All App User queries are scoped by `current_admin.isp_id`.
- Tested creating a fresh App User through the invitation acceptance flow.
- Tested listing App Users under the ISP Admin's ISP.
- Tested viewing one App User by ID.
- Tested updating allowed App User fields.
- Tested reactivating the test user.

Allowed update fields in initial Step 16C:

- `full_name`
- `phone_number`
- `status`

Deferred update fields:

- `email`
- `username`

Reason email and username updates are deferred:

- Email and username are login identifiers.
- Updating them requires extra case-insensitive uniqueness checks.
- Email changes may require a new email-verification flow.
- Username changes require strict format validation and duplicate prevention.
- These changes affect login, password reset, email verification, notifications, and account recovery.

Impact:

- Database schema: no change.
- Existing data: only local test invitation/App User data changed during testing.
- SE diagrams: later update ISP Admin use cases/activity flow to include App User management.
- Security: Step 16C confirms App User management actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin subscription plan management endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress â€” 2026-05-14

### Step 16D â€” ISP Admin Subscription Plan Management Endpoints

Completed and tested:

- Added ISP Admin subscription plan schemas.
- Added ISP Admin subscription plan service logic.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/plans.py`.
- Added endpoints:
  - `POST /api/v1/isp-admin/plans`
  - `GET /api/v1/isp-admin/plans`
  - `GET /api/v1/isp-admin/plans/{plan_id}`
  - `PATCH /api/v1/isp-admin/plans/{plan_id}`
- Connected subscription plan endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- All subscription plan queries are scoped by `current_admin.isp_id`.
- Tested creating a subscription plan.
- Tested duplicate plan-name prevention inside the same ISP.
- Tested listing subscription plans.
- Tested viewing one subscription plan by ID.
- Tested updating plan fields.
- Tested filtering active plans with `is_active=true`.
- Tested deactivating and reactivating a plan.

Current allowed plan fields:

- `plan_name`
- `monthly_price`
- `data_limit_gb`
- `speed_limit_mbps`
- `description`
- `is_active`

Impact:

- Database schema: no change.
- Existing data: only local test subscription plan data changed during testing.
- SE diagrams: later update ISP Admin use cases/activity flow to include subscription plan management.
- Security: Step 16D confirms subscription plan actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin user subscription assignment/listing endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress â€” 2026-05-14

### Step 16E â€” ISP Admin User Subscription Assignment and Management Endpoints

Completed and tested:

- Added ISP Admin user subscription schemas.
- Added ISP Admin user subscription service logic.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/subscriptions.py`.
- Added endpoints:
  - `POST /api/v1/isp-admin/subscriptions`
  - `GET /api/v1/isp-admin/subscriptions`
  - `GET /api/v1/isp-admin/subscriptions/{subscription_id}`
  - `PATCH /api/v1/isp-admin/subscriptions/{subscription_id}`
- Connected user subscription endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- Subscription listing/detail/update is scoped through the linked App User's `isp_id`.
- Subscription assignment verifies both:
  - the App User belongs to `current_admin.isp_id`
  - the Subscription Plan belongs to `current_admin.isp_id`
- Tested listing App Users for the ISP.
- Tested listing active plans for the ISP.
- Tested assigning a subscription to an App User.
- Tested listing all subscriptions for the ISP.
- Tested filtering subscriptions by App User ID.
- Tested viewing one subscription by ID.
- Tested updating subscription label/status/auto-renew.
- Tested suspending a subscription with `status = suspended`.
- Tested reactivating the subscription with `status = active`.

Subscription status values:

- `pending` â€” assigned but not active yet
- `active` â€” currently active subscription
- `suspended` â€” temporarily stopped, such as unpaid bill/admin action
- `expired` â€” ended by date
- `cancelled` â€” permanently cancelled

Database migration:

- Added Alembic migration `285ab0474b39_allow_suspended_user_subscription_status.py`.
- Migration updates `chk_subscription_status` to allow `suspended`.
- Existing data was not changed by the migration.
- Local migration application required pgAdmin/admin execution because `pulsefi_app` is intentionally not the owner of `user_subscriptions`.
- This confirms the future production need for a separate migration/admin database role instead of using the runtime app role for schema changes.

Impact:

- Database schema: changed only the `user_subscriptions.status` check constraint.
- Existing data: only local test subscription data changed during endpoint testing.
- SE diagrams: later update ISP Admin use cases/activity flow to include subscription assignment and suspension/reactivation.
- Security: Step 16E confirms subscription actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin router management endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress â€” 2026-05-14

### Step 16F â€” ISP Admin Router Management Endpoints

Completed and tested:

- Added ISP Admin router schemas.
- Added ISP Admin router service logic.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/routers.py`.
- Added endpoints:
  - `POST /api/v1/isp-admin/routers`
  - `GET /api/v1/isp-admin/routers`
  - `GET /api/v1/isp-admin/routers/{router_id}`
  - `PATCH /api/v1/isp-admin/routers/{router_id}`
- Connected router endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- Router creation verifies the target `user_subscription_id` belongs to an App User under `current_admin.isp_id`.
- Router listing/detail/update is scoped by `Router.isp_id = current_admin.isp_id`.
- Tested fetching an active user subscription.
- Tested creating a router linked to the subscription.
- Tested listing routers.
- Tested viewing one router by ID.
- Tested updating router name, model, IP, API endpoint, and status.
- Tested setting router status to `maintenance`.
- Tested reactivating router status back to `active`.

Router credential decision:

- Step 16F does not accept or store router passwords.
- `password_encrypted` exists in the database model for future real-router integration.
- Router credentials should only be added later after secure encryption helpers are implemented.
- Do not store raw router passwords.

Current router status values:

- `active`
- `inactive`
- `maintenance`

Impact:

- Database schema: no change.
- Existing data: only local test router data changed during endpoint testing.
- SE diagrams: later update ISP Admin use cases/activity flow to include router management.
- Security: Step 16F confirms router actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin dashboard/summary endpoint or Step 16 final cleanup/testing.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Current Backend State â€” 2026-05-14

Step 16A through Step 16F are complete and tested.

Completed Step 16 areas:

- Step 16A: ISP Admin protected router foundation and summary starter endpoint.
- Step 16B: ISP Admin App User invitation endpoints.
- Step 16C: ISP Admin App User management endpoints.
- Step 16D: ISP Admin subscription plan management endpoints.
- Step 16E: ISP Admin user subscription assignment and management endpoints.
- Step 16F: ISP Admin router management endpoints.

Current next step:

- Step 16G: ISP Admin dashboard/summary endpoint, or Step 16 final cleanup/testing.

Core rule remains:

- Every ISP Admin endpoint must use `get_current_isp_admin`.
- Every ISP Admin query must be scoped by `current_admin.isp_id`.

Important reminders:

- Do not update App User email/username casually; they affect login, verification, password reset, and uniqueness.
- Do not store router passwords until encrypted credential storage exists.
- Keep files modular and avoid large mixed-responsibility files.
- Future production DB setup should use a separate migration/admin role for Alembic and a restricted runtime role for FastAPI.

### ISP Admin Summary

The ISP Admin API includes a dashboard summary endpoint:

- `GET /api/v1/isp-admin/summary`

It returns ISP-scoped counts for:

- App Users
- Subscription Plans
- User Subscriptions
- Routers

All data is scoped to the authenticated ISP Admin's `isp_id`.


---

## Step 17 Progress â€” 2026-05-14

### Step 17A â€” App User Mobile Endpoint Foundation

Completed and tested:

- Added App User schema package under `app/schemas/app_user/`.
- Added App User service package under `app/services/app_user/`.
- Added App User endpoint package under `app/api/v1/endpoints/app_user/`.
- Added endpoint:
  - `GET /api/v1/me/summary`
- Connected App User routes to the main API router.
- Endpoint uses `get_current_app_user`.
- Endpoint uses the logged-in App User from the access token.
- Endpoint does not accept `user_id` from the request.
- Summary returns safe App User profile fields and subscription counts.
- Tested App User login.
- Tested `/api/v1/me/summary` with an App User token.
- Tested that an ISP Admin token cannot access `/api/v1/me/summary`.

Returned summary fields:

- `id`
- `isp_id`
- `full_name`
- `email`
- `username`
- `phone_number`
- `status`
- `email_verified_at`
- `created_at`
- `total_subscriptions`
- `active_subscriptions`

Security rules:

- App User mobile endpoints must use `get_current_app_user`.
- App User `/me` endpoints must never accept a target `user_id` from the request.
- App User `/me` endpoints must use `current_user.id` from the token.
- Do not expose password hashes, MFA secrets, reset tokens, or sensitive auth fields.

Impact:

- Database schema: no change.
- Existing data: read-only endpoint. Local test password may have changed if password reset was used for testing.
- SE diagrams: later update App User/mobile activity and sequence diagrams to include protected `/me` mobile endpoint flow.
- Security: Step 17A confirms App User-only route protection works.

Next Step 17 work:

- Add App User subscription endpoints.
- Likely endpoints:
  - `GET /api/v1/me/subscriptions`
  - `GET /api/v1/me/subscriptions/{subscription_id}`
- Continue using `get_current_app_user`.
- Continue using `current_user.id`; do not accept user IDs for App User self-service routes.

---

## Step 17 Progress â€” 2026-05-14

### Step 17B â€” App User Subscription Endpoints

Completed and tested:

- Added App User subscription schemas.
- Added App User subscription service logic.
- Added endpoint module: `app/api/v1/endpoints/app_user/subscriptions.py`.
- Added endpoints:
  - `GET /api/v1/me/subscriptions`
  - `GET /api/v1/me/subscriptions/{subscription_id}`
- Connected subscription endpoints to the App User router.
- Endpoints use `get_current_app_user`.
- Endpoints use the logged-in App User from the access token.
- Endpoints do not accept `user_id` from the request.
- Subscription list/detail queries are scoped by `UserSubscription.user_id = current_user.id`.
- List endpoint supports optional status filter:
  - `?status=pending`
  - `?status=active`
  - `?status=suspended`
  - `?status=expired`
  - `?status=cancelled`
- Response includes nested subscription plan summary data.
- Tested listing the logged-in App User's subscriptions.
- Tested viewing one subscription by ID.
- Tested filtering subscriptions by `status=active`.
- Tested that an ISP Admin token cannot access `/api/v1/me/subscriptions`.
- Tested that a fake/non-owned subscription ID returns `Subscription not found`.

Security rules:

- App User `/me` endpoints must use `get_current_app_user`.
- App User `/me` endpoints must never accept a target `user_id`.
- App User `/me` endpoints must only use `current_user.id` from the token.
- Do not expose another user's subscriptions.
- Do not expose sensitive auth fields.

Impact:

- Database schema: no change.
- Existing data: read-only endpoints.
- SE diagrams: later update App User/mobile activity and sequence diagrams to include subscription list/detail flow.
- Security: Step 17B confirms subscription access is scoped to the authenticated App User.

Next Step 17 work:

- Add App User router/device view endpoints, or App User usage endpoints.
- Continue using `get_current_app_user`.
- Continue using `current_user.id`; do not accept user IDs for App User self-service routes.

---

## Step 17 Progress â€” 2026-05-14

### Step 17C â€” App User Router and Device View Endpoints

Completed and tested:

- Added App User router schemas.
- Added App User device schemas.
- Added App User router service logic.
- Added App User device service logic.
- Added endpoint modules:
  - `app/api/v1/endpoints/app_user/routers.py`
  - `app/api/v1/endpoints/app_user/devices.py`
- Added endpoints:
  - `GET /api/v1/me/routers`
  - `GET /api/v1/me/routers/{router_id}`
  - `GET /api/v1/me/devices`
  - `GET /api/v1/me/devices/{device_id}`
- Connected router/device endpoints to the App User router.
- Endpoints use `get_current_app_user`.
- Endpoints use the logged-in App User from the access token.
- Endpoints do not accept `user_id` from the request.
- Router queries are scoped through:
  - `Router -> UserSubscription -> current_user.id`
- Device queries are scoped through:
  - `Device.user_id = current_user.id`
- Tested listing routers for the logged-in App User.
- Tested viewing one router by ID.
- Tested router status filtering.
- Created one local test device for endpoint testing.
- Tested listing devices for the logged-in App User.
- Tested viewing one device by ID.
- Tested filtering devices by `router_id`.
- Tested admin-token rejection for App User `/me` routes.
- Tested fake IDs return 404.

Important usage note:

- Step 17C only returns router/device identity and status.
- It does not return usage totals yet.
- Per-device `upload_mb`, `download_mb`, and `total_mb` should come from `usage_records`.
- Overall total usage should also come from `usage_records`.
- This is planned for Step 17D usage endpoints.

Security rules:

- App User `/me` endpoints must use `get_current_app_user`.
- App User `/me` endpoints must never accept a target `user_id`.
- App User `/me` endpoints must only use `current_user.id` from the token.
- Do not expose router `password_encrypted`.
- Do not expose router credentials.

Impact:

- Database schema: no change.
- Existing data: read-only endpoints; local test device may have been inserted during testing.
- SE diagrams: later update App User/mobile activity and sequence diagrams to include router/device viewing.
- Security: Step 17C confirms router/device access is scoped to the authenticated App User.

Next Step 17 work:

- Step 17D â€” App User usage endpoints.
- Required usage behavior:
  - total usage for the logged-in user
  - download/upload/total usage
  - per-device usage
  - per-router or per-subscription filtering
  - raw usage records for charts/history

---

## Latest App User Mobile Endpoints

Step 17E added App User alert endpoints.

Protected App User endpoints now include:

- GET /api/v1/me/summary
- GET /api/v1/me/subscriptions
- GET /api/v1/me/subscriptions/{subscription_id}
- GET /api/v1/me/routers
- GET /api/v1/me/routers/{router_id}
- GET /api/v1/me/devices
- GET /api/v1/me/devices/{device_id}
- GET /api/v1/me/usage/summary
- GET /api/v1/me/usage/devices
- GET /api/v1/me/usage/devices/{device_id}
- GET /api/v1/me/usage/records
- GET /api/v1/me/alerts
- GET /api/v1/me/alerts/{alert_id}
- PATCH /api/v1/me/alerts/{alert_id}/read

Security rule:

- App User /me endpoints use the authenticated token user and do not accept a target user_id.

---

## Latest App User Smart Feature Endpoints

Step 17F added App User prediction and recommendation endpoints.

Protected App User smart endpoints now include:

- GET /api/v1/me/predictions
- GET /api/v1/me/predictions/{prediction_id}
- GET /api/v1/me/recommendations
- GET /api/v1/me/recommendations/{recommendation_id}

Security rule:

- Prediction and recommendation endpoints use the authenticated token user and do not accept a target user_id.

---

## Latest App User Subscription Management Endpoints

Step 17G added App User plan change request endpoints.

Protected App User subscription management endpoints now include:

- POST /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests/{request_id}

Security rules:

- Plan change request endpoints use the authenticated token user.
- App Users cannot submit requests for another user.
- Requested plan must belong to the same ISP.
- Requested plan cannot equal the current plan.

---

## Latest App User Device Control Endpoints

Step 17H added App User device policy endpoints.

Protected App User device control endpoints now include:

- POST /api/v1/me/device-policies
- GET /api/v1/me/device-policies
- GET /api/v1/me/device-policies/{policy_id}

Security rules:

- Device policy endpoints use the authenticated token user.
- App Users cannot create policies for another user's device.
- Device ownership validation enforced before policy creation.
- Router actions are not yet executed directly in Step 17.

---

## Latest Current Backend Status ? 2026-05-15

Current phase: **Step 18 ? Router adapter and simulator layer**.

Completed:
- Platform Admin MVP endpoints.
- ISP Admin MVP endpoints.
- App User/mobile MVP endpoints through subscriptions, routers/devices, usage-adjacent views, alerts, predictions, recommendations, plan change requests, and device policy requests.
- Backend quality fixes for auth security, migrations, CI, production email-token guards, and API tests.

Next backend focus:
- Build a router adapter architecture starting with a simulator adapter.
- Real router integrations come later after safe credential encryption and router-specific capability handling are designed.


---

## Usage Ingestion MVP

PulseFi now supports simulator-based usage ingestion for demo/testing.

ISP Admin endpoint:

POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator

Behavior:

- Requires ISP Admin authentication.
- Router must belong to the logged-in ISP Admin ISP scope.
- Router must be active.
- Router must be linked to an active user subscription.
- Creates simulator usage records in usage_records.
- Creates per-device records when connected devices exist.
- Creates one router-level record when no connected devices exist.
- Uses source = simulator.

This is demo-safe and does not require storing router passwords or logging into real routers.

---

## Simulator Device Ingestion

PulseFi supports simulator-based connected-device ingestion for demo/testing.

ISP Admin endpoint:

POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices

Behavior:

- Requires ISP Admin authentication.
- Router must belong to the logged-in ISP Admin's ISP.
- Router must be active.
- Router must be linked to an active user subscription.
- Creates deterministic simulator devices for the router.
- Updates existing simulator devices instead of duplicating them.
- Creates device connection logs for connected, seen, or reconnected events.
- Does not require real router credentials.

---

## Simulator Device Ingestion

PulseFi supports simulator-based connected-device ingestion for demo/testing.

ISP Admin endpoint:

POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices

Behavior:

- Requires ISP Admin authentication.
- Router must belong to the logged-in ISP Admin's ISP.
- Router must be active.
- Router must be linked to an active user subscription.
- Creates deterministic simulator devices for the router.
- Updates existing simulator devices instead of duplicating them.
- Creates device connection logs for connected, seen, or reconnected events.
- Does not require real router credentials.

---

## Combined Simulator Ingestion

PulseFi supports a combined simulator ingestion endpoint for demo/testing.

ISP Admin endpoint:

POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/run

Behavior:

- Requires ISP Admin authentication.
- Router must belong to the logged-in ISP Admin's ISP.
- Runs simulator connected-device ingestion.
- Runs simulator usage ingestion.
- Creates or updates simulator devices.
- Creates device connection logs.
- Creates simulator usage records.
- Does not require real router credentials.

---

## ISP Admin Usage Visibility

PulseFi supports ISP Admin read-only visibility for usage records and device connection logs.

Endpoints:

GET /api/v1/isp-admin/usage-records
GET /api/v1/isp-admin/usage-records/{usage_record_id}
GET /api/v1/isp-admin/device-connection-logs
GET /api/v1/isp-admin/device-connection-logs/{connection_log_id}

Behavior:

- Requires ISP Admin authentication.
- Usage records are scoped to the logged-in ISP Admin's ISP.
- Device connection logs are scoped to the logged-in ISP Admin's ISP.
- Supports filters for dashboard views and troubleshooting.
- Does not modify usage/device data.

---

## Step 19 Usage Ingestion Status

Step 19 is complete for the MVP/demo backend.

PulseFi now supports:

- Simulator usage generation.
- Simulator connected-device generation.
- Device connection logs.
- Combined simulator ingestion for one-click demo updates.
- ISP Admin read-only visibility for usage records.
- ISP Admin read-only visibility for device connection logs.

The simulator flow remains demo-safe and does not require real router passwords or real router login.


### Step 20A Alert Generation

The backend now generates alerts after simulator ingestion for:

- High usage.
- Plan exceed risk.
- Unusual consumption.
- New connected device.

App Users can view generated alerts through `/api/v1/me/alerts` and mark alerts as read through `/api/v1/me/alerts/{alert_id}/read`.


### Step 20B Policy Failed Alerts

The backend now creates a `policy_failed` alert when device policy execution fails.

Example:

- A bandwidth limit policy without `bandwidth_limit_mbps` fails.
- The policy status becomes `failed`.
- A router action log is stored with status `failed`.
- The App User receives a `policy_failed` alert.


### Step 20C ISP Admin Alert Visibility

ISP Admins can now view App User alerts under their own ISP through:

- `GET /api/v1/isp-admin/alerts`
- `GET /api/v1/isp-admin/alerts/{alert_id}`

This is read-only dashboard visibility. Alerts still belong to App Users, not admins.


### Step 20D Alert Tests

Focused alert generation tests were added for:

- `plan_exceed_risk`
- `policy_failed`
- duplicate unread `policy_failed` prevention

More isolation tests are still planned.


### Step 20E Alert Isolation Tests

Alert ownership and ISP isolation tests were added.

They verify:

- App User alert queries are scoped by the authenticated user.
- ISP Admin alert queries are scoped through the App User ISP relationship.
- Additional filters do not remove ISP scoping.



### Step 21A Prediction Foundation

The backend can now generate rule-based usage predictions for user subscriptions.

ISP Admin endpoint:

- `POST /api/v1/isp-admin/predictions/subscriptions/{subscription_id}/generate`

The prediction estimates full-cycle usage from observed usage and average daily usage. Generated predictions are visible to App Users through:

- `GET /api/v1/me/predictions`
- `GET /api/v1/me/predictions/{prediction_id}`


### Step 21B Recommendation Foundation

The backend can now generate rule-based recommendations from prediction records.

ISP Admin endpoint:

- `POST /api/v1/isp-admin/recommendations/predictions/{prediction_id}/generate`

Generated recommendations are visible to App Users through:

- `GET /api/v1/me/recommendations`
- `GET /api/v1/me/recommendations/{recommendation_id}`

Recommendation types include:

- `upgrade_plan`
- `downgrade_plan`
- `stay_current`
- `monitor_usage`


### Step 21C Prediction and Recommendation Tests

Focused service tests were added for:

- Prediction generation math.
- Recommendation generation.
- Duplicate recommendation prevention.
- ISP-scoped recommendation generation.
- App User prediction/recommendation ownership queries.


### Step 21D Recommendation Cleanup Tests

Recommendation service tests now cover all MVP recommendation types:

- `upgrade_plan`
- `downgrade_plan`
- `stay_current`
- `monitor_usage`

Step 21 prediction and recommendation foundation is complete enough to support the next backend phase.



### Step 22 Planned Work

Next backend phase:

- Connect recommendations to subscription change requests.
- Add ISP Admin visibility for plan change requests.
- Add ISP Admin approve/reject flow.
- Keep all ISP Admin actions scoped by `current_admin.isp_id`.

