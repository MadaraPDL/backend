<!-- STEP_50P_REMAINING_STATUS_AND_MOBILE_FIXES_START -->
## Step 50P Remaining Status + Immediate Mobile Behavior Fixes (2026-05-28)

Status: Complete for current scope.

Completed Step 50P mobile behavior fixes:

1. Home usage source now follows the Usage tab source selection.
   - Added shared mobile app state for the usage display source:
     - `official`
     - `estimated`
   - Usage now uses the shared source state instead of local-only display state.
   - Home now loads both official and estimated usage summaries for the selected router.
   - Home renders the selected shared source instead of forcing official-first behavior.
   - Home labels the selected total clearly:
     - `Official service total`
     - `Estimated device total`

2. Old upgrade/downgrade recommendations are now actionable.
   - Recommendations with `recommendation_plan_id` still show direct actions:
     - `Request this upgrade`
     - `Request this downgrade`
   - Recommendations without `recommendation_plan_id` now still become actionable when type, text, or reason clearly mentions upgrade/downgrade.
   - Those older recommendations show `Open Service requests` so the App User can manually choose a plan.
   - The existing `createPlanChangeRequestFromRecommendation` flow remains the direct request path when a target plan exists.

Verification:
- Mobile TypeScript check passed with:
  - `npx.cmd tsc --noEmit`
- Mobile whitespace check passed with:
  - `git diff --check`

Remaining after Step 50P:
- Assistant quality pass is still next.
- ML/data pipeline is still not real ML yet.
- Push notifications are still not implemented.
- Full final deployed mobile smoke test remains intentionally deferred.
- Final report/presentation alignment is still pending.

Do not mark the Assistant quality pass complete yet.
Keep final full live smoke deferred.
Focused Expo checks are allowed after this mobile fix.
<!-- STEP_50P_REMAINING_STATUS_AND_MOBILE_FIXES_END -->


<!-- PULSEFI_ASSISTANT_REQUIREMENTS_START -->
## PulseFi Assistant Requirements / Planned Quality Pass (2026-05-28)

Status: Planned next quality pass, not complete yet.

The current PulseFi Assistant direction must be improved before final demo because the user does not want it to feel like a simple rules bot.

Required product direction:

- The assistant should feel like a contextual PulseFi helper, not a static FAQ/rules bot.
- It should use the App User's current PulseFi context where available:
  - selected router
  - selected service line/subscription
  - current monthly/daily usage
  - official vs estimated usage totals
  - connected devices
  - alerts
  - predictions
  - recommendations
  - plan/package details
  - recent service requests
- It should answer in plain language and explain why it is saying something.
- It should avoid pretending to know data that was not loaded.
- It should clearly say when data is missing, outdated, or unavailable.
- It should never expose secrets, debug tokens, internal IDs unnecessarily, or admin-only details.

Required mobile placement:

- Assistant entry should be visible from Home.
- Assistant/help actions should also be available near Recommendations/Insights where the user naturally asks:
  - Why am I getting this recommendation?
  - Should I upgrade or downgrade?
  - What does this prediction mean?
  - Why is my usage high?
- Recommendations should remain actionable:
  - If upgrade/downgrade recommendation has a target plan, user can request it directly.
  - If no target plan is attached, user can open Service requests and choose manually.

Desired MVP behavior:

- Start with a safer contextual assistant MVP using backend/app data summaries.
- It may use structured local logic first, but the UX should not look like a rigid rules bot.
- Answers should be generated from a compact context object and friendly templates.
- Later, it can evolve into a real LLM-backed assistant if deployment/security allows.

Suggested assistant intents for MVP:

1. Usage explanation:
   - Explain current daily/monthly usage.
   - Explain official vs estimated totals.
   - Explain why the graph shows a selected source.

2. Recommendation explanation:
   - Explain upgrade/downgrade recommendation.
   - Explain whether user should request the recommended plan.
   - Route user to Service requests when needed.

3. Prediction explanation:
   - Explain predicted usage, confidence, and risk level.
   - Explain what the user can do next.

4. Device explanation:
   - Explain which devices appear high usage.
   - Explain trusted/untrusted device meaning.
   - Explain limits/priority only if router supports it.

5. Alerts explanation:
   - Explain alert severity and next steps.
   - Keep language calm and practical.

Implementation notes:

- Keep assistant responses scoped to the current App User.
- Keep selected router/service line behavior consistent with the rest of mobile.
- Do not run final full live smoke test yet.
- Focused Expo checks are allowed after implementation.
<!-- PULSEFI_ASSISTANT_REQUIREMENTS_END -->


<!-- STEP_50O_MOBILE_POLISH_SYNC_START -->
## Step 50O Mobile UX Pagination / Service Request Polish Sync (2026-05-28)

Status: Step 50O is complete.

Completed mobile polish:

- Shared mobile pagination utilities/components were added:
  - `src/components/MobilePager.tsx`
  - `src/utils/mobilePagination.ts`

- Mobile Service Requests polish is complete:
  - More menu now uses `Service requests` instead of `Request a plan change`.
  - Change Plan, Suspend Subscription, and Suspend Account are shown as top tabs.
  - Target plans paginate when there are more than five.
  - Recent service requests paginate.

- Mobile Insights recommendation actions are improved:
  - Upgrade/downgrade recommendations with a target plan can create a request directly.
  - Upgrade/downgrade recommendations without a target plan route users to Service requests.
  - Predictions and Recommendations remain split into tab-style pages.

- Mobile list pagination is complete for current scope:
  - Alerts paginate.
  - Routers paginate.
  - Subscriptions / My package paginate.
  - Devices paginate.
  - Filters/search reset the relevant list back to page 1.

- Mobile Usage cleanup is complete:
  - Monthly/Daily usage remains the main usage style.
  - Official and Estimated usage remain separately visible.
  - User can choose what the main usage graph displays.
  - Monthly Daily Breakdown card was removed to keep Usage less cramped.

Important testing/deployment notes:

- Mobile is tested through Expo / Expo Go.
- Admin Web is deployed on Vercel.
- Backend is deployed on Render.
- Full final live smoke testing is still intentionally deferred.
- Focused live/mobile checks are allowed after each pushed feature/polish batch.
- Keep production `DEBUG=False`.
- Do not expose debug tokens in production.
- Continue protecting secrets and never print or commit environment values.
- Keep ISP Admin backend queries scoped by `current_admin.isp_id`.
- Do not store router passwords until encrypted credential storage exists.

Next recommended work:

1. Focused Expo check for Step 50O mobile polish.
2. PulseFi Assistant quality pass, if still needed.
3. Final report/demo alignment.
4. ML/data-pipeline explanation for presentation.
5. Full live smoke only after remaining project steps are complete.
<!-- STEP_50O_MOBILE_POLISH_SYNC_END -->


<!-- STEP_50M_ADMIN_WEB_POLISH_SYNC_START -->
## Step 50M Admin Web Polish / Pagination Sync (2026-05-28)

Status: Step 50M is complete.

Completed admin web/mobile UX cleanup since Step 50E:

- Step 50H mobile Usage cleanup is complete:
  - Home no longer fails completely when usage summary fails.
  - Mobile Usage has a cleaner Monthly/Daily layout.
  - Refresh labels were simplified.
  - Official and Estimated totals remain visible separately.
  - App User can choose which source the main usage graph shows.

- Step 50I mobile Insights cleanup is complete:
  - Predictions and Recommendations are split into tabs.
  - Prediction/recommendation lists use page controls instead of long scrolling.
  - Older user-facing insights are hidden from the mobile UI while remaining in backend/admin data.

- Step 50J ISP Admin Network Activity pagination is complete:
  - Daily Usage by User, Recent Usage Records, Device Connection Logs, and Router Action Logs use page controls.

- Step 50K ISP Admin Intelligence pagination is complete:
  - Recommendation History, Recent Reports, and run-detail items use page controls.

- Step 50L ISP Admin Monitoring pagination is complete:
  - Selected-user alerts use page controls.

- Step 50M shared admin pagination/polish is complete:
  - Shared admin pagination component/utilities were added.
  - App Users, Subscription Plans, Routers, App User Invitations, ISP Admin Invitations, Operations reports, and Operations service requests use page controls.
  - Pagination styling now lives in the real admin stylesheet: `src/styles/pulsefi-admin.css`.

Important deployment/testing notes:

- Admin Web is deployed on Vercel.
- Backend is deployed on Render.
- Mobile is tested through Expo / Expo Go.
- Full final live smoke testing is still intentionally deferred.
- Focused live checks are allowed after each pushed feature/polish batch.
- Keep production `DEBUG=False`; do not expose debug tokens in production.
- Continue protecting secrets and never print or commit environment values.
- Keep ISP Admin backend queries scoped by `current_admin.isp_id`.
- Do not store router passwords until encrypted credential storage exists.

Next recommended work:

1. Update/finalize mobile UX around Assistant placement and wording if still needed.
2. Prepare final report/demo alignment.
3. Prepare ML/data-pipeline explanation for presentation.
4. Run full live smoke only after remaining project steps are complete.
<!-- STEP_50M_ADMIN_WEB_POLISH_SYNC_END -->


