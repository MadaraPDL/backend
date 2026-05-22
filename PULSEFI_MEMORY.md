<!-- PULSEFI_SYNC_START -->
## Current Synchronized PulseFi Checkpoint - 2026-05-22

Current phase: **Step 40F complete - MFA backup-code generation/regeneration**.

Latest completed backend work:

- Step 40B added multi-method MFA support for Admins and App Users.
- Admins and App Users can now have Email MFA active, Authenticator MFA active, both active, or neither active.
- Backend added `email_mfa_enabled` and `authenticator_mfa_enabled` on `admins` and `app_users`.
- Backend keeps legacy `mfa_enabled` synchronized from active MFA method flags.
- Backend sends email MFA login codes through the shared email service when Email MFA is selected and email delivery is enabled.
- Backend supports verified MFA settings actions before enabling, disabling, or changing preferred MFA methods.
- Backend supports switching an existing MFA challenge to another active method through the MFA challenge-method flow.
- Step 40E updated `MFARequiredResponse` to expose `active_methods` and `backup_codes_available`.
- Step 40E added backup-code availability detection for login MFA fallback display.
- Step 40F added backup-code status and regeneration endpoints:
  - `GET /api/v1/auth/me/mfa/backup-codes/status`
  - `PATCH /api/v1/auth/me/mfa/backup-codes/regenerate`
- Step 40F stores only backup-code hashes.
- Step 40F returns raw backup codes one time only after verified regeneration.
- Step 40F revokes old unused backup codes during regeneration.
- Step 40F added backend tests for backup-code status, regeneration, revocation, and hash-only storage.

Latest completed admin web work:

- Admin Settings shows Email MFA status, Authenticator MFA status, and preferred MFA method.
- Admin Settings MFA actions require verification before enabling, disabling, or switching methods.
- Step 40E removed the pre-login admin MFA method selector.
- Admin login now asks only for identifier/email and password before MFA.
- Admin MFA verification page now shows fallback actions after password succeeds.
- Email fallback appears only when Email MFA is active.
- Backup-code fallback appears only when unused backup codes exist.
- MFA fallback UI was polished so it fits the PulseFi dark/light admin style.
- Step 40F added Admin Settings recovery backup-code UI.
- Admin Settings can show backup-code availability/count.
- Admin Settings can generate/regenerate backup codes after verified MFA challenge.
- Generated backup codes are displayed one time and can be copied.

Current product decision for MFA login UX:

- The login page must only ask for identifier/email and password.
- The user/admin must **not** choose default/email/authenticator before password verification.
- After password succeeds, backend must use `preferred_mfa_method` automatically and show that MFA challenge first.
- The MFA verification page should show fallback options under a “Try another way” / “Having trouble?” style section.
- Email fallback must appear only when `email_mfa_enabled=true`.
- Backup-code fallback must appear only when unused backup codes exist.
- Backup code is a recovery method, not a preferred MFA method.
- `preferred_mfa_method` must remain only `email` or `authenticator`.
- Backup codes must not be added to `preferred_mfa_method`.

Correct next recommended work:

1. Manually smoke test Admin Settings backup-code generation/regeneration.
2. Continue with Mobile App User MFA verification and mobile MFA fallback UX.
3. Later add App User mobile backup-code management if needed.
4. Later add production hardening around email delivery, Redis/shared rate limits, and deployment settings.

Rules that remain active:

- ISP Admin endpoints must use `get_current_isp_admin`.
- Every ISP Admin query must be scoped by `current_admin.isp_id`.
- App User `/me` endpoints must use `get_current_app_user`.
- App User mobile screens must not assume router actions are available; check router capabilities first.
- Do not store raw router passwords, ISP API keys, or RADIUS credentials until encrypted credential storage exists.
- MFA settings actions must require verification before changing MFA state.
- Backup codes must be shown only once and stored only as hashes.
- Email MFA in local development may expose `dev_email_code` only when `DEBUG=True`.
- Production must not expose OTP/dev codes.
- Real email delivery requires `EMAIL_DELIVERY_ENABLED=True` and SMTP configuration.
- Future assistants must treat this synchronized block as the current PulseFi source of truth unless a newer block exists.
- Historical sections below may mention older steps; this synchronized block is the current source of truth.
<!-- PULSEFI_SYNC_END -->

# PulseFi Project Memory

This file is the grouped project context for PulseFi. It should be read before continuing major backend work, especially when starting a new step.

## Project Overview

PulseFi is my Final Year Project: a Smart Network Monitoring and Optimization System.

The system helps users and ISP admins monitor, analyze, and optimize internet usage.

Core idea:
- Collect usage and connected-device data from router/network source.
- Show total usage, connected devices, per-device usage, alerts, predictions, recommendations, and device network policies.
- Help users avoid exceeding their plan.
- Help ISP admins manage users, plans, routers, usage records, reports, alerts, recommendations, and analytics.

Main roles:
- Platform Admin: creates/manages ISPs and ISP Admins.
- ISP Admin: manages app users, plans, subscriptions, routers, reports, and monitoring.
- App User: uses the mobile app to view usage, devices, alerts, predictions, recommendations, and apply device optimization actions.

Current stack:
- Backend: FastAPI
- Database: PostgreSQL
- ORM: async SQLAlchemy
- Mobile app later: React Native + TypeScript
- Admin dashboards later: web dashboards for Platform Admin and ISP Admin

## Working Preferences

When helping with PulseFi backend:
- Explain before giving big code blocks.
- Explain what file is edited, why it is needed, what the code does, and how it fits the architecture.
- Mention whether each change affects database schema, existing data, GitHub, tests, or SE diagrams.
- Do not create huge mixed-responsibility files.
- Split schemas, services, endpoints, and dependencies early when responsibilities grow.
- Keep code modular and clean.
- Use the GitHub backend repo as source of truth when needed: https://github.com/MadaraPDL/backend
- User is manually typing/running code locally in `C:\PulseFi\backend`.

## Completed Backend Foundation

The FastAPI backend foundation is complete:
- Project structure created under `app/`.
- `app/main.py` runs the FastAPI app.
- `app/core/config.py` loads settings from `.env`.
- `app/core/security.py` handles password hashing, JWT creation/decoding, secure tokens, token hashing, and numeric codes.
- `app/db/session.py` handles async SQLAlchemy database sessions.
- `app/api/v1/router.py` connects API routers.
- Health endpoint works.
- Swagger/OpenAPI works.

Security decisions:
- Passwords use Argon2 through `pwdlib[argon2]`.
- JWT uses `SECRET_KEY`, `ALGORITHM`, and access-token expiry.
- JWT payload includes `sub`, `account_type`, `iat`, and `exp`.
- Login requires `account_type` because admins and app users are stored in separate tables.

## Database / Models Status

Core PostgreSQL schema is already created.

Core model set is complete and import-tested:
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

Auth model set is complete and import-tested:
- AccountInvitation
- EmailVerificationToken
- PasswordResetToken
- MFABackupCode
- MFAChallenge

Important database/auth design:
- Account invitations are used instead of temporary passwords.
- Email verification is included.
- Forgot password uses expiring reset tokens.
- Admins and app users can log in with email or username.
- Usernames are optional, unique case-insensitively, and no spaces.
- MFA foundations are included.
- Backup codes should be single-use and stored hashed only.
- Authenticator secrets should be encrypted in the final deployable version.
- SMS verification is deferred.

## Auth Progress

Auth schemas were split under `app/schemas/auth/`:
- `common.py`
- `login.py`
- `mfa.py`
- `invitation.py`
- `password_reset.py`
- `email_verification.py`
- `current_user.py`

Auth services were split under `app/services/`:
- `account_service.py`
- `auth_service.py`
- `mfa_service.py`
- `invitation_service.py`
- `password_reset_service.py`
- `email_verification_service.py`

Auth endpoints were split under `app/api/v1/endpoints/auth/`:
- `login.py`
- `mfa.py`
- `invitations.py`
- `password_reset.py`
- `email_verification.py`
- `me.py`

Auth endpoints currently include:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/auth/invitations/accept`
- `POST /api/v1/auth/password/forgot`
- `POST /api/v1/auth/password/reset`
- `POST /api/v1/auth/email/verify`
- `GET /api/v1/auth/me`

## Step 14 Completed

Step 14 is complete and pushed.

Feature:
- Protected current-account route system.

Files added/split:
- `app/api/dependencies/auth_scheme.py`
- `app/api/dependencies/current_account.py`
- `app/api/dependencies/role_guards.py`
- `app/api/dependencies/__init__.py`
- `app/api/v1/endpoints/auth/me.py`

What works:
- Bearer token extraction.
- JWT decoding.
- Current account loading from admin/app_user table.
- Active account check.
- Admin-only dependency.
- App-user-only dependency.
- Admin role guard.
- `GET /api/v1/auth/me`.

Test result:
- Login through PowerShell worked.
- `/auth/me` returned the logged-in platform admin successfully.

GitHub:
- Step 14 pushed as commit `f2dcf09 Add protected current account dependencies`.

## Step 15A Completed

Step 15A is complete and pushed.

Feature:
- Platform Admin ISP management.

Endpoints:
- `POST /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps/{isp_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}`

Files added:
- `app/schemas/platform_admin/isps.py`
- `app/schemas/platform_admin/__init__.py`
- `app/services/platform_admin/isp_service.py`
- `app/services/platform_admin/__init__.py`
- `app/api/v1/endpoints/platform_admin/isps.py`
- `app/api/v1/endpoints/platform_admin/__init__.py`

What works:
- Platform Admin can create ISP.
- Platform Admin can list ISPs.
- Platform Admin can get one ISP.
- Platform Admin can update ISP info/status.
- `created_by_admin_id` is correctly saved.
- `updated_at` updates correctly.

## Step 15B Completed

Step 15B is complete and pushed.

Feature:
- Platform Admin creates ISP Admin invitations.
- Invited ISP Admin accepts invitation.
- Platform Admin lists ISP Admins under an ISP.

Endpoints:
- `POST /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins`
- Uses existing `POST /api/v1/auth/invitations/accept`.

Files added:
- `app/schemas/platform_admin/admin_invitations.py`
- `app/services/platform_admin/admin_invitation_service.py`
- `app/api/v1/endpoints/platform_admin/admin_invitations.py`

Important fix:
- The route prefix in `admin_invitations.py` must be `router = APIRouter(prefix="/isps/{isp_id}")`.
- Correct routes are:
  - `/api/v1/platform-admin/isps/{isp_id}/admin-invitations`
  - `/api/v1/platform-admin/isps/{isp_id}/admins`

What works:
- Platform Admin creates an ISP Admin invitation.
- Development response returns `dev_invitation_token` while `DEBUG=True`.
- Invited ISP Admin accepts invitation.
- ISP Admin account is created with `role="isp_admin"`.
- ISP Admin is linked to the correct `isp_id`.
- `created_by_admin_id` is linked to the inviting Platform Admin.
- Platform Admin can list ISP Admins under the ISP.
- ISP Admin can log in.

## Current Next Step

Next step:
- Start frontend integration after final backend hardening validation.

Likely scope:
- Platform Admin web dashboard.
- ISP Admin web dashboard.
- App User mobile app.
- Keep backend changes small and limited to blockers, API contract fixes, or safety corrections found during integration.

Possible endpoints:
- Use `docs/API_CONTRACT.md` as the frontend reference.
- Update the API contract whenever endpoint behavior or response shape changes.

## Pending Later Roadmap

After final backend hardening:
- Frontend integration.
- Final presentation/demo polish.
- Production deployment hardening.
## Pending SE Diagram Updates

Batch-update SE artifacts later for:
- Invitation-based onboarding.
- Email verification.
- Forgot password.
- Username login.
- MFA/2FA.
- Protected routes/current-user flow.
- Router adapter/capability architecture.
- Subscription change request flow.

Do not interrupt coding for tiny implementation details, but mention SE updates when changes affect actors, roles, use cases, DFD processes/data flows, ERD entities/attributes/relationships, sequence/activity diagrams, onboarding/security architecture, or router/deployment structure.

## Latest Progress Update

Step 15C is complete and tested:
- Platform Admin can view one ISP Admin.
- Platform Admin can update ISP Admin full name, phone number, and status.
- Platform Admin can deactivate/reactivate ISP Admins.
- ISP Admin management remains protected by `platform_admin` role only.

Step 15D is complete and tested:
- Added Platform Admin dashboard summary endpoint.
- Endpoint: `GET /api/v1/platform-admin/summary`
- Summary returns counts for ISPs, ISP Admins, and App Users by status.
- This is read-only and does not modify database rows.

Current next step:
- Step 15E: Platform Admin pending ISP Admin invitation management.
- Planned endpoints:
  - `GET /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
  - `PATCH /api/v1/platform-admin/isps/{isp_id}/admin-invitations/{invitation_id}/revoke`

