# PulseFi Backend Roadmap

## Current Position

Current phase: **Step 16 â€” ISP Admin management endpoints**.

Step 15 is complete and tested.

Recently completed:

- Step 14: Protected current-account route system.
- Step 15A: Platform Admin ISP management.
- Step 15B: Platform Admin ISP Admin invitations.
- Step 15C: Platform Admin ISP Admin account management.
- Step 15D: Platform Admin dashboard summary.
- Step 15E: Platform Admin pending ISP Admin invitation management.

Next step:

- Step 16: ISP Admin management endpoints.

---

## Completed Major Phases

### Phase 1 â€” Software Engineering Diagrams

Completed for now:

- Use Case Diagram.
- DFD Level 0.
- DFD Level 1.
- ER Diagram.
- User Activity Diagram.
- ISP Admin Activity Diagram.
- Sequence Diagrams.

The class diagram is skipped for now unless the developer decides to revisit it.

Pending future SE updates are listed near the bottom of this file.

### Phase 2 â€” Database Design

PostgreSQL database design is completed for now.

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

Auth columns added to `admins` and `app_users`:

- `username`
- `email_verified_at`
- `password_changed_at`
- `mfa_enabled`
- `mfa_required`
- `mfa_secret`
- `preferred_mfa_method`

### Phase 3 â€” Backend Foundation

Completed:

- FastAPI backend foundation.
- PostgreSQL async connection.
- SQLAlchemy async setup.
- Pydantic settings.
- JWT helpers.
- Argon2 password hashing.
- Health endpoint.
- Swagger docs.
- Modular backend folder structure.

### Phase 4 â€” SQLAlchemy Models

Completed and import-tested.

Core models:

- ISP
- Admin
- AppUser
- SubscriptionPlan
- UserSubscription
- Router
- Device
- DeviceConnectionLog
- UsageRecord
- Prediction
- Recommendation
- Alert
- DeviceNetworkPolicy
- RouterActionLog
- SubscriptionChangeRequest
- Report

Auth models:

- AccountInvitation
- EmailVerificationToken
- PasswordResetToken
- MFABackupCode
- MFAChallenge

### Phase 5 â€” Auth Schemas

Completed and split under `app/schemas/auth/`.

Modules:

- `common.py`
- `login.py`
- `mfa.py`
- `invitation.py`
- `password_reset.py`
- `email_verification.py`
- `current_user.py`

### Phase 6 â€” Auth Services

Completed and split under `app/services/`.

Auth-related services:

- `account_service.py`
- `auth_service.py`
- `mfa_service.py`
- `invitation_service.py`
- `password_reset_service.py`
- `email_verification_service.py`

The project should continue using focused service modules instead of large mixed files.

### Phase 7 â€” Auth Endpoints

Completed under `app/api/v1/endpoints/auth/`.

