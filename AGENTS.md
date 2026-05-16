# AGENTS.md Ã¢â‚¬â€ PulseFi Backend Instructions

## Project Name

PulseFi

## Main Rule for Codex / AI Coding Assistants

Before editing anything, read this file, `README.md`, and `ROADMAP.md`.

Do not make random architecture decisions without checking the existing project structure.

This backend is being built step by step by the student/developer, so changes should stay understandable, modular, and easy to explain.

---

## Current Backend Position

Current phase: **Step 18 complete - Router adapter and simulator foundation**.

Recently completed and tested:

- Step 14: Protected current-account route system.
- Step 15: Platform Admin MVP endpoints.
- Step 16: ISP Admin MVP endpoints.
- Step 17: App User/mobile MVP endpoints.
- Step 18A/18B: Router adapter interface and simulator adapter.
- Step 18C: Router policy execution service.
- Step 18D: App User device policy execution endpoint.
- Step 18E: ISP Admin router action log visibility.
- Step 18F: Router action integration tests.
- Step 18G: App User router capability visibility endpoint.

Current next backend work:`r`n`r`n- Step 20B: Generate policy failed alerts from failed router/device policy execution.

Important Step 18 result:

- Router execution currently uses the simulator adapter.
- Router capabilities are exposed to App Users.
- ISP Admins can view router action logs for their own ISP only.
- No router passwords or credentials are accepted or stored.

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

Step 19: Usage data ingestion and simulator usage generation.

Core rule:

- App User /me usage endpoints must only show data owned by the authenticated App User.
- ISP Admin usage/analytics endpoints must be scoped by current_admin.isp_id.
- Usage records created from simulator/router data must be tied to the correct router, subscription, user, and device when available.
- Do not invent real-router support yet; continue using the simulator adapter for MVP/demo data.

Expected Step 19 areas:

- Simulator usage generation.
- Store total usage records.
- Store per-device usage records when available.
- Manual ingestion trigger for MVP/demo.
- Later scheduled ingestion.
- Tests for ownership and ISP isolation.

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

## Backend Quality State â€” 2026-05-14

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

- 2026-05-10 â€” PostgreSQL database schema phase completed for the main PulseFi tables.
- 2026-05-10 â€” Core SQLAlchemy models completed and import-tested.
- 2026-05-11 â€” Authentication database update completed.
- 2026-05-11 â€” Authentication SQLAlchemy models completed and import-tested.
- 2026-05-11 â€” Authentication schemas completed.
- 2026-05-12 â€” Authentication services split into focused modules and import-tested.
- 2026-05-12 â€” Authentication endpoint package completed and Swagger/OpenAPI confirmed working.
- 2026-05-12 â€” Step 14 protected current-account route system completed.
- 2026-05-12 â€” Step 15 Platform Admin endpoint work completed through ISP/Admin management and summary features.
- 2026-05-13 â€” Backend foundation hardened for Step 16, including safer `.env.example`, production config validation, old-JWT invalidation after password reset, `get_current_isp_admin`, typo fixes, and `pyotp`.
- 2026-05-14 â€” Documentation cleanup completed for `README.md`, `ROADMAP.md`, and `AGENTS.md`.
- 2026-05-14 â€” Backend quality backlog added.
- 2026-05-14 â€” Limited PostgreSQL role `pulsefi_app` created and tested.
- 2026-05-14 â€” Alembic initialized, empty baseline migration created, and existing database stamped to revision `c384b4d102bc`.

Notes:

- Some earlier dates are â€œcompleted by this dateâ€ based on the project work log, not exact minute-by-minute timestamps.
- Future completed steps should be added here immediately after testing and before commit.

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

---

## AI Assistant Workflow Preferences

When helping with PulseFi, the assistant/Codex should follow these rules:

### Explanation style

- Give step-by-step instructions.
- Explain what each command or code block does.
- Explain which file is being edited.
- Explain why the edit is needed.
- Explain how the change fits the PulseFi architecture.
- Mention whether each change affects:
  - database schema
  - existing data
  - GitHub
  - tests
  - SE diagrams
- Do not dump large code without explaining it.
- When possible, explain under or near each code block, not only at the end.

### Coding style

- Keep files modular.
- Do not create huge mixed-responsibility files.
- Split schemas, services, endpoints, and dependencies by feature area.
- Endpoint files should stay thin.
- Business logic should go in services.
- Do not rewrite unrelated code.
- Do not invent database fields.
- Check existing models/database before writing code that depends on schema details.

