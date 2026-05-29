<!-- STEP_54C_ALIGNMENT_CHECKPOINT_START -->
## Step 54C Report/Demo + Final Smoke Prep Checkpoint (2026-05-29)

Status: Complete for documentation/checklist scope.

Completed:

- Step 53A Real ML MVP is complete and pushed.
- Step 53A documentation formatting hotfix is complete and pushed.
- Step 53C dedicated ML MVP documentation is complete and pushed:
  - docs/ML_MVP.md
- Step 54A report/demo alignment guide is complete and pushed:
  - docs/REPORT_DEMO_ALIGNMENT.md
- Step 54B final live smoke checklist prep is complete and pushed:
  - docs/FINAL_LIVE_SMOKE_CHECKLIST.md

Current ML status:

- PulseFi now includes a real reproducible offline ML MVP for next-day usage prediction.
- The ML MVP uses deterministic PulseFi-style generated demo usage data.
- The ML model target is next-day usage in GB.
- Evaluation metrics are MAE and RMSE.
- Generated ML artifacts remain local-only and gitignored.
- The deployed backend does not depend on ML artifacts.
- Existing rules-based intelligence remains the safe deployed fallback.

Current report/demo status:

- Report and presentation claims should now follow docs/REPORT_DEMO_ALIGNMENT.md.
- ML explanation should follow docs/ML_MVP.md.
- Final deployed smoke should follow docs/FINAL_LIVE_SMOKE_CHECKLIST.md when it is time to execute it.

Still deferred / future work:

- Final full live smoke is still deferred.
- Push notifications remain future work.
- Production ML runtime integration remains future work unless explicitly selected.
- Router password storage remains deferred until encrypted credential storage exists.
- Do not expose secrets, .env values, database URLs, API keys, JWT secrets, Render/Vercel/Neon/Brevo secrets, or MFA codes.

Recommended next step:

- Step 54D should be a final pre-smoke repo cleanliness check across backend, admin web, and mobile.
- Do not run full final live smoke until explicitly starting the final smoke phase.
<!-- STEP_54C_ALIGNMENT_CHECKPOINT_END -->

<!-- STEP_53A_REAL_ML_MVP_START -->
## Step 53A Real ML MVP - Offline Usage Prediction Pipeline (2026-05-29)

Status: Complete for the safe offline/demo ML scope.

What was added:

- Added a reproducible PulseFi offline ML pipeline for next-day usage prediction.
- Added reusable ML helpers under app/ml/:
  - usage_features.py
  - usage_metrics.py
  - usage_model.py
- Added reproducible scripts under scripts/ml/:
  - generate_demo_usage_dataset.py
  - train_usage_prediction_model.py
  - evaluate_usage_prediction_model.py
- Added deterministic ML tests under tests/ml/.
- Added artifacts/ml/.gitkeep and gitignored generated ML artifacts.
- Kept generated datasets, model files, metrics, and evaluations out of Git.

Dataset:

- Source: deterministic generated PulseFi-style demo usage records.
- Dataset rows: 896
- Demo service lines: 8
- Date range: 2026-01-08 to 2026-04-29
- Target: target_next_day_usage_gb, meaning next-day usage in GB.

Features:

- plan_monthly_limit_gb
- plan_speed_mbps
- device_count
- day_of_week
- is_weekend
- previous_day_usage_gb
- rolling_3_day_avg_gb
- rolling_7_day_avg_gb
- month_progress_ratio
- current_day_usage_gb

Model:

- Type: normalized_linear_regression_gradient_descent
- The model is trained from supervised historical usage rows.
- The model is saved as JSON, not pickle, to keep the artifact readable and safer for demo use.

Evaluation:

- Train rows: 716
- Test rows: 180
- MAE: 0.7203 GB
- RMSE: 1.302 GB

Architecture decision:

- This is intentionally an offline/demo ML MVP for the project report and demo.
- It does not require .env, secrets, live database access, Render, Vercel, Neon, or Brevo.
- It does not change production runtime behavior.
- Existing backend rules-based intelligence remains the safe deployed fallback.
- Backend integration can be considered later only if it is optional, artifact-safe, and falls back cleanly.

Limitations:

- The current dataset is generated demo data, not real ISP production data.
- The model proves a real reproducible ML workflow, but real-world accuracy would require real historical usage records.
- Future improvements can train on exported anonymized PulseFi usage records, compare multiple model types, and optionally connect the best model to backend intelligence behind a safe fallback.

Verification commands used:

- python -m compileall app tests scripts
- python -m pytest tests/ml
- python scripts/ml/generate_demo_usage_dataset.py
- python scripts/ml/train_usage_prediction_model.py
- python scripts/ml/evaluate_usage_prediction_model.py
- python -m pytest
- git diff --check

Still deferred:

- Final full live smoke remains deferred.
- Push notifications remain future work.
- No production ML runtime integration was added in Step 53A.
<!-- STEP_53A_REAL_ML_MVP_END -->

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
- Step 52 Assistant quality pass is complete for current mobile scope.
- Step 52B Assistant polish pass is complete; the Assistant remains local/contextual and not external LLM-backed.
- ML/data pipeline is still not real ML yet.
- Push notifications are still not implemented.
- Full final deployed mobile smoke test remains intentionally deferred.
- Final report/presentation alignment is still pending.