Current auth endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/auth/invitations/accept`
- `POST /api/v1/auth/password/forgot`
- `POST /api/v1/auth/password/reset`
- `POST /api/v1/auth/email/verify`

### Step 14 â€” Protected Route System

Completed:

- Bearer token extraction.
- JWT decoding.
- Current account loading.
- Admin/app-user dependency guards.
- Role guard helper.
- `GET /api/v1/auth/me`.
- Token invalidation after `password_changed_at`.

### Step 15 â€” Platform Admin Endpoints

Completed and tested.

#### Step 15A â€” Platform Admin ISP Management

- Create ISP.
- List ISPs.
- Get one ISP.
- Update ISP information/status.

#### Step 15B â€” Platform Admin ISP Admin Invitations

- Create ISP Admin invitation.
- Return development invitation token only while `DEBUG=True`.
- Invited ISP Admin accepts invitation through the auth invitation endpoint.
- ISP Admin account is created and linked to the correct ISP.

#### Step 15C â€” Platform Admin ISP Admin Account Management

- View one ISP Admin.
- Update ISP Admin full name, phone number, and status.
- Deactivate/reactivate ISP Admin.
- Protected by `platform_admin` role only.

#### Step 15D â€” Platform Admin Dashboard Summary

Endpoint:

- `GET /api/v1/platform-admin/summary`

Returns counts for ISPs, ISP Admins, and App Users by status.

#### Step 15E â€” Platform Admin Pending Invitation Management

Endpoints:

- `GET /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admin-invitations/{invitation_id}/revoke`

Behavior:

- List ISP Admin invitations for an ISP.
- Filter invitations by pending, accepted, revoked, or expired.
- Revoke pending ISP Admin invitations.
- Revoked invitations cannot be accepted.
- Revocation keeps audit history by setting `revoked_at`.

---

## Step 16 â€” ISP Admin Management Endpoints

Goal:

Build ISP Admin management features.

Core rule:

- ISP Admin manages only their own ISP's data.
- ISP Admin cannot create ISPs.
- ISP Admin cannot invite or manage ISP Admin accounts.
- ISP Admin cannot access other ISPs' data.

Expected endpoint areas:

- App user invitations.
- App user management.
- Subscription plan management.
- User subscription assignment.
- Router management.
- ISP-scoped dashboard/list endpoints.

Possible endpoint groups:

- `/isp-admin/users`
- `/isp-admin/invitations`
- `/isp-admin/plans`
- `/isp-admin/subscriptions`
- `/isp-admin/routers`

Tasks:

1. Add ISP Admin protected route package.
2. Add invite app user endpoint.
3. Add list users endpoint.
4. Add user detail endpoint.
5. Add update/deactivate user endpoint if needed.
6. Add create/list/update subscription plans.
7. Add assign subscription endpoint.
8. Add list subscriptions endpoint.
9. Add add/update router endpoint.
10. Add assign router to subscription endpoint.
11. Add tests/import checks.

SE update impact:

This affects ISP Admin use cases and activity diagrams.

---

## Step 17 â€” User Mobile App Endpoints

Goal:

Build backend endpoints needed by the React Native mobile app.

App User can:

- View own subscriptions.
- View usage.
- View devices.
- View alerts.
- View predictions.
- View recommendations.
- Request plan changes.
- Apply device policies.

Possible endpoint groups:

- `/me/subscriptions`
- `/me/usage`
- `/me/devices`
- `/me/alerts`
- `/me/predictions`
- `/me/recommendations`
- `/me/plan-change-requests`
- `/me/device-policies`

Important behavior:

- If the user has one subscription, show it directly.
- If the user has multiple subscriptions, allow subscription selection.
- Device-level features depend on router capability.

SE update impact:

This affects user activity diagrams, sequence diagrams, and DFD flows.

---

## Step 18 â€” Router Adapter and Simulator Layer

Goal:

Create a realistic router integration structure.

Do not hard-code one router type everywhere.

Tasks:

1. Create router adapter interface.
2. Create simulator adapter.
3. Add router capability checking.
4. Add router action result format.
5. Add service for applying device policy through adapter.
6. Add router action logging.
7. Add failure handling.
8. Add capability-based feature availability.
9. Prepare structure for first real router integration later.

Simulator should support demo features:

- Connected devices.
- Total usage.
- Per-device usage.
- New device events.
- Bandwidth limit simulation.
- Device priority simulation.

SE update impact:

This affects system architecture, DFD wording, sequence diagrams, ERD attributes, and deployment explanation.

---

## Step 19 â€” Usage Data Ingestion

Goal:

Add usage data flow.

Start with demo seed/simulator data, then later connect to real router data.

Tasks:

1. Add simulator usage generation.
2. Store total usage records.
3. Store device usage when available.
4. Store connected device records.
5. Store device connection logs.
6. Add ingestion service.
7. Add scheduled/manual ingestion trigger for MVP.
8. Add tests/import checks.

SE update impact:

This affects DFD data flows and sequence diagrams.

---

## Step 20 â€” Alerts System

Goal:

Generate useful alerts.

Alert types:

- High usage alert.
- New device connected alert.
- Plan exceed risk alert.
- Policy failed alert.

Tasks:

1. Add alert generation service.
2. Add high usage rule.
3. Add new device detection rule.
4. Add plan exceed risk alert.
5. Add policy failed alert.
6. Add alert read/list endpoints.
7. Add mark alert as read endpoint if needed.
8. Add tests/import checks.

SE update impact:

This affects alert flows in DFD, activity diagrams, and sequence diagrams.

---

## Step 21 â€” Prediction and Recommendation Logic

Goal:

Add smart analysis.

Start with rule-based/statistical logic before full ML.

Prediction tasks:

1. Calculate average daily usage.
2. Estimate end-of-cycle usage.
3. Predict plan exceed risk.
4. Store prediction records.
5. Connect predictions to alerts when needed.

Recommendation tasks:

1. Compare predicted usage with current plan.
2. Recommend upgrade if plan is too small.
3. Recommend downgrade if plan is too large.
4. Recommend staying on current plan if suitable.
5. Store reason.
6. Store confidence score.
7. Link recommendation to prediction when useful.

SE update impact:

This affects smart features, DFD, sequence diagrams, and documentation.

---

## Step 22 â€” Reports and Analytics

Goal:

Build ISP Admin reporting and analytics.

Report types:

- Usage report.
- Device report.
- Recommendation summary.
- Network performance summary.
- Router action log report.

Tasks:

1. Add report generation service.
2. Store report data as JSONB.
3. Add report list endpoint.
4. Add report detail endpoint.
5. Add generate report endpoint.
6. Add analytics summary endpoint.
7. Add tests/import checks.

SE update impact:

This affects ISP Admin flow and report generation sequence diagram.

---

## Step 23 â€” Frontend Integration

Goal:

Connect backend with frontend apps.

Frontends:

- React Native mobile app for regular users.
- ISP Admin web dashboard.
- Platform Admin web dashboard.

Recommended order:

1. Admin web basics.
2. Auth screens.
3. Invitation acceptance screens.
4. Login/MFA/forgot-password screens.
5. User management screens.
6. Plan management screens.
7. Subscription/router management screens.
8. Mobile user dashboard.
9. Mobile usage screens.
10. Mobile devices screens.
11. Mobile alerts screens.
12. Mobile predictions/recommendations screens.
13. Device policy action screens.

Important design rule:

Frontend should show/hide features depending on router capabilities.

---

## Step 24 â€” Deployment Preparation

Goal:

Prepare PulseFi for presentation/demo deployment.

Tasks:

1. Production environment variables.
2. Production PostgreSQL database.
3. Email service setup.
4. Production CORS settings.
5. Logging.
6. Error handling.
7. Security hardening.
8. Hosting backend.
9. Hosting web dashboards.
10. Mobile app build/testing.
11. Demo seed data.
12. Router simulator demo mode.
13. Deployment documentation.
14. Final presentation/demo flow.

Security checks:

- No secrets committed to GitHub.
- `.env` stays local.
- `.env.example` contains only safe placeholders.
- Passwords hashed.
- Reset tokens hashed.
- Backup codes hashed.
- MFA secret encryption planned/implemented before production.
- CORS locked down for production.

---

## Pending Software Engineering Updates

These should be batch-updated later in diagrams/documentation:

1. Invitation-based onboarding.
2. Email verification.
3. Forgot password.
4. Username/email login.
5. MFA/2FA.
6. Backup recovery codes.
7. Router adapter/capability model.
8. Subscription change request flow.
9. Multiple active subscriptions per user.
10. Router linked to subscription.
11. One subscription may have multiple routers.
12. Router simulator for MVP/demo.
13. Capability-based feature availability.
14. Platform Admin dashboard and ISP Admin management separation.
15. ISP Admin scoped access rule.

---

## Important Project Priority

The project must stay deployable by presentation time.

Prefer:

- Working MVP.
- Reliable demo.
- Clean backend.
- Clear frontend flow.
- Realistic router support.
- Simulator fallback.
- Secure auth.
- Good explanation.

Avoid:

- Overcomplicating before the MVP works.
- Pretending all routers are supported.
- Building huge messy files.
- Adding features that cannot be demonstrated.
- Changing database schema without reason.

---

## Backend Quality Progress Log

### 2026-05-14 — Limited DB Role and Alembic Baseline

Completed:

- Limited PostgreSQL role `pulsefi_app` was created and tested.
- Backend local `.env` was changed to use `pulsefi_app` instead of the `postgres` superuser.
- Database connection test confirmed: backend connects as `pulsefi_app`.
- Alembic was initialized with `alembic.ini` and `alembic/`.
- Alembic `env.py` was configured for the existing async SQLAlchemy setup.
- Alembic baseline revision was created: `c384b4d102bc_baseline_existing_database_schema.py`.
- Baseline migration intentionally has empty `upgrade()` and `downgrade()` because the real database schema already exists.
- Existing database was stamped as current Alembic head: `c384b4d102bc`.
- `alembic current` confirmed: `c384b4d102bc (head)`.

Impact:

- Database schema: only Alembic tracking table `alembic_version` was added/used.
- Existing PulseFi app tables: no change.
- Existing data: no change.
- SE diagrams: no immediate update needed because this is backend infrastructure, not user-facing behavior.

Future permission hardening reminder:

- `pulsefi_app` currently has enough permission to support local development and Alembic setup.
- Before production, revisit DB permissions.
- Preferred production design:
  - runtime backend role with only needed app permissions
  - separate migration role for Alembic schema changes
- Do not forget to reduce unnecessary schema-creation permissions for the runtime app role later.

Next quality improvements after this:

1. Add automated tests with `pytest` and `httpx`.
2. Add GitHub Actions CI.
3. Add structured logging.
4. Standardize API error responses.
5. Add seed/demo data.
6. Add production deployment documentation.

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