## Latest Progress Update

Step 15E is complete and tested:
- Platform Admin can list ISP Admin invitations for an ISP.
- Platform Admin can filter invitations by pending, accepted, revoked, or expired.
- Platform Admin can revoke a pending ISP Admin invitation.
- Revoked invitations cannot be accepted.
- Revoke keeps the invitation row for audit history by setting `revoked_at`.

Step 15 is now complete for Platform Admin MVP:
- 15A: Manage ISPs.
- 15B: Invite ISP Admins.
- 15C: Manage ISP Admin accounts.
- 15D: View Platform Admin summary metrics.
- 15E: Manage pending ISP Admin invitations.

Current next step:
- Step 16: ISP Admin management endpoints.
- ISP Admin must only manage data under their own ISP.
- ISP Admin cannot create ISPs or invite/manage ISP Admins.

## Latest Progress Update

Step 15E is complete and tested:
- Platform Admin can list ISP Admin invitations for an ISP.
- Platform Admin can filter invitations by pending, accepted, revoked, or expired.
- Platform Admin can revoke a pending ISP Admin invitation.
- Revoked invitations cannot be accepted.
- Revoke keeps the invitation row for audit history by setting `revoked_at`.

Step 15 is now complete for Platform Admin MVP:
- 15A: Manage ISPs.
- 15B: Invite ISP Admins.
- 15C: Manage ISP Admin accounts.
- 15D: View Platform Admin summary metrics.
- 15E: Manage pending ISP Admin invitations.

Current next step:
- Step 16: ISP Admin management endpoints.
- ISP Admin must only manage data under their own ISP.
- ISP Admin cannot create ISPs or invite/manage ISP Admins.

## Latest Progress Update

Step 15E is complete and tested:
- Platform Admin can list ISP Admin invitations for an ISP.
- Platform Admin can filter invitations by pending, accepted, revoked, or expired.
- Platform Admin can revoke a pending ISP Admin invitation.
- Revoked invitations cannot be accepted.
- Revocation keeps audit history by setting `revoked_at`.

Step 15 Platform Admin MVP is now complete:
- 15A: Manage ISPs.
- 15B: Invite ISP Admins.
- 15C: Manage ISP Admin accounts.
- 15D: View Platform Admin summary metrics.
- 15E: Manage pending ISP Admin invitations.

Current next step:
- Step 16: ISP Admin management endpoints.
- ISP Admin must only manage data under their own ISP.
- ISP Admin cannot create ISPs or invite/manage ISP Admins.

---

## Latest Progress Update Ã¯Â¿Â½ 2026-05-14

Backend quality improvements completed:

- Limited PostgreSQL runtime role `pulsefi_app` created and tested.
- Backend local `.env` uses `pulsefi_app` instead of `postgres`.
- Alembic initialized and baseline migration created.
- Existing database stamped to Alembic baseline.
- Pytest/httpx testing foundation added.
- Health endpoint test added.
- GitHub Actions backend CI added and confirmed passing.

Important DB permission reminder:

- `pulsefi_app` is intentionally limited and is not table owner.
- It can run the backend but cannot safely perform all schema migrations.
- Future production setup should use:
  - restricted runtime app DB role
  - separate migration/admin DB role for Alembic/schema changes

Step 16 ISP Admin progress:

- Step 16A completed and tested: ISP Admin router foundation and protected summary endpoint.
- Step 16B completed and tested: ISP Admin App User invitation endpoints.
- Step 16C completed and tested: ISP Admin App User list/detail/update endpoints.
- Step 16D completed and tested: ISP Admin subscription plan management endpoints.
- Step 16E completed and tested: ISP Admin user subscription assignment/list/detail/update endpoints.

Step 16E database migration:

- Added Alembic migration `285ab0474b39_allow_suspended_user_subscription_status.py`.
- Updated `user_subscriptions.status` check constraint to allow:
  - `pending`
  - `active`
  - `suspended`
  - `expired`
  - `cancelled`
- `suspended` means a subscription is temporarily stopped, such as unpaid bill/admin action.
- Migration SQL had to be applied locally through pgAdmin/admin because `pulsefi_app` is not owner of `user_subscriptions`.
- Alembic should be stamped to head after manual local application.

Current next step:

- Step 16F: ISP Admin router management endpoints.

Step 16F expected rule:

- Routers must be linked only to user subscriptions under `current_admin.isp_id`.
- Every router query must verify ownership through the linked user subscription and App User ISP.

---

## Step 16 Progress Ã¯Â¿Â½ 2026-05-14

### Step 16F Ã¯Â¿Â½ ISP Admin Router Management Endpoints

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

---

## Step 16G Ã¯Â¿Â½ ISP Admin Dashboard Summary

Completed and tested:

- Replaced the temporary ISP Admin summary endpoint with real dashboard metrics.
- Endpoint:
  - `GET /api/v1/isp-admin/summary`
- Added ISP Admin summary schemas.
- Added ISP Admin summary service logic.
- Summary returns ISP-scoped counts for:
  - App Users
  - Subscription Plans
  - User Subscriptions
  - Routers
- Subscription counts are scoped through the linked App User because `user_subscriptions` does not directly store `isp_id`.
- All summary queries remain scoped to `current_admin.isp_id`.
- Tested successfully with an ISP Admin token.

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: later update ISP Admin dashboard/use-case flow to include dashboard summary metrics.
- Security: confirmed ISP Admin summary only reads data under the logged-in admin's ISP.

Next step:

- Step 16 final cleanup/testing and documentation update.
- Then continue to Step 17: App User mobile endpoints.


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

## Step 17 Progress Ã¯Â¿Â½ 2026-05-14

### Step 17A Ã¯Â¿Â½ App User Mobile Endpoint Foundation

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

## Step 17 Progress Ã¯Â¿Â½ 2026-05-14

### Step 17B Ã¯Â¿Â½ App User Subscription Endpoints

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

## Step 17 Progress Ã¯Â¿Â½ 2026-05-14

### Step 17C Ã¯Â¿Â½ App User Router and Device View Endpoints

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

- Step 17D Ã¯Â¿Â½ App User usage endpoints.
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

## Step 17 Progress Ã¯Â¿Â½ 2026-05-15

### Step 17E Ã¯Â¿Â½ App User Alert Endpoints

Completed and tested:

- Added App User alert schemas.
- Added App User alert service logic.
- Added endpoint module: pp/api/v1/endpoints/app_user/alerts.py.
- Added endpoints:
  - GET /api/v1/me/alerts
  - GET /api/v1/me/alerts/{alert_id}
  - PATCH /api/v1/me/alerts/{alert_id}/read
- Connected alert endpoints to the App User router.
- Endpoints use get_current_app_user.
- Alert queries are scoped by Alert.user_id = current_user.id.
- App User endpoints do not accept user_id from the request.
- Tested App User login through PowerShell.
- Tested listing alerts for the logged-in App User.
- Tested empty alert list returns 0 alerts.
- Tested fake alert ID returns 404 Alert not found.
- Ran pytest successfully: 1 passed.
- Ran compileall successfully.

Impact:

- Database schema: no change.
- Existing data: only changes when marking an alert as read.
- SE diagrams: later update App User/mobile activity and sequence diagrams to include alert list/detail/read flow.
- Security: App User can only access their own alerts.

Next Step 17 work:

- Step 17F Ã¯Â¿Â½ App User predictions and recommendations endpoints, or plan change request endpoints.

---

## Step 17 Progress Ã¯Â¿Â½ 2026-05-15

### Step 17F Ã¯Â¿Â½ App User Prediction and Recommendation Endpoints

Completed and tested:

- Added App User prediction schemas.
- Added App User recommendation schemas.
- Added App User prediction service logic.
- Added App User recommendation service logic.
- Added endpoint modules:
  - pp/api/v1/endpoints/app_user/predictions.py
  - pp/api/v1/endpoints/app_user/recommendations.py
- Added endpoints:
  - GET /api/v1/me/predictions
  - GET /api/v1/me/predictions/{prediction_id}
  - GET /api/v1/me/recommendations
  - GET /api/v1/me/recommendations/{recommendation_id}
- Connected prediction and recommendation endpoints to the App User router.
- Endpoints use get_current_app_user.
- Prediction queries are scoped by Prediction.user_id = current_user.id.
- Recommendation queries are scoped by Recommendation.user_id = current_user.id.
- App User endpoints do not accept user_id from the request.
- Tested App User login through PowerShell.
- Tested listing predictions for the logged-in App User.
- Tested listing recommendations for the logged-in App User.
- Tested fake prediction ID returns 404 Prediction not found.
- Tested fake recommendation ID returns 404 Recommendation not found.
- Ran pytest successfully.
- Ran compileall successfully.

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: later update App User/mobile activity and sequence diagrams to include prediction and recommendation viewing.
- Security: App User can only access their own predictions and recommendations.

Next Step 17 work:

- Step 17G Ã¯Â¿Â½ App User subscription plan change request endpoints.

---

## Step 17 Progress Ã¯Â¿Â½ 2026-05-15

### Step 17G Ã¯Â¿Â½ App User Plan Change Request Endpoints

Completed and tested:

- Added App User plan change request schemas.
- Added App User plan change request service logic.
- Added endpoint module:
  - pp/api/v1/endpoints/app_user/plan_change_requests.py
- Added endpoints:
  - POST /api/v1/me/plan-change-requests
  - GET /api/v1/me/plan-change-requests
  - GET /api/v1/me/plan-change-requests/{request_id}
- Connected plan change request endpoints to the App User router.
- Endpoints use get_current_app_user.
- Plan change request queries are scoped by SubscriptionChangeRequest.user_id = current_user.id.
- App User endpoints do not accept user_id from the request.
- Added validation to reject requesting the same current plan before database commit.
- Confirmed PostgreSQL check constraint chk_requested_plan_different works correctly.
- Tested invalid same-plan request handling.
- Created a second ISP plan for successful endpoint testing.
- Tested successful App User plan change request creation.
- Tested request listing endpoint.
- Ran pytest successfully.
- Ran compileall successfully.

Impact:

- Database schema: no change.
- Existing data: creates pending plan change requests.
- SE diagrams: later update App User/mobile activity and sequence diagrams to include plan change request flow.
- Security:
  - App User can only access their own requests.
  - Requested plan must belong to the same ISP.
  - Recommendation ownership validation enforced.

Next Step 17 work:

- Step 17H Ã¯Â¿Â½ App User device policy endpoints.

---

## Step 17 Progress Ã¯Â¿Â½ 2026-05-15

### Step 17H Ã¯Â¿Â½ App User Device Policy Endpoints

Completed and tested:

- Added App User device policy schemas.
- Added App User device policy service logic.
- Added endpoint module:
  - pp/api/v1/endpoints/app_user/device_policies.py
- Added endpoints:
  - POST /api/v1/me/device-policies
  - GET /api/v1/me/device-policies
  - GET /api/v1/me/device-policies/{policy_id}