- Step 50J is complete: mobile Usage was simplified, mobile Insights now uses Predictions/Recommendations tabs with page controls, and ISP Admin Network Activity tables now use page controls instead of long scrolling; final full live smoke remains deferred.
- Step 50G PulseFi Assistant mobile MVP is complete and checked: More now includes a rules-based PulseFi Assistant that answers quick usage, plan-limit, alert, device-total, and next-action questions from existing mobile API data; no external AI call, backend schema change, or API behavior change was added.
- Step 50F mobile UX polish is complete and checked: mobile Home/Usage now include retry refresh actions and clearer selected-router/demo usage guidance; no backend schema or API behavior changed; final full live smoke remains deferred.
- Step 46K alert volume controls are complete and tested: repeated simulator runs no longer spam duplicate untrusted-device `policy_failed` alerts for the same user/subscription/device when an unread or recent alert already exists.
- Step 46J device trust enforcement is complete and tested: simulator usage records are created only for trusted connected devices, untrusted connected devices are blocked from simulator usage, and each blocked untrusted device can create a `policy_failed` alert.
- Step 47C admin password reset resend polish is complete: forgot-password uses reset links and the UI supports sending another reset email after success.
- Step 48C reset success UX is complete and tested: the shared web reset-password page no longer redirects to admin login after success and instead shows a neutral prompt telling the user to return to PulseFi and log in with the new credentials.
- Step 48B mobile MFA resend UX is complete and tested: login email MFA, Profile email-MFA enable, email-based MFA disable verification, and backup-code email verification all support resending email codes and replacing the active challenge token.
- Step 48B mobile password reset request flow is complete and tested: App User mobile login now includes Forgot Password, sends password reset email links through the deployed backend, supports sending another reset email, and keeps reset-token handling out of the mobile UI.
- Step 47B admin Settings verification resend is complete: MFA settings, backup-code regeneration, and account identity verification support sending/resending email verification codes.
- Step 47A admin login email MFA resend is complete: admin web shows send/resend code by email during MFA login and replaces the active challenge token after each resend.
<!-- PULSEFI_SYNC_START -->
## Current Synchronized PulseFi Checkpoint - 2026-05-24

Current phase: **Step 50O complete - mobile UX pagination/service-request polish is complete; Step 50P immediate mobile behavior fixes are planned next; final full live smoke test remains deferred until all remaining project steps are finished.**

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
- Step 43D final full smoke test remains intentionally postponed until deployment/email/mobile are ready.
- Step 44F added protected Platform Admin team invitation backend routes so existing Platform Admins can invite/list/revoke Platform Admin invitations and list Platform Admin accounts.
- Step 45 added Settings toggle navigation polish in both admin dashboards, controlled full-simulator scenarios, scheduled intelligence alert generation, deterministic Explain-this response text, and tests for alert/recommendation coverage.
- Step 46I ISP Admin selected-user Monitoring alerts is complete and live-tested: Monitoring now requires selecting an App User before alert details are shown, only high-usage and plan-limit alerts are shown (`high_usage` and `plan_exceed_risk`), Users no longer owns this alert workflow, the alert list is scroll-contained, ISP Admin login defaults to Overview, and admin session restore no longer clears valid tokens on temporary backend/network failures.
- Step 46J device trust enforcement is complete and tested: simulator usage records are created only for trusted connected devices, untrusted connected devices are blocked from simulator usage, and each blocked untrusted device creates a `policy_failed` alert.
- Step 50D App User mobile Daily Usage is complete and verified: backend exposes daily usage for App Users, Home and Usage totals now use the same selected-router summary source, Daily Usage is visible on mobile, Latest Records starts at 5 rows with Show 5 more, and device download/upload breakdown remains available.
- Step 50E demo usage clarity is complete: ISP Admin Daily Usage by User now shows usage kind as Official/Service total vs Estimated/Device estimate, includes All/Official/Estimated filters, and future simulator usage creates an official service total row plus estimated per-device rows for cleaner presentation data.
- Step 50F mobile UX polish is complete: mobile Home and Usage now have explicit retry refresh actions and clearer selected-router/demo usage guidance; no backend API/schema changes were made.
- Step 50G PulseFi Assistant mobile MVP is complete: More now includes a rules-based assistant that uses existing mobile data for quick usage, package-limit, alert, Official-vs-Estimated, and next-action explanations; no external AI/backend assistant service was added.

Deployment status:
- Railway deployment was abandoned.
- Current deployment stack is:
  - Neon PostgreSQL database.
  - Render backend web service.
  - Vercel admin web.
  - Expo mobile through Expo Go/EAS later.
- Neon async database URL handling was fixed for asyncpg:
  - `postgresql://` is converted to `postgresql+asyncpg://`.
  - `sslmode=require` is converted to `ssl=require`.
  - `channel_binding=require` is removed.
- `app/db/session.py` and `alembic/env.py` use `settings.async_database_url()`.
- Alembic migration against Neon reached latest head.
- First deployed Platform Admin was created in Neon.
- Render backend deployed successfully.
- Vercel admin web deployed successfully.
- Vercel admin web uses `VITE_API_BASE_URL=https://<render-backend>/api/v1`.
- Admin login and authenticator MFA worked from a phone outside the local network.
- Render CORS was fixed for `https://pulsefi-admin-web.vercel.app`.
- Browser CORS preflight checks returned `Access-Control-Allow-Origin: https://pulsefi-admin-web.vercel.app`.

Email delivery status:
- Gmail SMTP was attempted on Render with port 587/TLS and 465/SSL.
- Gmail SMTP failed from Render with `OSError: [Errno 101] Network is unreachable`.
- The failure happens before Gmail authentication, so the Gmail app password is not the root issue.
- Backend email error handling was patched so SMTP connection failures return clean email-delivery errors instead of raw 500 crashes.
- Invitation requests now reach the backend and return clean `503 Service Unavailable` when email delivery fails.
- HTTP email delivery is now handled through Brevo:
  - `EMAIL_DELIVERY_PROVIDER=brevo`
  - `BREVO_API_KEY`
  - `BREVO_API_URL`
  - `SMTP_FROM_EMAIL` and `SMTP_FROM_NAME` remain the sender identity fields for compatibility.
- Brevo email delivery is working for deployed invitation and verification flows.
- For Brevo, keep `SMTP_FROM_EMAIL` aligned with the verified sender/domain configured in Brevo.

Current deployment env direction:
- `DEBUG=False` in production/live testing.
- `ENABLE_INTELLIGENCE_SCHEDULER=False` during first deployment.
- Target email env for HTTP provider:
  - `EMAIL_DELIVERY_ENABLED=True`
  - `EMAIL_DELIVERY_PROVIDER=brevo`
  - `BREVO_API_URL`
  - `BREVO_API_KEY=<Render secret only>`
  - `SMTP_FROM_EMAIL=<verified Brevo sender email>` for quick testing
  - `SMTP_FROM_NAME=PulseFi`
  - `FRONTEND_ADMIN_URL=https://pulsefi-admin-web.vercel.app`
  - `BACKEND_CORS_ORIGINS=["https://pulsefi-admin-web.vercel.app"]`
- Never paste or commit Brevo API keys, SMTP passwords, database URLs, JWT secrets, Neon credentials, Render secrets, or Vercel secrets.

Current intelligence status:
- Automatic intelligence can run from the env-gated backend scheduler or the manual ISP Admin demo trigger.
- Scheduler controls are `ENABLE_INTELLIGENCE_SCHEDULER` and `INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES`.
- Each run is ISP-scoped and reuses existing daily predictions/recommendations while unread/recent alert checks prevent duplicate alert spam.
- Current prediction/recommendation intelligence is rules-based/heuristic MVP (`rule_based_v1` and `rule_based_recommendation_v1`), not a completed trained ML model. No training/inference pipeline is integrated yet.
- Full simulator scenarios now support `normal_usage`, `high_usage`, `near_plan_limit`, `exceeded_plan`, `new_device`, `policy_failure`, and `heavy_device_usage`.
- Alert/recommendation API responses include deterministic `explanation` text for a simple Explain-this MVP without external AI calls.

Active rules:
- Never commit `.env`, database URLs, JWT secrets, SMTP passwords, Brevo API keys, Neon passwords, Render secrets, or Vercel secrets.
- ISP Admin endpoints must use `get_current_isp_admin`.
- Every ISP Admin query must be scoped by `current_admin.isp_id`.
- App User `/me` endpoints must use `get_current_app_user`.
- Current-account `/auth/me/...` endpoints must only affect the signed-in account.
- MFA settings changes must require verification before sensitive enable/disable actions.
- Do not expose local DEBUG tokens/codes in real admin web or mobile UI.
- Do not store raw router passwords, ISP API keys, or RADIUS credentials until encrypted credential storage exists.

Next recommended phase:
- Continue after Step 50E with the next remaining feature work; keep the full live smoke test deferred until all remaining steps are finished.
- Keep ISP Admin daily usage queries scoped by `current_admin.isp_id`.
- Step 50E demo usage clarity is complete; next work should not run final live smoke yet.
- Do not implement full push notifications until deployed mobile login and device-token storage are smoke-tested. Next required pieces are mobile push token registration, notification preferences, backend notification dispatch service, and tests.
- Step 43D final full smoke test remains postponed until backend, admin web, email, and mobile are all ready.
<!-- PULSEFI_SYNC_END -->

# PulseFi Backend Quality Improvement Backlog

This file records the improvement items that should make PulseFi more professional, safer, easier to maintain, and more deployable.

These items are not all required before every small feature, but they should be completed before the project becomes too large or before final deployment/presentation.

---

## Current Context

Current backend phase: **Step 26 complete - final backend hardening before frontend integration**.

The backend MVP/demo foundation is complete through:

