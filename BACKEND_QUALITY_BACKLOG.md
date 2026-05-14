# PulseFi Backend Quality Improvement Backlog

This file records the improvement items that should make PulseFi more professional, safer, easier to maintain, and more deployable.

These items are not all required before every small feature, but they should be completed before the project becomes too large or before final deployment/presentation.

---

## Current Context

Current backend phase: **Step 16 â€” ISP Admin management endpoints**.

Step 15 Platform Admin endpoints are complete.

Step 16 must be built using the ISP Admin guard:

```python
get_current_isp_admin
```

Every ISP Admin query must be scoped by the authenticated admin's ISP:

```python
current_admin.isp_id
```

This prevents one ISP Admin from accessing another ISP's data.

---

## Recommended Improvement Order

### 1. Sync local repository with GitHub

Before continuing new work, make sure the local folder `C:\PulseFi\backend` is synced with GitHub.

Use:

```powershell
git status
```

If the working tree is clean:

```powershell
git pull
```

If the working tree has local changes, review them before pulling.

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: no change.

---

### 2. Create a limited PostgreSQL app role

Stop using the powerful `postgres` superuser for normal backend connections.

Create a limited role such as:

```text
pulsefi_app
```

The backend should connect using this limited role in `.env`.

Why:

- Better security.
- Safer deployment.
- Limits damage if backend credentials are exposed.

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: no change.

---

### 3. Add Alembic migrations

Add Alembic to track database schema changes properly.

Important first goal:

- Create a safe baseline that matches the current real PostgreSQL schema.

Why:

- Makes the database reproducible.
- Makes future schema changes trackable.
- Helps deployment and teamwork.

Impact:

- Database schema: no immediate change if baselined carefully.
- Existing data: no change if done correctly.
- SE diagrams: no change.

---

### 4. Add automated backend tests

Use:

- `pytest`
- `httpx`

Initial test areas:

- Auth login.
- Wrong login.
- Password reset.
- Invitation accept/revoke behavior.
- Platform Admin endpoints.
- Step 16 ISP Admin isolation.

Why:

- Prevents future changes from breaking old features.
- Makes the repo more serious.
- Helps catch security mistakes early.

Impact:

- Database schema: no change.
- Existing data: should avoid changing real development data; prefer a test database or isolated test records.
- SE diagrams: no change.

---

### 5. Add GitHub Actions CI

Add CI so every push can run backend checks automatically.

Initial CI checks:

- Install dependencies.
- Run import checks.
- Run Python compile check.
- Run tests after the test suite exists.

Why:

- GitHub catches broken pushes automatically.
- Improves professionalism.
- Makes the project easier to trust.

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: no change.

---

### 6. Build Step 16 with strict ISP isolation

All Step 16 endpoints must use:

```python
get_current_isp_admin
```

All Step 16 database queries must filter by:

```python
current_admin.isp_id
```

Expected Step 16 areas:

- Invite App Users.
- List App Users under the ISP.
- Manage App Users.
- Create/list/update subscription plans.
- Assign user subscriptions.
- Add/list/update routers.
- ISP-scoped dashboard/list endpoints.

Why:

- Prevents cross-ISP data leaks.
- Keeps role separation correct.
- Matches the project design.

Impact:

- Database schema: probably no change if the current schema is enough.
- Existing data: endpoints may create/update app users, plans, subscriptions, and routers.
- SE diagrams: yes, this affects ISP Admin use cases and activity flows.

---

### 7. Add structured logging

Replace random debugging with proper logging for important backend events.

Useful log events:

- Login success/failure.
- Permission denied.
- Invitation created/accepted/revoked.
- Password reset requested/completed.
- Router policy success/failure.
- Data ingestion success/failure.

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: no change.

---

### 8. Standardize API error responses

Make API errors consistent so frontend apps can handle them easily.

Example goal:

```json
{
  "error": "forbidden",
  "message": "You do not have permission to access this resource."
}
```

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: no change.

