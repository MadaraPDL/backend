# Latest Roadmap Status

Read this section first. It overrides older "current phase" sections below if they conflict.

## Current Position

Current phase:
- Step 15D has been implemented and tested.
- Step 15E is next.

## Step 14 Completed

Protected current-account route system:
- Bearer token extraction.
- JWT decoding.
- Current account loading.
- Admin/app-user dependency guards.
- Role guard helper.
- `GET /api/v1/auth/me`.

## Step 15A Completed

Platform Admin ISP management:
- Create ISP.
- List ISPs.
- Get one ISP.
- Update ISP information/status.

## Step 15B Completed

Platform Admin ISP Admin invitations:
- Create ISP Admin invitation.
- Development invitation token returned only while `DEBUG=True`.
- Invited ISP Admin accepts invitation through existing auth invitation endpoint.
- ISP Admin account is created and linked to the correct ISP.

## Step 15C Completed

Platform Admin ISP Admin account management:
- View one ISP Admin.
- Update ISP Admin full name, phone number, and status.
- Deactivate/reactivate ISP Admin.
- Protected by `platform_admin` role only.

## Step 15D Completed

Platform Admin dashboard summary:
- Endpoint: `GET /api/v1/platform-admin/summary`
- Returns counts for ISPs, ISP Admins, and App Users by status.
- Read-only endpoint.
- No database schema changes.

## Step 15E Next

Platform Admin pending invitation management:
- List ISP Admin invitations for an ISP.
- Revoke a pending ISP Admin invitation.

Planned endpoints:
- `GET /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admin-invitations/{invitation_id}/revoke`

## After Step 15E

Move to Step 16:
- ISP Admin management endpoints.
- ISP Admin manages only their own ISP's users, plans, subscriptions, routers, and related data.
- ISP Admin cannot create ISPs or invite/manage ISP Admins.

---
# PulseFi Roadmap

## Current Position

Current phase:

Step 13F — Testing authentication endpoints through Swagger/Postman.

Step 13E is structurally complete.

Swagger/OpenAPI loads successfully.

The split auth endpoint package exists and the API router includes the auth router.

## Completed Major Phases

## Phase 1 — Software Engineering Diagrams

Completed for now:

- Use Case Diagram
- DFD Level 0
- DFD Level 1
- ER Diagram
- User Activity Diagram
- ISP Admin Activity Diagram
- Sequence Diagrams

The class diagram is skipped for now unless the developer decides to revisit it.

Pending future SE updates are listed near the bottom of this file.

## Phase 2 — Database Design

PostgreSQL database design is completed for now.

Core tables include:

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

Auth tables include:

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

## Phase 3 — Backend Foundation

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

Main stack:

- FastAPI
- PostgreSQL
- SQLAlchemy async ORM
- asyncpg
- Pydantic
- JWT
- Argon2

## Phase 4 — SQLAlchemy Models

Completed and import-tested:

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

## Phase 5 — Auth Schemas

Completed and split under:

`app/schemas/auth/`

Schema modules:

- `common.py`
- `login.py`
- `mfa.py`
- `invitation.py`
- `password_reset.py`
- `email_verification.py`
- `current_user.py`

Import test passed.

## Phase 6 — Auth Services

Completed and split under:

`app/services/`

Auth-related services include:

- `account_service.py`
- `auth_service.py`
- `mfa_service.py`
- `invitation_service.py`
- `password_reset_service.py`
- `email_verification_service.py`

The project should continue using focused service modules instead of large mixed files.

## Phase 7 — Auth Endpoints

Structurally completed.

Auth endpoints are under:

`app/api/v1/endpoints/auth/`

