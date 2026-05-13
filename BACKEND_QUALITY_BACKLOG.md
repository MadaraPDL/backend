# PulseFi Backend Quality Improvement Backlog

This file records the improvement items that should make PulseFi more professional, safer, easier to maintain, and more deployable.

These items are not all required before every small feature, but they should be completed before the project becomes too large or before final deployment/presentation.

---

## Current Context

Current backend phase: **Step 16 — ISP Admin management endpoints**.

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
