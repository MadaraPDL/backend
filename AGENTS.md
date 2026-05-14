# AGENTS.md â€” PulseFi Backend Instructions

## Project Name

PulseFi

## Main Rule for Codex / AI Coding Assistants

Before editing anything, read this file, `README.md`, and `ROADMAP.md`.

Do not make random architecture decisions without checking the existing project structure.

This backend is being built step by step by the student/developer, so changes should stay understandable, modular, and easy to explain.

---

## Current Backend Position

Current phase: **Step 16 â€” ISP Admin management endpoints**.

Recently completed and tested:

- Step 14: Protected current-account route system.
- Step 15A: Platform Admin ISP management endpoints.
- Step 15B: Platform Admin ISP Admin invitation endpoints.
- Step 15C: Platform Admin ISP Admin account management endpoints.
- Step 15D: Platform Admin dashboard summary endpoint.
- Step 15E: Platform Admin pending ISP Admin invitation management.

Step 15 is complete. Step 16 is next.

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

## Current Next Step

Step 16: ISP Admin management endpoints.

Core rule:

- ISP Admins manage only data under their own `isp_id`.
- ISP Admins cannot create ISPs.
- ISP Admins cannot invite or manage ISP Admin accounts.
- ISP Admins cannot access another ISP's users, plans, subscriptions, routers, reports, or analytics.

Expected Step 16 areas:

- App user invitations.
- App user management.
- Subscription plan management.
- User subscription assignment.
- Router management.
- ISP-scoped dashboard/list endpoints.

---

## Project Summary

PulseFi is a Smart Network Monitoring and Optimization System.

It is designed for:

- Regular internet users using a mobile app.
- ISP Admins using a web dashboard.
- Platform Admins managing ISPs and ISP Admin accounts.

The system helps users and ISP admins monitor, analyze, and optimize internet usage.

PulseFi is not just a basic usage tracker. The goal is to make it a smart deployable system that can:

- Monitor total internet usage.
- Monitor connected devices.
- Show per-device consumption when the router supports it.
- Detect new connected devices.
- Send alerts for high usage or new devices.
- Predict future internet consumption.
- Predict whether a user may exceed their subscription plan.
- Recommend better internet plans.
- Allow users to limit bandwidth or prioritize selected devices.
- Allow ISP admins to manage users, plans, subscriptions, routers, reports, alerts, and analytics.

---

## Current Backend Stack

Use this stack unless the developer explicitly changes it:

- Backend: FastAPI
- Language: Python
- Database: PostgreSQL
- ORM: SQLAlchemy async ORM
- Database driver: asyncpg
- Validation: Pydantic
- Password hashing: Argon2 using `pwdlib[argon2]`
- Authentication: JWT access tokens
- MFA/TOTP: pyotp
- Frontend later:
  - React Native mobile app for users
  - Web dashboard for ISP Admins
  - Web dashboard for Platform Admins

---

## Local Project Path

The backend usually lives here:

```text
C:\PulseFi\backend
```

---

## GitHub Repository

```text
https://github.com/MadaraPDL/backend
```

---

## Architecture Style

This backend is a clean modular monolith.

Keep the project modular.

Do not create huge files that mix unrelated responsibilities.

Important structure:

- `app/api/dependencies/` for auth/current-account dependencies and role guards
- `app/api/v1/endpoints/` for API endpoints
- `app/core/` for config and security helpers
- `app/db/` for database session/base setup
- `app/models/` for SQLAlchemy models
- `app/schemas/` for Pydantic schemas
- `app/services/` for business logic

Endpoints should stay thin.

Business logic should go in services.

Shared security helpers should go in `app/core/security.py`.

Database session dependency should stay in `app/db/session.py`.

---

## Important Coding Rule

Avoid creating one huge file with many unrelated features.

Prefer focused modules like:

- `account_service.py`
- `auth_service.py`
- `mfa_service.py`
- `invitation_service.py`
- `password_reset_service.py`
- `email_verification_service.py`
- `platform_admin_service.py` or focused platform-admin services
- `isp_admin_user_service.py`
- `subscription_plan_service.py`
- `user_subscription_service.py`
- `router_service.py`
- `usage_service.py`
- `alert_service.py`
- `prediction_service.py`
- `recommendation_service.py`
- `report_service.py`

