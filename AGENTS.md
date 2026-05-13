# AGENTS.md — PulseFi Backend Instructions

## Project Name

PulseFi

## Main Rule for Codex / AI Coding Assistants

Before editing anything, read this file, `README.md`, and `ROADMAP.md`.

Do not make random architecture decisions without checking the existing project structure.

This backend is being built step by step by the student/developer, so changes should stay understandable, modular, and easy to explain.

---

## Current Backend Position

Current phase: **Step 16 — ISP Admin management endpoints**.

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