Current endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/auth/invitations/accept`
- `POST /api/v1/auth/password/forgot`
- `POST /api/v1/auth/password/reset`
- `POST /api/v1/auth/email/verify`

Swagger/OpenAPI loads successfully.

## Step 13F — Current Step: Auth Endpoint Testing

Goal:

Test all authentication endpoints through Swagger/Postman and fix any bugs.

## Step 13F-1 — Test Wrong Login

Test that wrong login credentials return 401.

Expected result:

- Wrong email/username/password should fail.
- Response should not leak whether the email/username exists.

## Step 13F-2 — Create Temporary Test Invitation

If `account_invitations` is empty, create one temporary invitation row.

Purpose:

- Test invitation acceptance.
- Confirm account creation works.
- Confirm accepted invitation is marked correctly.

## Step 13F-3 — Accept Invitation

Test:

`POST /api/v1/auth/invitations/accept`

Confirm:

- New admin or app user account is created.
- Password is hashed.
- Username is saved.
- Invitation is marked accepted.
- Expired/revoked invitations are rejected.
- Used invitations cannot be reused.

## Step 13F-4 — Login With Created Account

Test:

`POST /api/v1/auth/login`

Confirm:

- Correct login works.
- Login accepts email or username.
- Login uses account type.
- JWT is returned if MFA is not required.
- MFA challenge is returned if MFA is required.

## Step 13F-5 — Test MFA Verification

Test:

`POST /api/v1/auth/mfa/verify`

Confirm:

- Correct MFA code works.
- Wrong MFA code fails.
- Expired challenge fails.
- Used challenge cannot be reused.
- Backup code works only once.

## Step 13F-6 — Test Forgot Password

Test:

`POST /api/v1/auth/password/forgot`

Confirm:

- Response is generic.
- Existing account and non-existing account should receive similar visible response.
- In `DEBUG=True`, dev token may be shown only for testing.
- In production, raw reset token should not be shown in API response.

## Step 13F-7 — Test Password Reset

Test:

`POST /api/v1/auth/password/reset`

Confirm:

- Valid reset token works.
- Password is changed.
- Reset token is marked used.
- Old password fails.
- New password works.
- Expired/used reset token fails.

## Step 13F-8 — Test Email Verification

Test:

`POST /api/v1/auth/email/verify`

Confirm:

- Valid verification token works.
- Email verified timestamp is updated.
- Used token cannot be reused.
- Expired token fails.

If verification token is not auto-created yet, add or adjust the service flow later.

## Step 14 — Protected Route System

After auth endpoint testing, implement current-user and protected-route logic.

Main goals:

- Decode access token.
- Load the current account from the database.
- Support both admin and app user accounts.
- Add role-based access checks.
- Add `/auth/me`.

Tasks:

1. Create auth dependency module.
2. Add `get_current_account`.
3. Add `get_current_admin`.
4. Add `get_current_app_user`.
5. Add role check helpers.
6. Add `GET /api/v1/auth/me`.
7. Test with valid JWT.
8. Test with expired/invalid JWT.
9. Test admin-only access.
10. Test app-user-only access.

Expected result:

The backend can protect future endpoints cleanly.

## Step 15 — Platform Admin Endpoints

Goal:

Build Platform Admin features.

Platform Admin can:

- Create/view/update ISPs.
- Invite ISP Admins.
- View ISP Admins.
- Deactivate ISP/Admin if needed.

Possible endpoint groups:

- `/platform/isps`
- `/platform/admins`
- `/platform/invitations`

Tasks:

1. Add Platform Admin protected routes.
2. Add ISP create endpoint.
3. Add ISP list endpoint.
4. Add ISP detail endpoint.
5. Add ISP update endpoint.
6. Add ISP status update endpoint.
7. Add invite ISP Admin endpoint.
8. Add view ISP Admins endpoint.
9. Add tests/import checks.

SE update impact:

This affects use cases and admin flows if not already reflected.

## Step 16 — ISP Admin Management Endpoints

Goal:

Build ISP Admin management features.

ISP Admin can:

- Manage app users.
- Invite users.
- Manage subscription plans.
- Assign subscriptions.
- Manage routers.
- View users under ISP.

Possible endpoint groups:

- `/isp/users`
- `/isp/invitations`
- `/isp/plans`
- `/isp/subscriptions`
- `/isp/routers`

Tasks:

1. Add ISP Admin protected routes.
2. Add invite user endpoint.
3. Add list users endpoint.
4. Add user detail endpoint.
5. Add create/list/update plans.
6. Add assign subscription endpoint.
7. Add list subscriptions endpoint.
8. Add add/update router endpoint.
9. Add assign router to subscription endpoint.
10. Add tests/import checks.

SE update impact:

This affects ISP Admin use cases and activity diagrams.

## Step 17 — User Mobile App Endpoints

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

Tasks:

1. Add current user subscription endpoint.
2. Add total usage endpoint.
3. Add usage history endpoint.
4. Add connected devices endpoint.
5. Add per-device usage endpoint if available.
6. Add alerts endpoint.
7. Add predictions endpoint.
8. Add recommendations endpoint.
9. Add plan change request endpoint.
10. Add device bandwidth limit endpoint.
11. Add device priority endpoint.
12. Add tests/import checks.

Important behavior:

- If the user has one subscription, show it directly.
- If the user has multiple subscriptions, allow subscription selection.
- Device-level features depend on router capability.

SE update impact:

This affects user activity diagrams, sequence diagrams, and DFD flows.

## Step 18 — Router Adapter and Simulator Layer

Goal:

Create a realistic router integration structure.

Do not hard-code one router type everywhere.

Use a router adapter architecture.

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

## Step 19 — Usage Data Ingestion

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

Data examples:

- Total usage per subscription.
- Usage by day.
- Usage by hour if needed.
- Device-level usage when supported.
- Device online/offline changes.

SE update impact:

This affects DFD data flows and sequence diagrams.

## Step 20 — Alerts System

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

## Step 21 — Prediction and Recommendation Logic

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

Later ML improvement:

- Use historical usage patterns.
- Add anomaly detection.
- Add more advanced prediction model.

SE update impact:

This affects smart features, DFD, sequence diagrams, and documentation.

## Step 22 — Reports and Analytics

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

## Step 23 — Frontend Integration

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

For example:

- If router does not support bandwidth limit, do not show the bandwidth limit action as available.
- If per-device usage is unavailable, explain that this router does not support detailed device usage.

## Step 24 — Deployment Preparation

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
