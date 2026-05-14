# PulseFi Backend

PulseFi is a Smart Network Monitoring and Optimization System built for internet users, ISP administrators, and platform administrators.

The backend is a FastAPI + PostgreSQL service designed for a deployable Final Year Project MVP. It supports secure authentication, role-based access, ISP/platform management, and will later support usage monitoring, alerts, predictions, recommendations, router integration, and reports.

---

## Current Backend Status

Current phase: **Step 16 â€” ISP Admin management endpoints**.

Recently completed and tested:

- FastAPI backend foundation.
- PostgreSQL async SQLAlchemy setup.
- Core SQLAlchemy models.
- Auth models, schemas, services, and endpoints.
- Protected current-account route system.
- Platform Admin ISP management.
- Platform Admin ISP Admin invitation flow.
- Platform Admin ISP Admin account management.
- Platform Admin dashboard summary metrics.
- Platform Admin pending ISP Admin invitation management.

Step 15 is complete. The next backend work should start from Step 16.

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

## Step 16 Rule

ISP Admin endpoints must be scoped to the authenticated ISP Admin's own `isp_id`.

ISP Admins:

- Can manage only their own ISP's users, plans, subscriptions, routers, reports, and analytics.
- Cannot create ISPs.
- Cannot invite or manage ISP Admin accounts.
- Cannot access another ISP's users, plans, subscriptions, routers, reports, or analytics.

---

## Project Idea

PulseFi connects users, ISP admins, subscriptions, routers, devices, usage data, alerts, predictions, recommendations, and reports into one smart system.

A regular user should be able to use a mobile app to:

- View total internet usage.
- View their subscription or subscriptions.
- View connected devices.
- View per-device consumption when supported by the router.
- Receive high-usage alerts.
- Receive new-device-connected alerts.
- View future usage predictions.
- View plan recommendations.
- Request a subscription upgrade or downgrade.
- Apply bandwidth limits or device priority to selected devices when supported.

An ISP Admin should be able to use a web dashboard to:

- Manage app users.
- Invite users.
- Manage subscription plans.
- Assign user subscriptions.
- Manage router information.
- View usage records.
- View device records.
- View alerts and policy status.
- View recommendations and network analytics.
- Generate reports.
- View router action logs.
- Handle user subscription change requests.

A Platform Admin should be able to use a web dashboard to:

- Manage ISPs.
- Invite ISP Admins.
- Manage ISP Admin accounts.
- View platform-level summary metrics.

---

## User Types

### Platform Admin

The Platform Admin manages the platform itself.

Main responsibilities:

- Manage ISPs.
- Invite ISP Admins.
- Manage ISP Admin accounts.
- View platform-level summary data.

### ISP Admin

The ISP Admin represents one internet service provider.

Main responsibilities:

- Manage users under their ISP.
- Manage plans under their ISP.
- Assign subscriptions.
- Manage routers.
- View usage, devices, alerts, recommendations, reports, analytics, and router action logs for their ISP.

### App User

The App User is the regular internet customer using the mobile app.

Main responsibilities:

- Monitor their internet usage.
- View connected devices.
- Receive alerts.
- View predictions and recommendations.
- Request subscription changes.
- Apply device optimization actions when router capabilities allow it.

---

## Router Integration Concept

PulseFi should not pretend to support every router from day one.

The backend should use a router adapter architecture:

- Start with a simulator adapter for reliable demo/testing.
- Add one first supported router integration family or protocol if possible.
- Use router capabilities to show, hide, enable, or disable features.

Router feature tiers:

### Full Mode

Supports most features:

- Total usage.
- Connected devices.
- Per-device usage.
- New-device detection.
- Bandwidth limiting.
- Device prioritization.

### Partial Mode

Supports only some features exposed by the router.

### Basic Mode

Supports subscription-level usage, predictions, recommendations, and ISP-side analytics, but does not provide reliable device-level monitoring or device optimization.

---

## Authentication and Security