- Platform Admin flows.
- ISP Admin user, plan, subscription, router, analytics, alert, report, and review flows.
- App User /me mobile flows.
- Router simulator and policy execution.
- Usage ingestion.
- Alerts.
- Predictions.
- Recommendations.
- Plan change request integration.
- Demo seed helper.
- API contract documentation.
- Migration integrity hardening.
- Standard API error responses.
- Stricter auth rate limits: 5 attempts per 15 minutes.
- Final docs/status alignment.
- Codex P1 fixes for router response safety, OpenAPI errors, ISP ownership joins, device policy validation, and password reset token invalidation.
- Remaining P2/P3 hardening for fresh setup, auth rate limiting, stale plan-change review, database constraints, simulator capability honesty, and API tests.

Current next work:

- Begin frontend integration.
- Fix discovered blockers, contract mismatches, or small safety issues during frontend integration.
- Keep the API contract updated when backend behavior changes.

Important security rules that remain active:

- ISP Admin endpoints must use get_current_isp_admin.
- Every ISP Admin query must be scoped by current_admin.isp_id.
- App User /me routes must use the authenticated App User from the token and must not accept target user IDs from the request.
- Router passwords or raw router credentials must not be accepted or stored until encrypted credential storage is intentionally implemented.
- The current auth rate limiter is in-memory; replace it with Redis/shared-store rate limiting before production multi-worker deployment.
- X-Forwarded-For is trusted only from configured trusted proxy IPs.

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

### 2026-05-14 - Limited DB Role

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

### 2026-05-14 - Alembic Baseline

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

### 2026-05-14 - Limited PostgreSQL App Role

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

### 2026-05-14 - Alembic Baseline

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

## Step 16E/16F Quality Notes - 2026-05-14

### Step 16E Migration Permission Note

Completed:

- Added Alembic migration `285ab0474b39_allow_suspended_user_subscription_status.py`.
- Updated `user_subscriptions.status` check constraint to allow `suspended`.
- Final allowed subscription statuses:
  - `pending`
  - `active`
  - `suspended`
  - `expired`
  - `cancelled`

Important permission note:

- Local migration application required pgAdmin/admin execution because `pulsefi_app` is intentionally not the owner of `user_subscriptions`.
- This confirms the future production need for a separate migration/admin DB role for Alembic.
- The runtime FastAPI role should stay restricted.

### Step 16F Router Credential Note

Completed:

- ISP Admin router management endpoints were added and tested.
- Router records can be created, listed, viewed, updated, set to maintenance, and reactivated.
- Step 16F does not accept or store router passwords.

Important security note:

- `password_encrypted` exists in the database model for future real-router integration.
- Do not store raw router passwords.
- Add encrypted credential storage only after proper encryption helpers and key management are implemented.

---

## Step 17A Quality Notes - 2026-05-14

Completed:

- Added first App User/mobile protected endpoint: `GET /api/v1/me/summary`.
- Confirmed the endpoint uses `get_current_app_user`.
- Confirmed `/me` endpoint logic uses the authenticated App User from the token.

Important security rule:

- App User mobile endpoints must not accept a `user_id` to choose which user data to load.
- App User mobile endpoints should always use `current_user.id`.
- Admin tokens must not be accepted for App User `/me` endpoints.
- Sensitive fields must not be returned:
  - `password_hash`
  - `mfa_secret`
  - password reset tokens
  - email verification tokens
  - backup codes

Testing reminder:

- Future automated tests should include App User route protection.
- Add tests confirming admin tokens are rejected from `/api/v1/me/*`.
- Add tests confirming App User tokens only access their own records.

---

## Step 17B Quality Notes - 2026-05-14

Completed:

- Added App User subscription list/detail endpoints.
- Confirmed endpoints use `get_current_app_user`.
- Confirmed endpoint logic uses the authenticated App User from the token.
- Confirmed admin tokens are rejected from App User subscription endpoints.
- Confirmed fake/non-owned subscription IDs return 404.

Important security rule:

- App User mobile endpoints must not accept `user_id`.
- App User mobile endpoints should always use `current_user.id`.
- Subscription queries must always filter by `UserSubscription.user_id = current_user.id`.
- Future App User endpoints must follow the same `/me` ownership pattern.

Testing reminder:

- Future automated tests should verify:
  - App User can list only their own subscriptions.
  - App User can view only their own subscription details.
  - Admin tokens are rejected from `/api/v1/me/*`.
  - Fake/non-owned IDs return 404.

---

## Step 17C Quality Notes - 2026-05-14

Completed:

- Added App User router list/detail endpoints.
- Added App User device list/detail endpoints.
- Confirmed endpoints use `get_current_app_user`.
- Confirmed endpoint logic uses the authenticated App User from the token.
- Confirmed router queries are scoped through the user's subscriptions.
- Confirmed device queries are scoped by `Device.user_id = current_user.id`.
- Confirmed router credentials are not exposed.

Important security rule:

- App User mobile endpoints must not accept `user_id`.
- App User mobile endpoints should always use `current_user.id`.
- Router queries should only return routers linked to subscriptions owned by the current App User.
- Device queries should only return devices owned by the current App User.
- Never expose `password_encrypted` or router credential fields in App User responses.

Usage design reminder:

- Router/device endpoints show identity and status only.
- Usage totals/download/upload must be calculated from `usage_records`.
- Step 17D should aggregate:
  - total user usage
  - per-device usage
  - per-router usage
  - per-subscription usage
  - raw records for charts

Testing reminder:

- Future automated tests should verify:
  - App User can list only own routers.
  - App User can view only own router details.
  - App User can list only own devices.
  - App User can view only own device details.
  - Admin tokens are rejected from `/api/v1/me/*`.
  - Fake/non-owned IDs return 404.

---

## Step 17D Quality Notes - 2026-05-14

Completed:

- Added App User usage summary, per-device usage, one-device usage, and raw usage record endpoints.
- Confirmed usage endpoints use `get_current_app_user`.
- Confirmed usage endpoints use the authenticated App User from the token.
- Confirmed per-device usage includes:
  - upload usage
  - download usage
  - total usage
  - record count
  - first/last record times
- Confirmed overall user usage includes upload/download/total usage.

Important database/model note:

- `usage_records.total_mb` is a PostgreSQL generated column.
- Do not insert `total_mb` manually.
- Insert only `upload_mb` and `download_mb`.
- PostgreSQL computes `total_mb`.
- SQLAlchemy model must keep `total_mb` marked with `Computed(...)`.

Testing reminder:

- Future automated tests should verify:
  - App User can access only their own usage.
  - Admin tokens are rejected from `/api/v1/me/usage/*`.
  - Fake/non-owned devices return 404.
  - `total_mb` is returned correctly from the generated column.
  - Per-device usage and overall usage totals are calculated correctly.

## Baseline Migration Status Update

- Real baseline migration was generated and tested against a fresh temporary PostgreSQL database.
- The circular FK between `isps.created_by_admin_id` and `admins.isp_id` was handled by creating the `isps.created_by_admin_id` FK after both tables exist.

## Limited Database Role Status Update

- The backend database connection was moved away from the PostgreSQL superuser.
- A limited `pulsefi_app` database role is now used in `.env` for normal backend connections.
- The role has runtime table permissions and temporary schema creation permission while migrations are still being actively developed.


## Production Token Email Flow Guard Status Update

- Added `EMAIL_DELIVERY_ENABLED` setting.
- Added `require_email_delivery_for_production()` dependency guard.
- Password reset, ISP Admin invitation, and App User invitation token flows are now blocked in production when email delivery is not configured.
- Development mode can still expose dev-only tokens/codes while `DEBUG=True`.
- Added regression tests for the email delivery production guard.


## Backend CI PostgreSQL/Alembic Status Update

- Backend CI now starts a PostgreSQL 18 service.
- CI now runs `alembic upgrade head` and `alembic current` against a fresh PostgreSQL database.
- This prevents broken baseline migrations or future migration-order problems from reaching `main` unnoticed.


## Email MFA Production Guard Status Update

- Email-based MFA login is now blocked in production when email delivery is not configured.
- The auth service raises a specific email-delivery-required error before creating an email MFA challenge.
- The login endpoint converts that error into HTTP 503.
- Added a regression test to prevent email MFA codes from being created silently in production without email delivery.


## Auth API Regression Test Status Update

- Added API-level login regression tests.
- Added API-level password reset regression tests.
- Added API-level invitation email guard tests for Platform Admin ISP Admin invitations and ISP Admin App User invitations.
- These tests verify frontend-facing HTTP responses and help prevent accidental token leakage or token creation when production email delivery is blocked.


## API Test Structure Refactor Status Update

- Added shared `tests/api/conftest.py`.
- Moved repeated API test setup into a shared `api_client` fixture.
- Removed repeated FakeDB, TestClient, and database dependency override boilerplate from API test files.
- API tests are now cleaner and easier to extend.

---

## Historical Current Context Update - 2026-05-15

Current backend phase: **Step 24 in final readiness phase - Backend/demo readiness before frontend integration**.

Recent quality work completed:
- MFA-required login bypass fixed.
- Auth service and API regression tests added.
- Real Alembic baseline migration added and tested.
- GitHub Actions now checks PostgreSQL + Alembic migrations.
- Production token/email flows are guarded when email delivery is not configured.
- API test setup was refactored into shared fixtures.

Important Step 18 security reminder:
- Do not store raw router passwords.
- Do not expose router credentials.
- Start with a simulator adapter before real router integrations.


## MFA Setup Flow Status Update

- The MFA-required login dead-end was fixed.
- Accounts with `mfa_required=True` and `mfa_enabled=False` now receive a signed setup token and authenticator setup data.
- Setup confirmation is handled through `POST /api/v1/auth/mfa/setup/confirm`.
- MFA setup logic was placed in `app/services/mfa_setup_service.py` to keep `mfa_service.py` from becoming too large.
- API regression tests were added for MFA setup confirmation.


## MFA Setup Cleanup Status Update