### Workflow style

- Before starting a new step, check the current Git status.
- Before coding a new feature, check the relevant existing files.
- After coding, run import checks, pytest, compile checks, and git status.
- Test endpoints through PowerShell/Swagger before committing when the feature affects API behavior.
- Save important decisions in repo docs before committing.
- Keep `PULSEFI_MEMORY.md` as the compact source of truth for future chats.
- Keep `AGENTS.md` useful for Codex/AI coding assistants.
- Keep `ROADMAP.md` updated with current phase and next step.
- Keep `BACKEND_QUALITY_BACKLOG.md` updated with quality/security/deployment reminders.

### Logging/output style

- For successful commands, the user can summarize instead of pasting huge logs.
- For errors, paste the important error section.
- The assistant should identify the exact failing line/error and provide a focused fix.
- Avoid making the chat unnecessarily heavy with repeated huge logs.

### Security and local files

- Never ask the user to commit `.env`.
- Never ask the user to commit local passwords or tokens.
- `LOCAL_TEST_ACCOUNTS.md` is local only and should stay ignored by Git.
- Router passwords should not be accepted or stored until encrypted credential storage exists.
- Do not store raw router passwords.
- Do not expose access tokens in docs or GitHub.

### Memory/update rules

- After finishing a major backend step, update:
  - `PULSEFI_MEMORY.md`
  - `AGENTS.md`
  - `ROADMAP.md`
  - `README.md`
  - `BACKEND_QUALITY_BACKLOG.md` when the change affects quality/security/deployment
- Add dates for completed milestones when possible.
- Mention pending SE diagram updates when backend/design changes affect actors, flows, use cases, DFDs, ERDs, activity diagrams, or sequence diagrams.

## Latest PulseFi Backend Note

Step 16G is complete:

- ISP Admin dashboard summary endpoint is implemented.
- Endpoint: `GET /api/v1/isp-admin/summary`
- Counts users, plans, subscriptions, and routers under `current_admin.isp_id`.
- Subscription counts must use the linked App User because `user_subscriptions` has no direct `isp_id`.
- Continue enforcing ISP Admin isolation in every Step 16 and Step 17 endpoint.


---

## Critical New Chat Rule

When starting or continuing PulseFi in a new chat, the assistant must not guess from old chat context.

Before giving implementation steps, read or ask the user to provide the latest repo state from:

- `PULSEFI_MEMORY.md`
- `AGENTS.md`
- `ROADMAP.md`
- `README.md`
- `BACKEND_QUALITY_BACKLOG.md`

The assistant must follow the workflow style saved in `PULSEFI_MEMORY.md` and `AGENTS.md`:

- give step-by-step instructions
- explain every code block/command
- keep files modular
- check existing files/models before coding
- run import checks, pytest, compile checks, and git status before commit
- update repo memory/docs after major backend steps
- never commit `.env`, local passwords, tokens, or `LOCAL_TEST_ACCOUNTS.md`
- do not store router passwords until encrypted credential storage exists

Current backend state:

- Step 16A through Step 16F are complete and tested.
- Current next work is Step 17: App User/mobile endpoints.

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

## Required Assistant/Codex Response Style for PulseFi

The user strongly prefers careful, step-by-step backend help. Future assistants must follow this style.

### Before coding

- Check the current repo state first with `git status`.
- Read the relevant existing files before giving code.
- Do not guess database fields or model relationships.
- Check the real SQLAlchemy models/database behavior when exact fields matter.
- Explain what step we are doing and why it is the correct next step.
- Keep the current roadmap in mind.

### Code delivery style

- Give commands/code in small clear blocks.
- Explain under each code block:
  - what file is being edited
  - why the edit is needed
  - what the code does
  - how it fits the architecture
  - whether it affects database schema
  - whether it affects existing data
  - whether it affects GitHub
  - whether tests are needed
  - whether SE diagrams should later be updated
- Do not dump large code without explanation.
- Do not skip explanations just because the code was given.
- Do not assume the user already knows what the code does.

### Project architecture rules

- Keep files modular.
- Do not create huge mixed-responsibility files.
- Split code by feature area:
  - schemas
  - services
  - endpoints
  - dependencies
  - models only when schema/model change is needed