Step 52 Assistant quality pass is now marked complete for the focused mobile scope.
Keep final full live smoke deferred.
Focused Expo checks are allowed after this mobile fix.
<!-- STEP_50P_REMAINING_STATUS_AND_MOBILE_FIXES_END -->


<!-- STEP_52_ASSISTANT_QUALITY_PASS_START -->
## Step 52 PulseFi Assistant Quality Pass (2026-05-28)

Status: Corrected and complete for chatbot-style mobile MVP.

Completed mobile assistant quality pass:

- Corrected the Step 52 UX from contextual helper cards into a chatbot-style Assistant screen.
- Added a local contextual PulseFi Assistant response engine in the mobile app.
- Assistant now has a welcome message, chat history, user/assistant message bubbles, typed input, send button, and suggested question chips.
- Suggested chips send questions into the chat instead of only switching static cards.
- Home now has a visible Assistant entry that opens the chatbot with an initial question.
- More still has a dedicated PulseFi Assistant entry.
- Insights now has assistant help actions near predictions and recommendations that open the chatbot with contextual questions:
  - `What does this prediction mean?`
  - `Why am I getting this recommendation?`
  - `Should I upgrade?`
  - `Should I downgrade?`
- Assistant answers use loaded App User context where available:
  - selected router
  - selected service line/subscription
  - official and estimated usage totals
  - current package/plan details
  - connected devices and device usage
  - alerts
  - predictions
  - recommendations
  - recent service requests
- Assistant answers explain why they are saying something, give next steps, and clearly call out missing/unavailable data.
- The implementation remains a local/contextual chatbot MVP and does not call an external AI/LLM.
- Future LLM integration must go through a backend endpoint/proxy; never put OpenAI/LLM/API keys in the mobile app.
- No backend API change, schema change, environment change, or secret change was made.
- Existing recommendation request behavior remains intact:
  - direct target-plan recommendations can still create requests
  - older upgrade/downgrade recommendations without a target plan still route users to Service requests
  - stay/current/no-change recommendations do not show request actions

Verification:

- Mobile TypeScript check passed:
  - `npx.cmd tsc --noEmit`
- Mobile whitespace check passed:
  - `git diff --check`

Still deferred / pending:

- Full final live smoke remains deferred.
- Push notifications remain future work.
- Step 53 Real ML MVP remains next.
- ML/data-pipeline explanation remains next/pending as part of Step 53/report alignment.
- No backend API/schema migration was needed.
<!-- STEP_52_ASSISTANT_QUALITY_PASS_END -->

<!-- STEP_52B_ASSISTANT_POLISH_PASS_START -->
## Step 52B PulseFi Assistant Polish Pass (2026-05-28)

Status: Complete for the mobile local/contextual chatbot MVP.

Completed mobile assistant polish:

- Insights assistant help now passes structured launch context for the exact prediction or recommendation card the App User tapped, without showing raw IDs in the UI.
- The Assistant resolves that exact selected-service-line item from loaded context; if it cannot find it after refresh, it says so and falls back to the latest relevant item.
- Typed question intent detection now uses weighted scoring instead of first-match keywords, so prediction-risk, usage-high, plan-decision, device, alert, and service-request questions route more accurately.
- Assistant context now tracks source status as loaded, empty, or failed for routers, subscriptions, usage, devices, alerts, predictions, recommendations, service requests, plans, and router capabilities.
- Assistant answers can now explain failed refreshes separately from loaded-but-empty data, without exposing raw HTTP errors or internal details.
- Chat now adds the user bubble immediately, shows a short "checking your router context" assistant typing state, prevents duplicate sends while processing, and then adds the assistant response.
- Assistant response bubbles now include contextual action chips such as Open Usage, Open Insights, Open Devices, Open Alerts, and Open Service requests when those navigation targets are available.
- Suggested prompts were polished to natural App User questions and kept compact for mobile screens.
- Existing recommendation request behavior remains separate and intact: stay/current/no-change recommendations do not show request actions, and actionable upgrade/downgrade recommendations still use the existing Insights request flow.

Validation:

- Mobile `npx.cmd tsc --noEmit` passed.
- Mobile `git diff --check` passed with only Git CRLF normalization warnings.
- Mobile changes were committed and pushed to `MadaraPDL/pulsefi-mobile-app` main as `09230f0` (`Polish PulseFi assistant chat experience`).
- Focused Expo/manual mobile checking remains allowed, but final full live smoke remains deferred.

Architecture / safety:

- Assistant remains a local/contextual chatbot MVP using existing App User APIs and local response logic.
- No external AI/LLM call and no OpenAI/LLM/API key was added to the mobile app.
- Future LLM integration must go through a backend endpoint/proxy, never direct client-side keys.
- No backend API, schema, environment, or secret change was made.
- No admin web change was made.
- Step 53 Real ML MVP remains next.
<!-- STEP_52B_ASSISTANT_POLISH_PASS_END -->


<!-- PULSEFI_ASSISTANT_REQUIREMENTS_START -->
## PulseFi Assistant Requirements / Step 52 Quality Pass (2026-05-28)

Status: Corrected complete as chatbot-style mobile MVP after Step 52.