- Connected device policy endpoints to the App User router.
- Endpoints use get_current_app_user.
- Device policy queries are scoped by DeviceNetworkPolicy.requested_by_user_id = current_user.id.
- App User endpoints do not accept user_id from the request.
- Device ownership validation enforced before policy creation.
- Router ID automatically derived from the validated device.
- Tested successful device policy creation.
- Tested device policy listing endpoint.
- Tested fake policy ID returns 404 Device policy not found.
- Device policy requests currently remain in pending status until future router adapter execution layer is implemented.
- Ran pytest successfully.
- Ran compileall successfully.

Impact:

- Database schema: no change.
- Existing data: creates pending device policy requests.
- SE diagrams: later update App User/mobile activity and sequence diagrams to include device policy request flow.
- Security:
  - App User can only access their own policy requests.
  - Device ownership validation enforced before policy creation.

Next Backend Step:

- Step 18 Ã¯Â¿Â½ Router adapter and simulator layer.


## Backend Quality Fixes Completed

Recent quality fixes:
- MFA-required accounts can no longer bypass MFA setup and receive a normal login token.
- Added auth service regression tests for normal login, MFA challenge login, and MFA setup-required login.
- Replaced the empty Alembic baseline with a real baseline migration tested against a fresh PostgreSQL database.
- Handled the circular FK between `isps.created_by_admin_id` and `admins.isp_id` by creating the FK after both tables exist.
- Added a production guard so token-based email flows cannot silently run in production unless email delivery is configured.

- Backend CI now verifies Alembic migrations against a fresh PostgreSQL service before running tests.

- Email-based MFA is now guarded in production and cannot create email MFA challenges unless email delivery is configured.

- Added API-level auth tests for login, password reset, and invitation email-delivery guards.

- API test setup was refactored into `tests/api/conftest.py` with a shared `api_client` fixture.


## MFA Setup Flow Fix - 2026-05-15

Completed and tested:
- Added signed MFA setup token helpers.
- Added `MFASetupConfirmRequest`.
- Added separate `app/services/mfa_setup_service.py` to avoid making `mfa_service.py` too large.
- Login now returns setup data when `mfa_required=True` and `mfa_enabled=False`.
- Added endpoint:
  - `POST /api/v1/auth/mfa/setup/confirm`
- MFA setup confirmation verifies the authenticator code, enables MFA, stores the authenticator secret, and returns a normal access token.
- Added API tests for successful and invalid MFA setup confirmation.

Impact:
- Database schema: no change.
- Existing data: changes only when an account successfully confirms MFA setup.
- Security: fixes the MFA setup dead-end after the bypass was closed.
- SE diagrams: later update auth/login sequence to include MFA setup required -> setup confirm -> token issued.


## MFA Setup Token Hardening and Cleanup - 2026-05-15

Completed and tested:
- Hardened MFA setup-token handling.
- Moved setup-token JWT logic into `app/services/mfa_setup_token_service.py`.
- Kept MFA setup business logic in `app/services/mfa_setup_service.py`.
- Restored `app/services/mfa_service.py` to focus only on MFA challenge, verification, and backup-code logic.
- Removed duplicated MFA setup responsibility from `mfa_service.py`.
- Added tests for MFA setup-token validation.
- Confirmed tests pass after the cleanup.

Impact:
- Database schema: no change.
- Existing data: no change.
- Security: setup-token validation is stricter and MFA setup code is better isolated.
- Architecture: MFA files are now split by responsibility.


## Server-Side MFA Setup State - 2026-05-15

Completed and tested:
- Added `MFASetupChallenge` model and Alembic migration.
- Added `mfa_setup_challenges` table for pending MFA setup state.
- MFA setup tokens are now opaque random tokens.
- Only the setup token hash is stored in the database.
- The pending authenticator secret is stored server-side instead of inside a readable JWT payload.
- Successful setup marks the setup challenge as used.
- Invalid setup attempts increment `attempt_count`.
- Setup challenge expiry is enforced.
- Updated MFA setup services and tests.

Impact:
- Database schema: added `mfa_setup_challenges`.
- Existing data: no existing rows changed.
- Security: MFA setup token no longer exposes the authenticator secret in a client-readable JWT.
- SE diagrams: later update auth/login sequence and ERD to include pending MFA setup challenge storage.


## MFA Setup Secret Redaction - 2026-05-15

Completed and tested:
- Pending MFA setup secrets are redacted from `mfa_setup_challenges` after successful setup.
- Revoked MFA setup challenges now have their pending authenticator secret cleared.
- Expired, used, and revoked setup challenge secrets are cleaned when a new setup challenge is created.
- This reduces how long pending authenticator secrets remain in the database.

Impact:
- Database schema: no change.
- Existing data: inactive setup challenge secrets may be cleared during future setup challenge creation.
- Security: improves secret retention behavior, but full encryption at rest is still pending before production.


## MFA Setup Challenge Cleanup Service - 2026-05-15

Completed and tested:
- Added `app/services/mfa_setup_cleanup_service.py`.
- Added cleanup logic for old inactive MFA setup challenges.
- Cleanup removes setup challenge rows only when they are old enough and inactive:
  - used
  - revoked
  - expired
- Default retention is 7 days.
- Added service tests for cleanup count and invalid retention handling.

Impact:
- Database schema: no change.
- Existing data: no automatic deletion yet; this is only a callable cleanup service.
- Security: reduces long-term retention of inactive MFA setup challenge records once used by a future job/endpoint.
- Future work: connect this to a scheduled maintenance task, CLI command, or admin-only maintenance endpoint.


## MFA Secret Encryption at Rest - 2026-05-15

Completed and tested:
- Added encryption helper foundation using `cryptography`.
- Added `DATA_ENCRYPTION_KEY` setting.
- Added CI dummy encryption key for automated tests.
- Pending MFA setup secrets are encrypted in `mfa_setup_challenges`.
- Final account MFA secrets are encrypted in `admins.mfa_secret` and `app_users.mfa_secret`.
- Authenticator MFA verification decrypts the stored secret before validating the TOTP code.
- Added encryption-related tests.

Impact:
- Database schema: no change for this chunk.
- Existing data: existing plaintext MFA secrets would need migration/rotation before production if real users already configured MFA.
- Security: MFA secrets are now encrypted at rest for new setup flows.
- Deployment: production must configure `DATA_ENCRYPTION_KEY` securely and must not commit it.


## Auth Rate Limiting MVP - 2026-05-15