---

### 9. Add seed/demo data

Create safe scripts for fake demo data.

Demo data may include:

- Platform Admin.
- ISPs.
- ISP Admins.
- App Users.
- Plans.
- Subscriptions.
- Routers.
- Devices.
- Usage records.
- Alerts.
- Predictions.
- Recommendations.

Why:

- Makes the final presentation easier.
- Makes the app look realistic during testing.

Impact:

- Database schema: no change.
- Existing data: yes, inserts demo rows if run on the current database.
- SE diagrams: no change.

---

### 10. Add production deployment documentation

Create deployment docs covering:

- Environment variables.
- Database setup.
- Limited database role.
- Alembic migration commands.
- Email service setup.
- CORS setup.
- Backend hosting.
- Logging.
- Security checklist.
- Demo data setup.

Impact:

- Database schema: no change.
- Existing data: no change.
- SE diagrams: no change.

---

## Priority Summary

Best order:

1. Sync local repo.
2. Create limited PostgreSQL role.
3. Add Alembic baseline.
4. Add tests.
5. Add CI.
6. Build Step 16 endpoints with strict ISP isolation.
7. Add logging and clean errors.
8. Add seed/demo data.
9. Add deployment docs.

The main goal is to keep PulseFi deployable, secure, modular, and easy to explain for the Final Year Project demo.

---

## Completed Quality Work

### 2026-05-14 — Limited DB Role

Completed:

- Created and tested limited PostgreSQL app role: `pulsefi_app`.
- Updated local backend `.env` to use `pulsefi_app`.
- Confirmed database connection works as `pulsefi_app`.

Important future reminder:

- `pulsefi_app` should not keep unnecessary powerful permissions in production.
- Revisit permissions before deployment.
- Preferred future setup:
  - app/runtime role for FastAPI
  - separate migration role for Alembic

### 2026-05-14 — Alembic Baseline

Completed:

- Initialized Alembic.
- Configured Alembic for async SQLAlchemy.
- Connected Alembic to existing app settings and models.
- Created empty baseline migration: `c384b4d102bc`.
- Stamped existing database to Alembic head.
- Confirmed current revision: `c384b4d102bc (head)`.

Impact:

- Existing PulseFi tables were not recreated.
- Existing data was not changed.
- Alembic tracking table `alembic_version` is expected and normal.

Next quality work:

1. Add automated tests with `pytest` and `httpx`.
2. Add GitHub Actions CI.
3. Add structured logging.
4. Standardize API error responses.
5. Add safe seed/demo data.
6. Add production deployment docs.

---

## Completed Quality Work Log

### 2026-05-14 — Limited PostgreSQL App Role

Completed:

- Created and tested limited PostgreSQL app role: `pulsefi_app`.
- Updated local backend `.env` to use `pulsefi_app` instead of the `postgres` superuser.
- Confirmed backend database connection works as `pulsefi_app`.

Important future reminder:

- `pulsefi_app` should not keep unnecessary powerful permissions in production.
- Revisit permissions before deployment.
- Preferred future setup:
  - app/runtime role for FastAPI
  - separate migration/admin role for Alembic

### 2026-05-14 — Alembic Baseline

Completed:

- Initialized Alembic.
- Configured Alembic for async SQLAlchemy.
- Connected Alembic to existing app settings and models.
- Created empty baseline migration: `c384b4d102bc`.
- Stamped existing database to Alembic head.
- Confirmed current revision: `c384b4d102bc (head)`.

Impact:

- Existing PulseFi tables were not recreated.
- Existing data was not changed.
- Alembic tracking table `alembic_version` is expected and normal.

Next quality work:

1. Add automated tests with `pytest` and `httpx`.
2. Add GitHub Actions CI.
3. Add structured logging.
4. Standardize API error responses.
5. Add safe seed/demo data.
6. Add production deployment docs.

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