The PulseFi Assistant direction was corrected in Step 52 so the mobile assistant feels like a contextual chatbot instead of helper cards or a simple rules bot.

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
- Later, it can evolve into a real LLM-backed assistant only through a backend endpoint/proxy; never put LLM/API keys in the mobile client.

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
2. Step 52 Assistant quality pass is now complete for current mobile scope.
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

1. Step 52 Assistant quality pass is now complete for current mobile scope.
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
- Step 46I ISP Admin selected-user Monitoring alerts is complete and live-tested: Monitoring now requires selecting an App User before alert details are shown, only high-usage and plan-limit alerts are shown (`high_usage` and `plan_exceed_risk`), Users no longer owns this alert workflow, the alert list is scroll-contained, ISP Admin login defaults to Overview, and admin session restore no longer clears valid tokens on temporary backend/network failures.
- Step 46J device trust enforcement is complete and tested: simulator usage records are created only for trusted connected devices, untrusted connected devices are blocked from simulator usage, and each blocked untrusted device creates a `policy_failed` alert.
- Step 50D App User mobile Daily Usage is complete and verified: backend exposes daily usage for App Users, Home and Usage totals now use the same selected-router summary source, Daily Usage is visible on mobile, Latest Records starts at 5 rows with Show 5 more, and device download/upload breakdown remains available.
- Step 50E demo usage clarity is complete: ISP Admin Daily Usage by User now shows usage kind as Official/Service total vs Estimated/Device estimate, includes All/Official/Estimated filters, and future simulator usage creates an official service total row plus estimated per-device rows for cleaner presentation data.
- Step 50F mobile UX polish is complete: mobile Home and Usage now have explicit retry refresh actions and clearer selected-router/demo usage guidance; no backend API/schema changes were made.
- Step 50G PulseFi Assistant mobile MVP is complete: More now includes a rules-based assistant that uses existing mobile data for quick usage, package-limit, alert, Official-vs-Estimated, and next-action explanations; no external AI/backend assistant service was added.

<!-- PULSEFI_SYNC_START -->
## Current Synchronized PulseFi Checkpoint - 2026-05-24

Current phase: **Step 52B Assistant polish pass complete - PulseFi Assistant remains a local/contextual chatbot-style mobile MVP with targeted Insights explanations, weighted typed-question routing, source load-status notes, typing state, and contextual action chips; Step 53 Real ML MVP remains next; report/demo alignment follows; push notifications and final full live smoke remain deferred.**

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
- Step 43D final full smoke test remains postponed until backend, admin web, email, and mobile are all ready.
<!-- PULSEFI_SYNC_END -->

# AGENTS.md - PulseFi Backend Instructions

## Project Name

PulseFi

## Main Rule for Codex / AI Coding Assistants

Before editing anything, read this file, `README.md`, and `ROADMAP.md`.

Do not make random architecture decisions without checking the existing project structure.

This backend is being built step by step by the student/developer, so changes should stay understandable, modular, and easy to explain.

---

## Current Backend Position


Recently completed and tested:

- Step 14: Protected current-account route system.
- Step 15: Platform Admin MVP endpoints.
- Step 16: ISP Admin MVP endpoints.
- Step 17: App User/mobile MVP endpoints.
- Step 18: Router adapter and simulator foundation.
- Step 19: Usage ingestion and simulator demo data flow.
- Step 20: Alerts system.
- Step 21: Predictions and recommendations.
- Step 22: Recommendation to plan change request integration and ISP Admin review.
- Step 23: ISP Admin analytics and reports.
- Step 24: Backend/demo readiness, API contract snapshot, demo seed helper, and review package.
- Step 25A: Migration integrity hardening.
- Step 25B: Standard API error response foundation.
- Step 25C: Auth-sensitive rate limits tightened to 5 attempts per 15 minutes.
- Step 25D: API contract refreshed for standard errors and rate limits.
- Step 25E: Final docs/status alignment.
- Step 26A-E: Codex P1 backend fixes.
- Step 26F: Remaining P2/P3 quality hardening before frontend integration.

Current next backend work:

- Start frontend integration after final validation.
- Keep backend changes limited to discovered blockers, contract fixes, and small safety corrections.
- Do not start large new backend feature expansions until frontend integration confirms the API needs.

Important active rules:

- ISP Admin endpoints must use get_current_isp_admin.
- Every ISP Admin query must be scoped by current_admin.isp_id.
- App User /me endpoints must use get_current_app_user and must not accept arbitrary target user IDs.
- Router credentials must not be accepted or stored until encrypted credential storage is intentionally implemented.
- Router capability responses must clearly show simulator/demo mode while the simulator adapter is used.
- Auth rate limiting is in-memory MVP protection; use a shared store before production multi-worker deployment.
- Keep files modular and avoid large mixed-responsibility files.

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

Start frontend integration for:

- Platform Admin web dashboard.
- ISP Admin web dashboard.
- App User mobile app.

Backend rule during frontend integration:

- Keep fixes small and scoped.
- Update `docs/API_CONTRACT.md` when endpoint behavior or response shape changes.
- Do not add large new backend features unless frontend integration proves they are required.

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

---

## Backend Quality State - 2026-05-14

The backend has a limited PostgreSQL app role and an Alembic baseline.