- Endpoint files should stay thin.
- Business logic should go in service files.
- Do not rewrite unrelated code.
- Do not make broad architecture changes without reason.

### Testing workflow

After coding, always give checks before commit:

- import checks for the new schemas/services/endpoints
- main API router import check
- model import check when a model changed
- `pytest`
- `compileall`
- endpoint tests through PowerShell/Swagger when API behavior changed
- `git status`

When endpoint testing is needed, give PowerShell commands and explain what each one proves.

### Commit workflow

Before committing:

- Confirm tests passed.
- Confirm endpoint behavior worked.
- Confirm `git status` shows only expected files.
- Update docs/memory for major backend steps.
- Do not commit temporary test scripts.
- Do not commit `.env`.
- Do not commit local passwords, reset tokens, access tokens, invitation tokens, or `LOCAL_TEST_ACCOUNTS.md`.

After a successful step, update as needed:

- `PULSEFI_MEMORY.md`
- `AGENTS.md`
- `ROADMAP.md`
- `README.md`
- `BACKEND_QUALITY_BACKLOG.md` for quality/security/deployment notes

### Error handling style

When there is an error:

- Identify the exact failing line or exact cause.
- Explain why it happened.
- Give the smallest safe fix.
- Do not jump to unrelated changes.
- Retest after the fix.

### Security rules

- For ISP Admin endpoints, always use `get_current_isp_admin`.
- For ISP Admin queries, always scope by `current_admin.isp_id`.
- For App User/mobile `/me` endpoints, always use `get_current_app_user`.
- App User `/me` endpoints must never accept `user_id`.
- App User `/me` endpoints must use `current_user.id` from the token.
- Never expose password hashes, MFA secrets, reset tokens, invitation tokens, backup codes, or router credentials.
- Do not store router passwords until encrypted credential storage exists.

### Logging/chat style

- The user may summarize successful logs instead of pasting everything.
- For errors, the user should paste the important error section.
- Future assistants should avoid making the chat heavy with repeated huge logs.
- If the chat becomes laggy, continue from GitHub memory files in a fresh chat.

### New chat rule

At the start of a new PulseFi backend chat, read or ask the user to provide the latest state from:

- `PULSEFI_MEMORY.md`
- `AGENTS.md`
- `ROADMAP.md`
- `README.md`
- `BACKEND_QUALITY_BACKLOG.md`

Then continue from the latest completed step.

---

## Latest Completed App User Work

Step 17E is complete.

Completed endpoints:

- GET /api/v1/me/alerts
- GET /api/v1/me/alerts/{alert_id}
- PATCH /api/v1/me/alerts/{alert_id}/read

Rules confirmed:

- Use get_current_app_user.
- Scope alert queries by Alert.user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Do not expose sensitive auth fields.

Next likely Step 17 work:

- App User predictions/recommendations endpoints.
- Or App User subscription plan change request endpoints.

---

## Latest Completed App User Smart Feature Work

Step 17F is complete.

Completed endpoints:

- GET /api/v1/me/predictions
- GET /api/v1/me/predictions/{prediction_id}
- GET /api/v1/me/recommendations
- GET /api/v1/me/recommendations/{recommendation_id}

Rules confirmed:

- Use get_current_app_user.
- Scope prediction queries by Prediction.user_id = current_user.id.
- Scope recommendation queries by Recommendation.user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Do not expose sensitive auth fields.

Next likely Step 17 work:

- App User subscription plan change request endpoints.

---

## Latest Completed App User Subscription Management Work

Step 17G is complete.

Completed endpoints:

- POST /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests/{request_id}

Rules confirmed:

- Use get_current_app_user.
- Scope plan change request queries by SubscriptionChangeRequest.user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Requested plan must differ from the current plan.
- Requested plan must belong to the same ISP.
- Validate recommendation ownership before linking.

Next likely Step 17 work:

- App User device policy endpoints.

---

## Latest Completed App User Device Control Work

Step 17H is complete.

Completed endpoints:

- POST /api/v1/me/device-policies
- GET /api/v1/me/device-policies
- GET /api/v1/me/device-policies/{policy_id}

Rules confirmed:

- Use get_current_app_user.
- Scope device policy queries by DeviceNetworkPolicy.requested_by_user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Validate device ownership before policy creation.
- Device policies remain pending until future router adapter execution.

Next backend work:

- Step 18 â€” Router adapter and simulator layer.

---

## Latest Current State Update ? 2026-05-15

Current backend position: **Step 18 ? Router adapter and simulator layer**.

Completed:
- Step 16 ISP Admin MVP endpoints are complete.
- Step 17 App User/mobile MVP endpoints are complete through device policy requests.
- Backend quality fixes are complete for MFA login enforcement, Alembic baseline migration, PostgreSQL CI migration checks, production email-token guards, and auth API regression tests.

Next backend step:
- Step 18: create the router adapter foundation and simulator adapter.

Step 18 rule:
- Do not connect to real routers yet.
- Do not store raw router passwords.
- Start with a simulator adapter so router behavior can be demoed safely and tested reliably.


## Step 20A Completed

Alert generation is now connected to simulator ingestion.

Completed alert types:

- `high_usage`
- `plan_exceed_risk`
- `unusual_consumption`
- `new_device_connected`

The `alerts.alert_type` check constraint was updated through Alembic to allow Step 20 alert types.

Important next rule:

- `policy_failed` is allowed by the database constraint but still needs generation logic from failed router/device policy execution.
- App User alert endpoints already exist and must stay scoped by `get_current_app_user`.
- ISP Admin alert visibility, if added, must be scoped by `current_admin.isp_id`.


## Step 20C Completed

ISP Admins now have read-only visibility into App User alerts under their ISP.

Important rules:

- ISP Admin alert queries must use `get_current_isp_admin`.
- Alert queries must be scoped by `current_admin.isp_id`.
- Current alerts belong to App Users.
- Do not treat current `alerts` rows as admin-owned notifications.
- Admin-owned notifications would require a future separate design.

Next recommended work:

- Add focused alert tests and ownership/isolation tests.


## Step 20D Completed

Focused alert generation tests were added.

Covered:

- `plan_exceed_risk`
- `policy_failed`
- duplicate unread `policy_failed` prevention

Next recommended work:

- App User alert ownership isolation tests.
- ISP Admin alert ISP isolation tests.
- New device and unusual consumption alert tests.


## Step 20E Completed

Alert ownership and ISP isolation tests were added.

Important rules:

- App User alert access must stay scoped by `current_user.id`.
- ISP Admin alert access must stay scoped by `current_admin.isp_id`.
- ISP Admin alert visibility is read-only and shows App User alerts, not admin-owned notifications.

Next recommended work:

- New device alert test.
- Unusual consumption alert test.
- Then close Step 20 and move to Step 21 prediction/recommendation logic.



## Step 21A Completed

Prediction foundation is complete.

Completed:

- Rule-based prediction generation service.
- ISP Admin prediction generation endpoint.
- Prediction rows stored in the existing `predictions` table.
- App User can view generated predictions through existing `/me/predictions` endpoints.

Important rules:

- ISP Admin prediction generation must remain scoped by `current_admin.isp_id`.
- App User prediction visibility must remain scoped by `current_user.id`.
- This is rule-based/statistical prediction for MVP, not full ML yet.

Next recommended work:

- Step 21B: Generate recommendations based on predictions and available plans.


## Step 21B Completed

Recommendation foundation is complete.

Completed:

- Rule-based recommendation generation service.
- ISP Admin recommendation generation endpoint.
- Recommendation rows stored in the existing `recommendations` table.
- App User can view generated recommendations through existing `/me/recommendations` endpoints.
- Recommendation type check constraint updated through Alembic/manual DB application if needed.

Important rules:

- ISP Admin recommendation generation must remain scoped by `current_admin.isp_id`.
- App User recommendation visibility must remain scoped by `current_user.id`.
- This is rule-based recommendation logic for MVP.
- Do not treat this as full ML yet.

Next recommended work:

- Step 21C: Prediction/recommendation tests and isolation tests.


## Step 21C Completed

Prediction and recommendation service tests were added.

Covered:

- Prediction generation math.
- `stay_current` recommendation generation.
- `upgrade_plan` recommendation generation.
- Duplicate new recommendation prevention.
- ISP-scoped recommendation generation query.
- App User prediction/recommendation ownership query filters.

Important rules:

- ISP Admin prediction/recommendation generation must remain scoped by `current_admin.isp_id`.
- App User prediction/recommendation visibility must remain scoped by `current_user.id`.

Next recommended work:

- Add downgrade/monitor recommendation tests if needed.
- Consider subscription change request integration from recommendation rows.


## Step 21D Completed

Recommendation cleanup tests were added.

Covered recommendation types:

- `upgrade_plan`
- `downgrade_plan`
- `stay_current`
- `monitor_usage`

Step 21 is complete enough to move forward.

Next recommended options:

- Connect recommendation rows to subscription change request flow.
- Or move to ISP Admin reporting/analytics/dashboard improvements.

Important rules remain:

- ISP Admin prediction/recommendation generation must stay scoped by `current_admin.isp_id`.
- App User prediction/recommendation visibility must stay scoped by `current_user.id`.



## Step 22 Planned

Next phase:

Recommendation to plan change request integration.

Planned work:

- Review existing App User plan change request flow.
- Add ISP Admin subscription change request visibility.
- Add ISP Admin approve/reject handling.
- Add tests and docs.

Important rules:

- App User requests must stay scoped by `current_user.id`.
- ISP Admin queries/actions must stay scoped by `current_admin.isp_id`.
- Recommendation-linked requests must verify ownership.


---

## Step 22 Progress - 2026-05-16

### Step 22A/22B - Recommendation to Plan Change Request Integration

Completed and tested:

- Added App User ability to create a subscription change request from a recommendation.
- Added endpoint:
  - `POST /api/v1/me/recommendations/{recommendation_id}/plan-change-request`
- Added request schema:
  - `MyRecommendationPlanChangeRequestCreate`
- Updated manual plan change request validation so `request_type` only accepts:
  - `upgrade`
  - `downgrade`
- Recommendation types are mapped safely:
  - `upgrade_plan` -> `upgrade`
  - `downgrade_plan` -> `downgrade`
- Non-plan recommendations are rejected:
  - `stay_current`
  - `monitor_usage`
- The service verifies:
  - recommendation belongs to the authenticated App User
  - subscription belongs to the authenticated App User
  - requested plan belongs to the user's ISP
  - requested plan is active
  - recommendation points to the same subscription
  - recommendation points to the same requested plan
  - current plan and requested plan are different
  - duplicate pending requests for the same recommendation are blocked
- Recommendation status is set to `accepted` after a successful plan change request.
- No Alembic migration was needed because the database already allows recommendation status `accepted`.
- Added integration tests for:
  - successful upgrade recommendation -> plan change request
  - duplicate pending recommendation request prevention
  - rejecting non-plan recommendations
- Updated old ownership integration test to use valid subscription change request types.

Validation completed:

- Import checks passed.
- Pytest passed.
- Compile check passed.

Impact:

- Database schema: no change.
- Existing data: no direct migration or data rewrite.
- GitHub: Step 22 files and tests changed.
- SE diagrams: later update App User recommendation/plan-change request sequence and activity flow.

Next backend work:

- Step 22C: ISP Admin plan change request review endpoints.
- Likely endpoints:
  - `GET /api/v1/isp-admin/plan-change-requests`
  - `GET /api/v1/isp-admin/plan-change-requests/{request_id}`
  - `PATCH /api/v1/isp-admin/plan-change-requests/{request_id}/review`
- Required rule:
  - ISP Admin must only see and review requests for users under `current_admin.isp_id`.


---

## Step 22 Progress - 2026-05-16

### Step 22C - ISP Admin Plan Change Request Review

Completed and tested:

- Added ISP Admin plan change request review endpoints:
  - `GET /api/v1/isp-admin/plan-change-requests`
  - `GET /api/v1/isp-admin/plan-change-requests/{request_id}`
  - `PATCH /api/v1/isp-admin/plan-change-requests/{request_id}/review`
- Added ISP Admin schemas for:
  - plan change request responses
  - review request payloads
  - review decision validation
  - request status filtering
- Added ISP Admin service logic for:
  - listing plan change requests under the current ISP
  - viewing one plan change request under the current ISP
  - approving pending requests
  - rejecting pending requests
- Approval behavior:
  - request must be pending
  - requested plan must belong to the ISP
  - requested plan must be active
  - user subscription is updated to the requested plan
  - request status becomes `approved`
  - review admin, review time, and admin response are saved
- Rejection behavior:
  - request must be pending
  - subscription plan is not changed
  - request status becomes `rejected`
  - review admin, review time, and admin response are saved