- Removed duplicated MFA setup logic from `mfa_service.py`.
- `mfa_service.py` now stays focused on MFA challenge/verify behavior.
- `mfa_setup_service.py` handles setup business logic.
- `mfa_setup_token_service.py` handles setup-token JWT creation and validation.
- Setup-token hardening tests were added and passed.


## Server-Side MFA Setup State Status Update

- Replaced readable JWT-based MFA setup state with server-side pending setup storage.
- Added `mfa_setup_challenges` table.
- Setup token sent to the client is now opaque.
- Setup token hash, pending authenticator secret, expiry, used marker, and attempt count are stored server-side.
- This fixes the previous issue where the raw authenticator secret was included inside a signed but readable JWT.


## MFA Setup Secret Redaction Status Update

- Used, revoked, and expired MFA setup challenge secrets are now redacted.
- Revoking old setup challenges clears their pending authenticator secret.
- Successful MFA setup copies the secret to the account and clears it from the setup challenge row.
- Full encryption at rest is still required before production for account MFA secrets and future router credentials.


## MFA Setup Challenge Cleanup Service Status Update

- Added a cleanup service for old inactive MFA setup challenges.
- The cleanup service deletes only setup challenges that are used, revoked, or expired and older than the retention window.
- The service is not scheduled yet.
- Future production work should connect cleanup services to a scheduled worker or maintenance command.


## MFA Secret Encryption Status Update

- Added encryption helper foundation with `DATA_ENCRYPTION_KEY`.
- New pending MFA setup secrets are encrypted at rest.
- New final account MFA secrets are encrypted at rest.
- MFA verification decrypts account MFA secrets before validating authenticator codes.
- Remaining production work:
  - migrate or rotate any existing plaintext MFA secrets if real users exist
  - add rate limiting
  - add real DB-backed auth/MFA integration tests
  - reuse encryption helper later for router credentials


## Auth Rate Limiting Status Update

- Added MVP in-memory rate limiting for auth-sensitive endpoints.
- Current rate limiter protects login, MFA verification, MFA setup confirmation, password reset, and invitation acceptance.
- Added tests for rate-limit behavior.
- Remaining production work:
  - replace in-memory limiter with Redis/shared-store limiter before multi-worker deployment
  - add DB-backed integration tests for auth/MFA/rate-limit flows


## Final Pre-Step-18 Hardening Status Update

- MFA setup-token design is now server-side and opaque-token based.
- Pending and final MFA secrets are encrypted at rest for new setup flows.
- Auth-sensitive endpoints have MVP in-memory rate limits.
- MFA setup cleanup service is now wired to a runnable maintenance command.
- `.pytest_cache` cleanup/ignore handling was checked.

Remaining before real production:
- Redis/shared-store rate limiting.
- Real email sending.
- Real DB-backed integration tests.
- Secret migration/rotation plan for any existing plaintext MFA secrets.
- Deployment-grade secret management.

---

## Resolved Quality Items

### Fixed malformed requirements.txt

Status: resolved.

The dependency file now uses real line breaks instead of literal `\n` characters.

Why this mattered:
- Fresh installs were failing.
- GitHub Actions dependency installation could fail even if local tests passed.

Impact:
- Database schema: no change.
- Existing data: no change.
- SE diagrams: no change.

### Covered MFA-required login behavior with regression tests

Status: resolved / guarded by tests.

Added tests for:
- MFA-required accounts must receive MFA setup before a token is issued.
- Accounts without required MFA can still receive a normal token.

Test file:
- `tests/test_auth_service_mfa_required.py`

Impact:
- Database schema: no change.
- Existing data: no change.
- API behavior: no intended change; existing secure behavior is now protected.
- SE diagrams: no change.

---

## DB-Backed Integration Testing Status Update

Status: started.

Completed:
- Added integration test fixture using a real AsyncSession and transaction rollback.
- Added first real PostgreSQL-backed integration test for admin invitation acceptance plus MFA setup-required login behavior.

Covered flow:
- Create ISP.
- Create AccountInvitation.
- Accept invitation.
- Create Admin account.
- Confirm admin MFA is required but not enabled.
- Confirm login returns MFA setup instead of an access token.

Important local DB note:
- Local development database had stale Alembic revision 285ab0474b39.
- Current valid head is 68eea2a5b4d2.
- Local database was repaired manually because the runtime role pulsefi_app is intentionally not allowed to perform schema creation.
- Future migrations/schema repairs should use an admin or migration DB role, not the runtime app role.

Remaining DB-backed test priorities:
1. Duplicate invitation/email/username behavior.
2. MFA setup confirmation success/failure with real DB rows.
3. ISP Admin cross-ISP isolation.
4. App User ownership isolation.
5. Subscription, router, device policy, alert, prediction, and recommendation ownership.

---

## DB-Backed Invitation Duplicate Test Status Update

Completed:
- Added real PostgreSQL-backed tests for duplicate email and duplicate username rejection during admin invitation acceptance.
- Updated integration fixture to use NullPool so asyncpg connections are not reused across closed Windows event loops.

Covered:
- Existing email prevents second account creation.
- Existing username prevents second account creation.
- Rejected duplicate invitation remains unaccepted.

Remaining priority:
1. DB-backed MFA setup confirmation success/failure tests.
2. DB-backed ISP Admin cross-ISP isolation tests.
3. DB-backed App User ownership tests.

---

## DB-Backed MFA Setup Confirmation Test Status Update

Completed:
- Added real PostgreSQL-backed tests for MFA setup confirmation success and invalid-code failure.

Covered:
- Correct authenticator code enables MFA.
- Final account MFA secret is encrypted at rest.
- Used setup challenge is marked used.
- Used setup challenge authenticator secret is cleared.
- Wrong authenticator code does not enable MFA.
- Wrong code increments attempt_count.

Remaining priority:
1. DB-backed ISP Admin cross-ISP isolation tests.
2. DB-backed App User ownership tests.
3. Subscription, router, device policy, alert, prediction, and recommendation ownership tests.

---

## DB-Backed ISP Admin Isolation Test Status Update

Completed:
- Added combined real PostgreSQL-backed ISP Admin isolation test.

Covered:
- ISP Admin from one ISP cannot access another ISP's App User.
- ISP Admin from one ISP cannot access another ISP's Subscription Plan.
- ISP Admin from one ISP cannot access another ISP's User Subscription.
- ISP Admin from one ISP cannot access another ISP's Router.

Remaining priority:
1. DB-backed App User ownership isolation tests.
2. DB-backed App User action ownership tests.

---

## DB-Backed App User Read Ownership Test Status Update

Completed:
- Added combined real PostgreSQL-backed App User read ownership test.

Covered:
- App User cannot read another user's Alert.
- App User cannot read another user's Prediction.
- App User cannot read another user's Recommendation.

Schema cleanup discovered:
- Alert severity check constraint contains typo "meduim".
- Recommendation type check constraint contains typo "downgrade_pan".

Remaining priority:
1. DB-backed App User action ownership test.
2. Later schema cleanup migration for enum/check-constraint typos.

---

## DB-Backed App User Action Ownership Test Status Update

Completed:
- Added combined real PostgreSQL-backed App User action ownership test.

Covered:
- App User cannot create a device policy for another user's device.
- App User cannot create a plan change request using another user's subscription.
- App User cannot create a plan change request using another user's recommendation.
- Blocked action attempts do not create policy/change-request rows.

Immediate ownership hardening pass:
- Complete.

Next priority:
1. Continue Step 18.
2. Later schema cleanup migration for check-constraint typos:
   - "meduim" -> "medium"
   - "downgrade_pan" -> "downgrade_plan"



---

## Step 19 Usage Ingestion Quality Notes

Step 19A/19B added simulator usage ingestion.

Quality/security reminders:

- Keep ingestion endpoints ISP-scoped.
- Do not allow ISP Admins to ingest usage for routers outside their ISP.
- Avoid double-counting usage by not storing router-total and per-device records for the same time window unless a future aggregation model separates them clearly.
- Keep real-router credentials deferred until encrypted credential storage is intentionally implemented.
- Add integration tests for usage ingestion ownership/isolation.
- Add scheduled ingestion later after manual ingestion is stable.

---

## Step 19C Device Ingestion Quality Notes

Quality/security reminders:

- Keep simulator device ingestion scoped by current_admin.isp_id.
- Do not create duplicate devices for repeated simulator runs.
- Keep connection logs useful for future alert generation.
- Add integration tests for cross-ISP router/device ingestion isolation.
- Later connect new-device connection logs to alert generation.

---

## Step 19C Device Ingestion Quality Notes

Quality/security reminders:

- Keep simulator device ingestion scoped by current_admin.isp_id.
- Do not create duplicate devices for repeated simulator runs.
- Keep connection logs useful for future alert generation.
- Add integration tests for cross-ISP router/device ingestion isolation.
- Later connect new-device connection logs to alert generation.

---

## Step 19D Combined Ingestion Quality Notes

Quality/security reminders:

- Keep combined simulator ingestion scoped by current_admin.isp_id.
- Device ingestion should run before usage ingestion so per-device usage can be generated.
- Keep simulator event_type values aligned with database constraints.
- Add integration tests for the combined endpoint.
- Later add scheduler support after manual ingestion remains stable.
- Later connect connection logs to alert generation.

---

## Step 19E Visibility Endpoint Quality Notes

Quality/security reminders:

- Keep usage record visibility scoped through Router.isp_id.
- Keep device connection log visibility scoped through Router.isp_id.
- Add integration tests for cross-ISP isolation.
- Add pagination tests for usage records and connection logs.
- Later connect these endpoints to ISP Admin dashboard tables.

---