Completed and tested:
- Added shared in-memory rate limiting dependency.
- Applied rate limits to auth-sensitive endpoints:
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/mfa/verify`
  - `POST /api/v1/auth/mfa/setup/confirm`
  - `POST /api/v1/auth/password/forgot`
  - `POST /api/v1/auth/password/reset`
  - `POST /api/v1/auth/invitations/accept`
- Added unit tests for the rate limiter.
- Added API-level login rate-limit regression test.

Impact:
- Database schema: no change.
- Existing data: no change.
- Security: reduces brute-force/login/MFA/reset/invitation guessing risk.
- Production note: current limiter is in-memory and suitable for local/demo/single-server use. Production should use Redis or another shared store.


## Final Pre-Step-18 Hardening Pass - 2026-05-15

Completed and tested:
- Added encryption helper foundation with `DATA_ENCRYPTION_KEY`.
- Encrypted pending MFA setup secrets at rest.
- Encrypted final account MFA secrets at rest for new MFA setup flows.
- Added MVP in-memory rate limiting for auth-sensitive endpoints.
- Added API-level login rate-limit test.
- Applied auth rate limits to login, MFA verify, MFA setup confirm, password reset, and invitation acceptance.
- Added maintenance command:
  - `python -m app.maintenance.cleanup_mfa_setup_challenges`
- Added parser tests for the maintenance command.
- Cleaned local pytest cache handling and ensured cache ignore rules.

Remaining production hardening:
- Replace in-memory rate limiter with Redis/shared-store rate limiting before multi-worker deployment.
- Add real DB-backed integration tests for auth, MFA, invitations, ISP isolation, and App User ownership.
- Configure real email delivery.
- Migrate/rotate any existing plaintext MFA secrets if real users already configured MFA before encryption.
- Reuse encryption helpers for future router credentials.

## Recent Quality/Security Fixes

- Fixed malformed `requirements.txt` where dependencies were stored on one line with literal `\n` characters.
  - Fresh `pip install -r requirements.txt` should now work.
  - This removed a CI/fresh setup blocker.

- Verified and protected the MFA-required login behavior.
  - If an account has `mfa_required=True` and `mfa_enabled=False`, login must return an MFA setup response instead of issuing a normal access token.
  - Added regression tests in `tests/test_auth_service_mfa_required.py`.
  - App users with `mfa_required=False` can still log in normally when MFA is not enabled.

Current security note:
- MFA-required bypass is considered covered by regression tests.
- Continue improving remaining production items:
  - Real PostgreSQL-backed integration tests.
  - Real email delivery.
  - Redis/DB-backed rate limiting.
  - `DATA_ENCRYPTION_KEY` rotation plan.

## DB-Backed Integration Testing Started - 2026-05-15

Completed and tested:
- Added shared integration DB fixture:
  - tests/integration/conftest.py
- Added first real PostgreSQL-backed integration test:
  - tests/integration/test_auth_invitation_mfa_integration.py
- Test covers:
  - real ISP row creation
  - real account invitation row creation
  - invitation acceptance through service logic
  - real Admin account creation
  - admin MFA-required defaults
  - login returning MFA setup instead of access token

Local DB repair note:
- Local dev database had stale Alembic revision 285ab0474b39.
- Current repo migration chain is:
  - 11d8754136bc
  - 846ac0977099
  - 68eea2a5b4d2
- Local DB was repaired by manually creating mfa_setup_challenges with admin privileges and updating alembic_version to 68eea2a5b4d2.
- This was a local dev DB repair only, not an application code change.

Impact:
- Database schema: no new migration in this step.
- Existing data: integration test data rolls back after test.
- Security: invitation plus MFA setup-required flow now has DB-backed coverage.
- SE diagrams: no change.

Next recommended quality work:
- Add DB-backed tests for duplicate invitations/usernames.
- Add DB-backed tests for ISP Admin isolation.
- Add DB-backed tests for App User ownership.

## DB-Backed Invitation Duplicate Tests - 2026-05-15

Completed and tested:
- Added DB-backed duplicate email protection test for admin invitation acceptance.
- Added DB-backed duplicate username protection test for admin invitation acceptance.
- Updated integration DB fixture to use a fresh async engine with NullPool.
- This avoids asyncpg connection reuse across closed Windows pytest event loops.

Impact:
- Database schema: no change.
- Existing data: no lasting change; tests roll back.
- API behavior: no change.
- Security/data integrity: duplicate admin account creation is now covered by real DB-backed tests.
- SE diagrams: no change.

Next recommended DB-backed tests:
- MFA setup confirmation success/failure with real DB rows.
- ISP Admin cross-ISP isolation.
- App User ownership isolation.

## DB-Backed MFA Setup Confirmation Tests - 2026-05-15

Completed and tested:
- Added DB-backed MFA setup confirmation integration tests.
- Test file:
  - tests/integration/test_mfa_setup_integration.py
- Covered successful MFA setup confirmation:
  - creates real ISP/Admin rows
  - creates real MFA setup challenge
  - verifies authenticator TOTP code
  - enables account MFA
  - stores final account MFA secret encrypted
  - marks setup challenge as used
  - clears setup challenge authenticator secret
- Covered invalid MFA setup confirmation:
  - rejects wrong authenticator code
  - keeps account MFA disabled
  - keeps account MFA secret empty
  - increments setup challenge attempt_count

Impact:
- Database schema: no change.
- Existing data: no lasting change; tests roll back.
- API behavior: no change.
- Security: MFA setup success and invalid-code failure now have DB-backed coverage.
- SE diagrams: no change.

Next recommended DB-backed tests:
- ISP Admin cross-ISP isolation.
- App User ownership isolation.

## DB-Backed ISP Admin Isolation Test - 2026-05-15

Completed and tested:
- Added combined DB-backed ISP Admin cross-ISP isolation test.
- Test file:
  - tests/integration/test_isp_admin_isolation_integration.py
- Covered that ISP Admin from ISP A cannot access ISP B:
  - App User
  - Subscription Plan
  - User Subscription
  - Router

Impact:
- Database schema: no change.
- Existing data: no lasting change; test rolls back.
- API behavior: no change.
- Security: core ISP Admin multi-tenant isolation now has DB-backed coverage.
- SE diagrams: no change.

Next recommended DB-backed tests:
- App User ownership isolation.
- App User action ownership for plan change requests and device policies.

## DB-Backed App User Read Ownership Test - 2026-05-15

Completed and tested:
- Added combined DB-backed App User read ownership isolation test.
- Test file:
  - tests/integration/test_app_user_ownership_integration.py
- Covered that App User A cannot read App User B:
  - Alert
  - Prediction
  - Recommendation

Real DB constraint notes found during testing:
- Prediction risk_level must use allowed DB values such as "low".
- Alert severity constraint currently allows "low", "meduim", "high", "critical".
- Alert type constraint allows "high_usage", "new_device", "plan_exceeds_risk", "policy_failed", "system".
- Recommendation type constraint allows "upgrade_plan", "downgrade_pan", "keep_plan", "optimize_usage".

Schema cleanup needed later:
- Fix typo "meduim" to "medium".
- Fix typo "downgrade_pan" to "downgrade_plan".

Impact:
- Database schema: no change.
- Existing data: no lasting change; test rolls back.
- API behavior: no change.
- Security: App User read ownership now has DB-backed coverage.
- SE diagrams: no change.

Next recommended test:
- App User action ownership for device policies and subscription change requests.

## DB-Backed App User Action Ownership Test - 2026-05-15

Completed and tested:
- Added combined DB-backed App User action ownership test.
- Test file:
  - tests/integration/test_app_user_action_ownership_integration.py
- Covered that App User A cannot:
  - create a device policy for App User B's device
  - create a plan change request using App User B's subscription
  - create a plan change request using App User B's recommendation
- Also confirms blocked attempts do not create DeviceNetworkPolicy or SubscriptionChangeRequest rows.

Impact:
- Database schema: no change.
- Existing data: no lasting change; test rolls back.
- API behavior: no change.
- Security: App User action ownership now has DB-backed coverage.
- SE diagrams: no change.

Current quality status:
- DB-backed integration testing now covers:
  - invitation acceptance and MFA setup-required login
  - duplicate invitation/account protection
  - MFA setup confirmation success/failure
  - ISP Admin cross-ISP isolation
  - App User read ownership
  - App User action ownership

Next backend step:
- Continue Step 18.


---

## Step 18 Progress Ã¯Â¿Â½ 2026-05-16

### Step 18A/18B Ã¯Â¿Â½ Router Adapter Interface and Simulator Adapter

Completed and tested:

- Added router adapter package: `app/router_adapters/`.
- Added router adapter interface contract in `app/router_adapters/base.py`.
- Added standardized router capability model.
- Added standardized router device snapshot model.
- Added standardized router action result model.
- Added simulator router adapter in `app/router_adapters/simulator.py`.
- Added adapter registry in `app/router_adapters/registry.py`.
- For now, every router uses the simulator adapter.
- The simulator supports demo capabilities for:
  - connected device listing
  - total usage capability flag
  - per-device usage capability flag
  - bandwidth limit simulation
  - device priority simulation
- No real router credentials are accepted or stored.
- No raw router passwords are stored.
- Import checks passed.
- App import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed: 40 tests passed.
- Integration tests confirmed they are using `TEST_DATABASE_URL` with database name `pulsefi_test`.

Impact:

- Database schema: no change.
- Existing dev data: no change.
- Test database: used safely by integration tests.
- SE diagrams: later update architecture/DFD/sequence diagrams to include router adapter registry, simulator adapter, and capability-based router support.
- Security: safe because this step does not touch router credentials.

Next:

- Step 18C Ã¯Â¿Â½ Add service layer that uses the router adapter registry to apply pending device network policies and create router action logs.

---

## Step 18 Progress Ã¯Â¿Â½ 2026-05-16

### Step 18C Ã¯Â¿Â½ Router Policy Execution Service

Completed and tested:

- Added router action service package: `app/services/router_actions/`.
- Added `device_policy_execution_service.py`.
- Added service function: `execute_device_network_policy`.
- The service can load a pending `DeviceNetworkPolicy`.
- The service loads the related router and device.
- The service uses the router adapter registry to pick the correct router adapter.
- For now, the registry uses the simulator adapter.
- The service supports simulated execution for:
  - `bandwidth_limit`
  - `device_priority`
- The service checks router capabilities before applying actions.
- The service creates a `RouterActionLog` for audit/history.
- The service updates device policy status:
  - `applied` when simulator action succeeds
  - `failed` when simulator action fails
- Non-pending policies are not executed again.
- Import checks passed.
- App import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests continue using `TEST_DATABASE_URL` with database name `pulsefi_test`.

Impact:

- Database schema: no change.
- Existing dev data: no change unless the service is called manually/later by an endpoint.
- Test database: safe; tests use `pulsefi_test`.
- SE diagrams: later update router/device-policy sequence flow to show policy request -> execution service -> adapter registry -> simulator/real adapter -> router action log.
- Security: no router passwords or credentials are accepted or stored.

Next:

- Step 18D Ã¯Â¿Â½ Add safe API endpoint for executing a pending device policy through the router execution service.

---

## Step 18 Progress Ã¯Â¿Â½ 2026-05-16

### Step 18D Ã¯Â¿Â½ App User Device Policy Execution Endpoint

Completed and tested:

- Added safe App User endpoint:
  - `PATCH /api/v1/me/device-policies/{policy_id}/execute`
- Endpoint uses `get_current_app_user`.
- Endpoint checks ownership before execution by loading the policy through `get_my_device_policy`.
- App Users can only execute their own device policies.
- Only pending device policies can be executed.
- Execution uses the Step 18C router policy execution service.
- Execution goes through the router adapter registry.
- Current execution uses the simulator adapter.
- Successful execution updates policy status to `applied`.
- Failed execution updates policy status to `failed` and saves `failure_reason`.
- A `RouterActionLog` is created for execution history.
- Response returns:
  - updated device policy
  - router action log
  - execution message
- Added App User response schemas for router action logs and policy execution responses.
- Import checks passed.
- App import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests continue using `TEST_DATABASE_URL` with database name `pulsefi_test`.

Impact:

- Database schema: no change.
- Existing dev data: changes only when the endpoint is called; it updates policy status and creates a router action log.
- Test database: safe; tests use `pulsefi_test`.
- SE diagrams: later update App User device policy flow to show policy request -> execute endpoint -> execution service -> adapter registry -> simulator adapter -> router action log.
- Security: ownership check is enforced before router execution.
- Router credentials: no router passwords or credentials are accepted or stored.

Next:

- Step 18E Ã¯Â¿Â½ Add ISP Admin/router action log visibility or add tests for policy execution endpoint.

---

## Step 18 Progress Ã¯Â¿Â½ 2026-05-16

### Step 18E Ã¯Â¿Â½ ISP Admin Router Action Log Visibility

Completed and tested:

- Added ISP Admin router action log schemas.
- Added ISP Admin router action log service.
- Added ISP Admin router action log endpoint module.
- Added endpoints:
  - `GET /api/v1/isp-admin/router-action-logs`
  - `GET /api/v1/isp-admin/router-action-logs/{action_log_id}`
- ISP Admins can list router action logs for their own ISP.
- ISP Admins can view one router action log by ID.
- Router action log queries are scoped through the related router:
  - `Router.isp_id == current_admin.isp_id`
- List endpoint supports filters:
  - `router_id`
  - `policy_id`
  - `status`
  - `action_type`
  - `limit`
  - `offset`
- Endpoints are read-only.
- No router credentials or passwords are exposed.
- Import checks passed.
- App import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests continue using `TEST_DATABASE_URL` with database name `pulsefi_test`.

Impact:

- Database schema: no change.
- Existing dev data: no change because endpoints are read-only.
- Test database: safe; tests use `pulsefi_test`.
- SE diagrams: later update ISP Admin dashboard/use cases to include router action log visibility.
- Security: strict ISP scoping is enforced through router ownership.

Next:

- Step 18F Ã¯Â¿Â½ Add focused tests for router action execution and ISP Admin router action log isolation, or add router capability visibility endpoint.

---

## Step 18 Progress Ã¯Â¿Â½ 2026-05-16

### Step 18F Ã¯Â¿Â½ Router Policy Execution and Router Action Log Integration Tests

Completed and tested:

- Added focused integration test file:
  - `tests/integration/test_router_action_execution_integration.py`
- Added test for router policy execution:
  - creates ISP, App User, plan, subscription, router, device, and pending device policy
  - executes the policy through `execute_device_network_policy`
  - confirms policy status becomes `applied`
  - confirms `applied_at` is set
  - confirms `failure_reason` stays empty
  - confirms a `RouterActionLog` row is created
  - confirms action log uses simulator adapter response
- Added test for ISP Admin router action log isolation:
  - creates ISP A and ISP B
  - creates router action log under ISP B
  - confirms ISP A cannot list or view ISP B's action log
  - confirms ISP B can list and view its own action log
- Focused test initially caught a simulator typo:
  - `succe=True` was corrected to `success=True`
- Fixed simulator router adapter success response.
- Focused router action integration tests passed.
- Full test suite passed.
- Integration tests continue using `TEST_DATABASE_URL` with database name `pulsefi_test`.

Impact:

- Database schema: no change.
- Existing dev data: no change.
- Test database: used safely by integration tests.
- SE diagrams: no immediate diagram update, but later router policy execution and action log visibility should be reflected.
- Security: tests now verify ISP Admin router action log access is scoped by ISP ownership.

Next:

- Step 18G Ã¯Â¿Â½ Add router capability visibility endpoint or Step 18 cleanup/docs before moving to Step 19 usage ingestion.

---

## Step 18 Progress Ã¯Â¿Â½ 2026-05-16

### Step 18G Ã¯Â¿Â½ App User Router Capability Visibility Endpoint

Completed and tested:

- Added App User router capability response schema.
- Added router capability service helper:
  - `get_my_router_capabilities`
- Added endpoint:
  - `GET /api/v1/me/routers/{router_id}/capabilities`
- Endpoint uses `get_current_app_user`.
- Endpoint first loads the router through `get_my_router`, so the router must belong to the authenticated App User.
- Capability data comes from the router adapter registry.
- Current adapter is the simulator adapter.
- Response includes:
  - `router_id`
  - `adapter_name`
  - `can_read_total_usage`
  - `can_read_connected_devices`
  - `can_read_device_usage`
  - `can_apply_bandwidth_limit`
  - `can_apply_device_priority`
- This allows the mobile app to show/hide router features safely.
- Import checks passed.
- App import check passed.
- API router import check passed.
- Compile check passed.
- Pytest passed.
- Integration tests continue using `TEST_DATABASE_URL` with database name `pulsefi_test`.

Impact:

- Database schema: no change.
- Existing dev data: no change because endpoint is read-only.
- Test database: safe; tests use `pulsefi_test`.
- SE diagrams: later update App User router/device flow to include capability-based feature availability.
- Security: App User can only view capabilities for their own router.
- Router credentials: no router passwords or credentials are exposed.

Next:

- Step 18 cleanup/docs, then Step 19 Ã¯Â¿Â½ usage data ingestion and simulator usage generation.

---

## Step 19 Progress Ã¯Â¿Â½ 2026-05-16

### Step 19A/19B Ã¯Â¿Â½ Simulator Usage Ingestion Service and ISP Admin Trigger Endpoint

Completed and tested:

- Added usage ingestion service package:
  - `app/services/usage_ingestion/`
- Added simulator usage ingestion service.
- Added ISP Admin manual simulator ingestion endpoint:
  - `POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator`
- Endpoint uses `get_current_isp_admin`.
- Router lookup is scoped by `current_admin.isp_id`.
- Simulator ingestion only works for active routers.
- Router must be linked to an active user subscription.
- If connected devices exist, ingestion creates per-device usage records.
- If no connected devices exist, ingestion creates one router-level usage record with `device_id = null`.
- Usage records are stored with `source = "simulator"`.
- App User usage summary can read the generated usage through existing `/api/v1/me/usage/summary`.

Important design decision:

- The simulator does not create both router-total and per-device records for the same time window.
- This avoids double-counting in App User usage totals.
- Real router integration is still deferred.
- No router passwords or credentials are accepted or stored.

Impact:

- Database schema: no change.
- Existing data: new simulator usage records are added only when the endpoint is triggered.
- Security: ISP Admin ingestion is scoped to the logged-in admin's ISP.
- SE diagrams: later update DFD and sequence diagrams to show simulator/router usage ingestion.

Testing:

- Usage ingestion service import check passed.
- ISP Admin usage ingestion endpoint import check passed.
- API router import check passed.
- FastAPI app import check passed.
- Compile check passed.
- Pytest passed.
- Manual endpoint test passed with ISP Admin token.
- Generated usage appeared through the existing App User usage API.

Next step:

- Step 19C Ã¯Â¿Â½ connected device ingestion/update from simulator data, including device connection logs for new/seen devices.

---

## Step 19 Progress Ã¢â‚¬â€ 2026-05-16

### Step 19C Ã¢â‚¬â€ Simulator Connected Device Ingestion

Completed and tested:

- Added simulator connected-device ingestion service.
- Added endpoint:
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices
- Endpoint uses get_current_isp_admin.
- Router lookup is scoped by current_admin.isp_id.
- Device ingestion only works for active routers.
- Router must be linked to an active user subscription.
- Router subscription must be active.
- Simulator creates deterministic demo devices per router:
  - Simulator Phone
  - Simulator Laptop
  - Simulator Smart TV
- Existing simulator devices are updated instead of duplicated.
- Device connection logs are created for connected, seen, or reconnected events.

Impact:

- Database schema: no change.
- Existing data: adds/updates simulator device rows and device connection logs only when endpoint is triggered.
- Security: ISP Admin cannot ingest devices for routers outside their ISP.
- SE diagrams: later update DFD and sequence diagrams to show connected-device ingestion and connection logs.

Testing:

- Device ingestion service import check passed.
- ISP Admin schema import check passed.
- ISP Admin endpoint import check passed.
- API router import check passed.
- FastAPI app import check passed.
- Compile check passed.
- Pytest passed.
- Manual endpoint test passed.

Next step:

- Step 19D Ã¢â‚¬â€ combine simulator device ingestion and usage ingestion into a single demo ingestion flow, or add ISP Admin visibility for device connection logs.

---

## Step 19 Progress - 2026-05-16

### Step 19C - Simulator Connected Device Ingestion

Completed and tested:

- Added simulator connected-device ingestion service.
- Added endpoint:
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices
- Endpoint uses get_current_isp_admin.
- Router lookup is scoped by current_admin.isp_id.
- Device ingestion only works for active routers.
- Router must be linked to an active user subscription.
- Router subscription must be active.
- Simulator creates deterministic demo devices per router:
  - Simulator Phone
  - Simulator Laptop
  - Simulator Smart TV
- Existing simulator devices are updated instead of duplicated.
- Device connection logs are created for connected, seen, or reconnected events.

Impact:

- Database schema: no change.
- Existing data: adds/updates simulator device rows and device connection logs only when endpoint is triggered.
- Security: ISP Admin cannot ingest devices for routers outside their ISP.
- SE diagrams: later update DFD and sequence diagrams to show connected-device ingestion and connection logs.

Testing:

- Device ingestion service import check passed.
- ISP Admin schema import check passed.
- ISP Admin endpoint import check passed.
- API router import check passed.
- FastAPI app import check passed.
- Compile check passed.
- Pytest passed.
- Manual endpoint test passed.

Next step:

- Step 19D - combined simulator ingestion flow or ISP Admin device connection log visibility.

---

## Step 19 Progress - 2026-05-16

### Step 19D - Combined Simulator Ingestion Flow

Completed and tested:

- Added combined simulator ingestion service.
- Added endpoint:
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/run
- Combined flow runs device ingestion first.
- Combined flow runs usage ingestion second.
- Existing standalone endpoints remain available:
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices
  - POST /api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator
- Endpoint uses get_current_isp_admin.
- Router lookup remains scoped by current_admin.isp_id.
- One demo request can now update devices, device connection logs, and usage records.
- Fixed simulator device logs to use allowed event_type values.
- Repeated simulator device sightings now use connected instead of seen.

Impact:

- Database schema: no change.
- Existing data: adds/updates simulator device rows, connection logs, and usage records only when endpoint is triggered.
- Security: ISP Admin cannot run ingestion for routers outside their ISP.
- SE diagrams: later update sequence diagrams to show the combined simulator ingestion flow.

Testing:

- Full ingestion service import check passed.
- Full ingestion schema import check passed.
- ISP Admin endpoint import check passed.
- API router import check passed.
- FastAPI app import check passed.
- Compile check passed.
- Pytest passed.
- Manual combined endpoint test passed.

Next step:

- Step 19E - ISP Admin visibility for usage records and device connection logs.

---

## Step 19 Progress - 2026-05-16

### Step 19E - ISP Admin Usage and Device Connection Log Visibility

Completed and tested:

- Added ISP Admin usage record schemas.
- Added ISP Admin device connection log schemas.
- Added ISP Admin usage record service.
- Added ISP Admin device connection log service.
- Added endpoints:
  - GET /api/v1/isp-admin/usage-records
  - GET /api/v1/isp-admin/usage-records/{usage_record_id}
  - GET /api/v1/isp-admin/device-connection-logs
  - GET /api/v1/isp-admin/device-connection-logs/{connection_log_id}
- Usage records are scoped through Router.isp_id = current_admin.isp_id.
- Device connection logs are scoped through Router.isp_id = current_admin.isp_id.
- List endpoints support filters for router, device/user/subscription where relevant, source/event_type, time range, limit, and offset.

Impact:

- Database schema: no change.
- Existing data: no change; read-only visibility endpoints.
- Security: ISP Admin cannot view usage records or connection logs outside their ISP.
- SE diagrams: later update ISP Admin dashboard/reporting/data-flow diagrams to include usage and connection-log visibility.

Testing:

- ISP Admin schemas import check passed.
- ISP Admin services import check passed.
- ISP Admin endpoint import checks passed.
- API router import check passed.
- FastAPI app import check passed.
- Compile check passed.
- Pytest passed.
- Manual list/detail endpoint tests passed.

Next step:

- Step 19F - integration tests and Step 19 cleanup/finalization.

---

## Step 19 Progress - 2026-05-16

### Step 19F - Simulator Ingestion Tests and Step 19 Cleanup

Completed and tested:

- Added focused simulator ingestion service tests.
- Added regression coverage for simulator device event types.
- Confirmed simulator device payloads are deterministic per router.
- Confirmed simulator-generated MAC addresses are unique.
- Confirmed the invalid event_type value seen does not return.
- Confirmed combined simulator ingestion runs device ingestion before usage ingestion.
- Refactored simulator device event type selection into a helper function.

Impact:

- Database schema: no change.
- Existing data: no change.
- Security: no token, credential, or router password changes.
- Quality: Step 19 now has regression coverage for the event_type constraint issue found during manual testing.

Testing:

- New Step 19F test file passed.
- Full pytest passed.
- Compile check passed.

Step 19 status:

- Step 19A: simulator usage ingestion service - complete.
- Step 19B: ISP Admin manual usage ingestion endpoint - complete.
- Step 19C: simulator connected-device ingestion and connection logs - complete.
- Step 19D: combined simulator ingestion endpoint - complete.
- Step 19E: ISP Admin usage and connection-log visibility - complete.
- Step 19F: tests and cleanup - complete.

Next step:

- Step 20 - Alerts system.

---

## Step 20 Progress - 2026-05-16

### Step 20A - Alert Generation Service

Completed and tested:

- Added modular alert generation service under `app/services/alerts/`.
- Connected alert generation to ISP Admin simulator ingestion endpoints.
- Added automatic alert generation for:
  - `high_usage`
  - `plan_exceed_risk`
  - `unusual_consumption`
  - `new_device_connected`
- Added `alerts_created` fields to simulator ingestion responses.
- Added Alembic migration to update the `alerts.alert_type` check constraint.
- Confirmed old `chk_alert_type` constraint blocked `plan_exceed_risk`.
- Fixed the constraint so Step 20 alert types are allowed.
- Tested simulator ingestion with a tiny temporary plan limit.
- Confirmed a plan exceed alert can be generated.
- Confirmed App User can view alerts through `/api/v1/me/alerts`.
- Confirmed App User can mark an alert as read through `/api/v1/me/alerts/{alert_id}/read`.
- Restored the original plan limit after local testing.

Important behavior:

- High usage alert triggers at 80% of plan limit.
- Plan exceed risk alert triggers at 100% or more of plan limit.
- Unusual consumption alert triggers when the latest usage window is at least 3x the recent average and enough previous windows exist.
- New device alert triggers when simulator discovers a newly connected device.
- Duplicate unread alerts are avoided.

Impact:

- Database schema: yes, alert type check constraint updated.
- Existing data: no existing rows deleted.
- API behavior: simulator ingestion can now create alerts.
- App User/mobile: existing alert list/detail/mark-read endpoints now have generated alerts to show.
- SE diagrams: later update alert flows in DFD, user activity diagram, and sequence diagrams.

Pending Step 20 work:

- Step 20B: Generate `policy_failed` alerts from failed router/device policy execution.
- Step 20C: Add ISP Admin alert visibility if needed for dashboard monitoring.
- Step 20D: Add focused tests for alert generation and ownership isolation.

---

## Step 20 Progress - 2026-05-16

### Step 20B - Policy Failed Alerts

Completed and tested:

- Connected failed device policy execution to the alert generation system.
- Added `generate_policy_failed_alert_for_policy`.
- Failed device policy execution now creates a `policy_failed` App User alert.
- Confirmed failed `bandwidth_limit` policy creates:
  - failed `DeviceNetworkPolicy`
  - failed `RouterActionLog`
  - unread `policy_failed` alert
- Updated `router_action_logs.action_type` database check constraint to allow:
  - `bandwidth_limit`
  - `device_priority`
- Applied the router action constraint manually through pgAdmin because the limited app DB role is not the owner of `router_action_logs`.
- Stamped Alembic to the latest head after manual schema application.

Impact:

- Database schema: yes, router action type check constraint updated.
- Existing data: no rows deleted.
- API behavior: failed device policy execution now creates an App User alert.
- App User/mobile: users can now see policy failure alerts.
- SE diagrams: later update device policy failure alert flow.

Current next Step 20 work:

- Step 20C: Add ISP Admin alert visibility if needed for dashboard monitoring.
- Step 20D: Add focused alert generation tests and ownership/isolation tests.

---

## Step 20 Progress - 2026-05-16

### Step 20C - ISP Admin Alert Visibility

Completed and tested:

- Added ISP Admin alert schemas.
- Added ISP Admin alert service.
- Added ISP Admin alert endpoints.
- Added endpoints:
  - `GET /api/v1/isp-admin/alerts`
  - `GET /api/v1/isp-admin/alerts/{alert_id}`
- ISP Admins can view App User alerts under their own ISP.
- Alert queries are scoped through `AppUser.isp_id == current_admin.isp_id`.
- Added filters for:
  - user
  - subscription
  - device
  - alert type
  - severity
  - status
  - created date range
- Confirmed ISP Admin can list and view alerts for users under their ISP.
- ISP Admin alert access is read-only for now.
- Admins do not have personal alerts yet; current alerts belong to App Users.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: ISP Admin dashboard can now view user alerts.
- Security: ISP Admin alert visibility is scoped by current_admin.isp_id.
- SE diagrams: later update ISP Admin dashboard alert visibility flow.

Current next Step 20 work:

- Step 20D: Add focused alert tests and ownership/isolation tests.

---

## Step 20 Progress - 2026-05-16

### Step 20D - Alert Generation Tests

Completed:

- Added focused alert generation service tests.
- Tested `plan_exceed_risk` alert creation.
- Tested `policy_failed` alert creation.
- Tested duplicate unread `policy_failed` alert prevention.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: no new endpoint behavior.
- Quality: improves confidence in Step 20 alert generation logic.

Pending test expansion:

- App User alert ownership isolation.
- ISP Admin alert ISP isolation.
- New device alert generation.
- Unusual consumption alert generation.

---

## Step 20 Progress - 2026-05-16

### Step 20E - Alert Ownership and ISP Isolation Tests

Completed:

- Added service-level alert isolation tests.
- Tested App User alert list queries include `current_user.id`.
- Tested App User alert detail queries require both `alert_id` and `current_user.id`.
- Tested ISP Admin alert list queries join through App User and filter by `AppUser.isp_id`.
- Tested ISP Admin alert detail queries require both `alert_id` and `AppUser.isp_id`.
- Tested ISP Admin alert filters do not remove ISP scoping.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: no new endpoint behavior.
- Security: improves confidence that alert access is scoped correctly.

Pending Step 20 test expansion:

- New device alert generation test.
- Unusual consumption alert generation test.

---

## Step 21 Progress - 2026-05-16

### Step 21A - Prediction Foundation

Completed and tested:

- Added modular prediction service under `app/services/predictions/`.
- Added rule-based usage prediction generation.
- Added ISP Admin prediction generation endpoint:
  - `POST /api/v1/isp-admin/predictions/subscriptions/{subscription_id}/generate`
- Prediction logic calculates:
  - observed usage in GB
  - average daily usage in GB
  - predicted full-cycle usage in GB
  - confidence score
  - risk level
- Risk levels:
  - `low`: predicted usage below 80% of plan limit
  - `medium`: predicted usage from 80% to below 100%
  - `high`: predicted usage at or above 100%
- Prediction rows are stored in the existing `predictions` table.
- App User can view generated predictions through existing:
  - `GET /api/v1/me/predictions`
  - `GET /api/v1/me/predictions/{prediction_id}`
- ISP Admin prediction generation is scoped by `current_admin.isp_id`.

Impact:

- Database schema: no change.
- Existing data: prediction rows can be inserted when endpoint is used.
- API behavior: ISP Admin can generate prediction records for subscriptions under their ISP.
- App User/mobile: users can now see generated prediction records.
- SE diagrams: later update prediction generation flow in DFD and sequence diagrams.

Current next Step 21 work:

- Step 21B: Recommendation foundation based on predictions and available plans.

---

## Step 21 Progress - 2026-05-16

### Step 21B - Recommendation Foundation

Completed and tested:

- Added modular recommendation generation service under `app/services/recommendations/`.
- Added rule-based recommendation generation from prediction records.
- Added ISP Admin recommendation generation endpoint:
  - `POST /api/v1/isp-admin/recommendations/predictions/{prediction_id}/generate`
- Recommendation logic supports:
  - `upgrade_plan`
  - `downgrade_plan`
  - `stay_current`
  - `monitor_usage`
- Added ISP Admin recommendation response schemas.
- Connected ISP Admin recommendation endpoint to the ISP Admin router.
- Generated recommendations are stored in the existing `recommendations` table.
- App User can view generated recommendations through existing:
  - `GET /api/v1/me/recommendations`
  - `GET /api/v1/me/recommendations/{recommendation_id}`
- Recommendation generation is scoped by `current_admin.isp_id`.
- Added Alembic migration to update `recommendations.recommendation_type` check constraint.
- Confirmed recommendation generation works after updating the database constraint.

Important behavior:

- If predicted usage exceeds current plan capacity, the system recommends an upgrade when a better active plan exists.
- If predicted usage is far below the current plan, the system may recommend a downgrade when a suitable smaller active plan exists.
- If the current plan is suitable, the system recommends staying on the current plan.
- If no better plan exists, the system recommends monitoring usage.
- Duplicate new recommendations for the same prediction are avoided.

Impact:

- Database schema: yes, recommendation type check constraint updated.
- Existing data: no existing rows deleted.
- API behavior: ISP Admin can generate recommendation records from predictions.
- App User/mobile: users can now see generated recommendation records.
- SE diagrams: later update recommendation generation flow in DFD and sequence diagrams.

Current next Step 21 work:

- Step 21C: Add prediction/recommendation tests and isolation tests.

---

## Step 21 Progress - 2026-05-16

### Step 21C - Prediction and Recommendation Tests

Completed:

- Added focused service tests for prediction generation.
- Tested prediction generation math:
  - observed usage
  - average daily usage
  - predicted full-cycle usage
  - confidence score
  - risk level
- Added focused service tests for recommendation generation.
- Tested `stay_current` recommendation path.
- Tested `upgrade_plan` recommendation path.
- Tested duplicate new recommendation prevention.
- Tested ISP Admin recommendation generation keeps ISP scope.
- Tested App User prediction detail query includes `current_user.id`.
- Tested App User recommendation detail query includes `current_user.id`.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: no new endpoint behavior.
- Quality: improves confidence in Step 21 prediction/recommendation logic and ownership scoping.

Pending Step 21 work:

- Add downgrade and monitor usage path tests if needed.
- Connect recommendations to subscription change request flow if needed.

---

## Step 21 Progress - 2026-05-16

### Step 21D - Recommendation Cleanup Tests

Completed:

- Added `downgrade_plan` recommendation path test.
- Added `monitor_usage` recommendation path test.
- Confirmed recommendation generation test coverage now includes:
  - `upgrade_plan`
  - `downgrade_plan`
  - `stay_current`
  - `monitor_usage`
  - duplicate new recommendation prevention
  - ISP-scoped recommendation generation query
  - App User prediction/recommendation ownership query filters

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: no new endpoint behavior.
- Quality: Step 21 recommendation paths are now covered by focused service tests.

Step 21 status:

- Step 21A complete: Prediction generation foundation.
- Step 21B complete: Recommendation generation foundation.
- Step 21C complete: Prediction/recommendation service tests.
- Step 21D complete: Recommendation cleanup path tests.

Recommended next backend work:

- Connect recommendations to subscription change request flow if needed.
- Or move to reporting/analytics/dashboard improvements.

---

## Step 22 Planning - 2026-05-16

Step 21 is complete enough to move forward.

Completed Step 21 items:

- Step 21A: Prediction generation foundation.
- Step 21B: Recommendation generation foundation.
- Step 21C: Prediction and recommendation service tests.
- Step 21D: Recommendation cleanup path tests.

Next backend step:

### Step 22 - Recommendation to Plan Change Request Integration

Goal:

Connect generated recommendations to the existing subscription change request flow.

Planned work:

- Step 22A: Review existing App User plan change request flow.
- Step 22B: Add ISP Admin plan change request list/detail visibility.
- Step 22C: Add ISP Admin approve/reject behavior.
- Step 22D: Add tests and docs.

Important rules:

- App User plan change requests must stay scoped by `current_user.id`.
- ISP Admin plan change request queries must stay scoped by `current_admin.isp_id`.
- Recommendation-linked requests must verify the recommendation belongs to the same App User.
- Do not let ISP Admins act on requests from another ISP.


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


---

## Step 25B Progress - 2026-05-17

### Standard API Error Response Foundation

Completed and tested:

- Added shared API error response helpers:
  - `app/core/api_errors.py`
- Registered FastAPI exception handlers in:
  - `app/main.py`
- Standardized HTTP error responses into this shape:
  - `error`
  - `message`
  - optional `details`
- Standardized validation errors with:
  - `error = validation_error`
  - `message = Request validation failed`
  - `details = validation error list`
- Standardized unexpected server errors so internal exception details are not leaked.
- Updated existing API tests that still expected the old FastAPI `detail` response key.
- Added API tests for:
  - normal HTTPException response shape
  - validation error response shape
  - internal server error redaction

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: error response format changed from `detail` to `error/message`.
- Frontend integration: easier because web/mobile clients can handle errors consistently.
- SE diagrams: no direct update needed.

Next work:

- Continue Step 25 quality hardening before frontend integration.

---

## Step 25C Progress - 2026-05-17

### Tightened Auth Rate Limits

Completed and tested:

- Updated auth-sensitive endpoint rate limits to 5 attempts per 15 minutes.
- Updated login rate-limit regression test from 10 allowed attempts to 5 allowed attempts.

Affected endpoints:

- POST /api/v1/auth/login
- POST /api/v1/auth/mfa/verify
- POST /api/v1/auth/mfa/setup/confirm
- POST /api/v1/auth/password/forgot
- POST /api/v1/auth/password/reset
- POST /api/v1/auth/invitations/accept

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: stricter 429 rate limiting for auth-sensitive endpoints.
- Security: improves protection against brute-force login, MFA, reset-token, and invitation-token guessing.
- Production note: current limiter is still in-memory and should later be replaced with Redis/shared-store rate limiting for multi-worker deployment.

---

## Step 25D Progress - 2026-05-17

### API Contract Refresh for Error Responses and Rate Limits

Completed:

- Updated docs/API_CONTRACT.md with the standard API error response shape.
- Documented frontend handling for error, message, and optional details.
- Documented auth rate limit behavior: 5 attempts per 15 minutes.
- Documented affected auth endpoints.
- Documented expected rate_limited response.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: no new runtime change; this documents Step 25B and Step 25C behavior.
- Frontend integration: improved because web/mobile clients now know how to handle backend errors and rate limits.
- SE diagrams: no direct update needed.

---

## Step 25E Progress - 2026-05-17

### Final Docs and Status Alignment Before Frontend Integration

Completed:

- Updated README.md current backend status to Step 25 complete.
- Updated AGENTS.md current backend position to Step 25 complete.
- Updated ROADMAP.md current position to Step 25 complete.
- Updated BACKEND_QUALITY_BACKLOG.md current context to Step 25 complete.
- Confirmed the documented next step is frontend integration.

Final backend readiness status:

- Backend MVP/demo foundation is complete through Step 25E.
- Next work should focus on frontend integration.
- Backend changes during frontend integration should be limited to required P0/P1 fixes or API contract updates.

Production reminders:

- Replace in-memory auth rate limiting with Redis/shared-store rate limiting before production multi-worker deployment.
- Configure real email delivery before production token/email flows.
- Keep router credential storage deferred until encrypted credential storage is intentionally implemented.
- Keep DATA_ENCRYPTION_KEY and all secrets out of Git.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: no runtime change.
- GitHub/docs: final project status alignment.
- SE diagrams: no direct update needed for this cleanup.

---

## Step 26A Progress - 2026-05-17

### Removed Admin-Only Router Fields from App User Router Responses

Completed and tested:

- Reduced App User router response schema to safe mobile-facing fields only.
- Removed admin/management fields from /api/v1/me/routers responses:
  - isp_id
  - assigned_by_admin_id
  - router_ip
  - mac_address
  - api_endpoint
  - username
- Confirmed password_encrypted is not exposed.
- Added regression test confirming App User router response excludes admin-only fields.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: App User router response is now safer and smaller.
- Frontend integration: mobile app should use router id, subscription id, name, model, status, and timestamps only.
- Security: reduces exposure of router management/credential-adjacent information.

Codex review item addressed:

- P1 router management fields leak to app-user responses.

---

## Step 26A Progress - 2026-05-17

### Removed Admin-Only Router Fields from App User Router Responses

Completed and tested:

- Reduced App User router response schema to safe mobile-facing fields only.
- Removed admin/management fields from /api/v1/me/routers responses:
  - isp_id
  - assigned_by_admin_id
  - router_ip
  - mac_address
  - api_endpoint
  - username
- Confirmed password_encrypted is not exposed.
- Added regression test confirming App User router response excludes admin-only fields.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: App User router response is now safer and smaller.
- Frontend integration: mobile app should use router id, subscription id, name, model, status, and timestamps only.
- Security: reduces exposure of router management/credential-adjacent information.

Codex review item addressed:

- P1 router management fields leak to app-user responses.

---

## Step 26A Progress - 2026-05-17

### Removed Admin-Only Router Fields from App User Router Responses

Completed and tested:

- Reduced App User router response schema to safe mobile-facing fields only.
- Removed admin/management fields from /api/v1/me/routers responses:
  - isp_id
  - assigned_by_admin_id
  - router_ip
  - mac_address
  - api_endpoint
  - username
- Confirmed password_encrypted is not exposed.
- Added regression test confirming App User router response excludes admin-only fields.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: App User router response is now safer and smaller.
- Frontend integration: mobile app should use router id, subscription id, name, model, status, and timestamps only.
- Security: reduces exposure of router management/credential-adjacent information.

Codex review item addressed:

- P1 router management fields leak to app-user responses.

---

## Step 26A Progress - 2026-05-17

### Removed Admin-Only Router Fields from App User Router Responses

Completed and tested:

- Reduced App User router response schema to safe mobile-facing fields only.
- Removed admin/management fields from /api/v1/me/routers responses:
  - isp_id
  - assigned_by_admin_id
  - router_ip
  - mac_address
  - api_endpoint
  - username
- Confirmed password_encrypted is not exposed.
- Added regression test confirming App User router response excludes admin-only fields.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: App User router response is now safer and smaller.
- Frontend integration: mobile app should use router id, subscription id, name, model, status, and timestamps only.
- Security: reduces exposure of router management/credential-adjacent information.

Codex review item addressed:

- P1 router management fields leak to app-user responses.

---

## Step 26B Progress - 2026-05-17

### Fixed OpenAPI Error Schema Documentation Mismatch

Completed and tested:

- Added custom OpenAPI helper: app/core/openapi.py.
- Connected custom OpenAPI generation in app/main.py.
- Added standard OpenAPI schemas:
  - APIErrorResponse
  - APIValidationErrorResponse
- Replaced default FastAPI 422 documentation with the standard validation error shape.
- Added documented 429 responses for auth-sensitive rate-limited endpoints.
- Added documented 401/403 responses for protected endpoints.
- Added documented 404 responses for path-parameter endpoints.
- Added documented 500 response shape.
- Added OpenAPI regression tests.
- Updated docs/API_CONTRACT.md with the OpenAPI error schema contract.

Impact:

- Database schema: no change.
- Existing data: no change.
- Runtime API behavior: no change.
- OpenAPI/Swagger behavior: changed to better match standard runtime error responses.
- Frontend integration: improved because generated clients and docs now understand error/message/details responses.

Codex review item addressed:

- P1 OpenAPI still documents default FastAPI validation errors.

---

## Step 26C Progress - 2026-05-17

### Hardened ISP Ownership Paths for Usage, Ingestion, and Analytics

Completed and tested:

- Added shared ISP Admin ownership-scope helpers:
  - apply_router_isp_ownership_scope
  - apply_usage_record_isp_ownership_scope
- Hardened ISP Admin usage record list/detail queries to require the full ownership chain.
- Hardened simulator usage ingestion router lookup to require the full router -> subscription -> user -> ISP chain when ISP scope is provided.
- Hardened simulator device ingestion router lookup to require the full router -> subscription -> user -> ISP chain when ISP scope is provided.
- Hardened analytics usage aggregation to require consistent router, subscription, user, and ISP ownership.
- Added regression tests confirming ownership-scope SQL includes the required joins and ISP filters.

Ownership rule now enforced more strictly for affected services:

- Router -> UserSubscription -> AppUser -> ISP
- UsageRecord -> Router
- UsageRecord -> UserSubscription
- UsageRecord -> AppUser
- Router/UserSubscription/AppUser must agree on ownership before usage is read or aggregated.

Impact:

- Database schema: no change.
- Existing data: no migration or rewrite.
- API behavior: malformed cross-ISP-linked records are less likely to appear in ISP Admin usage/analytics results.
- Security: reduces cross-ISP leakage risk from inconsistent or malformed linked rows.
- Frontend integration: safer dashboard usage/analytics data.

Codex review item addressed:

- P1 some ISP ownership paths depend on partial joins.

---

## Step 26D Progress - 2026-05-17

### Validated App User Device Policy Request Types and Action Fields

Completed and tested:

- Tightened App User device policy request validation.
- Changed policy_type from a free string to supported values only:
  - bandwidth_limit
  - device_priority
- Added validation that bandwidth_limit policies require bandwidth_limit_mbps.
- Added validation that bandwidth_limit policies reject priority_level.
- Added validation that device_priority policies require priority_level.
- Added validation that device_priority policies reject bandwidth_limit_mbps.
- Added tests for invalid policy types and missing/incorrect action fields.
- Added tests for valid bandwidth_limit and device_priority policy requests.

Impact:

- Database schema: no change.
- Existing data: no change.
- API behavior: invalid device policy requests are now rejected before they can be saved.
- Frontend integration: mobile app now gets immediate validation errors for unsupported or malformed policy requests.
- Security/quality: prevents unsupported pending policies from being created and failing later during execution.

Codex review item addressed:

- P1 device policy creation accepts invalid policy types.

---

## Step 26E Progress - 2026-05-17

### Invalidated Old Password Reset Tokens Account-Wide

Completed and tested:

- Added helper to mark active password reset tokens as used for one account.
- New password reset token creation now invalidates existing active reset tokens for the same account.
- Successful password reset now invalidates all active reset tokens for the same account.
- Kept reset token lookup based on token hash.
- Added focused service tests for:
  - invalidating existing tokens when creating a new reset token
  - invalidating all active account tokens after successful password reset

Impact:

- Database schema: no change.
- Existing data: no migration or rewrite.
- API behavior: old password reset links for the same account become unusable after a newer reset token is created or after a password reset succeeds.
- Security: reduces risk from older leaked reset links remaining valid until expiry.
- Frontend integration: no UI change needed; reset failures already return the normal invalid/expired token response.

Codex review item addressed:

- P1 password reset tokens are not invalidated account-wide.

---

## Step 26F Progress - 2026-05-17

### Remaining P2/P3 Backend Hardening Before Frontend Integration

Completed:

- Expanded `.env.example` with `DATA_ENCRYPTION_KEY`, `EMAIL_DELIVERY_ENABLED`, `TEST_DATABASE_URL`, and trusted proxy guidance.
- Added email verification rate limiting at 5 attempts per 15 minutes.
- Aligned MFA login and MFA setup challenge attempt counters to 5 attempts.
- Hardened rate-limit client identification so `X-Forwarded-For` is trusted only from configured trusted proxy IPs.
- Added stale plan-change approval protection: ISP Admin approval now rejects with 409 Conflict if the subscription plan changed after request creation.
- Added SQLAlchemy model check constraints and an Alembic migration for device policy, recommendation, report, and user subscription enum-like fields.
- Added simulator honesty fields to router capability responses: `integration_mode` and `is_simulator`.
- Added focused API/service tests for rate limits, email verification throttling, stale plan-change review, model constraints, simulator capability mode, ISP Admin scope wiring, and device policy validation responses.

Validation notes:

- Focused auth, plan-change, model-constraint, router capability, and high-risk API tests passed.
- Alembic sees the new migration as head.
- Local `alembic upgrade head` is blocked by the expected limited runtime DB role because `pulsefi_app` is not table owner; apply this migration with a migration/admin DB role.

Impact:

- Database schema: yes, new check-constraint migration.
- Existing data: no data rewrite.
- API behavior: email verification is now rate-limited; stale plan-change approval returns 409; router capabilities expose simulator mode.
- Frontend integration: safer and clearer before web/mobile work begins.
- SE diagrams: later mention simulator/demo mode in router capability flow if diagrams are updated.

## 2026-05-18 Frontend/Admin UI + Auth Integration Handoff

The PulseFi admin frontend has been updated in `C:\PulseFi\pulsefi-admin-web`.

Current frontend structure:
- `npm run dev` loads the real admin web app shell.
- `npm run dev:design` loads the temporary design preview hub.
- `src/App.tsx` switches by `import.meta.env.MODE === "design"`.
- `src/App.real.tsx` is the real admin web app shell.
- `src/PulseFiDesignPreviewApp.tsx` and `src/PulseFiDesignHub.tsx` are design/dev-only.
- The real admin app must not expose App User, States, White/Black switch, or manual role tabs.
- The real product has one shared admin login page.
- Backend token/account role should route:
  - Platform Admin -> Platform Admin dashboard
  - ISP Admin -> ISP Admin dashboard
- App User UI is only design reference for the future React Native mobile app, not part of the admin web product.

Frontend auth integration progress:
- Added `src/api/adminAuth.ts`.
- Login now calls `POST /api/v1/auth/login`.
- Login request now includes `account_type: "admin"`.
- Frontend then attempts to route using role from login response, JWT payload, or `GET /api/v1/auth/me`.
- `npm run lint` and `npm run build` passed after the `adminAuth.ts` update.

Current blocker:
- Backend returns `429 rate_limited` after repeated login attempts.
- Earlier backend returned `422 validation_error` because `account_type` was missing; this has been fixed on frontend.
- Codex should inspect backend auth rate-limit implementation and provide a clean local-dev reset/fix without weakening production security.
- Codex should verify `/auth/me` response shape includes enough role/account info for frontend routing.
- Codex should verify MFA-required flow for ISP Admin and connect/finish the frontend MFA verification path.

Important security/product rules:
- Do not store or display router passwords until encryption is implemented.
- ISP Admin backend queries must remain scoped by `current_admin.isp_id`.
- Platform Admin and ISP Admin are the only admin roles.
- App User is not an admin role.
- Design preview hub must stay development-only.

## 2026-05-18 Auth/UI Integration Cleanup

Completed:
- Added a development-only auth rate-limit reset endpoint:
  - `POST /api/v1/auth/rate-limit/reset`
  - Available only when `DEBUG=True`.
  - Hidden from OpenAPI.
  - Clears the existing in-memory rate-limit state without changing production limits.
- Added API regression coverage for:
  - local DEBUG reset clears the login rate-limit bucket
  - reset endpoint returns 404 when `DEBUG=False`
  - `/auth/me` returns the frontend routing shape including `account_type`, `account_id`, `role`, `username`, status, and MFA fields
- Confirmed backend MFA behavior:
  - `mfa_required=True` and `mfa_enabled=False` returns `mfa_setup_required` and does not issue an access token.
  - `mfa_enabled=True` returns `mfa_required` and must be completed through `/api/v1/auth/mfa/verify`.
- Updated the real admin frontend shell so:
  - `npm run dev` loads the real admin login/dashboard app.
  - `npm run dev:design` loads the design preview hub.
  - the real app no longer renders `PulseFiWhiteDesignPreview` or `PulseFiPlatformAdminWhitePreview`.
  - routing uses the backend admin role saved from login/MFA result.
  - only `platform_admin` and `isp_admin` are accepted as admin roles.
  - MFA verify and MFA setup confirm are wired to backend endpoints.
- Removed the temporary `src/App.backup.tsx` file from the frontend source tree.

Local dev reset command:
- If repeated bad login attempts trigger `429 rate_limited` while `DEBUG=True`, call:
  - `POST http://127.0.0.1:8000/api/v1/auth/rate-limit/reset`