PulseFi uses secure invitation-based onboarding.

Authentication design:

- Platform Admin invites ISP Admins.
- ISP Admins invite App Users.
- Invited accounts accept an expiring setup link.
- Invited accounts set their own password.
- Invited accounts choose a username.
- Login accepts email or username plus `account_type`.
- Passwords are hashed using Argon2 through `pwdlib[argon2]`.
- JWT access tokens include account ID, account type, issued-at time, and expiration time.
- Password reset tokens are expiring and single-use.
- Old tokens are rejected after `password_changed_at`.
- Email verification is included.
- MFA supports authenticator app, email OTP, and backup recovery codes.
- Backup codes are single-use and stored hashed.
- SMS verification is deferred for now because it adds recurring production cost.

---

## Backend Technology

- FastAPI
- Python
- PostgreSQL
- Async SQLAlchemy
- asyncpg
- Pydantic / pydantic-settings
- JWT with PyJWT
- Argon2 password hashing through `pwdlib[argon2]`
- pyotp for authenticator-app MFA

---

## Backend Structure

Main structure:

- `app/main.py`
- `app/core/config.py`
- `app/core/security.py`
- `app/db/session.py`
- `app/db/base.py`
- `app/api/dependencies/`
- `app/api/v1/router.py`
- `app/api/v1/endpoints/`
- `app/models/`
- `app/schemas/`
- `app/services/`

Architecture style:

- Clean modular monolith.
- Keep endpoint files thin.
- Put business logic in services.
- Keep schemas split by feature area.
- Avoid huge mixed-responsibility files.

---

## Development Commands

Run the backend from the project root:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Root endpoint:

```text
/
```

Health endpoint:

```text
/api/v1/health
```

Basic app import test:

```powershell
.\venv\Scripts\python.exe -c "from app.main import app; print('App imported successfully')"
```

API router import test:

```powershell
.\venv\Scripts\python.exe -c "from app.api.v1.router import api_router; print('API router imported successfully')"
```

Current Step 16 preparation import test:

```powershell
.\venv\Scripts\python.exe -c "from app.api.dependencies import get_current_isp_admin; from app.core.config import settings; print('Step 16 foundation imported successfully.')"
```

---

## Deployment Goal

PulseFi should be deployable by presentation time.

The MVP should prioritize:

- Reliable backend.
- Secure authentication.
- Clear Platform Admin, ISP Admin, and App User flows.
- Working database.
- Demo-friendly router simulator.
- Usage data flow.
- Alerts.
- Predictions and recommendations.
- Reports.
- Frontend integration.

Avoid claiming universal router support before it exists. Use simulator support and capability-based feature availability for a realistic MVP.

---

## Backend Quality Progress — 2026-05-14

The backend quality foundation was improved before continuing Step 16.

Completed on 2026-05-14:

- Created and tested a limited PostgreSQL application role: `pulsefi_app`.
- Updated local `.env` to connect with `pulsefi_app` instead of the `postgres` superuser.
- Confirmed the backend connects successfully as `pulsefi_app`.
- Initialized Alembic.
- Configured Alembic to use the same async PostgreSQL URL from `app/core/config.py`.
- Configured Alembic to read SQLAlchemy metadata from `Base.metadata`.
- Created an empty baseline migration for the existing database schema.
- Stamped the current database at Alembic head: `c384b4d102bc`.
- Confirmed Alembic current revision: `c384b4d102bc (head)`.

Important database note:

- Existing PulseFi tables and data were not recreated, deleted, or changed.
- Alembic created/uses the normal `alembic_version` tracking table.
- `pulsefi_app` was temporarily granted `CREATE` on schema `public` so Alembic could create `alembic_version`.

Future permission hardening:

- Before production deployment, revisit database permissions.
- The preferred production setup is to separate responsibilities:
  - an application role for normal backend runtime access
  - a migration/admin role for Alembic schema changes
- After migrations are properly managed, avoid giving the normal runtime app role unnecessary schema-creation power.

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