## Step 19 Final Quality Notes

Step 19 is complete for the MVP/demo backend.

Remaining future improvements:

- Add deeper integration tests using the test database for cross-ISP isolation.
- Add scheduler support after manual ingestion remains stable.
- Add alert generation from high usage and new device connection logs.
- Add production-grade logging around ingestion success/failure.
- Keep real-router credential support deferred until encrypted credential storage is intentionally designed.

---

## Step 20A Quality Note - 2026-05-16

Completed:

- Alert generation service added.
- Alert generation connected to simulator ingestion.
- Alert type check constraint updated through Alembic.
- Manual behavior test confirmed generated alerts can be viewed and marked as read by the App User.

Quality reminders:

- Add focused tests for:
  - high usage alert generation
  - plan exceed risk alert generation
  - unusual consumption alert generation
  - new device alert generation
  - duplicate unread alert prevention
  - App User alert ownership isolation
  - ISP Admin alert scoping if ISP Admin alert visibility is added
- Add `policy_failed` alert generation from failed router/device policy execution.
- Consider daily/monthly usage timeline endpoints for mobile charts later.


---

## Step 20B Quality Note - 2026-05-16

Completed:

- `policy_failed` alert generation added.
- Failed device policy execution was manually tested.
- Router action type check constraint updated.

Quality reminders:

- Add tests for failed policy alert generation.
- Add tests that App Users cannot read another user's policy failed alerts.
- Add tests that ISP Admin alert visibility, if added, is scoped by `current_admin.isp_id`.
- Consider creating a migration/admin DB role so Alembic can apply schema changes without manual pgAdmin steps.


---

## Step 20C Quality Note - 2026-05-16

Completed:

- ISP Admin read-only alert visibility added.
- ISP Admin alert list/detail queries are scoped by ISP.

Quality reminders:

- Add tests that ISP Admins cannot view alerts from another ISP.
- Add tests that App Users cannot view another user's alerts.
- Add tests for alert filters:
  - status
  - severity
  - alert_type
  - user_id
  - device_id
- Consider whether admin-owned notifications are needed later as a separate feature.


---

## Step 20D Quality Note - 2026-05-16

Completed:

- Added focused alert generation tests.
- Added duplicate unread policy-failed alert prevention test.

Still needed:

- App User ownership isolation tests.
- ISP Admin cross-ISP isolation tests.
- New device alert tests.
- Unusual consumption alert tests.


---

## Step 20E Quality Note - 2026-05-16

Completed:

- Added App User alert ownership query tests.
- Added ISP Admin alert ISP-scope query tests.
- Added test that extra ISP Admin alert filters keep ISP scoping.

Still needed:

- New device alert generation test.
- Unusual consumption alert generation test.


---

## Step 21A Quality Note - 2026-05-16

Completed:

- Rule-based prediction generation added.
- ISP Admin prediction generation endpoint added.
- Manual API test confirmed prediction generation and App User prediction visibility.

Quality reminders:

- Add focused tests for prediction generation.
- Add tests that ISP Admin cannot generate predictions for another ISP's subscription.
- Add tests that App Users cannot view another user's predictions.
- Add recommendation generation tests after Step 21B.
- Later, compare rule-based prediction against real collected usage data for better accuracy.


---

## Step 21B Quality Note - 2026-05-16

Completed:

- Rule-based recommendation generation added.
- ISP Admin recommendation generation endpoint added.
- Recommendation type check constraint updated.
- Manual API test confirmed recommendation generation and App User recommendation visibility.

Quality reminders:

- Add focused tests for recommendation generation.
- Add tests that ISP Admin cannot generate recommendations from another ISP's predictions.
- Add tests that App Users cannot view another user's recommendations.
- Add tests for duplicate new recommendation prevention.
- Add tests for upgrade, downgrade, stay current, and monitor usage paths.


---

## Step 21C Quality Note - 2026-05-16

Completed:

- Added Step 21 prediction/recommendation service tests.
- Added recommendation duplicate-prevention test.
- Added ownership and ISP-scope query tests.

Still useful later:

- Downgrade recommendation path test.
- Monitor usage path test.
- End-to-end API tests for prediction and recommendation generation.
- Subscription change request integration tests.


---

## Step 21D Quality Note - 2026-05-16

Completed:

- Added downgrade recommendation path test.
- Added monitor usage recommendation path test.
- All MVP recommendation types now have focused service test coverage.

Still useful later:

- End-to-end API tests for prediction generation.
- End-to-end API tests for recommendation generation.
- Subscription change request integration tests.
- More realistic ML/data-quality validation once real router usage data exists.


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

## Step 25B Quality Note - 2026-05-17

Completed:

- Added standard API error response handlers.
- HTTP errors now return a consistent frontend-friendly response shape:
  - `error`
  - `message`
  - optional `details`
- Validation errors now return `validation_error` with validation details.
- Unexpected server errors return a safe generic message.
- Updated old tests from `detail` expectations to `message`.
- Added focused API error response tests.

Impact:

- Database schema: no change.
- Existing data: no change.
- Frontend readiness: improved.
- Security: internal exception details are not exposed in standard 500 responses.

---

## Step 25C Quality Note - 2026-05-17

Completed:

- Tightened auth-sensitive endpoint rate limits to 5 attempts per 15 minutes.
- Updated login rate-limit API test to match the stricter threshold.

Security note:

- This improves MVP/demo protection.
- The limiter is still in-memory, so Redis/shared-store rate limiting remains needed before production multi-worker deployment.

---

## Step 25D Quality Note - 2026-05-17

Completed:

- Refreshed API contract documentation after standard API error responses and stricter auth rate limits.
- Added frontend-facing guidance for standard error payloads.
- Added frontend-facing guidance for auth rate-limit handling.

Impact:

- Frontend readiness improved.
- No database or runtime code changes.


---

## Step 26A Quality Note - 2026-05-17

Completed:

- Fixed P1 Codex finding: App User router responses exposed admin/management fields.
- App User router schema now excludes router IP, MAC address, API endpoint, username, ISP ID, assignment admin ID, and password_encrypted.
- Added regression test for safe App User router response shape.

Impact:

- Frontend blocker reduced.
- No database change.

---

## Step 26B Quality Note - 2026-05-17

Completed:

- Fixed P1 Codex finding: OpenAPI documented FastAPI default detail-based validation errors while runtime used standard error/message/details responses.
- Added custom OpenAPI error schemas and response documentation.
- Added tests verifying OpenAPI uses APIErrorResponse and APIValidationErrorResponse.

Impact:

- Frontend-generated clients should now see the correct standard error shape.
- No database change.

---

## Step 26C Quality Note - 2026-05-17

Completed:

- Fixed P1 Codex finding: some ISP usage, ingestion, and analytics ownership paths depended on partial joins.
- Added shared ownership-scope helpers for router and usage-record ISP scoping.
- Updated usage visibility, simulator ingestion, and analytics usage aggregation to require fuller ownership chains.
- Added regression tests for ownership-scope query construction.

Impact:

- Frontend blocker reduced.
- No database change.
- Cross-ISP leakage risk from malformed linked records is reduced.

---

## Step 26D Quality Note - 2026-05-17

Completed:

- Fixed P1 Codex finding: Device policy creation accepted invalid policy types.
- App User device policy request schema now allows only bandwidth_limit and device_priority.
- Action-specific fields are now validated before saving.
- Added focused schema validation tests.

Impact:

- Frontend blocker reduced.
- No database change.
- Unsupported device policies are rejected at request validation time.

---

## Step 26E Quality Note - 2026-05-17

Completed:

- Fixed P1 Codex finding: password reset tokens were not invalidated account-wide.
- Creating a new reset token now marks existing active reset tokens for the same account as used.
- Successful password reset now marks active reset tokens for the same account as used.
- Added focused password reset service tests.

Impact:

- Final Codex P1 issue addressed.
- No database change.
- Password reset flow is safer before frontend integration.

## Current Backend Quality Backlog ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Auth/UI Integration Issues

Status update - 2026-05-18:

- P1 local auth rate-limit unblocker is fixed with a DEBUG-only reset endpoint at `POST /api/v1/auth/rate-limit/reset`.
- P1 `/auth/me` role contract is covered by an API regression test and returns `account_type`, `account_id`, `role`, identity, status, and MFA fields.
- P1 MFA frontend dead-end is fixed in the real admin web app by wiring MFA verify and MFA setup confirm.
- P1 frontend production routing is cleaned up so real admin dashboards no longer render the design preview components.
- Step 27C follow-up: page load now validates existing admin tokens with `GET /api/v1/auth/me`; invalid, expired, or App User tokens clear the admin session and return to login.
- Remaining production hardening: replace in-memory rate limiting with Redis/shared-store rate limiting before multi-worker deployment.

### P1 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Admin login rate limit blocks local development
Frontend login now sends the required `account_type: "admin"` field, but backend returns:
- `429 rate_limited`
- Message: `Too many attempts. Please try again later.`

Required:
- Done: implementation is in `app/api/dependencies/rate_limit.py`.
- Done: local reset is `POST /api/v1/auth/rate-limit/reset` while `DEBUG=True`.
- Done: production rate limiting is not weakened; reset returns 404 when `DEBUG=False`.
- Done: docs now describe how to clear/reset local auth rate limit during development.
- Add/confirm tests for:
  - successful admin login with `account_type=admin`
  - missing `account_type` returns validation error
  - Done: repeated failures return 429
  - Done: successful login attempt behavior after reset

### P1 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Verify `/auth/me` role contract
Frontend now falls back to `GET /api/v1/auth/me` to determine admin role.