- Restarting the backend process also clears the in-memory limiter.

Production note:
- The reset endpoint is disabled outside DEBUG.
- The limiter is still in-memory and must be replaced with Redis/shared-store rate limiting before multi-worker production deployment.

## Step 27C - Admin Auth Routing, Session Restore, and MFA Integration - 2026-05-18

Frontend checkpoint completed in `C:\PulseFi\pulsefi-admin-web`.

Completed:
- Reconciled the admin app split:
  - normal `npm run dev` and production build load the real admin app
  - `npm run dev:design` / Vite `--mode design` load the design preview hub
  - App User preview remains design-only and is not a production admin role
- Preserved existing dashboard work:
  - Platform Admin summary, ISP create/list/update, and ISP Admin invitation workflow
  - ISP Admin summary, App User invitations, App User management, plans, subscriptions, routers, monitoring, operations, network activity, and intelligence center
- Finished shared admin auth routing:
  - login sends `account_type: "admin"`
  - normal token response saves an admin session and routes by backend role
  - page load with an existing token now calls `GET /api/v1/auth/me`
  - invalid/expired tokens, non-admin accounts, and App User tokens clear local admin session and return to login
  - only `platform_admin` and `isp_admin` are accepted in admin web
- Finished MFA frontend flow:
  - `mfa_required` responses show MFA verification and submit `POST /api/v1/auth/mfa/verify`
  - `mfa_setup_required` responses show MFA setup and submit `POST /api/v1/auth/mfa/setup/confirm`
  - session is saved only after the backend returns a valid admin token

