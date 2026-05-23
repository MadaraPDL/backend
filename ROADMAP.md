<!-- PULSEFI_SYNC_START -->
## Current Synchronized PulseFi Checkpoint - 2026-05-23

Current phase: **Step 44C complete - deployed admin web connected to Render backend**.

Completed before deployment:
- Step 41 admin auth/lifecycle/layout polish is complete.
- Step 42A App User service request backend/mobile flow is complete.
- Step 42B mobile MFA setup + service request polish is complete.
- Step 42C LAN smoke test and router/service-line polish is complete.
- Step 42D ISP Admin Operations context and actionable reports polish is complete.
- Step 42E local demo data cleanup is complete.
- Step 42F final LAN presentation smoke test passed.
- Step 43A mobile selected-router context across Home/Usage/Devices/Alerts/Plan Request is complete.
- Step 43B mobile Insights selected-router polish is complete.
- Step 43C App User mobile MFA settings is complete.

Deployment status:
- Railway deployment was abandoned.
- Current stack is:
  - Neon PostgreSQL database.
  - Render backend web service.
  - Vercel admin web.
  - Expo/EAS mobile later.
- Neon async database URL handling was fixed for asyncpg:
  - `postgresql://` is converted to `postgresql+asyncpg://`.
  - `sslmode=require` is converted to `ssl=require`.
  - `channel_binding=require` is removed.
- `app/db/session.py` and `alembic/env.py` use `settings.async_database_url()`.
- Alembic migration against Neon reached latest head.
- First deployed Platform Admin was created in Neon.
- Render backend was deployed successfully.
- Vercel admin web was deployed successfully.
- Vercel admin web uses `VITE_API_BASE_URL=https://<render-backend>/api/v1`.
- Admin login from a phone outside the local network worked, confirming the deployed admin web can reach the deployed backend.

Current first-deploy settings:
- `DEBUG=True`
- `EMAIL_DELIVERY_ENABLED=False`
- `ENABLE_INTELLIGENCE_SCHEDULER=False`
- SMTP is intentionally off for first deployment.
- Authenticator MFA works without SMTP.
- Email MFA, invitations, and password reset email delivery still need SMTP before production-style mode.

Active rules:
- Never commit `.env`, database URLs, JWT secrets, SMTP passwords, Neon passwords, Render secrets, or Vercel secrets.
- ISP Admin endpoints must use `get_current_isp_admin`.
- Every ISP Admin query must be scoped by `current_admin.isp_id`.
- App User `/me` endpoints must use `get_current_app_user`.
- Current-account `/auth/me/...` endpoints must only affect the signed-in account.
- MFA settings changes must require verification before sensitive enable/disable actions.
- Do not expose local DEBUG tokens/codes in real admin web or mobile UI.
- Do not store raw router passwords, ISP API keys, or RADIUS credentials until encrypted credential storage exists.

Next recommended phase:
- Step 44D: configure mobile app to use the deployed backend.
- Step 44E: enable SMTP later and switch toward production-style settings.
- Step 43D final full smoke test remains intentionally postponed until backend, admin web, and mobile are all deployed/configured.
<!-- PULSEFI_SYNC_END -->

# PulseFi Backend Roadmap

## Current Position

Current phase: **Step 26 complete - final backend hardening before frontend integration**.

Step 16 through Step 26 are complete and tested for the MVP/demo backend.

Completed latest readiness work:

- Step 24A: Backend readiness checklist and stale docs cleanup.
- Step 24B: API contract snapshot for frontend integration.
- Step 24C: Demo seed and readiness helper.
- Step 24D: Final backend review package before Codex/frontend work.
- Step 25A: Migration integrity hardening.
- Step 25B: Standard API error response foundation.
- Step 25C: Auth rate limits tightened to 5 attempts per 15 minutes.
- Step 25D: API contract refreshed for standard errors and rate limits.
- Step 25E: Final docs/status alignment.
- Step 26A-E: Codex P1 backend fixes.
- Step 26F: Remaining P2/P3 quality hardening before frontend integration.

Next step:

- Start frontend integration for Platform Admin dashboard, ISP Admin dashboard, and App User mobile app.

Current frontend checkpoint:

- Step 27C completed locally for the admin web app:
  - real admin app vs design preview mode split
  - shared admin login with `account_type: "admin"`
  - verified session restoration through `GET /api/v1/auth/me`
  - role-based routing for `platform_admin` and `isp_admin`
  - no App User admin role in production admin web
  - MFA verify and MFA setup-confirm flows wired to backend endpoints

- Step 27D added ISP Admin intelligence/dashboard integration:
  - `GET /api/v1/isp-admin/recommendations`
  - `GET /api/v1/isp-admin/recommendations/{recommendation_id}`
  - ISP Admin recommendation viewing stays scoped to `current_admin.isp_id`
  - the real Intelligence Center connects analytics, recommendations, reports, prediction generation, recommendation generation, and automatic intelligence runs
  - frontend API configuration remains `VITE_API_BASE_URL` with local fallback only
  - local `.env` files remain uncommitted

Backend rule during frontend integration:

- Fix discovered blockers, contract mismatches, or small safety issues.
- Regenerate or update docs/API_CONTRACT.md when endpoint behavior changes.
- Avoid large new backend feature expansion until the MVP frontend is connected.

---

## Completed Major Phases

### Phase 1 - Software Engineering Diagrams

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

### Phase 2 - Database Design

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

### Phase 3 - Backend Foundation

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

### Phase 4 - SQLAlchemy Models

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

### Phase 5 - Auth Schemas

Completed and split under `app/schemas/auth/`.

Modules:

- `common.py`
- `login.py`
- `mfa.py`
- `invitation.py`
- `password_reset.py`
- `email_verification.py`
- `current_user.py`

### Phase 6 - Auth Services

Completed and split under `app/services/`.

Auth-related services:

- `account_service.py`
- `auth_service.py`
- `mfa_service.py`
- `invitation_service.py`
- `password_reset_service.py`
- `email_verification_service.py`

The project should continue using focused service modules instead of large mixed files.

### Phase 7 - Auth Endpoints

Completed under `app/api/v1/endpoints/auth/`.