Required:
- Done: ensure `/auth/me` returns enough information for frontend routing:
  - `account_type`
  - `account_id`
  - `role`
  - email/username if available
- Done: Platform Admin is distinguishable from ISP Admin by `role`.
- Done in frontend: App User is not accepted in admin web login.

### P1 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â MFA-required flow incomplete in frontend
Backend exposes:
- `/api/v1/auth/mfa/verify`
- `/api/v1/auth/mfa/setup/confirm`

Required:
- Done: MFA verify uses `POST /api/v1/auth/mfa/verify` with `challenge_token` and `code`.
- Done: frontend MFA verification screen is connected.
- Done: `mfa_required=true` and `mfa_enabled=false` returns `mfa_setup_required` and no access token.
- Done: frontend setup flow calls `POST /api/v1/auth/mfa/setup/confirm`; setup-only flow cannot bypass token issuance.

### P1 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Frontend/admin production routing
Current real frontend shell still uses design preview dashboard components as temporary dashboard views.

Required:
- Done: mock dashboard preview imports were removed from the real app shell.
- Done: backend token/session role decides Platform Admin vs ISP Admin routing.
- Done: no visible role switch in production.
- Done: App User product preview remains design-only under `npm run dev:design`.
- Done: admin settings identity updates now have a backend contract:
  `POST /api/v1/auth/me/profile-update-challenge` starts MFA verification and
  `PATCH /api/v1/auth/me/identity` updates email/username after MFA succeeds.
- Done: password reset requests now send a reset link email instead of relying
  on a manual token-copy flow; DEBUG can return a local reset URL for testing.

### P2 ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â Tests needed
Add or expand tests for:
- admin login
- `/auth/me`
- MFA verify
- rate limit behavior
- platform admin routing data
- ISP admin isolation by `current_admin.isp_id`
- invitation flows
- subscription flows
- usage/alerts/recommendations once connected.

## Automatic Intelligence Scheduler Follow-up

Done:
- Added scheduler-ready automatic intelligence service.
- Added environment-gated local/demo scheduler.
- Added idempotency guard to avoid duplicate prediction/recommendation rows.
- Step 27D added ISP Admin recommendation viewing routes and connected recommendation history in the real Intelligence Center.
- Step 45 added automatic alert generation to scheduled/manual intelligence runs.
- Step 45 added controlled simulator scenarios and deterministic Explain-this response text.
- Step 45 tests cover high usage alerts, new device alerts, policy failure alerts, plan upgrade recommendations, and normal/no-alert behavior.
- Current intelligence remains rules-based/heuristic MVP; no trained ML pipeline is integrated.

Follow-up:
- Convert FastAPI `on_event` startup/shutdown hooks to lifespan to remove warnings.
- Add prediction list endpoints if dashboard prediction history is needed.
- Move scheduler to a production worker/cron system before multi-worker deployment.
- Add push notifications only after deployed mobile login and device-token storage are smoke-tested.
- Push notification pieces needed: mobile push token registration, notification preferences, backend notification dispatch service, and tests.

## Network Integration / RADIUS Backlog

- Add ISP integration settings model for simulator/manual/csv/radius_api modes.
- Add encrypted credential storage before storing ISP API keys, router credentials, or RADIUS credentials.
- Add RADIUS/API adapter interface for official usage sync, plan/profile changes, suspend/reactivate, and account status sync.
- Add billing/invoice models for paid/unpaid/overdue subscription state.
- Add router/CPE adapter support for live per-device rate polling and/or cumulative byte counters.
- Add ingestion logic that estimates per-device usage from live Mbps polling intervals when counters are unavailable.
- Add counter reset handling when router byte counters go backwards after reboot/reset.
- Add alert visibility so ISP Admin sees operational alerts only, while App User keeps private app alerts.
- Keep simulator as the demo/local adapter representing RADIUS/API/router integrations.

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

FINAL DEMO CHECKPOINT: Backend Render, DB Neon, Admin web Vercel, Mobile Android APK/EAS working. Use C:\PulseFi\pulsefi-mobile-app as real mobile repo. Do not use C:\PulseFi\pulsefi-mobile. Working flows: Platform Admin, Platform Team invites, ISP creation, ISP Admin invite, App User invite, invitation accept redirects to login, router-only service-line creation, active service-line simulator, deployed web/mobile data. Email pending Brevo OTP. Keep DEBUG=True and EMAIL_DELIVERY_ENABLED=False until Brevo is verified.

## Brevo Email Delivery Update

PulseFi now uses Brevo as the only active production email delivery provider.

Required deployment environment variables:
- EMAIL_DELIVERY_ENABLED=True
- EMAIL_DELIVERY_PROVIDER=brevo
- BREVO_API_URL=https://api.brevo.com/v3/smtp/email
- BREVO_API_KEY=<deployment secret only>
- SMTP_FROM_EMAIL=<verified Brevo sender email>
- SMTP_FROM_NAME=PulseFi
- FRONTEND_ADMIN_URL=https://pulsefi-admin-web.vercel.app

Old SMTP, Resend, and Mailtrap delivery paths were removed from active backend code to simplify deployment and avoid unused provider configuration.
Never commit Brevo API keys or any .env files.

## PulseFi Current Truth - Step 46+ Forward Plan

### Current phase


Live deployment notes:

- Backend is deployed on Render.
- Admin web is deployed on Vercel.
- Mobile app/APK is handled through Expo.
- Brevo email delivery is configured.
- `ENABLE_INTELLIGENCE_SCHEDULER=True` is enabled.
- `INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES=15` is enabled.
- Push notifications are deferred until alert/recommendation behavior is stable.

---

### Step 46A - Shared usage summary backend

Status: implemented.

PulseFi now uses calculated usage summary API fields. These are not database columns.

Required usage summary fields:

- `today_usage_gb`
- `monthly_usage_gb`
- `current_cycle_usage_gb`
- `total_usage_gb`
- `plan_limit_gb`
- `remaining_gb`
- `usage_percent`
- `is_unlimited`
- `cycle_start`
- `cycle_end`
- `last_record_end`

Important truth:

- `usage_summaries` is a calculated API response.
- It is built from `user_subscriptions`, `subscription_plans`, and `usage_records`.
- It is not a new database column.

---

### Step 46B - ISP Admin selected-user plan usage

Status: implemented and live-tested.

Correct UX:

- ISP Admin Users table should stay compact.
- Users table is for finding/selecting users.
- Selected user panel shows one circular usage card per subscription/service line/plan.
- Multiple subscriptions must show multiple separate cards.
- Each card has its own used/limit, percent, remaining, today usage, monthly/current-cycle usage, and total usage.

---

### Step 46C - App User mobile usage visibility

Status: planned for mobile step.

Mobile app should not only show total consumption. It should show:

- used / plan limit
- remaining GB
- today usage
- monthly/current-cycle usage
- total usage
- per-plan/per-service-line usage
- unlimited-plan handling

Home should show a small summary only. Detailed usage belongs in the Usage tab.

---

### Step 46D - Automatic usage alert tiers

Status: implemented/finalizing.

Plan usage alerts should be automatic after usage ingestion.

Expected tiers:

- `50%+` of plan: `Usage warning`
- `80%+` of plan: `High internet usage`
- `100%+` of plan: `Plan usage limit reached`

Implementation truth:

- Do not add a new DB alert type for rapid usage yet.
- `Usage warning`, `High internet usage`, and `Rapid high internet usage` may all use `alert_type="high_usage"` with different titles.
- `Plan usage limit reached` should use `alert_type="plan_exceed_risk"`.

---

### Step 46E - Rapid high-usage alerts

Status: implemented/finalizing.

Rapid usage is different from monthly plan percentage. It should trigger even on large plans.

Expected rapid triggers:

- One large usage update can trigger rapid usage.
- Multiple usage ingestions in a short period can trigger rapid usage.
- About `2 GB+` in a short/one-hour window should trigger rapid usage.
- About `2 GB+` total created within about `10 minutes` should trigger rapid usage.
- About `5 GB+` within `24 hours` should trigger rapid usage.

Important example:

- A `450 GB` plan user consuming `4 GB` in about `2 minutes` through multiple simulator runs should still receive `Rapid high internet usage`.

---

### Step 46F - Simulator alert spam correction

Status: implemented/finalizing.

One full simulator run should not create 8 alerts.

Correct simulator behavior:

- Max one new-device summary alert per run.
- Max one usage alert per subscription per run.
- Full simulator should not create duplicate alerts through both simulator alert generation and intelligence alert generation.
- Intelligence may refresh predictions/recommendations after simulation, but simulator should not create duplicate alert spam through the intelligence path.

Expected result:

- A simulator run may create around 1-2 meaningful alerts, not many duplicate alerts.

---

### Step 46G - Prediction/recommendation non-spam behavior

Status: implemented/finalizing.

Predictions/recommendations should be state-based, not event-spam.

Correct behavior:

- Same-day prediction should update in place, not create many duplicate prediction rows.
- Recommendation should only create a new row if the recommendation state changes.
- `stay_current -> stay_current`: do not create/push duplicates.
- `stay_current -> upgrade_plan`: create a new recommendation.
- `upgrade_plan` to same plan -> same plan: do not duplicate.
- `upgrade_plan` to different plan: create a new recommendation.
- `upgrade_plan -> monitor_usage`: create a new recommendation.
- `stay_current` can refresh daily, effectively after midnight, but not every usage run.

Important truth:

- Alerts are closer to an event log.
- Recommendations are a state/decision layer and must not spam.

---

### Step 46H - Mobile alert/recommendation list cleanup

Status: planned for mobile step.

The mobile app currently becomes too crowded when alerts/recommendations build up.