Backend contract changes:
- None in this checkpoint.
- Existing local-dev reset remains `POST /api/v1/auth/rate-limit/reset` when `DEBUG=True`.

Validation completed:
- Frontend lint passed.
- Frontend production build passed.
- Frontend design-mode build passed.

Manual browser testing still needed:
- Start backend and frontend, then test Platform Admin login, ISP Admin login, session refresh, expired-token clearing, MFA verify, MFA setup confirm, and invitation URL token cleanup.

## Automatic Intelligence Idempotency Update

The automatic intelligence service now avoids duplicate prediction and recommendation rows on repeated scheduler runs.

Behavior:
- Reuses today's existing prediction for each subscription when present.
- Reuses an existing recommendation for that prediction when present.
- Creates only missing prediction/recommendation records.
- Repeated scheduler ticks should skip/reuse already processed subscriptions instead of duplicating rows.

## Step 27D - ISP Admin Intelligence, Recommendations, and Real Dashboard Integration - 2026-05-18

Backend updates:
- Added ISP Admin recommendation viewing routes:
  - `GET /api/v1/isp-admin/recommendations`
  - `GET /api/v1/isp-admin/recommendations/{recommendation_id}`
- Recommendation list supports `status`, `user_id`, `subscription_id`, `limit`, and `offset` filters.
- Recommendation ownership is scoped through App User, subscription, optional linked prediction, and `current_admin.isp_id`.
- Non-owned or fake recommendations return `404`.
- Platform Admin and App User accounts cannot access ISP Admin recommendation routes.
- Database schema did not change.