Do not put login, invitations, password reset, email verification, MFA, users, plans, routers, reports, and analytics all in one service file.

---

## Important Role Rules

Platform Admin:

- Manages ISPs.
- Invites and manages ISP Admins.
- Views platform summary metrics.
- Does not represent a normal ISP customer.

ISP Admin:

- Manages only their own ISP's users, plans, subscriptions, routers, reports, and analytics.
- Can invite app users under their own ISP later.
- Cannot create ISPs.
- Cannot invite ISP Admins.
- Cannot manage ISP Admin accounts.
- Cannot access another ISP's data.

App User:

- Uses the mobile app.
- Views their own subscriptions, usage, devices, alerts, predictions, and recommendations.
- Can request subscription upgrades/downgrades.
- Can apply device optimization actions when router capability allows.

---

## Authentication Design Decisions

The system uses invitation-based onboarding.

Do not implement temporary passwords.

Account onboarding flow:

- Platform Admin invites ISP Admins.
- ISP Admins invite regular app users.
- Invited users/admins receive an expiring setup link.
- The invited person accepts the invitation.
- The invited person verifies control of their email.
- The invited person chooses a username.
- The invited person sets their own password.

Login design:

- Admins and app users are stored in separate tables.
- Login request includes `account_type`.
- Login accepts either email or username as the identifier.
- Email is still required for invitations, verification, password reset, notifications, and recovery.
- Username is optional but useful for easier login.
- Username should be unique case-insensitively.
- Username should have no spaces.

Security design:

- Passwords must be hashed with Argon2.
- Never store plain passwords.
- JWT tokens must include account ID as subject, `account_type`, issued-at time, and expiry time.
- Forgot-password responses must be generic to avoid account enumeration.
- Password reset tokens must be expiring and single-use.
- Old sessions should be invalid after password reset using `password_changed_at`.
- Current-account dependency should reject tokens issued before the latest `password_changed_at`.

MFA design:

- Support multiple MFA methods.
- Authenticator-app MFA should be supported.
- Email-based MFA/OTP should be supported.
- Backup recovery codes should be supported.
- Backup codes must be single-use only.
- Store only hashed backup codes.
- When backup codes are regenerated, old unused codes should be revoked/deleted or replaced.
- Platform Admins and ISP Admins should have MFA required or strongly enforced.
- Regular users may have optional MFA initially.

Authenticator secret rule:

- Do not store raw TOTP secrets in plaintext in the final deployable version.
- The existing `mfa_secret` column can store encrypted text.
- Generate the raw secret during setup.
- Show the raw secret once through QR setup.
- Encrypt before saving.
- Decrypt only briefly when verifying.

Email verification:

- Email verification tokens are only for verifying email ownership.
- Email verification tokens are not the same as email MFA login challenges.
- Email MFA login challenges should use `mfa_challenges`.

SMS:

- SMS verification is deferred for now because it adds recurring production cost.
- Do not add SMS unless explicitly requested later.

---

## Database Notes

The database already exists in PostgreSQL.

Do not guess schema details when exact columns are needed.

Inspect existing models or the database before changing models.

Core tables:

- `isps`
- `admins`
- `app_users`
- `subscription_plans`
- `user_subscriptions`
- `routers`
- `devices`
- `device_connection_logs`
- `usage_records`
- `predictions`
- `recommendations`
- `alerts`
- `device_network_policies`
- `router_action_logs`
- `subscription_change_requests`
- `reports`

Auth tables:

- `account_invitations`
- `email_verification_tokens`
- `password_reset_tokens`
- `mfa_backup_codes`
- `mfa_challenges`

Important auth columns already exist on `admins` and `app_users`:

- `username`
- `email_verified_at`
- `password_changed_at`
- `mfa_enabled`
- `mfa_required`
- `mfa_secret`
- `preferred_mfa_method`

Important database decisions:

- UUID primary keys use `gen_random_uuid()`.
- PostgreSQL `gen_random_uuid()` works.
- Use `PG_UUID(as_uuid=True)` in SQLAlchemy where appropriate.
- Use PostgreSQL `JSONB` where flexible structured data is needed.
- `subscription_plans` has a composite unique constraint on `(isp_id, plan_name)`.
- `user_subscriptions` allows multiple active subscriptions per user.
- A user may have separate subscriptions, such as family and work/gaming subscriptions.
- Routers should link to a specific user subscription.
- One subscription may have multiple routers, such as a main router plus repeaters.
- Each router belongs to one subscription.
- `devices.updated_at` is kept.
- `devices.created_at` is not necessary because `first_seen` covers that timing.
- `reports.report_data` is JSONB.
- `reports.created_at` stores when the report was created.

---

## Router Integration Design

Do not design PulseFi as supporting only one router type forever.

Use a router adapter architecture.

First deployable MVP:

- Support one first router integration family or protocol.
- Include a simulator adapter for reliable demo/testing.

Long-term router support:

- Different routers may expose different features.
- Use capability-based router support instead of a simple supported/unsupported flag.

Router fields/concepts may include:

- `vendor`
- `firmware_version`
- `connection_mode`
- `capabilities` as JSONB

Feature tiers:

Full mode:

- Total usage.
- Connected devices.
- Per-device usage.
- New-device alerts.
- Bandwidth limiting.
- Device prioritization.

Partial mode:

- Only the features exposed by the router are available.

Basic mode:

- Subscription-level usage, predictions, and recommendations from ISP-side data.
- No reliable per-device monitoring.
- No device optimization.

Device-level features depend on router capability.

---

## Subscription Change Design

Regular users can request plan upgrades or downgrades for their own subscriptions.

The actual subscription change is handled by the ISP Admin.

Users can directly apply device optimization actions such as bandwidth limit or device priority without ISP Admin approval.

---

## Commands

Run from the backend root.

App import test:

```powershell
.\venv\Scripts\python.exe -c "from app.main import app; print('App imported successfully')"
```

API router import test:

```powershell
.\venv\Scripts\python.exe -c "from app.api.v1.router import api_router; print('API router imported successfully')"
```

Step 16 foundation import test:

```powershell
.\venv\Scripts\python.exe -c "from app.api.dependencies import get_current_isp_admin; from app.core.config import settings; print('Step 16 foundation imported successfully.')"
```

