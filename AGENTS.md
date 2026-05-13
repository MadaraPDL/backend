# Latest PulseFi Backend Status

Read this section first. It overrides older "current phase" sections below if they conflict.

## Current Backend Position

Current phase: Step 15E is next.

Recently completed and tested:
- Step 14: Protected current-account route system.
- Step 15A: Platform Admin ISP management endpoints.
- Step 15B: Platform Admin ISP Admin invitation endpoints.
- Step 15C: Platform Admin ISP Admin account management endpoints.
- Step 15D: Platform Admin dashboard summary endpoint.

## Completed Platform Admin Endpoints

Protected by `platform_admin` role only:

- `POST /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps/{isp_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}`

- `POST /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`

- `GET /api/v1/platform-admin/summary`

## Current Next Step

Step 15E: Platform Admin pending ISP Admin invitation management.

Planned endpoints:
- `GET /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admin-invitations/{invitation_id}/revoke`

## Important Role Rule

ISP Admins must not be allowed to create ISPs, invite other ISP Admins, or manage other ISPs.

Platform Admin:
- manages ISPs
- invites/manages ISP Admins
- views platform summary metrics

ISP Admin:
- manages only their own ISP's users, plans, subscriptions, routers, reports, and analytics
- can invite app users under their own ISP later
- cannot invite ISP Admins

---
# AGENTS.md — PulseFi Backend Instructions

## Project Name

PulseFi

## Main Rule for Codex

Before editing anything, read this file, `README.md`, and `ROADMAP.md`.

Do not make random architecture decisions without checking the existing project structure.

This backend is being built step by step by the student/developer, so explain changes clearly and keep the project understandable.

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
- Frontend later:
  - React Native mobile app for users
  - Web dashboard for ISP Admins
  - Web dashboard for Platform Admins

## Local Project Path

The backend usually lives here:

C:\PulseFi\backend

## GitHub Repository

The backend repository is:

https://github.com/MadaraPDL/backend

## Architecture Style

This backend is a clean modular monolith.

Keep the project modular.

Do not create huge files that mix unrelated responsibilities.

Important structure:

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

## Important Coding Rule

Avoid creating one huge file with many unrelated features.

Prefer focused modules like:

- `account_service.py`
- `auth_service.py`
- `mfa_service.py`
- `invitation_service.py`
- `password_reset_service.py`
- `email_verification_service.py`
- `router_service.py`
- `usage_service.py`
- `alert_service.py`
- `prediction_service.py`
- `recommendation_service.py`
- `report_service.py`

Do not put login, invitations, password reset, email verification, MFA, users, plans, routers, reports, and analytics all in one service file.

## Current Project Phase

The project is currently around:

Step 13F — Testing authentication endpoints through Swagger/Postman.

Step 13E is structurally complete.

Auth endpoints currently exist under:

`app/api/v1/endpoints/auth/`

Current auth endpoints include:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/auth/invitations/accept`
- `POST /api/v1/auth/password/forgot`
- `POST /api/v1/auth/password/reset`
- `POST /api/v1/auth/email/verify`

The next backend work should continue from auth testing, then move to protected routes and current-user dependencies.

## Current Auth Testing Plan

Continue with Step 13F.

Test these in order:

1. Test wrong login returns 401.
2. Create one temporary test invitation row if `account_invitations` is empty.
3. Accept invitation through Swagger.
4. Confirm the test account is created.
5. Confirm the invitation is marked accepted.
6. Login with the created account.
7. Test MFA verification if required.
8. Test forgot password.
9. Confirm generic forgot-password response.
10. Confirm dev reset token only while `DEBUG=True`.
11. Reset password with reset token.
12. Login with the new password.
13. Confirm old password fails.
14. Test email verification if a token exists.
15. Add or adjust helper/service flow if email verification token is not auto-created.

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
- Login request should include `account_type`.
- Login should accept either email or username as the identifier.
- Email is still required for invitations, verification, password reset, notifications, and recovery.
- Username is optional but useful for easier login.
- Username should be unique case-insensitively.
- Username should have no spaces.

Security design:

- Passwords must be hashed with Argon2.
- Never store plain passwords.
- JWT tokens must include:
  - account ID as subject
  - `account_type`
  - issued-at time
  - expiry time
- Forgot-password responses must be generic to avoid account enumeration.
- Password reset tokens must be expiring and single-use.
- Old sessions should be considered invalid after password reset using `password_changed_at`.

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

## Database Notes

The database already exists in PostgreSQL.

Do not guess schema details when exact columns are needed.

Inspect existing models or the database before changing models.

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

- Total usage
- Connected devices
- Per-device usage
- New-device alerts
- Bandwidth limiting
- Device prioritization

Partial mode:

- Only the features exposed by the router are available.

Basic mode:

- Subscription-level usage, predictions, and recommendations from ISP-side data.
- No reliable per-device monitoring.
- No device optimization.

Device-level features depend on router capability.

## Subscription Change Design

Regular users can request plan upgrades or downgrades for their own subscriptions.

The actual subscription change is handled by the ISP Admin.

Users can directly apply device optimization actions such as bandwidth limit or device priority without ISP Admin approval.

## Commands

Run from the backend root:

`.\venv\Scripts\python.exe -c "from app.main import app; print('App imported successfully')"`

`.\venv\Scripts\python.exe -c "from app.api.v1.router import api_router; print('API router imported successfully')"`

`.\venv\Scripts\python.exe -c "from app.schemas.auth import *; print('Auth schemas imported successfully')"`

Run the server:

`.\venv\Scripts\python.exe -m uvicorn app.main:app --reload`

Swagger URL:

`http://127.0.0.1:8000/docs`

Health endpoint:

`/api/v1/health`

## Software Engineering Diagram Update Rules

The developer wants reminders when backend/design changes require SE diagram updates.

Recommend SE updates when changes affect:

- Actors or roles
- Use cases
- Major user/admin flows
- DFD processes or data flows
- ERD entities, relationships, or attributes
- Sequence diagrams
- Activity diagrams
- Security/onboarding architecture
- Router/deployment structure
- Major system behavior

Do not interrupt for tiny implementation details.

Pending SE updates to batch later:

- Invitation-based onboarding
- Email verification
- Forgot password
- Username/email login
- MFA/2FA
- Backup recovery codes
- Router adapter/capability model
- Subscription change request flow

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
