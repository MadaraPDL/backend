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
- Step 15C: Platform Admin manages ISP Admin accounts.

Likely scope:
- View one ISP Admin.
- Update ISP Admin basic info/status.
- Deactivate/reactivate ISP Admin.
- Keep route protection as Platform Admin only.
- Keep files split under platform_admin schemas/services/endpoints.

Possible endpoints:
- `GET /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`

## Pending Later Roadmap

After Step 15:
- Step 16: ISP Admin management endpoints.
- Step 17: User mobile app endpoints.
- Step 18: Router adapter/simulator layer.
- Step 19: Usage data ingestion.
- Step 20: Alerts system.
- Step 21: Prediction/recommendation logic.
- Step 22: Reports and analytics.
- Step 23: Frontend integration.
- Step 24: Deployment preparation.

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

## Latest Progress Update ï¿½ 2026-05-14

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

## Step 16 Progress ï¿½ 2026-05-14

### Step 16F ï¿½ ISP Admin Router Management Endpoints

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

## Step 16G ï¿½ ISP Admin Dashboard Summary

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

## Step 17 Progress ï¿½ 2026-05-14

### Step 17A ï¿½ App User Mobile Endpoint Foundation

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

## Step 17 Progress ï¿½ 2026-05-14

### Step 17B ï¿½ App User Subscription Endpoints

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

## Step 17 Progress ï¿½ 2026-05-14

### Step 17C ï¿½ App User Router and Device View Endpoints

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

- Step 17D ï¿½ App User usage endpoints.
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

## Step 17 Progress ï¿½ 2026-05-15

### Step 17E ï¿½ App User Alert Endpoints

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

- Step 17F ï¿½ App User predictions and recommendations endpoints, or plan change request endpoints.

---

## Step 17 Progress ï¿½ 2026-05-15

### Step 17F ï¿½ App User Prediction and Recommendation Endpoints

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

- Step 17G ï¿½ App User subscription plan change request endpoints.

---

## Step 17 Progress ï¿½ 2026-05-15

### Step 17G ï¿½ App User Plan Change Request Endpoints

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

- Step 17H ï¿½ App User device policy endpoints.

---

## Step 17 Progress ï¿½ 2026-05-15

### Step 17H ï¿½ App User Device Policy Endpoints

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

- Step 18 ï¿½ Router adapter and simulator layer.


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


## MFA Setup Flow Fix ? 2026-05-15

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


## MFA Setup Token Hardening and Cleanup ? 2026-05-15

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


## Server-Side MFA Setup State ? 2026-05-15

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


## MFA Setup Secret Redaction ? 2026-05-15

Completed and tested:
- Pending MFA setup secrets are redacted from `mfa_setup_challenges` after successful setup.
- Revoked MFA setup challenges now have their pending authenticator secret cleared.
- Expired, used, and revoked setup challenge secrets are cleaned when a new setup challenge is created.
- This reduces how long pending authenticator secrets remain in the database.

Impact:
- Database schema: no change.
- Existing data: inactive setup challenge secrets may be cleared during future setup challenge creation.
- Security: improves secret retention behavior, but full encryption at rest is still pending before production.


## MFA Setup Challenge Cleanup Service ? 2026-05-15

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


## MFA Secret Encryption at Rest ? 2026-05-15

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


## Auth Rate Limiting MVP ? 2026-05-15

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


## Final Pre-Step-18 Hardening Pass ? 2026-05-15

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

## Step 18 Progress ï¿½ 2026-05-16

### Step 18A/18B ï¿½ Router Adapter Interface and Simulator Adapter

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

- Step 18C ï¿½ Add service layer that uses the router adapter registry to apply pending device network policies and create router action logs.

---

## Step 18 Progress ï¿½ 2026-05-16

### Step 18C ï¿½ Router Policy Execution Service

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

- Step 18D ï¿½ Add safe API endpoint for executing a pending device policy through the router execution service.

---

## Step 18 Progress — 2026-05-16

### Step 18D — App User Device Policy Execution Endpoint

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

- Step 18E — Add ISP Admin/router action log visibility or add tests for policy execution endpoint.

---

## Step 18 Progress — 2026-05-16

### Step 18E — ISP Admin Router Action Log Visibility

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

- Step 18F — Add focused tests for router action execution and ISP Admin router action log isolation, or add router capability visibility endpoint.

---

## Step 18 Progress — 2026-05-16

### Step 18F — Router Policy Execution and Router Action Log Integration Tests

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

- Step 18G — Add router capability visibility endpoint or Step 18 cleanup/docs before moving to Step 19 usage ingestion.

---

## Step 18 Progress — 2026-05-16

### Step 18G — App User Router Capability Visibility Endpoint

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

- Step 18 cleanup/docs, then Step 19 — usage data ingestion and simulator usage generation.

---

## Step 19 Progress — 2026-05-16

### Step 19A/19B — Simulator Usage Ingestion Service and ISP Admin Trigger Endpoint

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

- Step 19C — connected device ingestion/update from simulator data, including device connection logs for new/seen devices.

---

## Step 19 Progress â€” 2026-05-16

### Step 19C â€” Simulator Connected Device Ingestion

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

- Step 19D â€” combine simulator device ingestion and usage ingestion into a single demo ingestion flow, or add ISP Admin visibility for device connection logs.

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