- Security/isolation:
  - all ISP Admin plan change request queries are scoped through `AppUser.isp_id`
  - ISP Admins cannot list, view, or review requests from another ISP
- Added integration tests for:
  - approving own ISP request
  - rejecting own ISP request
  - preventing access to another ISP's request
  - preventing double review of already-reviewed requests
- Endpoint smoke test passed through FastAPI routes.

Validation completed:

- Import checks passed.
- New integration tests passed.
- Full pytest suite passed.
- Compile check passed.
- Endpoint smoke test passed.

Impact:

- Database schema: no change.
- Existing data: no migration or data rewrite.
- GitHub: Step 22C endpoint, schemas, services, and tests changed.
- SE diagrams: later update ISP Admin plan change request review activity and sequence flow.

Next backend work:

- Step 22 final cleanup/review, then continue to the next roadmap phase.
- Likely next major backend phase: reports and analytics, unless we choose to do final backend quality cleanup first.


---

## Step 23 Progress - 2026-05-16

### Step 23A - ISP Admin Analytics Summary Foundation

Completed and tested:

- Added ISP Admin analytics summary endpoint:
  - `GET /api/v1/isp-admin/analytics/summary`
- Added optional period filters:
  - `period_start`
  - `period_end`
- Added ISP Admin analytics response schema.
- Added ISP Admin analytics service logic.
- Analytics summary returns:
  - total users
  - active users
  - total subscriptions
  - active subscriptions
  - total routers
  - active routers
  - pending/approved/rejected plan change request counts
  - total/unread/critical alert counts
  - total/new/accepted recommendation counts
  - total usage in MB and GB
- Security/isolation:
  - analytics data is scoped by `current_admin.isp_id`
  - usage, alerts, recommendations, subscriptions, and plan change request counts are scoped through the linked App User ISP
  - router counts are scoped by `Router.isp_id`
- Added focused integration test for:
  - analytics counts
  - usage period filtering
  - cross-ISP isolation
- Endpoint smoke test passed through FastAPI route.

Validation completed:

- Import checks passed.
- New integration test passed.
- Full pytest suite passed.
- Compile check passed.
- Endpoint smoke test passed.

Impact:

- Database schema: no change.
- Existing data: read-only analytics endpoint, no migration or data rewrite.
- GitHub: Step 23A endpoint, schema, service, and test changed.
- SE diagrams: later update ISP Admin dashboard/reporting analytics flow.

Next backend work:

- Step 23B: report generation/list/detail using the existing `reports` table.
- Likely endpoints:
  - `POST /api/v1/isp-admin/reports`
  - `GET /api/v1/isp-admin/reports`
  - `GET /api/v1/isp-admin/reports/{report_id}`


---

## Step 23 Progress - 2026-05-16

### Step 23B - ISP Admin Stored Report Generation/List/Detail

Completed and tested:

- Added ISP Admin report endpoints:
  - `POST /api/v1/isp-admin/reports`
  - `GET /api/v1/isp-admin/reports`
  - `GET /api/v1/isp-admin/reports/{report_id}`
- Added ISP Admin report schemas:
  - `ISPAdminReportCreateRequest`
  - `ISPAdminReportResponse`
  - `ISPAdminReportType`
- Added ISP Admin report service logic for:
  - generating a stored report
  - listing reports under the current ISP
  - viewing one report under the current ISP
- MVP report generation uses the existing valid database report type:
  - `usage_report`
- The generated report stores analytics summary data inside `reports.report_data` as JSONB:
  - `summary_type = usage_analytics_summary`
  - `summary = analytics summary payload`
- No Alembic migration was needed because the existing `reports` table already supports JSONB `report_data`.
- The database report type constraint allows `usage_report`, so Step 23B uses that instead of inventing a new `analytics_summary` report type.
- Security/isolation:
  - reports are scoped by `Report.isp_id`
  - ISP Admins can only list/view reports from their own ISP
  - generated reports use `current_admin.isp_id`
- Added integration tests for:
  - report generation
  - stored report JSON payload
  - report list/detail
  - cross-ISP report isolation
- Endpoint smoke test passed through FastAPI route.

Validation completed:

- Import checks passed.
- Report table constraints checked.
- New integration tests passed.
- Full pytest suite passed.
- Compile check passed.
- Endpoint smoke test passed.

Impact:

- Database schema: no change.
- Existing data: reports are created only when endpoint is called.
- GitHub: Step 23B endpoint, schemas, services, and tests changed.
- SE diagrams: later update ISP Admin report generation/list/detail sequence and activity flow.

Next backend work:

- Step 23C: expand report types or add report analytics polish.
- Possible next report types using existing allowed DB values:
  - `device_report`
  - `alert_report`
  - `recommendation_report`
  - `network_performance_report`


---

## Step 23 Progress - 2026-05-16

### Step 23C - Expanded Stored Report Types

Completed and tested:

- Expanded ISP Admin stored report generation to support all existing database-allowed report types:
  - `usage_report`
  - `device_report`
  - `alert_report`
  - `recommendation_report`
  - `network_performance_report`
- No Alembic migration was needed because these report types already exist in the `reports` table constraint.
- `usage_report` continues to store usage analytics summary data.
- `alert_report` stores:
  - total alerts
  - unread alerts
  - critical alerts
  - counts by alert type
  - counts by severity
- `recommendation_report` stores:
  - total recommendations
  - counts by recommendation status
  - counts by recommendation type
- `device_report` stores:
  - total devices
  - connected devices
  - trusted devices
  - untrusted devices
  - counts by device status
  - counts by device type
- `network_performance_report` stores:
  - total routers
  - active routers
  - inactive routers
  - total usage MB/GB
  - router action counts by status
  - router action counts by action type
- Security/isolation:
  - all report data remains scoped by `current_admin.isp_id`
  - device reports scope through App User ISP ownership
  - router/network reports scope through Router ISP ownership
- Added integration tests for expanded report types.
- Endpoint smoke test passed through FastAPI routes for all report types.

Validation completed:

- Import checks passed.
- Expanded report type integration test passed.
- Full pytest suite passed.
- Compile check passed.
- Endpoint smoke test passed.

Impact:

- Database schema: no change.
- Existing data: no migration or rewrite.
- GitHub: report schema, report service, and expanded report test changed.
- SE diagrams: later update ISP Admin report generation flow to mention multiple report types.

Next backend work:

- Step 23D: Reports and analytics final cleanup/review.
- Then Step 24: backend/demo readiness before frontend integration.


---

## Step 23 Progress - 2026-05-16

### Step 23C - Expanded Stored Report Types

Completed and tested:

- Expanded ISP Admin stored report generation to support all existing database-allowed report types:
  - `usage_report`
  - `device_report`
  - `alert_report`
  - `recommendation_report`
  - `network_performance_report`
- No Alembic migration was needed because these report types already exist in the `reports` table constraint.
- `usage_report` continues to store usage analytics summary data.
- `alert_report` stores:
  - total alerts
  - unread alerts
  - critical alerts
  - counts by alert type
  - counts by severity
- `recommendation_report` stores:
  - total recommendations
  - counts by recommendation status
  - counts by recommendation type
- `device_report` stores:
  - total devices
  - connected devices
  - trusted devices
  - untrusted devices
  - counts by device status
  - counts by device type
- `network_performance_report` stores:
  - total routers
  - active routers
  - inactive routers
  - total usage MB/GB
  - router action counts by status
  - router action counts by action type
- Security/isolation:
  - all report data remains scoped by `current_admin.isp_id`
  - device reports scope through App User ISP ownership
  - router/network reports scope through Router ISP ownership
- Added integration tests for expanded report types.
- Endpoint smoke test passed through FastAPI routes for all report types.

Validation completed:

- Import checks passed.
- Expanded report type integration test passed.
- Full pytest suite passed.
- Compile check passed.
- Endpoint smoke test passed.

Impact:

- Database schema: no change.
- Existing data: no migration or rewrite.
- GitHub: report schema, report service, and expanded report test changed.
- SE diagrams: later update ISP Admin report generation flow to mention multiple report types.

Next backend work:

- Step 23D: Reports and analytics final cleanup/review.
- Then Step 24: backend/demo readiness before frontend integration.


---

## Step 24 Progress - 2026-05-16

### Step 24A - Backend Readiness Checklist and Stale Docs Cleanup

Completed:

- Confirmed Step 23 is complete:
  - Step 23A ISP Admin analytics summary
  - Step 23B stored reports
  - Step 23C expanded report types
  - Step 23D final cleanup/review