Frontend updates:
- The real ISP Admin dashboard Intelligence Center now connects analytics summary, recommendation history, recent reports, active subscriptions, prediction generation, recommendation generation, and automatic intelligence runs.
- The frontend API client remains environment-based:
  - `VITE_API_BASE_URL` when set
  - fallback `http://127.0.0.1:8000/api/v1`
- `.env` files remain local/uncommitted.

Validation target:
- Backend: pytest, compileall, git diff --check, git status.
- Frontend: lint, production build, design build, git diff --check, git status.
- Manual browser checks still need backend and frontend running together.

## Frontend/Backend Checkpoint - ISP Admin Invites ISP Admin

Added same-ISP ISP Admin invitation support.

Backend:
- `POST /api/v1/isp-admin/admin-invitations`
- `GET /api/v1/isp-admin/admin-invitations`
- `PATCH /api/v1/isp-admin/admin-invitations/{invitation_id}/revoke`

Security rule:
- ISP Admin invitation endpoints are scoped by `current_admin.isp_id`.
- ISP Admin cannot choose or override `isp_id`.
- Invited account role is always `isp_admin`.
- Invitation uses existing account invitation acceptance flow.

Frontend:
- ISP Admin dashboard now includes ISP Admin invitation management.
- ISP Admin can create, list, filter, and revoke same-ISP ISP Admin invitations.
- Development invitation token is shown only if backend returns it.