Current completed quality work:

- `pulsefi_app` PostgreSQL role exists for backend runtime DB access.
- Local `.env` should use `pulsefi_app`, not `postgres`.
- Alembic is initialized.
- Alembic reads the database URL from `app.core.config.settings.DATABASE_URL`.
- Alembic imports `Base.metadata` from `app.db.base`.
- Alembic imports `app.models` so all SQLAlchemy models are registered.
- Existing DB schema was baselined with revision `c384b4d102bc`.
- Current DB was stamped to Alembic head.
- Existing PulseFi tables/data were not recreated or changed.

Important migration rule:

- Do not autogenerate or apply migrations carelessly.
- The current baseline migration is intentionally empty because the database already existed before Alembic.
- Future database schema changes should be created as Alembic migrations after checking the real DB/models carefully.

Important DB permission reminder:

- `pulsefi_app` was granted enough permission for local development and Alembic setup, including creating the Alembic tracking table.
- Before production deployment, revisit and harden permissions.
- Prefer a separate migration/admin role for Alembic and a more restricted runtime app role for FastAPI.
- Do not leave unnecessary schema creation permissions on the normal app role in production without reviewing the risk.

Next recommended quality work:

1. Add `pytest` and `httpx` tests.
2. Add GitHub Actions CI.
3. Add structured logging.
4. Standardize API error responses.
5. Add safe seed/demo data.
6. Add deployment documentation.
7. Continue Step 16 only through `get_current_isp_admin` and always filter by `current_admin.isp_id`.

---

## Milestone Completion Log

Known completed milestones:

- 2026-05-10 - PostgreSQL database schema phase completed for the main PulseFi tables.
- 2026-05-10 - Core SQLAlchemy models completed and import-tested.
- 2026-05-11 - Authentication database update completed.
- 2026-05-11 - Authentication SQLAlchemy models completed and import-tested.
- 2026-05-11 - Authentication schemas completed.
- 2026-05-12 - Authentication services split into focused modules and import-tested.
- 2026-05-12 - Authentication endpoint package completed and Swagger/OpenAPI confirmed working.
- 2026-05-12 - Step 14 protected current-account route system completed.
- 2026-05-12 - Step 15 Platform Admin endpoint work completed through ISP/Admin management and summary features.
- 2026-05-13 - Backend foundation hardened for Step 16, including safer `.env.example`, production config validation, old-JWT invalidation after password reset, `get_current_isp_admin`, typo fixes, and `pyotp`.
- 2026-05-14 - Documentation cleanup completed for `README.md`, `ROADMAP.md`, and `AGENTS.md`.
- 2026-05-14 - Backend quality backlog added.
- 2026-05-14 - Limited PostgreSQL role `pulsefi_app` created and tested.
- 2026-05-14 - Alembic initialized, empty baseline migration created, and existing database stamped to revision `c384b4d102bc`.

Notes:

- Some earlier dates are "completed by this date" based on the project work log, not exact minute-by-minute timestamps.
- Future completed steps should be added here immediately after testing and before commit.

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

## Step 16 Progress - 2026-05-14

### Step 16A - ISP Admin Router Foundation

Completed:

- Created ISP Admin endpoint package under `app/api/v1/endpoints/isp_admin/`.
- Added ISP Admin router prefix: `/api/v1/isp-admin`.
- Added Swagger tag: `ISP Admin`.
- Added protected starter endpoint: `GET /api/v1/isp-admin/summary`.
- Connected ISP Admin router to the main API v1 router.
- Confirmed `get_current_isp_admin` is used by the starter summary endpoint.
- Import checks passed.
- Pytest passed.
- Compile check passed.

Current behavior:

- The starter summary endpoint is protected by the ISP Admin guard.
- It returns the authenticated ISP Admin ID and ISP ID.
- It does not change database data.

Next Step 16 work:

- Replace/expand the temporary summary endpoint with real ISP-scoped counts later.
- Continue with ISP Admin App User invitation and management endpoints.
- Every Step 16 query must filter by `current_admin.isp_id`.

---

## Step 16 Progress - 2026-05-14

### Step 16B - ISP Admin App User Invitation Endpoints

Completed:

- Added ISP Admin schemas under `app/schemas/isp_admin/`.
- Added App User invitation request/response schemas.
- Added ISP Admin services under `app/services/isp_admin/`.
- Added service logic for creating, listing, finding, and revoking App User invitations.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/user_invitations.py`.
- Added endpoints:
  - `POST /api/v1/isp-admin/user-invitations`
  - `GET /api/v1/isp-admin/user-invitations`
  - `PATCH /api/v1/isp-admin/user-invitations/{invitation_id}/revoke`
- Connected user invitation endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- All invitation queries are scoped by `current_admin.isp_id`.
- Development invitation token is returned only while `DEBUG=True`.
- Import checks passed.
- Pytest passed.
- Compile check passed.

Impact:

- Database schema: no change.
- Existing data: no change unless the new endpoints are called.
- SE diagrams: later update ISP Admin use cases/activity flow to include App User invitation flow.

Next Step 16 work:

- Test App User invitation endpoints through Swagger/Postman.
- Then add ISP Admin App User listing/detail/update endpoints.

---

## Step 16 Testing Progress - 2026-05-14

### Step 16B - App User Invitation Endpoints Tested

Tested successfully:

- ISP Admin login worked after password reset.
- `GET /api/v1/isp-admin/summary` confirmed the account is a valid ISP Admin.
- `POST /api/v1/isp-admin/user-invitations` created an App User invitation.
- Created invitation was correctly scoped to the ISP Admin's `isp_id`.
- Created invitation used `account_type = app_user`.
- Created invitation stored `invited_by_admin_id` as the logged-in ISP Admin.
- `GET /api/v1/isp-admin/user-invitations?status=pending` listed the pending invitation.
- Duplicate pending invitation test prevented duplicate active invitations.
- `PATCH /api/v1/isp-admin/user-invitations/{invitation_id}/revoke` revoked the invitation.
- Second revoke attempt was rejected.
- Pending list after revoke returned empty.
- Revoked list showed the revoked invitation.

Impact:

- Database schema: no change.
- Existing data: only local test invitation/reset data changed.
- SE diagrams: later update ISP Admin use cases/activity flow to include App User invitation management.
- Security: Step 16B confirmed ISP Admin invitation actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin App User listing/detail/update endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress - 2026-05-14

### Step 16C - ISP Admin App User Management Endpoints

Completed and tested:

- Added ISP Admin App User management schemas.
- Added ISP Admin App User management service logic.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/users.py`.
- Added endpoints:
  - `GET /api/v1/isp-admin/users`
  - `GET /api/v1/isp-admin/users/{user_id}`
  - `PATCH /api/v1/isp-admin/users/{user_id}`
- Connected App User management endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- All App User queries are scoped by `current_admin.isp_id`.
- Tested creating a fresh App User through the invitation acceptance flow.
- Tested listing App Users under the ISP Admin's ISP.
- Tested viewing one App User by ID.
- Tested updating allowed App User fields.
- Tested reactivating the test user.

Allowed update fields in initial Step 16C:

- `full_name`
- `phone_number`
- `status`

Deferred update fields:

- `email`
- `username`

Reason email and username updates are deferred:

- Email and username are login identifiers.
- Updating them requires extra case-insensitive uniqueness checks.
- Email changes may require a new email-verification flow.
- Username changes require strict format validation and duplicate prevention.
- These changes affect login, password reset, email verification, notifications, and account recovery.

Impact:

- Database schema: no change.
- Existing data: only local test invitation/App User data changed during testing.
- SE diagrams: later update ISP Admin use cases/activity flow to include App User management.
- Security: Step 16C confirms App User management actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin subscription plan management endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress - 2026-05-14

### Step 16D - ISP Admin Subscription Plan Management Endpoints

Completed and tested:

- Added ISP Admin subscription plan schemas.
- Added ISP Admin subscription plan service logic.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/plans.py`.
- Added endpoints:
  - `POST /api/v1/isp-admin/plans`
  - `GET /api/v1/isp-admin/plans`
  - `GET /api/v1/isp-admin/plans/{plan_id}`
  - `PATCH /api/v1/isp-admin/plans/{plan_id}`
- Connected subscription plan endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- All subscription plan queries are scoped by `current_admin.isp_id`.
- Tested creating a subscription plan.
- Tested duplicate plan-name prevention inside the same ISP.
- Tested listing subscription plans.
- Tested viewing one subscription plan by ID.
- Tested updating plan fields.
- Tested filtering active plans with `is_active=true`.
- Tested deactivating and reactivating a plan.

Current allowed plan fields:

- `plan_name`
- `monthly_price`
- `data_limit_gb`
- `speed_limit_mbps`
- `description`
- `is_active`

Impact:

- Database schema: no change.
- Existing data: only local test subscription plan data changed during testing.
- SE diagrams: later update ISP Admin use cases/activity flow to include subscription plan management.
- Security: Step 16D confirms subscription plan actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin user subscription assignment/listing endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress - 2026-05-14

### Step 16E - ISP Admin User Subscription Assignment and Management Endpoints

Completed and tested:

- Added ISP Admin user subscription schemas.
- Added ISP Admin user subscription service logic.
- Added endpoint module: `app/api/v1/endpoints/isp_admin/subscriptions.py`.
- Added endpoints:
  - `POST /api/v1/isp-admin/subscriptions`
  - `GET /api/v1/isp-admin/subscriptions`
  - `GET /api/v1/isp-admin/subscriptions/{subscription_id}`
  - `PATCH /api/v1/isp-admin/subscriptions/{subscription_id}`
- Connected user subscription endpoints to the ISP Admin router.
- All endpoints use `get_current_isp_admin`.
- Subscription listing/detail/update is scoped through the linked App User's `isp_id`.
- Subscription assignment verifies both:
  - the App User belongs to `current_admin.isp_id`
  - the Subscription Plan belongs to `current_admin.isp_id`
- Tested listing App Users for the ISP.
- Tested listing active plans for the ISP.
- Tested assigning a subscription to an App User.
- Tested listing all subscriptions for the ISP.
- Tested filtering subscriptions by App User ID.
- Tested viewing one subscription by ID.
- Tested updating subscription label/status/auto-renew.
- Tested suspending a subscription with `status = suspended`.
- Tested reactivating the subscription with `status = active`.

Subscription status values:

- `pending` - assigned but not active yet
- `active` - currently active subscription
- `suspended` - temporarily stopped, such as unpaid bill/admin action
- `expired` - ended by date
- `cancelled` - permanently cancelled

Database migration:

- Added Alembic migration `285ab0474b39_allow_suspended_user_subscription_status.py`.
- Migration updates `chk_subscription_status` to allow `suspended`.
- Existing data was not changed by the migration.
- Local migration application required pgAdmin/admin execution because `pulsefi_app` is intentionally not the owner of `user_subscriptions`.
- This confirms the future production need for a separate migration/admin database role instead of using the runtime app role for schema changes.

Impact:

- Database schema: changed only the `user_subscriptions.status` check constraint.
- Existing data: only local test subscription data changed during endpoint testing.
- SE diagrams: later update ISP Admin use cases/activity flow to include subscription assignment and suspension/reactivation.
- Security: Step 16E confirms subscription actions are scoped by `current_admin.isp_id`.

Next Step 16 work:

- Add ISP Admin router management endpoints.
- Continue using `get_current_isp_admin`.
- Continue filtering all ISP Admin queries by `current_admin.isp_id`.

---

## Step 16 Progress - 2026-05-14

### Step 16F - ISP Admin Router Management Endpoints

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

## Current Backend State - 2026-05-14

Step 16A through Step 16F are complete and tested.

Completed Step 16 areas:

- Step 16A: ISP Admin protected router foundation and summary starter endpoint.
- Step 16B: ISP Admin App User invitation endpoints.
- Step 16C: ISP Admin App User management endpoints.
- Step 16D: ISP Admin subscription plan management endpoints.
- Step 16E: ISP Admin user subscription assignment and management endpoints.
- Step 16F: ISP Admin router management endpoints.

Current next step:

- Step 16G: ISP Admin dashboard/summary endpoint, or Step 16 final cleanup/testing.

Core rule remains:

- Every ISP Admin endpoint must use `get_current_isp_admin`.
- Every ISP Admin query must be scoped by `current_admin.isp_id`.

Important reminders:

- Do not update App User email/username casually; they affect login, verification, password reset, and uniqueness.
- Do not store router passwords until encrypted credential storage exists.
- Keep files modular and avoid large mixed-responsibility files.
- Future production DB setup should use a separate migration/admin role for Alembic and a restricted runtime role for FastAPI.

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

## Latest PulseFi Backend Note

Step 16G is complete:

- ISP Admin dashboard summary endpoint is implemented.
- Endpoint: `GET /api/v1/isp-admin/summary`
- Counts users, plans, subscriptions, and routers under `current_admin.isp_id`.
- Subscription counts must use the linked App User because `user_subscriptions` has no direct `isp_id`.
- Continue enforcing ISP Admin isolation in every Step 16 and Step 17 endpoint.


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

## Step 17 Progress - 2026-05-14

### Step 17A - App User Mobile Endpoint Foundation

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

## Step 17 Progress - 2026-05-14

### Step 17B - App User Subscription Endpoints

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

## Step 17 Progress - 2026-05-14

### Step 17C - App User Router and Device View Endpoints

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

- Step 17D - App User usage endpoints.
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

## Latest Completed App User Work

Step 17E is complete.

Completed endpoints:

- GET /api/v1/me/alerts
- GET /api/v1/me/alerts/{alert_id}
- PATCH /api/v1/me/alerts/{alert_id}/read

Rules confirmed:

- Use get_current_app_user.
- Scope alert queries by Alert.user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Do not expose sensitive auth fields.

Next likely Step 17 work:

- App User predictions/recommendations endpoints.
- Or App User subscription plan change request endpoints.

---

## Latest Completed App User Smart Feature Work

Step 17F is complete.

Completed endpoints:

- GET /api/v1/me/predictions
- GET /api/v1/me/predictions/{prediction_id}
- GET /api/v1/me/recommendations
- GET /api/v1/me/recommendations/{recommendation_id}

Rules confirmed:

- Use get_current_app_user.
- Scope prediction queries by Prediction.user_id = current_user.id.
- Scope recommendation queries by Recommendation.user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Do not expose sensitive auth fields.

Next likely Step 17 work:

- App User subscription plan change request endpoints.

---

## Latest Completed App User Subscription Management Work

Step 17G is complete.

Completed endpoints:

- POST /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests
- GET /api/v1/me/plan-change-requests/{request_id}

Rules confirmed:

- Use get_current_app_user.
- Scope plan change request queries by SubscriptionChangeRequest.user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Requested plan must differ from the current plan.
- Requested plan must belong to the same ISP.
- Validate recommendation ownership before linking.

Next likely Step 17 work:

- App User device policy endpoints.

---

## Latest Completed App User Device Control Work

Step 17H is complete.

Completed endpoints:

- POST /api/v1/me/device-policies
- GET /api/v1/me/device-policies
- GET /api/v1/me/device-policies/{policy_id}

Rules confirmed:

- Use get_current_app_user.
- Scope device policy queries by DeviceNetworkPolicy.requested_by_user_id = current_user.id.
- Do not accept user_id in App User /me routes.
- Validate device ownership before policy creation.
- Device policies remain pending until future router adapter execution.

Next backend work:

- Step 18 - Router adapter and simulator layer.

---

## Historical Current State Update - 2026-05-15

Historical backend position at that time: **Step 18 - Router adapter and simulator layer**.

Completed:
- Step 16 ISP Admin MVP endpoints are complete.
- Step 17 App User/mobile MVP endpoints are complete through device policy requests.
- Backend quality fixes are complete for MFA login enforcement, Alembic baseline migration, PostgreSQL CI migration checks, production email-token guards, and auth API regression tests.

Next backend step:
- Step 18: create the router adapter foundation and simulator adapter.

Step 18 rule:
- Do not connect to real routers yet.
- Do not store raw router passwords.
- Start with a simulator adapter so router behavior can be demoed safely and tested reliably.


## Step 20A Completed

Alert generation is now connected to simulator ingestion.

Completed alert types:

- `high_usage`
- `plan_exceed_risk`
- `unusual_consumption`
- `new_device_connected`

The `alerts.alert_type` check constraint was updated through Alembic to allow Step 20 alert types.

Important next rule:

- `policy_failed` is allowed by the database constraint but still needs generation logic from failed router/device policy execution.
- App User alert endpoints already exist and must stay scoped by `get_current_app_user`.
- ISP Admin alert visibility, if added, must be scoped by `current_admin.isp_id`.


## Step 20C Completed

ISP Admins now have read-only visibility into App User alerts under their ISP.

Important rules:

- ISP Admin alert queries must use `get_current_isp_admin`.
- Alert queries must be scoped by `current_admin.isp_id`.
- Current alerts belong to App Users.
- Do not treat current `alerts` rows as admin-owned notifications.
- Admin-owned notifications would require a future separate design.

Next recommended work:

- Add focused alert tests and ownership/isolation tests.


## Step 20D Completed

Focused alert generation tests were added.

Covered:

- `plan_exceed_risk`
- `policy_failed`
- duplicate unread `policy_failed` prevention

Next recommended work:

- App User alert ownership isolation tests.
- ISP Admin alert ISP isolation tests.
- New device and unusual consumption alert tests.


## Step 20E Completed

Alert ownership and ISP isolation tests were added.

Important rules:

- App User alert access must stay scoped by `current_user.id`.
- ISP Admin alert access must stay scoped by `current_admin.isp_id`.
- ISP Admin alert visibility is read-only and shows App User alerts, not admin-owned notifications.

Next recommended work:

- New device alert test.
- Unusual consumption alert test.
- Then close Step 20 and move to Step 21 prediction/recommendation logic.



## Step 21A Completed

Prediction foundation is complete.

Completed:

- Rule-based prediction generation service.
- ISP Admin prediction generation endpoint.
- Prediction rows stored in the existing `predictions` table.
- App User can view generated predictions through existing `/me/predictions` endpoints.

Important rules:

- ISP Admin prediction generation must remain scoped by `current_admin.isp_id`.
- App User prediction visibility must remain scoped by `current_user.id`.
- This is rule-based/statistical prediction for MVP, not full ML yet.

Next recommended work:

- Step 21B: Generate recommendations based on predictions and available plans.


## Step 21B Completed

Recommendation foundation is complete.

Completed:

- Rule-based recommendation generation service.
- ISP Admin recommendation generation endpoint.
- Recommendation rows stored in the existing `recommendations` table.
- App User can view generated recommendations through existing `/me/recommendations` endpoints.
- Recommendation type check constraint updated through Alembic/manual DB application if needed.

Important rules:

- ISP Admin recommendation generation must remain scoped by `current_admin.isp_id`.
- App User recommendation visibility must remain scoped by `current_user.id`.
- This is rule-based recommendation logic for MVP.
- Do not treat this as full ML yet.

Next recommended work:

- Step 21C: Prediction/recommendation tests and isolation tests.


## Step 21C Completed

Prediction and recommendation service tests were added.

Covered:

- Prediction generation math.
- `stay_current` recommendation generation.
- `upgrade_plan` recommendation generation.
- Duplicate new recommendation prevention.
- ISP-scoped recommendation generation query.
- App User prediction/recommendation ownership query filters.

Important rules:

- ISP Admin prediction/recommendation generation must remain scoped by `current_admin.isp_id`.
- App User prediction/recommendation visibility must remain scoped by `current_user.id`.

Next recommended work:

- Add downgrade/monitor recommendation tests if needed.
- Consider subscription change request integration from recommendation rows.


## Step 21D Completed

Recommendation cleanup tests were added.

Covered recommendation types:

- `upgrade_plan`
- `downgrade_plan`
- `stay_current`
- `monitor_usage`

Step 21 is complete enough to move forward.

Next recommended options:

- Connect recommendation rows to subscription change request flow.
- Or move to ISP Admin reporting/analytics/dashboard improvements.

Important rules remain:

- ISP Admin prediction/recommendation generation must stay scoped by `current_admin.isp_id`.
- App User prediction/recommendation visibility must stay scoped by `current_user.id`.



## Step 22 Planned

Next phase:

Recommendation to plan change request integration.

Planned work:

- Review existing App User plan change request flow.
- Add ISP Admin subscription change request visibility.
- Add ISP Admin approve/reject handling.
- Add tests and docs.

Important rules:

- App User requests must stay scoped by `current_user.id`.
- ISP Admin queries/actions must stay scoped by `current_admin.isp_id`.
- Recommendation-linked requests must verify ownership.


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




## Current Assistant/Codex Instructions ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â Frontend/Auth Handoff

When continuing PulseFi from this point:

1. Read these files first:
   - `PULSEFI_MEMORY.md`
   - `AGENTS.md`
   - `ROADMAP.md`
   - `README.md`
   - `BACKEND_QUALITY_BACKLOG.md`

2. Also inspect the frontend repo:
   - `C:\PulseFi\pulsefi-admin-web`
   - Current important files:
     - `src/App.tsx`
     - `src/App.real.tsx`
     - `src/api/adminAuth.ts`
     - `src/PulseFiDesignPreviewApp.tsx`
     - `src/PulseFiDesignHub.tsx`
     - `src/pulsefi-white-design.css`

3. Product structure rule:
   - There are only two admin roles:
     - Platform Admin
     - ISP Admin
   - App User is not an admin role.
   - Admin web app has one shared admin login page.
   - Role routing must come from backend-authenticated account data, not from a visible UI role switch.
   - App User UI belongs to the future React Native mobile app.

4. Preview mode rule:
   - `npm run dev` should run the real admin web app.
   - `npm run dev:design` should run the temporary UI/UX preview hub.
   - The preview hub must remain dev/design-only.
   - Do not expose App User/States/theme preview tabs in the production admin app.

5. Current auth issue:
   - Frontend now sends `account_type: "admin"` to `/api/v1/auth/login`.
   - Backend previously returned 422 because `account_type` was missing.
   - Backend now returns `429 rate_limited` after repeated attempts.
   - Fix the local-dev rate-limit blocker cleanly.
   - Verify `/auth/me` role mapping.
   - Complete the MFA-required frontend flow.

6. Safety/security rules:
   - Do not store or expose router passwords until encryption exists.
   - Keep all ISP Admin queries scoped by `current_admin.isp_id`.
   - Do not weaken production authentication/rate-limit behavior just to make local testing easier.
   - Prefer a dev-only reset/documented workaround for local rate-limit issues.

7. Required response style:
   - Give step-by-step commands.
   - Explain each changed code block.
   - Run checks before commit.
   - Update docs/memory after major changes.
   - Be honest about what is mocked, incomplete, or not yet backend-connected.
## Current PulseFi Implementation Notes

Current backend checkpoint:
- Automatic ISP intelligence run is implemented and pushed.
- Scheduler exists for local/demo use only and is disabled by default.
- Keep tests running with ENABLE_INTELLIGENCE_SCHEDULER=false.
- Do not allow automatic intelligence to create duplicate predictions/recommendations on repeated runs.
- Next cleanup target: convert FastAPI on_event startup/shutdown hooks to lifespan.

## Latest Working Notes - 2026-05-20 10:32

- When testing admin web or mobile on phone, run backend with --host 0.0.0.0 and use the PC LAN IP in frontend/mobile API URLs.
- Mobile app should use EXPO_PUBLIC_API_BASE_URL=http://<PC_LAN_IP>:8000/api/v1.
- Do not commit .env files containing local IPs or SMTP/secrets.
- Active mobile app folder is pulsefi-mobile-app, not the earlier locked pulsefi-mobile SDK 55 folder.

## Latest Working Notes - 2026-05-20 10:34

- When testing admin web or mobile on phone, run backend with --host 0.0.0.0 and use the PC LAN IP in frontend/mobile API URLs.
- Mobile app should use EXPO_PUBLIC_API_BASE_URL=http://<PC_LAN_IP>:8000/api/v1.
- Do not commit .env files containing local IPs or SMTP/secrets.
- Active mobile app folder is pulsefi-mobile-app, not the earlier locked pulsefi-mobile SDK 55 folder.

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

## 2026-05-28 - PulseFi Assistant/Codex Workflow Update

- For deployed PulseFi UI work, run local static checks/builds before pushing, but treat the live deployed admin/mobile URLs as the final UI QA target.
- Do not rely on localhost screenshots when the user explicitly says live deployment is the target.
- For Overview changes, improve existing panels first; do not add new sections unless the user explicitly requests them.
- For ISP Admin Router UI, preserve both actions: View and Run full simulator.
- For recommendation UI, do not show plan-change actions for stay/current/no-change recommendations.

<!-- PULSEFI_REAL_ML_REQUIRED_UPDATE_START -->
## Real ML MVP Instruction (2026-05-28)

When continuing PulseFi:
- Treat the real ML MVP as a required remaining project step, not only optional future work.
- Current intelligence is rules-based and should remain as fallback.
- Implement ML safely and reproducibly:
  - data preparation script,
  - training script,
  - evaluation metrics,
  - documented model inputs/outputs,
  - no secrets,
  - no paid external ML services.
- Prefer a small practical model over a large unstable model.
- Recommended first model: usage prediction from PulseFi-style historical usage data.
- Optional second model: plan exceed-risk or plan-risk classifier.
- Do not run the final full live smoke test until Assistant quality pass, ML MVP, and report/demo alignment are complete.
<!-- PULSEFI_REAL_ML_REQUIRED_UPDATE_END -->