- Started Step 24 backend/demo readiness phase.
- Verified production settings guardrails:
  - strong non-placeholder SECRET_KEY required when DEBUG=False
  - wildcard CORS blocked when DEBUG=False
  - DATA_ENCRYPTION_KEY required when DEBUG=False
- Verified CORS middleware is wired through BACKEND_CORS_ORIGINS.
- Verified API router and FastAPI app imports.
- Checked for accidental Step 24 temp files.
- Checked for accidental Step 24 migrations.
- Ran tests and compile checks.

Impact:

- Database schema: no change.
- Existing data: no change.
- GitHub: docs/readiness status update only.
- SE diagrams: no change yet.

Next backend work:

- Step 24B: create API contract snapshot for frontend integration.
- Step 24C: create demo seed/readiness helper.
- Step 24D: final backend review package before Codex review.


---

## Step 24 Progress - 2026-05-16

### Step 24B - API Contract Snapshot for Frontend Integration

Completed:

- Generated `docs/API_CONTRACT.md` from FastAPI OpenAPI.
- The contract groups backend routes by OpenAPI tags.
- The contract includes:
  - HTTP method
  - path
  - intended frontend area
  - auth guidance
  - request body schema summary
  - response status codes
  - endpoint summary
- Added frontend integration notes for:
  - shared auth
  - Platform Admin dashboard
  - ISP Admin dashboard
  - Mobile App
  - deployment/CORS
- This gives the future frontend/mobile work a stable backend API reference.

Validation completed:

- Generated API contract successfully.
- Full pytest suite passed.
- Compile check passed.

Impact:

- Database schema: no change.
- Existing data: no change.
- GitHub: added API contract documentation.
- SE diagrams: no direct change.

Next backend work:

- Step 24C: demo seed/readiness helper.
- Step 24D: final backend review package before Codex review.


---

## Step 24 Progress - 2026-05-16

### Step 24C - Demo Seed and Readiness Helper

Completed:

- Added local demo seed helper:
  - `scripts/seed_demo_data.py`
- The helper refuses to run when `DEBUG=False`.
- The helper supports:
  - dry run by default
  - actual write only with `--apply`
- Demo data includes:
  - Platform Admin demo account
  - ISP Admin demo account
  - App User demo account
  - Demo ISP
  - demo subscription plans
  - active user subscription
  - demo router
  - demo devices
  - demo usage records
  - demo alerts
  - demo recommendation
  - demo pending plan change request
- Demo accounts use `mfa_required=False` and `mfa_enabled=False` so frontend/demo login returns a normal JWT without requiring MFA setup.
- Fixed script import path so the script can run directly from the `scripts/` folder.
- Corrected demo alert values to match database constraints:
  - `new_device_connected`
  - `critical`
- Corrected demo email domain from `.local` to `pulsefi-demo.com` because the response email validator rejects `.local`.
- Demo credentials:
  - Platform Admin: `platform.demo@pulsefi-demo.com`
  - ISP Admin: `isp.demo@pulsefi-demo.com`
  - App User: `user.demo@pulsefi-demo.com`
  - password: `PulseFiDemo123!`

Validation completed:

- Script compile check passed.
- Dry run passed.
- Demo seed apply passed.
- Demo App User login passed.
- Demo ISP Admin login passed.
- Demo Platform Admin login passed.
- Full pytest suite passed.
- Compile check passed.

Impact:

- Database schema: no change.
- Existing data: demo data is created/updated only when the script is run with `--apply`.
- GitHub: added demo seed helper.
- SE diagrams: no direct change.

Next backend work:

- Step 24D: final backend review package before Codex review.


---

## Step 24 Progress - 2026-05-16

### Step 24D - Final Backend Review Package Before Codex

Completed:

- Added final backend review package:
  - docs/BACKEND_REVIEW_PACKAGE.md
- Added standalone Codex review prompt:
  - docs/CODEX_REVIEW_PROMPT.md
- Review package summarizes:
  - current backend status
  - completed Step 22/23/24 readiness work
  - active security rules
  - known risks
  - validation commands
  - recommended Codex review prompt
  - suggested next work after Codex
- Codex review should happen after Step 24D is committed and pushed, before frontend integration.

Impact:

- Database schema: no change.
- Existing data: no change.
- GitHub: review docs updated.
- SE diagrams: no direct change.

Next work:

- Run Codex backend improvement review.
- Fix P0/P1 issues from Codex.
- Then begin frontend integration.