Run the server:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger URL:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
/api/v1/health
```

---

## Software Engineering Diagram Update Rules

The developer wants reminders when backend/design changes require SE diagram updates.

Recommend SE updates when changes affect:

- Actors or roles.
- Use cases.
- Major user/admin flows.
- DFD processes or data flows.
- ERD entities, relationships, or attributes.
- Sequence diagrams.
- Activity diagrams.
- Security/onboarding architecture.
- Router/deployment structure.
- Major system behavior.

Do not interrupt for tiny implementation details.

Pending SE updates to batch later:

- Invitation-based onboarding.
- Email verification.
- Forgot password.
- Username/email login.
- MFA/2FA.
- Backup recovery codes.
- Router adapter/capability model.
- Subscription change request flow.
- Multiple active subscriptions per user.
- Router linked to subscription.
- One subscription may have multiple routers.
- Router simulator for MVP/demo.
- Capability-based feature availability.
- Platform Admin dashboard and ISP Admin management separation.
- ISP Admin scoped access rule.

---

## Explanation Style

When giving code or implementation steps:

- Explain which file is being edited.
- Explain why the edit is needed.
- Explain what the code does.
- Explain how it fits the project architecture.
- Say whether it affects:
  - database schema
  - existing data
  - GitHub
  - tests
  - SE diagrams

Do not just dump code without explanation.

---

## Before Editing

Before editing:

- Read the relevant files first.
- Understand the existing structure.
- Do not rewrite unrelated code.
- Do not make broad changes without reason.
- Do not invent missing database fields.

After editing:

- Summarize exactly what changed.
- Mention tests to run.
- Mention whether a Git commit/push is needed.
- Mention whether SE diagrams should be updated.

---

## Backend Quality State — 2026-05-14

The backend has a limited PostgreSQL app role and an Alembic baseline.

Current completed quality work:

- `pulsefi_app` PostgreSQL role exists for backend runtime DB access.
- Local `.env` should use `pulsefi_app`, not `postgres`.
- Alembic is initialized.
- Alembic reads the database URL from `app.core.config.settings.DATABASE_URL`.
- Alembic imports `Base.metadata` from `app.db.base`.
- Alembic imports `app.models` so all SQLAlchemy models are registered.
- Existing DB schema was baselined with revision `c384b4d102bc`.
- Current DB was stamped to Alembic head.
- Existing PulseFi tables/data were not recreated or changed.

Important migration rule:

- Do not autogenerate or apply migrations carelessly.
- The current baseline migration is intentionally empty because the database already existed before Alembic.
- Future database schema changes should be created as Alembic migrations after checking the real DB/models carefully.

Important DB permission reminder:

- `pulsefi_app` was granted enough permission for local development and Alembic setup, including creating the Alembic tracking table.
- Before production deployment, revisit and harden permissions.
- Prefer a separate migration/admin role for Alembic and a more restricted runtime app role for FastAPI.
- Do not leave unnecessary schema creation permissions on the normal app role in production without reviewing the risk.

Next recommended quality work:

1. Add `pytest` and `httpx` tests.
2. Add GitHub Actions CI.
3. Add structured logging.
4. Standardize API error responses.
5. Add safe seed/demo data.
6. Add deployment documentation.
7. Continue Step 16 only through `get_current_isp_admin` and always filter by `current_admin.isp_id`.

---

## Milestone Completion Log

Known completed milestones:

- 2026-05-10 — PostgreSQL database schema phase completed for the main PulseFi tables.
- 2026-05-10 — Core SQLAlchemy models completed and import-tested.
- 2026-05-11 — Authentication database update completed.
- 2026-05-11 — Authentication SQLAlchemy models completed and import-tested.
- 2026-05-11 — Authentication schemas completed.
- 2026-05-12 — Authentication services split into focused modules and import-tested.
- 2026-05-12 — Authentication endpoint package completed and Swagger/OpenAPI confirmed working.
- 2026-05-12 — Step 14 protected current-account route system completed.
- 2026-05-12 — Step 15 Platform Admin endpoint work completed through ISP/Admin management and summary features.
- 2026-05-13 — Backend foundation hardened for Step 16, including safer `.env.example`, production config validation, old-JWT invalidation after password reset, `get_current_isp_admin`, typo fixes, and `pyotp`.
- 2026-05-14 — Documentation cleanup completed for `README.md`, `ROADMAP.md`, and `AGENTS.md`.
- 2026-05-14 — Backend quality backlog added.
- 2026-05-14 — Limited PostgreSQL role `pulsefi_app` created and tested.
- 2026-05-14 — Alembic initialized, empty baseline migration created, and existing database stamped to revision `c384b4d102bc`.

Notes:

- Some earlier dates are “completed by this date” based on the project work log, not exact minute-by-minute timestamps.
- Future completed steps should be added here immediately after testing and before commit.

---

## Testing Progress — 2026-05-14

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

## CI Progress — 2026-05-14

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

## Step 16 Progress — 2026-05-14

### Step 16A — ISP Admin Router Foundation

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

## Step 16 Progress — 2026-05-14

### Step 16B — ISP Admin App User Invitation Endpoints

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

## Step 16 Testing Progress — 2026-05-14

### Step 16B — App User Invitation Endpoints Tested

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

## Step 16 Progress — 2026-05-14

### Step 16C — ISP Admin App User Management Endpoints

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

## Step 16 Progress — 2026-05-14

### Step 16D — ISP Admin Subscription Plan Management Endpoints

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

## Step 16 Progress — 2026-05-14

### Step 16E — ISP Admin User Subscription Assignment and Management Endpoints

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

- `pending` — assigned but not active yet
- `active` — currently active subscription
- `suspended` — temporarily stopped, such as unpaid bill/admin action
- `expired` — ended by date
- `cancelled` — permanently cancelled

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

## Step 16 Progress — 2026-05-14

### Step 16F — ISP Admin Router Management Endpoints

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
