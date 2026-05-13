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