## Frontend Checkpoint - Final Admin UI/UX Cleanup and Theme Support

Completed final admin web UI/UX cleanup in the frontend repo.

Frontend commit:
- pulsefi-admin-web: 5ee1003

Completed:
- Cleaned redundant UI changes from the admin web app.
- Removed the redundant Platform Admin separate ISP Admin Invitations sidebar/page.
- Kept Platform Admin ISP Admin invitation create/list/filter/revoke inside ISP Management after selecting an ISP.
- Preserved Platform Admin ISP Admin Accounts as a separate section for accepted admin accounts.
- Preserved Platform Admin real features: Overview, ISP Management, ISP Admin Accounts, and System Health/Platform Readiness.
- Preserved ISP Admin real sections: Overview, Users, App User Invitations, ISP Admin Invitations, Plans, Subscriptions, Routers, Intelligence, Monitoring, Operations, and Network.
- Added live admin dark/light mode support.
- Theme persists with localStorage key pulsefi-admin-theme.
- Live admin wrapper uses data-theme="dark" / data-theme="light".
- Added topbar theme toggle for Platform Admin and ISP Admin dashboards.
- Cleaned old CSS patch blocks and temporary layout/auth fixes.
- Preserved dark login, hidden login logo, full-width login button, forgot-password below password input, compact MFA page, compact MFA code input, and compact MFA buttons.
- Fixed Platform Admin sidebar/navigation cleanup.
- Kept table scrolling inside cards and avoided whole-page horizontal scrolling.
- Deleted temporary CSS backup file src/styles/pulsefi-admin.css.fullwidth-backup.

Validation reported:
- 
pm.cmd run lint passed.
- 
pm.cmd run build passed.
- 
pm.cmd run build -- --mode design passed.
- git diff --check passed with only CRLF normalization warnings.

Manual smoke test still required:
- Platform Admin login, theme toggle, Overview, ISPs, ISP Admin Accounts, System Health.
- ISP Admin login, theme toggle, Overview, Users, App User Invitations, ISP Admin Invitations, Plans, Subscriptions, Routers, Intelligence, Monitoring, Operations, Network.
- End-to-end invitation flow: ISP Admin invites another ISP Admin, invitee accepts, new ISP Admin logs in and sees same-ISP scoped dashboard.

## Admin Settings and Reset Link Checkpoint

Backend:
- Added reset-link email delivery for `POST /api/v1/auth/password/forgot`.
- Password reset links use `FRONTEND_ADMIN_URL/reset-password?token=...`.
- Production responses do not expose raw reset tokens or reset URLs.
- DEBUG responses may include `dev_reset_url` for local testing.
- Added authenticated settings identity flow:
  - `POST /api/v1/auth/me/profile-update-challenge`
  - `PATCH /api/v1/auth/me/identity`
- Email/username updates require MFA verification before database updates.
- No database migration was needed.

Frontend:
- Settings is now a full dashboard page for Platform Admin and ISP Admin instead of a topbar popover.
- Settings includes theme switching, session details, email/username update with 2FA, password reset email request, shortcuts, and logout.
- Login forgot-password sends a reset email.
- `/reset-password?token=...` opens the reset page, reads the token once, removes it from the URL, and submits the reset token only to the reset endpoint.

## Mobile App + Admin State Persistence Checkpoint - 2026-05-20 10:32

Frontend/admin update:
- Fixed mobile browser/admin dashboard state loss when switching apps.
- Admin MFA challenge/setup step is persisted in sessionStorage so switching to the authenticator app and returning does not reset back to login.
- Platform Admin active sidebar section is persisted in localStorage.
- ISP Admin active sidebar section is persisted in localStorage.
- This fixes returning from App User Invitations, Settings, Users, etc. back to Overview after browser/app switching.

Mobile app update:
- Created real App User mobile app project at C:\PulseFi\pulsefi-mobile-app using Expo + React Native + TypeScript.
- Used Expo SDK 54 for Expo Go compatibility.
- Installed expo-secure-store and React Navigation dependencies.
- Added App User login flow using POST /api/v1/auth/login with account_type="app_user".
- Added SecureStore-backed mobile session persistence.
- Added API client using EXPO_PUBLIC_API_BASE_URL.
- Added Home screen connected to GET /api/v1/me/summary.
- Added AppUserSession and AppUserSummary TypeScript types.
- Fixed mobile API client syntax issue caused by a malformed fetch template string.
- Current mobile checkpoint target: login with real App User account and load /me/summary.

Current local mobile project:
- C:\PulseFi\pulsefi-mobile-app is the active mobile app folder.
- C:\PulseFi\pulsefi-mobile is the older locked SDK 55 attempt and should be cleaned later after reboot if no longer needed.

Next steps:
1. Confirm App User mobile login works against LAN backend.
2. Add mobile bottom tabs.
3. Add Usage, Devices, Alerts, Subscriptions, Predictions, and Recommendations screens.
4. Add alert mark-as-read.
5. Add recommendation-to-plan-change-request action if needed for demo.
6. Then proceed to deployment/demo readiness.

## Mobile App + Admin State Persistence Checkpoint - 2026-05-20 10:34

Frontend/admin update:
- Fixed mobile browser/admin dashboard state loss when switching apps.
- Admin MFA challenge/setup step is persisted in sessionStorage so switching to the authenticator app and returning does not reset back to login.
- Platform Admin active sidebar section is persisted in localStorage.
- ISP Admin active sidebar section is persisted in localStorage.

Mobile app update:
- Created real App User mobile app project at C:\PulseFi\pulsefi-mobile-app using Expo + React Native + TypeScript.
- Used Expo SDK 54 for Expo Go compatibility.
- Installed expo-secure-store and React Navigation dependencies.
- Added App User login flow using POST /api/v1/auth/login with account_type="app_user".
- Added SecureStore-backed mobile session persistence.
- Added API client using EXPO_PUBLIC_API_BASE_URL.
- Added Home screen connected to GET /api/v1/me/summary.
- Fixed mobile API client malformed fetch template string issue.
- Current mobile checkpoint target: login with real App User account and load /me/summary.

Current local mobile project:
- C:\PulseFi\pulsefi-mobile-app is the active mobile app folder.
- C:\PulseFi\pulsefi-mobile is the older locked SDK 55 attempt and can be cleaned later after reboot if no longer needed.

Next steps:
1. Confirm App User mobile login works against LAN backend.
2. Add mobile bottom tabs.
3. Add Usage, Devices, Alerts, Subscriptions, Predictions, and Recommendations screens.
4. Add alert mark-as-read.
5. Add recommendation-to-plan-change-request action if needed for demo.
6. Then proceed to deployment/demo readiness.



## Latest Step 29L Mobile / Directional Bandwidth Checkpoint

Step 29L is complete.

What changed:

- Backend `DeviceNetworkPolicy` now has `download_limit_mbps` and `upload_limit_mbps`.
- `bandwidth_limit_mbps` remains for backward compatibility.
- `MyDevicePolicyCreate` accepts directional limits for `bandwidth_limit` policies.
- Router action execution writes directional limits into `command_payload`.
- Simulator router adapter returns directional limits in `response_payload`.
- Admin web router management has a **Run full simulator** action.
- Mobile Devices screen has custom Download Mbps / Upload Mbps inputs.
- Backend tests passed after dev/test DB columns were added.
- Mobile custom bandwidth limits were completed and committed.

Important follow-up:

- Add capability-aware mobile UI for router actions.
- Add clearer display of router action result details if needed.
- Update diagrams later for directional bandwidth policy actions.