Mobile should not show endless raw history by default.

Mobile UX plan:

- Home shows only the most important active alert.
- Home shows only the latest meaningful recommendation.
- Alerts tab should show active/recent important alerts first.
- Recommendations tab/section should show latest meaningful recommendation first.
- History should be behind `View all`, filters, or pagination.
- Pull-to-refresh and auto-refresh should be handled in the mobile step.

Important:

- The mobile app part will be handled separately in the mobile step.
- Do not mix mobile UI cleanup into backend Step 46 unless required by API contracts.

---

### Step 46I - ISP Admin high-usage alerts per selected user

Status: planned next.

Current issue:

- ISP Admin monitoring can become too broad if it shows all users combined.
- Admin should be able to view high-usage alerts per selected user.

Backend truth:

- ISP Admin alerts endpoint already supports filters:
  - `user_id`
  - `user_subscription_id`
  - `device_id`
  - `alert_type`
  - `severity`
  - `status`
  - date range
- Backend already scopes ISP Admin alert queries by `current_admin.isp_id`.

Frontend/admin next step:

- Add selected-user alert panel in Users or Monitoring.
- Show high-usage alerts for the selected user only.
- Default Monitoring can show summary, but detailed alert review should support user filtering.
- For high usage specifically, call alerts API with user filter and `alert_type=high_usage`.

---

### Step 46J - Device trust enforcement

Status: planned next.

Current issue:

- Device has `is_trusted`, but trust state does not fully enforce network access.

Correct rule:

- If a device is not trusted, it should not be allowed to use Wi-Fi.

Backend/device truth:

- Devices already have:
  - `is_trusted`
  - `status`
- Mobile/app user endpoint already supports changing trust:
  - `PATCH /api/v1/app/me/devices/{device_id}/trust`

Next backend behavior:

- When `is_trusted=false`, device should be treated as blocked/untrusted.
- Simulator usage should not generate usage records for blocked/untrusted devices.
- Device status should clearly reflect blocked/untrusted behavior if needed.
- New untrusted devices should generate a clear alert and/or require approval.
- Later real-router integration should translate untrusted/blocked state into router MAC blocking.

Important technical note:

- Router action logs currently allow action types such as `bandwidth_limit` and `device_priority`.
- If we add real `block_device` actions, we need a safe migration/check constraint update.
- Until real router integration exists, simulator enforcement should be implemented first.

---

### Step 46K - Admin/mobile alert volume rules

Status: planned.

Alerts should not be unlimited spam, but also should not be blocked forever.

Correct alert behavior:

- Usage alerts should have cooldown/rate-limiting.
- Plan tier alerts should not resend every simulator click.
- Rapid usage should not send duplicates immediately.
- New device alerts should be summarized per run instead of one alert per discovered simulator device.
- Important repeated events may create later alerts after cooldown.
- Mobile should display recent/active important alerts first and hide older history behind filters/pagination.

---

### Step 47 - Real ML prediction pipeline

Status: planned after Step 46 stabilizes.

Current intelligence is rules-based/heuristic MVP, not trained ML.

ML should mainly power prediction, not only recommendations.

Correct ML structure:

- usage data -> ML prediction -> risk level -> recommendation/alert support

Step 47 target:

- predict end-of-cycle usage
- predict plan exceed risk
- estimate risk level
- support plan recommendation decisions
- optionally improve anomaly/rapid usage detection later

Planned inputs:

- current cycle usage
- plan limit
- days elapsed
- days remaining
- average daily usage
- recent 7-day usage
- highest daily spike
- connected device count
- rapid usage spike count

Planned outputs:

- predicted end-cycle usage
- risk level: low / medium / high
- exceed probability
- recommended action

Implementation direction:

- add `numpy`, `pandas`, `scikit-learn`, `joblib`
- train first model from simulator/historical usage records
- save/load model artifact
- keep rule-based fallback when model artifact is missing
- store results in existing predictions flow

---

### Step 48 - Focused chatbot / AI explainer

Status: planned after Step 46 and Step 47.

Do not build a generic chatbot first.

Useful version:

- Explain this alert.
- Explain this recommendation.
- Why is this user high risk?
- Why did PulseFi recommend this plan?
- What should the user/admin do next?

Security rule:

- Only pass scoped alert/recommendation/usage summary/plan context.
- Do not pass secrets, passwords, API keys, MFA codes, raw tokens, router credentials, or unrestricted database content.

---

### Step 49 - Push notifications

Status: deferred until Step 46 alert/recommendation behavior is stable.

Do not continue push notifications until:

- alerts are not spammy
- recommendations are not spammy
- simulator alert behavior is stable
- mobile alert/recommendation display strategy is clear

Future push pieces:

- push token registration
- notification preferences
- Expo push service
- push dispatch on new important alert
- push dispatch on meaningful recommendation state change
- no push for repeated `stay_current`
- no sensitive details in notification body
- notification tap opens Alerts or Recommendation detail

---

### Step 50 - Final live QA and presentation cleanup

Status: planned.

Final QA should cover:

- Render backend
- Neon database
- Vercel admin web
- Expo APK mobile app
- Brevo email delivery
- invitation flows
- password reset
- simulator
- selected-user usage cards
- alert tiers
- rapid high-usage alerts
- recommendation state-change behavior
- admin per-user high-usage alert filtering
- device trust enforcement
- mobile alert/recommendation cleanup
- ML prediction after Step 47
- Platform Admin flows
- ISP Admin flows
- App User mobile flows

---

### Tomorrow continuation checkpoint

Continue from:

1. Verify latest Step 46 backend tests pass.
2. Commit/push any remaining Step 46 backend changes if not already committed.
3. Redeploy Render.
4. Test one simulator run:
   - no 8-alert spam
   - max one new-device summary alert
   - max one usage alert
   - no duplicate intelligence alerts
5. Implement Step 46I:
   - ISP Admin high-usage alerts per selected user.
6. Implement Step 46J:
   - device trust enforcement.
7. Leave mobile UI cleanup for the mobile step.
8. Leave push notifications until alert/recommendation behavior is stable.

---

### SE documentation note

SE diagrams/docs should be updated after these implementation steps stabilize.

Required future SE updates:

- Use Case Diagram: usage summaries, alert tiers, rapid alerts, profile tab, ML predictions, chatbot, push notifications, device trust/blocking
- DFD Level 1: usage ingestion -> alert generation -> intelligence -> recommendations -> mobile/admin display
- Component Diagram: usage summary service, alert service, intelligence service, future ML module, future notification service, device trust enforcement
- Mobile screen map: Home, Usage, Devices, Alerts, Profile
- API/Feature coverage matrix: usage summaries, alert tiers, recommendation refresh, admin alert filters, device trust enforcement, auto-refresh/push status

### Step 46I completion note - ISP Admin selected-user alerts

Status: complete and live-tested.

What changed:
- ISP Admin Monitoring now keeps general analytics visible.
- Alert review is selected-user based.
- Alerts are not shown globally for all users in the Monitoring detail panel.
- The selected-user alert list only shows:
  - `high_usage`
  - `plan_exceed_risk`
- The Users page no longer owns this alert workflow.
- The Monitoring alert list is scroll-contained instead of stretching the page.
- ISP Admin login now defaults to Overview instead of restoring the last saved section.
- Admin session restore no longer clears a valid saved token on temporary non-auth backend/network failures.

API contract impact:
- No backend endpoint change was required.
- Existing `GET /api/v1/isp-admin/alerts` filters were reused:
  - `user_id`
  - `alert_type`
  - `limit`
  - `offset`
- ISP Admin alert access remains scoped by `current_admin.isp_id`.

Presentation/report note:
- PulseFi currently implements logical provisioning and simulator-backed network events.
- Real ISP database/API integration and real router provisioning are production integration layers.
- In production, PulseFi would connect through secure ISP APIs/webhooks, RADIUS/PPPoE, MikroTik RouterOS API, TR-069/USP, or a local router agent.

### Step 46J completion note - Device trust enforcement

Status: complete and tested locally.

What changed:
- Simulator usage ingestion now separates connected devices into trusted and untrusted devices.
- Trusted connected devices can still generate simulator usage records.
- Untrusted connected devices no longer generate simulator usage records.
- Every blocked untrusted device creates a `policy_failed` alert titled `Untrusted device usage blocked`.
- Simulator usage responses now include:
  - `blocked_devices`
  - `policy_alerts_created`
- This is simulator-backed enforcement, not real router enforcement yet.

Networking meaning:
- PulseFi now treats device trust as an enforcement rule in the simulator.
- This models what a real router/controller/RADIUS integration would later do: block or prevent usage from untrusted devices.
- Real router provisioning remains a future production integration layer through MikroTik RouterOS API, RADIUS/PPPoE, TR-069/USP, ISP APIs/webhooks, or a secure local router agent.

Testing:
- Focused simulator ingestion tests passed.
- Full backend compile/test checks passed locally.

### Step 46 finalization note - Monitoring, trust enforcement, and alert volume rules

Status: complete and tested locally.

Completed Step 46I:
- ISP Admin Monitoring now requires selecting an App User before user-specific alert details are shown.
- Monitoring only shows selected-user `high_usage` and `plan_exceed_risk` alerts in that workflow.
- The Users page no longer owns the selected-user alert workflow.
- ISP Admin dashboard login defaults to Overview.
- Admin session restore no longer clears valid saved tokens on temporary non-auth backend/network failures.

Completed Step 46J:
- Simulator usage ingestion now separates connected devices into trusted and untrusted devices.
- Trusted connected devices can generate simulator usage records.
- Untrusted connected devices no longer generate simulator usage records.
- Blocked untrusted devices can create `policy_failed` alerts titled `Untrusted device usage blocked`.
- Simulator usage responses include `blocked_devices` and `policy_alerts_created`.