Current auth endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/auth/invitations/accept`
- `POST /api/v1/auth/password/forgot`
- `POST /api/v1/auth/password/reset`
- `POST /api/v1/auth/email/verify`

### Step 14 - Protected Route System

Completed:

- Bearer token extraction.
- JWT decoding.
- Current account loading.
- Admin/app-user dependency guards.
- Role guard helper.
- `GET /api/v1/auth/me`.
- Token invalidation after `password_changed_at`.

### Step 15 - Platform Admin Endpoints

Completed and tested.

#### Step 15A - Platform Admin ISP Management

- Create ISP.
- List ISPs.
- Get one ISP.
- Update ISP information/status.

#### Step 15B - Platform Admin ISP Admin Invitations

- Create ISP Admin invitation.
- Return development invitation token only while `DEBUG=True`.
- Invited ISP Admin accepts invitation through the auth invitation endpoint.
- ISP Admin account is created and linked to the correct ISP.

#### Step 15C - Platform Admin ISP Admin Account Management

- View one ISP Admin.
- Update ISP Admin full name, phone number, and status.
- Deactivate/reactivate ISP Admin.
- Protected by `platform_admin` role only.

#### Step 15D - Platform Admin Dashboard Summary

Endpoint:

- `GET /api/v1/platform-admin/summary`

Returns counts for ISPs, ISP Admins, and App Users by status.

#### Step 15E - Platform Admin Pending Invitation Management

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

## Step 16 - ISP Admin Management Endpoints

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

## Step 17 - User Mobile App Endpoints

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

## Step 18 - Router Adapter and Simulator Layer

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

## Step 19 - Usage Data Ingestion

Goal:

Add usage data flow.

Start with demo seed/simulator data, then later connect to real router data.

Tasks:

1. Add simulator usage generation.
2. Store total usage records.git status
3. Store device usage when available.
4. Store connected device records.
5. Store device connection logs.
6. Add ingestion service.
7. Add scheduled/manual ingestion trigger for MVP.
8. Add tests/import checks.

SE update impact:

This affects DFD data flows and sequence diagrams.

---

## Step 20 - Alerts System

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

## Step 21 - Prediction and Recommendation Logic

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

## Step 22 - Reports and Analytics

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

## Step 23 - Frontend Integration

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

## Step 24 - Deployment Preparation

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

### 2026-05-14 - Limited DB Role and Alembic Baseline

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

- 2026-05-10 - PostgreSQL database schema phase completed for the main PulseFi tables.
- 2026-05-10 - Core SQLAlchemy models completed and import-tested.
- 2026-05-11 - Authentication database update completed.
- 2026-05-11 - Authentication SQLAlchemy models completed and import-tested.
- 2026-05-11 - Authentication schemas completed.
- 2026-05-12 - Authentication services split into focused modules and import-tested.
- 2026-05-12 - Authentication endpoint package completed and Swagger/OpenAPI confirmed working.
- 2026-05-12 - Step 14 protected current-account route system completed.
- 2026-05-12 - Step 15 Platform Admin endpoint work completed through ISP/Admin management and summary features.
- 2026-05-13 - Backend foundation hardened for Step 16, including safer `.env.example`, production config validation, old-JWT invalidation after password reset, `get_current_isp_admin`, typo fixes, and `pyotp`.
- 2026-05-14 - Documentation cleanup completed for `README.md`, `ROADMAP.md`, and `AGENTS.md`.
- 2026-05-14 - Backend quality backlog added.
- 2026-05-14 - Limited PostgreSQL role `pulsefi_app` created and tested.
- 2026-05-14 - Alembic initialized, empty baseline migration created, and existing database stamped to revision `c384b4d102bc`.

Notes:

- Some earlier dates are -completed by this date- based on the project work log, not exact minute-by-minute timestamps.
- Future completed steps should be added here immediately after testing and before commit.

---

## Testing Progress - 2026-05-14

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

## CI Progress - 2026-05-14

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

## Step 16 Progress - 2026-05-14

### Step 16A - ISP Admin Router Foundation

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

## Step 16 Progress - 2026-05-14

### Step 16B - ISP Admin App User Invitation Endpoints

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

## Step 16 Testing Progress - 2026-05-14

### Step 16B - App User Invitation Endpoints Tested

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

## Step 16 Progress - 2026-05-14

### Step 16C - ISP Admin App User Management Endpoints

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

## Step 16 Progress - 2026-05-14

### Step 16D - ISP Admin Subscription Plan Management Endpoints

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

## Step 16 Progress - 2026-05-14

### Step 16E - ISP Admin User Subscription Assignment and Management Endpoints

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

- `pending` - assigned but not active yet
- `active` - currently active subscription
- `suspended` - temporarily stopped, such as unpaid bill/admin action
- `expired` - ended by date
- `cancelled` - permanently cancelled

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

## Step 16 Progress - 2026-05-14

### Step 16F - ISP Admin Router Management Endpoints

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

## Current Backend State - 2026-05-14

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

## Step 16G - ISP Admin Dashboard Summary

Completed:

- `GET /api/v1/isp-admin/summary`
- Real ISP-scoped dashboard counts for users, plans, subscriptions, and routers.
- Subscription counting uses join through `AppUser.isp_id`.
- No database schema change.

Step 16 status:

- Step 16A through Step 16G are complete and tested.
- Remaining Step 16 work: final cleanup/testing and docs.


---

## Step 17 Progress - 2026-05-14

### Step 17A - App User Mobile Endpoint Foundation

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

## Step 17 Progress - 2026-05-14

### Step 17B - App User Subscription Endpoints

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

## Step 17 Progress - 2026-05-14

### Step 17C - App User Router and Device View Endpoints

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

- Step 17D - App User usage endpoints.
- Required usage behavior:
  - total usage for the logged-in user
  - download/upload/total usage
  - per-device usage
  - per-router or per-subscription filtering
  - raw usage records for charts/history

---

### Step 17E - App User Alert Endpoints

Completed on 2026-05-15.

Endpoints:

- GET /api/v1/me/alerts
- GET /api/v1/me/alerts/{alert_id}
- PATCH /api/v1/me/alerts/{alert_id}/read

Behavior:

- App Users can list their own alerts.
- App Users can view one alert by ID.
- App Users can mark one alert as read.
- All alert queries are scoped by the authenticated App User.
- App User routes do not accept user_id from the request.

Next:

- Step 17F - App User predictions/recommendations endpoints or plan change request endpoints.

---

### Step 17F - App User Prediction and Recommendation Endpoints

Completed on 2026-05-15.

Endpoints:

- GET /api/v1/me/predictions
- GET /api/v1/me/predictions/{prediction_id}
- GET /api/v1/me/recommendations
- GET /api/v1/me/recommendations/{recommendation_id}

Behavior:

- App Users can list their own predictions.
- App Users can view one prediction by ID.
- App Users can list their own recommendations.
- App Users can view one recommendation by ID.
- All queries are scoped by the authenticated App User.
- App User routes do not accept user_id from the request.

Next:

- Step 17G - App User subscription plan change request endpoints.

---

### Step 17G - App User Plan Change Request Endpoints

Completed on 2026-05-15.

Endpoints:

- POST /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests/{request_id}

Behavior:

- App Users can create subscription plan change requests.
- App Users can list their own requests.
- App Users can view one request by ID.
- All queries are scoped by the authenticated App User.
- Requested plan must differ from the current plan.
- Requested plan must belong to the same ISP.

Next:

- Step 17H - App User device policy endpoints.

---

### Step 17H - App User Device Policy Endpoints

Completed on 2026-05-15.

Endpoints:

- POST /api/v1/me/device-policies
- GET /api/v1/me/device-policies
- GET /api/v1/me/device-policies/{policy_id}

Behavior:

- App Users can create device network policy requests.
- App Users can list their own device policy requests.
- App Users can view one device policy request by ID.
- All queries are scoped by the authenticated App User.
- Device ownership validation enforced before policy creation.
- Device policy requests remain pending until router execution layer implementation.

Next:

- Step 18 - Router adapter and simulator layer.

---

## Historical Current State Update - 2026-05-15

Historical backend position at that time: **Step 18 - Router adapter and simulator layer**.

Recently completed:
- Step 16: ISP Admin management endpoints.
- Step 17: App User/mobile endpoints through device policy requests.
- Backend quality/security fixes:
  - MFA setup enforcement.
  - Real Alembic baseline migration.
  - GitHub Actions PostgreSQL + Alembic migration checks.
  - Production email delivery guards.
  - Auth API regression tests.

Next:
- Step 18A: Router adapter interface.
- Step 18B: Simulator router adapter.
- Step 18C: Service layer for router sync/action simulation.
- Step 18D: Safe API endpoints/logging around simulated router actions.

---

## Step 18 Progress - 2026-05-16

### Step 18A/18B - Router Adapter Interface and Simulator Adapter

Completed:

- Created router adapter architecture under `app/router_adapters/`.
- Added adapter interface contract.
- Added simulator adapter for reliable demo/testing.
- Added adapter registry.
- Simulator currently supports:
  - connected device listing
  - bandwidth limit simulation
  - device priority simulation
  - capability reporting

Testing:

- Router adapter import check passed.
- FastAPI app import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed: 40 tests passed.
- Integration tests used `pulsefi_test` through `TEST_DATABASE_URL`.

Next:

- Step 18C - Router adapter service layer for applying device policies and writing router action logs.

---

## Step 18 Progress - 2026-05-16

### Step 18C - Router Policy Execution Service

Completed:

- Added `app/services/router_actions/`.
- Added router policy execution service.
- Device network policies can now be executed through the router adapter registry.
- Simulator adapter is used for current execution.
- Router action logs are created for execution history.
- Policy status is updated to `applied` or `failed`.
- Non-pending policies are not executed again.

Testing:

- Router action service import check passed.
- FastAPI app import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests used `pulsefi_test` through `TEST_DATABASE_URL`.

Next:

- Step 18D - API endpoint for safely triggering pending device policy execution.

---

## Step 18 Progress - 2026-05-16

### Step 18D - App User Device Policy Execution Endpoint

Completed:

- Added endpoint:
  - `PATCH /api/v1/me/device-policies/{policy_id}/execute`
- Endpoint is protected by App User authentication.
- Endpoint verifies the policy belongs to the authenticated App User before execution.
- Endpoint only executes pending policies.
- Execution uses the router policy execution service.
- Current execution uses the simulator router adapter.
- Router action logs are created during execution.
- Execution response includes the updated policy and action log.

Testing:

- Device policy execution schema import check passed.
- Device policy endpoint import check passed.
- FastAPI app import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests used `pulsefi_test` through `TEST_DATABASE_URL`.

Next:

- Step 18E - Add visibility for router action logs, likely ISP Admin first, or add focused integration tests for policy execution.

---

## Step 18 Progress - 2026-05-16

### Step 18E - ISP Admin Router Action Log Visibility

Completed:

- Added ISP Admin router action log visibility.
- Added endpoints:
  - `GET /api/v1/isp-admin/router-action-logs`
  - `GET /api/v1/isp-admin/router-action-logs/{action_log_id}`
- Router action log access is scoped through `Router.isp_id`.
- ISP Admins can only see logs for routers under their own ISP.
- Supported filters:
  - router ID
  - policy ID
  - status
  - action type
  - pagination

Testing:

- Router action log schema import check passed.
- Router action log service import check passed.
- Router action log endpoint import check passed.
- FastAPI app import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests used `pulsefi_test` through `TEST_DATABASE_URL`.

Next:

- Step 18F - Add focused tests for router action execution and ISP Admin router action log isolation, or add router capability visibility endpoint.

---

## Step 18 Progress - 2026-05-16

### Step 18F - Router Policy Execution and Router Action Log Integration Tests

Completed:

- Added focused integration tests for router policy execution.
- Added focused integration tests for ISP Admin router action log isolation.
- Confirmed policy execution creates router action logs.
- Confirmed policy status updates to `applied` after simulator success.
- Confirmed ISP Admins cannot access router action logs from another ISP.
- Fixed simulator adapter typo caught by the new test:
  - changed `succe=True` to `success=True`

Testing:

- Focused router action integration test passed.
- Full pytest suite passed.
- Tests used `pulsefi_test` through `TEST_DATABASE_URL`.

Next:

- Step 18G - Add router capability visibility endpoint or Step 18 cleanup before Step 19 usage ingestion.

---

## Step 18 Progress - 2026-05-16

### Step 18G - App User Router Capability Visibility Endpoint

Completed:

- Added endpoint:
  - `GET /api/v1/me/routers/{router_id}/capabilities`
- Added App User router capability response schema.
- Added service helper for reading capabilities from the router adapter registry.
- Current capability source is the simulator adapter.
- Endpoint is App User protected.
- Endpoint only returns capabilities for routers owned by the authenticated App User.
- Capability response helps the frontend decide which router features to show or disable.

Testing:

- Router capabilities schema import check passed.
- Router capabilities service import check passed.
- App User router endpoint import check passed.
- FastAPI app import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests used `pulsefi_test` through `TEST_DATABASE_URL`.

Next:

- Step 18 cleanup/docs, then Step 19 - usage data ingestion and simulator usage generation.

---

## Step 19 Progress ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Usage Data Ingestion

### Step 19A/19B ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Completed

Completed:

- Added simulator usage ingestion service.
- Added ISP Admin manual ingestion trigger endpoint:
  - `POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator`
- Usage records are tied to:
  - App User
  - User Subscription
  - Router
  - Device when available
- Endpoint is ISP-scoped through the authenticated ISP Admin.
- App User usage endpoints can read the generated simulator usage.

Next:

- Step 19C: simulator connected-device ingestion/update and connection logs.

---

## Step 19 Progress - Connected Device Ingestion

### Step 19C - Completed

Completed:

- Added simulator connected-device ingestion service.
- Added ISP Admin manual endpoint:
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices
- Simulator creates or updates demo devices for a router.
- Simulator creates device connection logs.
- Endpoint is scoped to the authenticated ISP Admin's ISP.

Next:

- Step 19D: combined simulator ingestion flow or ISP Admin device connection log visibility.

---

## Step 19 Progress - Connected Device Ingestion

### Step 19C - Completed

Completed:

- Added simulator connected-device ingestion service.
- Added ISP Admin manual endpoint:
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices
- Simulator creates or updates demo devices for a router.
- Simulator creates device connection logs.
- Endpoint is scoped to the authenticated ISP Admin's ISP.

Next:

- Step 19D: combined simulator ingestion flow or ISP Admin device connection log visibility.

---

## Step 19 Progress - Combined Simulator Ingestion

### Step 19D - Completed

Completed:

- Added combined simulator ingestion service.
- Added ISP Admin manual endpoint:
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/run
- The combined endpoint runs connected-device ingestion first.
- The combined endpoint runs usage ingestion second.
- This gives a one-click demo flow for router/device/usage simulator data.
- Simulator device connection logs use allowed event_type values.

Next:

- Step 19E: ISP Admin visibility for usage records and device connection logs.

---

## Step 19 Progress - ISP Admin Usage Visibility

### Step 19E - Completed

Completed:

- Added ISP Admin usage record visibility endpoints.
- Added ISP Admin device connection log visibility endpoints.
- Usage records are scoped through the router's ISP.
- Device connection logs are scoped through the router's ISP.
- These endpoints support the future ISP Admin dashboard.

Next:

- Step 19F: integration tests and Step 19 cleanup/finalization.

---

## Step 19 Finalization - Completed

Step 19 is complete.

Completed:

- Simulator usage ingestion.
- ISP Admin manual usage ingestion trigger.
- Simulator connected-device ingestion.
- Device connection log creation.
- Combined simulator ingestion flow.
- ISP Admin usage record visibility.
- ISP Admin device connection log visibility.
- Simulator ingestion regression tests.

Next phase:

- Step 20: Alerts system.

Expected Step 20 work:

- High usage alerts.
- New device connected alerts.
- Plan exceed risk alerts.
- Policy failed alerts.
- App User alert visibility improvements if needed.
- ISP Admin alert visibility if needed.


### Step 20A - Alert Generation Service

Completed:

- Added alert generation service.
- Added high usage alert.
- Added plan exceed risk alert.
- Added unusual consumption alert.
- Added new device connected alert.
- Connected alert generation to simulator ingestion.
- Updated `alerts.alert_type` database check constraint through Alembic.
- Confirmed App User alert list and mark-read flow work with generated alerts.

Pending:

- Generate `policy_failed` alerts from failed device policy/router action execution.
- Add ISP Admin alert visibility if needed.
- Add focused alert tests.


### Step 20B - Policy Failed Alerts

Completed:

- Failed device policy execution now generates a `policy_failed` alert for the App User.
- Router action type constraint was updated to support:
  - `bandwidth_limit`
  - `device_priority`
- Manual DB constraint update was needed locally because the runtime app DB role is not the owner of `router_action_logs`.

Pending:

- ISP Admin alert visibility if needed.
- Focused automated tests for alert generation and ownership isolation.


### Step 20C - ISP Admin Alert Visibility

Completed:

- Added read-only ISP Admin alert visibility.
- Added:
  - `GET /api/v1/isp-admin/alerts`
  - `GET /api/v1/isp-admin/alerts/{alert_id}`
- ISP Admins can view App User alerts under their own ISP.
- Queries are scoped through the App User ISP relationship.
- Admin-owned personal alerts are not part of the MVP yet.

Pending:

- Focused tests for alert generation.
- Ownership/isolation tests for App User and ISP Admin alert access.


### Step 20D - Alert Generation Tests

Completed:

- Added focused tests for `plan_exceed_risk` alert generation.
- Added focused tests for `policy_failed` alert generation.
- Added duplicate unread `policy_failed` alert prevention test.

Pending:

- App User alert ownership isolation tests.
- ISP Admin alert ISP isolation tests.
- New device and unusual consumption alert tests.


### Step 20E - Alert Ownership and ISP Isolation Tests

Completed:

- Added alert ownership/isolation tests.
- App User alert queries must include current user scope.
- ISP Admin alert queries must include ISP scope through App User.
- Extra filters keep ISP scoping intact.

Pending:

- New device alert generation test.
- Unusual consumption alert generation test.



### Step 21A - Prediction Foundation

Completed:

- Added rule-based usage prediction generation.
- Added ISP Admin endpoint to generate predictions for subscriptions.
- Stored predictions in the existing `predictions` table.
- Prediction estimates full-cycle usage from observed usage and average daily usage.
- App Users can view generated predictions through existing mobile prediction endpoints.

Pending:

- Step 21B: Generate recommendations from predictions.
- Step 21C: Connect high-risk predictions to alerts if needed.
- Step 21D: Add prediction/recommendation tests.


### Step 21B - Recommendation Foundation

Completed:

- Added rule-based recommendation generation from predictions.
- Added ISP Admin endpoint to generate recommendations from predictions.
- Stored recommendations in the existing `recommendations` table.
- App Users can view generated recommendations through existing mobile recommendation endpoints.
- Updated recommendation type database constraint for Step 21 recommendation types.

Pending:

- Step 21C: Add prediction/recommendation tests and isolation tests.
- Step 21D: Connect recommendations to subscription change request flow if needed.


### Step 21C - Prediction and Recommendation Tests

Completed:

- Added prediction generation tests.
- Added recommendation generation tests.
- Added duplicate recommendation prevention test.
- Added recommendation ISP-scope query test.
- Added App User prediction/recommendation ownership query tests.

Pending:

- Downgrade recommendation test.
- Monitor usage recommendation test.
- Optional subscription-change integration.


### Step 21D - Recommendation Cleanup Tests

Completed:

- Added downgrade recommendation path test.
- Added monitor usage recommendation path test.
- Recommendation test coverage now includes all MVP recommendation types:
  - `upgrade_plan`
  - `downgrade_plan`
  - `stay_current`
  - `monitor_usage`

Step 21 is now complete enough to move forward.

Pending optional work:

- Connect recommendations to subscription change requests.
- Add end-to-end API tests for prediction and recommendation generation.



---

## Step 21 Completion - 2026-05-16

Step 21 is complete enough to move forward.

Completed:

- Step 21A: Prediction generation foundation.
- Step 21B: Recommendation generation foundation.
- Step 21C: Prediction and recommendation service tests.
- Step 21D: Recommendation cleanup path tests.

Step 21 delivered:

- Rule-based usage prediction generation.
- Rule-based recommendation generation.
- App User visibility through existing prediction and recommendation endpoints.
- ISP Admin generation endpoints for predictions and recommendations.
- Focused tests for prediction math, recommendation paths, duplicate prevention, ownership scoping, and ISP scoping.

---

## Step 22 - Recommendation to Plan Change Request Integration

Goal:

Connect recommendation rows to the subscription change request flow.

Why:

- Step 21 generates recommendations.
- App Users can already create subscription change requests.
- The existing plan change request service already supports `recommendation_id`.
- Step 22 should make the flow complete:
  - user receives recommendation
  - user requests plan change based on recommendation
  - ISP Admin reviews the request
  - ISP Admin approves or rejects the request

Planned breakdown:

### Step 22A - Review existing plan change request flow

- Review App User plan change request endpoint.
- Review schema validation.
- Review ownership checks.
- Confirm recommendation-linked request behavior.

### Step 22B - ISP Admin plan change request visibility

- Add ISP Admin list/detail endpoints for subscription change requests.
- Scope all queries by `current_admin.isp_id`.

### Step 22C - ISP Admin approve/reject flow

- Add approve/reject endpoint.
- Approval should update the request status.
- Approval may update the user subscription plan if safe.
- Rejection should store/reuse a clear status and optional reason if supported by schema.

### Step 22D - Tests and docs

- Add service tests for ISP scoping.
- Add tests for approve/reject behavior.
- Update docs/memory after completion.

Important security rule:

- ISP Admins must only view or act on subscription change requests belonging to users under their own ISP.


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





## Current Roadmap Update ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Admin Frontend/Auth Handoff

### Completed / In Progress
- Admin frontend now has a separated design preview mode and real app mode.
- `npm run dev` is intended for the real admin web app.
- `npm run dev:design` is intended for UI/UX preview only.
- Real admin shell now has one shared login page.
- Frontend login now sends `account_type: "admin"` to `/api/v1/auth/login`.
- App User screens in the preview are design reference only for the later React Native mobile app.

### Next Required Work
1. Fix backend local-dev login blocker:
   - Investigate `429 rate_limited` during admin login.
   - Provide clean local reset or dev-safe handling.
   - Do not remove production rate-limit protection.

2. Finish real admin auth flow:
   - Confirm `/auth/login` response shape.
   - Confirm `/auth/me` response shape.
   - Ensure frontend can route by authenticated admin role.
   - Platform Admin should route to Platform Admin dashboard.
   - ISP Admin should route to ISP Admin dashboard.
   - No visible role switch in production.

3. Finish MFA frontend/backend flow:
   - Login should show MFA verification when backend returns MFA required.
   - Connect `/api/v1/auth/mfa/verify`.
   - Handle invalid/expired MFA codes.
   - Handle backup-code option if backend supports it.
   - Clarify behavior when `mfa_required=true` but `mfa_enabled=false`.

4. Convert design preview pages into production admin pages:
   - Replace mock data with API calls.
   - Add protected routes.
   - Add loading/error/empty states inside real pages.
   - Keep design hub dev-only.

5. Frontend pages to connect first:
   - Shared admin login
   - Platform Admin overview / ISPs / ISP admin invitations
   - ISP Admin overview / user invitations / subscriptions
   - Then routers, devices, usage, alerts, recommendations, reports.

6. Later phases:
   - React Native App User mobile app.
   - Router sync MVP.
   - Usage prediction/recommendations.
   - Deployment and final presentation polish.

## Current Backend Checkpoint ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Automatic Intelligence

Completed:
- Added `POST /api/v1/isp-admin/intelligence/run`.
- Added ISP-scoped automatic intelligence service.
- Added local/demo scheduler controlled by:
  - `ENABLE_INTELLIGENCE_SCHEDULER`
  - `INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES`
- Added idempotency protection:
  - Reuses today's prediction when it already exists.
  - Reuses existing recommendation for that prediction.
  - Avoids duplicate prediction/recommendation rows on repeated scheduler ticks.
- Verified scheduler behavior locally.
- Backend tests passed with scheduler disabled; only FastAPI `on_event` warnings remain.

Next Steps:
1. Cleanup leftover auth/rate-limit reset files and commit them if valid.
2. Convert FastAPI startup/shutdown `@app.on_event` hooks to lifespan to remove warnings.
3. Connect frontend Intelligence Center to `POST /api/v1/isp-admin/intelligence/run`.
4. Add better seeded tests for automatic intelligence.
5. Add prediction list endpoints if dashboard prediction history is needed.
6. Add simulator/demo controls to generate usage data from dashboard.
7. Review duplicate generated test/demo data and optionally add cleanup scripts.
8. Prepare production scheduling plan: worker/cron/queue instead of in-process scheduler.

## Admin Web UI/UX Checkpoint

Status: Complete

Completed:
- Final live admin UI cleanup.
- Platform Admin redundant invitation page removed.
- Platform Admin ISP Admin invitations merged into ISP Management.
- Platform Admin sidebar simplified.
- ISP Admin dashboard sections preserved.
- Dark/light theme support added to live admin app.
- Auth/login/MFA screens polished.
- Old temporary CSS patches cleaned.

Next:
- Run full backend + frontend smoke test.
- Verify Platform Admin selected-ISP workflows.
- Verify ISP Admin same-ISP invitation acceptance flow.
- Continue with next product feature after smoke test passes.

## Current Frontend/Mobile Status - 2026-05-20 10:32

- Admin web now preserves pending MFA state during authenticator-app switching.
- Admin web now preserves current Platform/ISP dashboard section instead of resetting to Overview.
- App User mobile app MVP has started in C:\PulseFi\pulsefi-mobile-app.
- Mobile app currently contains login, SecureStore session persistence, API client, and /me/summary Home screen.
- Next mobile milestone: bottom-tab navigation and real App User screens for usage, devices, alerts, subscriptions, predictions, and recommendations.

## Current Frontend/Mobile Status - 2026-05-20 10:34

- Admin web now preserves pending MFA state during authenticator-app switching.
- Admin web now preserves current Platform/ISP dashboard section instead of resetting to Overview.
- App User mobile app MVP has started in C:\PulseFi\pulsefi-mobile-app.
- Mobile app currently contains login, SecureStore session persistence, API client, and /me/summary Home screen.
- Next mobile milestone: bottom-tab navigation and real App User screens for usage, devices, alerts, subscriptions, predictions, and recommendations.

## Future Network Integration Roadmap

The production direction is RADIUS/API/router integration.

Planned future modules:

1. ISP Integration Settings for simulator/manual/csv/radius_api modes.
2. Billing Center for invoices, paid/unpaid/overdue status, suspend/reactivate, and external/manual action tracking.
3. RADIUS/API Adapter for official usage sync, profile changes, and account status updates.
4. Router/CPE Adapter for connected devices, live per-device rates, counters, and device-level actions.
5. Alert Visibility Hardening so ISP Admin sees operational alerts only.

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