Completed Step 46K:
- Duplicate/volume control was added for simulator untrusted-device policy alerts.
- Repeated simulator runs do not spam duplicate `policy_failed` alerts for the same user/subscription/device when an unread or recent alert already exists.

Networking/report note:
- PulseFi currently implements logical provisioning and simulator-backed network enforcement.
- Real router provisioning is a future production integration layer through MikroTik RouterOS API, RADIUS/PPPoE, TR-069/USP, ISP APIs/webhooks, or a secure local router agent.
- Real ISP database/API synchronization is also a future production integration layer.
- The current deployed prototype uses PulseFi's own PostgreSQL database and simulator ingestion to prove the workflow.

Known later mobile improvement:
- App User mobile selected-router context still needs a dedicated mobile cleanup pass.
- Usage endpoints already support `router_id`, but the mobile app must consistently pass the selected router.
- App User alerts need router-aware filtering later so selected-router alert views do not remain user-wide.

### Step 47 completion note - Deployed email and admin resend UX

Status: complete and live-tested.

What changed:
- Invitations are working through deployed email delivery.
- Password reset email/link flow has been tested from the admin web.
- Admin login MFA now supports sending/resending email verification codes.
- Admin Settings MFA actions now support resending email verification codes.
- Backup-code regeneration verification now supports resending email verification codes.
- Account identity/profile verification now supports resending email verification codes.
- Password reset remains link-based, not numeric-code based, and the admin UI now says `Send another reset email` after a reset email is sent.

Email provider note:
- The deployed email provider is Brevo.
- Do not commit Brevo API keys or any Render/Vercel/Neon secrets.
- Production must keep DEBUG=False so dev-only reset URLs and email codes are not exposed.

Next step:
- Start mobile auth/router-context improvement.
- Mobile needs Forgot Password / Reset Password UX.
- Mobile selected-router context must consistently drive Home, Usage, Devices, Alerts, Plan/Insights.
- App User alerts may need backend/router_id filtering if the mobile alert view should become selected-router specific.

### Step 48 mobile auth polish note

Status: Step 48B/48C complete and pushed.

Completed:
- Mobile App User login screen now has Forgot Password.
- Mobile forgot-password requests call `/auth/password/forgot` with `account_type=app_user`.
- Mobile forgot-password supports sending another reset email after success.
- Mobile login MFA supports resending email verification codes.
- Mobile Profile/Settings MFA flows support resending email verification codes for:
  - enabling Email MFA,
  - disabling MFA with email verification,
  - regenerating backup codes with email verification.
- The shared deployed reset-password web page is now account-neutral after successful reset.
- Reset success no longer redirects to admin login.
- The success prompt tells the user to return to PulseFi and log in with the new credentials.

Security notes:
- Password reset remains link-based, not numeric-code based.
- Mobile does not expose reset tokens or dev reset URLs.
- Production must keep `DEBUG=False`.

Next:
- Step 49 selected-router context cleanup.
- Selected router must consistently control Home, Usage, Devices, Alerts, Plan/Insights.
- App User alerts may need backend `router_id` filtering if selected-router alert views should be precise.

### Step 49 mobile selected-router correctness

Status: Step 49 complete and smoke-tested.

Completed:
- Mobile selected-router context now drives Home, Usage, Devices, and Alerts.
- Duplicate router names are disambiguated with router ID prefixes.
- More opens on Routers first instead of Plans/Subscriptions.
- Usage screen now has a circular/donut usage graph.
- Usage fetches selected-router summary and records using `router_id`.
- Devices fetch selected-router devices and device-usage using `router_id`.
- App User alerts now support selected-router filtering through backend `router_id`.
- Backend alert filtering verifies router ownership through `Router.user_subscription_id -> UserSubscription.user_id`.
- Mobile Alerts no longer shows internal server error after the backend ownership fix.
- Full smoke test passed with two routers having the same display name but different usage totals.

Security/data correctness notes:
- Router IDs are never trusted alone.
- Backend verifies router ownership before returning router-scoped alerts.
- Selected-router data must remain consistent before ML/prediction upgrades.

Next:
- Mobile navigation restructure / More cleanup.
- Move important screens out of More where appropriate.
- Then continue chatbot, UI polish, live smoke test, push notifications, ML/data pipeline, and final report alignment.

### Step 50A ISP Admin router creation UX cleanup

Status: Step 50A complete and pushed.

Completed:
- ISP Admin Router Management no longer shows the confusing `New service line` / `Existing service line` choice.
- Router creation now follows the actual PulseFi workflow:
  - select App User,
  - select package/plan,
  - enter subscription label/start date,
  - enter router details,
  - PulseFi creates the linked subscription automatically,
  - router is linked to that subscription.
- MAC address is now required in the router form.
- API endpoint and router username remain optional fields for future real-router/API integration.
- Advanced helper text was removed to keep the form cleaner.
- User-facing wording now favors `assigned subscription` / `package` instead of `service line` where possible.

Reason:
- ISP Admin currently does not have a separate subscription creation workflow, so `Existing service line` was confusing and not useful for the current product/demo flow.
- The UI now matches the real FYP workflow more clearly.

Next:
- Step 50B mobile navigation restructure / More cleanup.
- Make the mobile app more user-friendly before chatbot, push notifications, ML, and final report alignment.

### Step 50D daily usage handoff

Status: Step 50D is in progress, not complete.

Confirmed completed before this handoff:
- Step 49 selected-router correctness was smoke-tested:
  - Home, Usage, Devices, and Alerts follow the selected router.
  - Duplicate router names are disambiguated with router ID prefix.
  - Usage has a circular/donut graph.
  - Alerts are router-scoped through backend router ownership filtering.
- Step 50A ISP Admin router creation UX cleanup was completed and pushed:
  - Removed confusing `New service line` / `Existing service line` create flow.
  - Router creation now follows the real demo workflow: select App User, select package/plan, enter subscription label/start date, enter router details.
  - PulseFi creates a linked subscription automatically for the router.
  - MAC address is required.
  - API endpoint and router username remain optional future router-integration fields.
  - Advanced router integration helper text was removed.

Current Step 50D goal:
- Add Daily Usage views before ML work.
- App User mobile should show daily usage for the selected router.
- ISP Admin web should later show daily usage by selected App User/router.
- Daily usage should be a real feature, not future work.

Backend Step 50D1:
- App User daily usage endpoint was started:
  - intended endpoint: `GET /api/v1/me/usage/daily?router_id=<router-id>&days=7`
  - intended response: one row per usage day with upload/download/total/record count.
- In the next chat, verify whether this backend patch was committed/pushed by checking git status/log.
- If it is not committed, complete backend daily endpoint first.

Mobile Step 50D2 problem:
- Mobile daily usage/device-breakdown patch caused JSX/TypeScript errors in `src/screens/UsageScreen.tsx`.
- The last known TypeScript errors were around broken JSX parent/fragment/closing tags.
- Do not continue adding features until `UsageScreen.tsx` is repaired.
- Safer next-chat approach:
  1. Inspect current `src/screens/UsageScreen.tsx`.
  2. Either revert only the broken patch or replace the screen with a clean version.
  3. Preserve existing working features:
     - selected-router usage summary,
     - circular usage graph,
     - download/upload totals,
     - latest records,
     - router ID prefix display.
  4. Re-add daily usage carefully in a smaller patch.
  5. Limit Latest Records to 10 initially with a `Show 10 more records` button to avoid endless scrolling.
  6. Add device download/upload breakdown only after the screen compiles.

Important feature decisions:
- True live usage updates are future/advanced work.
- Current demo-friendly behavior should be:
  - refresh when Home/Usage opens,
  - pull-to-refresh,
  - optional polling while the Usage screen is focused.
- True live telemetry requires continuous router/CPE/ISP ingestion plus WebSocket/SSE or another streaming mechanism.

Next required order:
1. Repair mobile `UsageScreen.tsx` JSX and make `npx.cmd tsc --noEmit` pass.
2. Verify/commit backend daily usage endpoint if not already committed.
3. Add mobile Daily Usage card safely.
4. Add record pagination/limit so Latest Records does not scroll endlessly.
5. Then add ISP Admin daily usage view.
6. Only after daily usage is stable, continue mobile UX polish, chatbot, push notifications, ML/data pipeline, and final report alignment.

Commands for next chat:
- Mobile:
  - `cd C:\PulseFi\pulsefi-mobile-app`
  - `git status`
  - `npx.cmd tsc --noEmit`
  - inspect `src/screens/UsageScreen.tsx`
- Backend:
  - `cd C:\PulseFi\backend`
  - `git status`
  - `git log --oneline -5`
  - verify whether Step 50D1 backend daily endpoint is committed.


- Full live smoke testing is intentionally deferred until the remaining project steps are finished; do not mark Step 50 fully complete until the final live smoke pass is done.

- Step 50H mobile usage cleanup is complete: Home no longer fails completely when usage summary fails, Usage now has a cleaner Monthly/Daily layout, Refresh labels were simplified, Official and Estimated totals are shown separately, and the user can choose which source the main usage graph displays.

- Step 50I mobile Insights cleanup is complete: Predictions and Recommendations are split into tabs, each list uses page controls like records/logs, and older user-facing insights are hidden from the mobile UI while remaining in backend/admin data.

- Step 50J admin Network Activity pagination is complete: ISP Admin Network tables now paginate Daily Usage by User, Recent Usage Records, Device Connection Logs, and Router Action Logs with compact table controls instead of long scrolling lists.

