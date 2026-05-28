<!-- STEP_50P_REMAINING_STATUS_AND_MOBILE_FIXES_START -->
## Step 50P Remaining Status + Immediate Mobile Behavior Fixes (2026-05-28)

Status: Planned next coding step, not complete yet.

Overall remaining-step status:

- Mobile auth + account recovery: done for current scope.
  - Mobile MFA settings, email MFA resend, backup-code/email verification, and mobile password reset request flow are already complete.

- Mobile selected-router context cleanup: done for current scope.
  - Home, Usage, Devices, Alerts, Service Requests, and Insights already follow selected-router context for the current scope.

- Mobile UI/UX polish: done for current scope.
  - Shared mobile pagination exists.
  - Service Requests tabs exist.
  - Alerts, Routers, Subscriptions/My Package, Devices, Usage, and Insights were polished for the current scope.

- Mobile navigation restructure: partially done.
  - More/Service Requests/Insights/Usage flows were improved.
  - A full navigation redesign is not separately complete.

- Chatbot / AI Assistant: partially done.
  - A rules-based Assistant MVP exists.
  - Assistant quality pass is still needed because it should not feel like a static rules bot.

- ML/data pipeline + prediction upgrade: not fully done as real ML.
  - Current prediction/recommendation behavior is closer to rules/data-driven intelligence.
  - Final report/presentation must clearly explain current rules-based intelligence versus future real ML upgrade.

- Push notifications: not done.
  - In-app alerts exist.
  - Real push notifications are not implemented yet.

- Mobile deployed full smoke test: not done.
  - Full final live smoke remains intentionally deferred.

- Final report/presentation alignment: not done.
  - Needs final alignment after remaining app behavior fixes and Assistant quality pass.

Immediate Step 50P mobile bugs to fix before Assistant quality pass:

1. Home usage source should follow the Usage tab source selection.
   - Current problem: after simulator creates official rows, Home can show Official usage even when the user wants Estimated/device usage.
   - Required behavior:
     - If App User chooses Estimated in Usage, Home should show Estimated device total.
     - If App User chooses Official in Usage, Home should show Official service total.
   - Suggested implementation:
     - Add shared mobile app state/context for `official` vs `estimated` usage display source.
     - Usage screen should use that shared state instead of local-only `totalDisplaySource`.
     - Home screen should load both official and estimated usage summaries and render the shared selected source.
     - Home label should clearly say `Official service total` or `Estimated device total`.

2. Old upgrade/downgrade recommendations must be actionable.
   - Current problem: some older recommendations say upgrade/downgrade but show no button because they do not have `recommendation_plan_id`.
   - Required behavior:
     - If upgrade/downgrade recommendation has `recommendation_plan_id`, show direct action:
       - `Request this upgrade`
       - `Request this downgrade`
     - If upgrade/downgrade recommendation has no `recommendation_plan_id`, show:
       - `Open Service requests`
     - The fallback button should route the user to Service Requests so they can manually choose a plan.
   - Detection should consider recommendation type, recommendation text, and reason so older recommendations still become actionable when they clearly mention upgrade/downgrade.

Do these Step 50P fixes before starting the Assistant quality pass.

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
- Step 46I ISP Admin selected-user Monitoring alerts is complete and live-tested: Monitoring now requires selecting an App User before alert details are shown, only high-usage and plan-limit alerts are shown (`high_usage` and `plan_exceed_risk`), Users no longer owns this alert workflow, the alert list is scroll-contained, ISP Admin login defaults to Overview, and admin session restore no longer clears valid tokens on temporary backend/network failures.
- Step 46J device trust enforcement is complete and tested: simulator usage records are created only for trusted connected devices, untrusted connected devices are blocked from simulator usage, and each blocked untrusted device creates a `policy_failed` alert.

# PulseFi Backend API Contract

Generated at: `2026-05-18`

This file is a frontend integration snapshot generated from FastAPI OpenAPI.

Use it as the starting reference for:

- Platform Admin web dashboard
- ISP Admin web dashboard
- App User mobile app
- Shared authentication flows

Important:

- This file documents the current backend API shape.
- Authentication notes are frontend guidance, not a replacement for backend security checks.
- Before frontend implementation, confirm request/response details in Swagger if needed.

## Route Groups

## App User

| Method | Path | Frontend Area | Auth | Request Body | Responses | Summary |
|---|---|---|---|---|---|---|
| GET | `/api/v1/me/alerts` | Mobile App | App User JWT | `None` | 200, 422 | List My Alerts Endpoint |
| GET | `/api/v1/me/alerts/{alert_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Alert Endpoint |
| PATCH | `/api/v1/me/alerts/{alert_id}/read` | Mobile App | App User JWT | `None` | 200, 422 | Mark My Alert As Read Endpoint |
| GET | `/api/v1/me/device-policies` | Mobile App | App User JWT | `None` | 200, 422 | List My Device Policies Endpoint |
| POST | `/api/v1/me/device-policies` | Mobile App | App User JWT | `MyDevicePolicyCreate` | 201, 422 | Create My Device Policy Endpoint |
| GET | `/api/v1/me/device-policies/{policy_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Device Policy Endpoint |
| PATCH | `/api/v1/me/device-policies/{policy_id}/deactivate` | Mobile App | App User JWT | `None` | 200, 404, 422 | Deactivate My Device Policy Endpoint |
| PATCH | `/api/v1/me/device-policies/{policy_id}/execute` | Mobile App | App User JWT | `None` | 200, 422 | Execute My Device Policy Endpoint |
| GET | `/api/v1/me/devices` | Mobile App | App User JWT | `None` | 200, 422 | List My Devices Endpoint |
| GET | `/api/v1/me/devices/{device_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Device Endpoint |
| PATCH | `/api/v1/me/devices/{device_id}/trust` | Mobile App | App User JWT | `{"is_trusted": true/false}` | 200, 404, 422 | Update My Device Trust Endpoint |
| GET | `/api/v1/me/plan-change-requests` | Mobile App | App User JWT | `None` | 200, 422 | List My Plan Change Requests Endpoint |
| POST | `/api/v1/me/plan-change-requests` | Mobile App | App User JWT | `MyPlanChangeRequestCreate` | 201, 422 | Create My Plan Change Request Endpoint |
| GET | `/api/v1/me/plan-change-requests/{request_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Plan Change Request Endpoint |
| GET | `/api/v1/me/plans` | Mobile App | App User JWT | `None` | 200 | List My Available Plans Endpoint |
| GET | `/api/v1/me/predictions` | Mobile App | App User JWT | `None` | 200, 422 | List My Predictions Endpoint |
| GET | `/api/v1/me/predictions/{prediction_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Prediction Endpoint |
| GET | `/api/v1/me/recommendations` | Mobile App | App User JWT | `None` | 200, 422 | List My Recommendations Endpoint |
| GET | `/api/v1/me/recommendations/{recommendation_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Recommendation Endpoint |
| POST | `/api/v1/me/recommendations/{recommendation_id}/plan-change-request` | Mobile App | App User JWT | `MyRecommendationPlanChangeRequestCreate` | 201, 422 | Create Plan Change Request From Recommendation Endpoint |
| GET | `/api/v1/me/routers` | Mobile App | App User JWT | `None` | 200, 422 | List My Routers Endpoint |
| GET | `/api/v1/me/routers/{router_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Router Endpoint |
| GET | `/api/v1/me/routers/{router_id}/capabilities` | Mobile App | App User JWT | `None` | 200, 422 | Get My Router Capabilities Endpoint |
| GET | `/api/v1/me/subscriptions` | Mobile App | App User JWT | `None` | 200, 422 | List My Subscriptions Endpoint |
| GET | `/api/v1/me/subscriptions/{subscription_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Subscription Endpoint |
| GET | `/api/v1/me/summary` | Mobile App | App User JWT | `None` | 200 | Get My Summary Endpoint |
| GET | `/api/v1/me/usage/devices` | Mobile App | App User JWT | `None` | 200, 422 | List My Device Usage Endpoint |
| GET | `/api/v1/me/usage/devices/{device_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Device Usage Endpoint |
| GET | `/api/v1/me/usage/records` | Mobile App | App User JWT | `None` | 200, 422 | List My Usage Records Endpoint |
| GET | `/api/v1/me/usage/summary` | Mobile App | App User JWT | `None` | 200, 422 | Get My Usage Summary Endpoint |

## Auth

| Method | Path | Frontend Area | Auth | Request Body | Responses | Summary |
|---|---|---|---|---|---|---|
| POST | `/api/v1/auth/email/verify` | Shared Auth | Public or token-flow endpoint | `VerifyEmailRequest` | 200, 422, 429 | Verify Email |
| POST | `/api/v1/auth/invitations/accept` | Shared Auth | Public or token-flow endpoint | `AcceptInvitationRequest` | 201, 422, 429 | Accept Account Invitation |
| POST | `/api/v1/auth/login` | Shared Auth | Public or token-flow endpoint | `LoginRequest` | 200, 422, 429 | Login |
| GET | `/api/v1/auth/me` | Mobile App | App User JWT | `None` | 200 | Get Me |
| PATCH | `/api/v1/auth/me/identity` | Shared Auth | Current account JWT | `UpdateCurrentUserIdentityRequest` | 200, 401, 409, 422, 429 | Update current account email and username after MFA verification |
| POST | `/api/v1/auth/me/profile-update-challenge` | Shared Auth | Current account JWT | `None` | 200, 400, 422, 429 | Start MFA verification for account settings changes |
| POST | `/api/v1/auth/mfa/setup/confirm` | Shared Auth | Check endpoint dependency | `MFASetupConfirmRequest` | 200, 422, 429 | Confirm Mfa Setup |
| POST | `/api/v1/auth/mfa/verify` | Shared Auth | Public or token-flow endpoint | `MFAVerifyRequest` | 200, 422, 429 | Verify Mfa |
| POST | `/api/v1/auth/password/forgot` | Shared Auth | Public or token-flow endpoint | `ForgotPasswordRequest` | 200, 422, 429 | Forgot Password |
| POST | `/api/v1/auth/password/reset` | Shared Auth | Public or token-flow endpoint | `ResetPasswordRequest` | 200, 422, 429 | Reset Password |

## Health

| Method | Path | Frontend Area | Auth | Request Body | Responses | Summary |
|---|---|---|---|---|---|---|
| GET | `/api/v1/health` | Ops / Health Check | Public or token-flow endpoint | `None` | 200 | Health Check |

## ISP Admin

| Method | Path | Frontend Area | Auth | Request Body | Responses | Summary |
|---|---|---|---|---|---|---|
| GET | `/api/v1/isp-admin/alerts` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Alerts Endpoint |
| GET | `/api/v1/isp-admin/alerts/{alert_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Alert Endpoint |
| GET | `/api/v1/isp-admin/analytics/summary` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Analytics Summary Endpoint |
| GET | `/api/v1/isp-admin/device-connection-logs` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Device Connection Logs Endpoint |
| GET | `/api/v1/isp-admin/device-connection-logs/{connection_log_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Device Connection Log Endpoint |
| POST | `/api/v1/isp-admin/intelligence/run` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Run Intelligence Endpoint |
| GET | `/api/v1/isp-admin/plan-change-requests` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Plan Change Requests Endpoint |
| GET | `/api/v1/isp-admin/plan-change-requests/{request_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Plan Change Request Endpoint |
| PATCH | `/api/v1/isp-admin/plan-change-requests/{request_id}/review` | ISP Admin Web Dashboard | ISP Admin JWT | `ISPAdminPlanChangeRequestReviewRequest` | 200, 422 | Review Plan Change Request Endpoint |
| GET | `/api/v1/isp-admin/plans` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Subscription Plans Endpoint |
| POST | `/api/v1/isp-admin/plans` | ISP Admin Web Dashboard | ISP Admin JWT | `SubscriptionPlanCreateRequest` | 201, 422 | Create Subscription Plan Endpoint |
| GET | `/api/v1/isp-admin/plans/{plan_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Subscription Plan Endpoint |
| PATCH | `/api/v1/isp-admin/plans/{plan_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `SubscriptionPlanUpdateRequest` | 200, 422 | Update Subscription Plan Endpoint |
| POST | `/api/v1/isp-admin/predictions/subscriptions/{subscription_id}/generate` | ISP Admin Web Dashboard | ISP Admin JWT | `ISPAdminPredictionGenerateRequest` | 201, 422 | Generate Prediction For Subscription Endpoint |
| GET | `/api/v1/isp-admin/recommendations` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Recommendations Endpoint |
| GET | `/api/v1/isp-admin/recommendations/{recommendation_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Recommendation Endpoint |
| POST | `/api/v1/isp-admin/recommendations/predictions/{prediction_id}/generate` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 201, 422 | Generate Recommendation For Prediction Endpoint |
| GET | `/api/v1/isp-admin/reports` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Reports Endpoint |
| POST | `/api/v1/isp-admin/reports` | ISP Admin Web Dashboard | ISP Admin JWT | `ISPAdminReportCreateRequest` | 201, 422 | Generate Report Endpoint |
| GET | `/api/v1/isp-admin/reports/{report_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Report Endpoint |
| GET | `/api/v1/isp-admin/router-action-logs` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Router Action Logs Endpoint |
| GET | `/api/v1/isp-admin/router-action-logs/{action_log_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Router Action Log Endpoint |
| GET | `/api/v1/isp-admin/routers` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Routers Endpoint |
| POST | `/api/v1/isp-admin/routers` | ISP Admin Web Dashboard | ISP Admin JWT | `RouterCreateRequest` | 201, 422 | Create Router Endpoint |
| GET | `/api/v1/isp-admin/routers/{router_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Router Endpoint |
| PATCH | `/api/v1/isp-admin/routers/{router_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `RouterUpdateRequest` | 200, 422 | Update Router Endpoint |
| GET | `/api/v1/isp-admin/subscriptions` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List User Subscriptions Endpoint |
| POST | `/api/v1/isp-admin/subscriptions` | ISP Admin Web Dashboard | ISP Admin JWT | `UserSubscriptionCreateRequest` | 201, 422 | Create User Subscription Endpoint |
| GET | `/api/v1/isp-admin/subscriptions/{subscription_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get User Subscription Endpoint |
| PATCH | `/api/v1/isp-admin/subscriptions/{subscription_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `UserSubscriptionUpdateRequest` | 200, 422 | Update User Subscription Endpoint |
| GET | `/api/v1/isp-admin/summary` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200 | Get Isp Admin Summary Endpoint |
| POST | `/api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator` | ISP Admin Web Dashboard | ISP Admin JWT | `{'anyOf': [{'$ref': '#/components/schemas/SimulatorUsageIngestionRequest'}, {'type': 'null'}], 'title': 'Request'}` | 201, 422 | Run Simulator Usage Ingestion Endpoint |
| POST | `/api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/devices` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 201, 422 | Run Simulator Device Ingestion Endpoint |
| POST | `/api/v1/isp-admin/usage-ingestion/routers/{router_id}/simulator/run` | ISP Admin Web Dashboard | ISP Admin JWT | `{'anyOf': [{'$ref': '#/components/schemas/SimulatorUsageIngestionRequest'}, {'type': 'null'}], 'title': 'Request'}` | 201, 422 | Run Full Simulator Ingestion Endpoint |
| GET | `/api/v1/isp-admin/usage-records` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List Usage Records Endpoint |
| GET | `/api/v1/isp-admin/usage-records/{usage_record_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get Usage Record Endpoint |
| GET | `/api/v1/isp-admin/user-invitations` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List App User Invitations Endpoint |
| POST | `/api/v1/isp-admin/user-invitations` | ISP Admin Web Dashboard | ISP Admin JWT | `AppUserInvitationCreateRequest` | 201, 422 | Create App User Invitation Endpoint |
| PATCH | `/api/v1/isp-admin/user-invitations/{invitation_id}/revoke` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Revoke App User Invitation Endpoint |
| GET | `/api/v1/isp-admin/users` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | List App Users Endpoint |
| GET | `/api/v1/isp-admin/users/{user_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `None` | 200, 422 | Get App User Endpoint |
| PATCH | `/api/v1/isp-admin/users/{user_id}` | ISP Admin Web Dashboard | ISP Admin JWT | `AppUserUpdateRequest` | 200, 422 | Update App User Endpoint |

## Platform Admin

| Method | Path | Frontend Area | Auth | Request Body | Responses | Summary |
|---|---|---|---|---|---|---|
| GET | `/api/v1/platform-admin/isps` | Platform Admin Web Dashboard | Platform Admin JWT | `None` | 200, 422 | List Isps Endpoint |
| POST | `/api/v1/platform-admin/isps` | Platform Admin Web Dashboard | Platform Admin JWT | `ISPCreateRequest` | 201, 422 | Create Isp Endpoint |
| GET | `/api/v1/platform-admin/isps/{isp_id}` | Platform Admin Web Dashboard | Platform Admin JWT | `None` | 200, 422 | Get Isp Endpoint |
| PATCH | `/api/v1/platform-admin/isps/{isp_id}` | Platform Admin Web Dashboard | Platform Admin JWT | `ISPUpdateRequest` | 200, 422 | Update Isp Endpoint |
| GET | `/api/v1/platform-admin/isps/{isp_id}/admin-invitations` | Platform Admin Web Dashboard | Platform Admin JWT | `None` | 200, 422 | List Isp Admin Invitations Endpoint |
| POST | `/api/v1/platform-admin/isps/{isp_id}/admin-invitations` | Platform Admin Web Dashboard | Platform Admin JWT | `ISPAdminInvitationCreateRequest` | 201, 422 | Create Isp Admin Invitation Endpoint |
| PATCH | `/api/v1/platform-admin/isps/{isp_id}/admin-invitations/{invitation_id}/revoke` | Platform Admin Web Dashboard | Platform Admin JWT | `None` | 200, 422 | Revoke Isp Admin Invitation Endpoint |
| GET | `/api/v1/platform-admin/isps/{isp_id}/admins` | Platform Admin Web Dashboard | Platform Admin JWT | `None` | 200, 422 | List Isp Admins Endpoint |
| GET | `/api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}` | Platform Admin Web Dashboard | Platform Admin JWT | `None` | 200, 422 | Get Isp Admin Endpoint |
| PATCH | `/api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}` | Platform Admin Web Dashboard | Platform Admin JWT | `ISPAdminUpdateRequest` | 200, 422 | Update Isp Admin Endpoint |
| GET | `/api/v1/platform-admin/summary` | Platform Admin Web Dashboard | Platform Admin JWT | `None` | 200 | Get Platform Admin Summary Endpoint |

## Untagged

| Method | Path | Frontend Area | Auth | Request Body | Responses | Summary |
|---|---|---|---|---|---|---|
| GET | `/` | Shared / Internal | Public or token-flow endpoint | `None` | 200 | Root |

## Frontend Integration Notes

### Shared Auth

- Login starts at `POST /api/v1/auth/login`.
- MFA-required accounts should follow the MFA response flow.
- Store JWT securely on the client side.
- Send JWT using `Authorization: Bearer <token>`.
- Account settings identity changes use a two-step MFA flow:
  - `POST /api/v1/auth/me/profile-update-challenge`
  - `PATCH /api/v1/auth/me/identity`
- Password reset emails send a reset link built from the admin web base URL and `/reset-password?token=...`; production responses must not expose raw reset tokens or reset URLs.

### Platform Admin Dashboard

- Use platform-admin endpoints only with Platform Admin accounts.
- Main responsibilities: ISP and ISP Admin management.

### ISP Admin Dashboard

- Use ISP Admin endpoints only with ISP Admin accounts.
- Main responsibilities: users, plans, subscriptions, routers, usage, analytics, reports, recommendations, alerts, and plan change request review.
- ISP Admin data must stay scoped to the admin's ISP.

### Mobile App

- Use `/me/...` endpoints with App User accounts.
- Main responsibilities: user summary, subscriptions, routers, devices, usage, alerts, predictions, recommendations, plan change requests, and device policies.
- Router capability responses include `integration_mode` and `is_simulator` so the mobile app can clearly label simulator/demo actions.


### Device Policy Directional Bandwidth Contract

`POST /api/v1/me/device-policies` supports App User device network policies.

For `policy_type = "bandwidth_limit"`, new mobile clients should send:

```json
{
  "device_id": "<device_id>",
  "policy_type": "bandwidth_limit",
  "download_limit_mbps": 10,
  "upload_limit_mbps": 2
}
```

Backward compatibility:

- `bandwidth_limit_mbps` is still accepted for older clients.
- If only `bandwidth_limit_mbps` is sent, the backend treats it as both download and upload limit.
- `PATCH /api/v1/me/device-policies/{policy_id}/execute` applies the pending policy through the router adapter.
- Simulator mode stores directional limits in router action payloads.

### Deployment / CORS

- Frontend origins must be configured in `BACKEND_CORS_ORIGINS`.
- Wildcard CORS is blocked when `DEBUG=False`.

### Invitation Email Delivery

- `POST /api/v1/platform-admin/isps/{isp_id}/admin-invitations` sends the ISP Admin invitation email through the configured SMTP transport when `EMAIL_DELIVERY_ENABLED=True`.
- `POST /api/v1/isp-admin/user-invitations` sends the App User invitation email through the configured SMTP transport when `EMAIL_DELIVERY_ENABLED=True`.
- `POST /api/v1/auth/password/forgot` sends a password reset link through the configured SMTP transport when an account exists.
- SMTP configuration uses `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`, `SMTP_USE_TLS`, and `SMTP_USE_SSL`.
- Invitation accept links are built from a valid request `Origin` only while
  `DEBUG=True`; otherwise they are built from `FRONTEND_ADMIN_URL`.
- Password reset links follow the same rule: local DEBUG requests from a valid
  `http` or `https` Origin can generate LAN admin-web links, while production
  ignores Origin and uses `FRONTEND_ADMIN_URL`.
- `dev_invitation_token` is a local development helper and is only populated when `DEBUG=True`; production responses must not expose invitation tokens.
- The frontend should remove `token` from `/accept-invitation` URLs immediately after reading it and submit the token only in the `POST /api/v1/auth/invitations/accept` request body.
- The real admin web must not render `dev_invitation_token`, `dev_email_code`,
  `dev_reset_url`, local DEBUG helper boxes, or manual token-entry helpers.

---

## Standard Error Response Contract

PulseFi API errors now use a consistent frontend-friendly shape.

### Normal HTTP errors

```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

Common error values include:

- bad_request
- unauthorized
- forbidden
- not_found
- conflict
- validation_error
- rate_limited
- service_unavailable
- client_error
- server_error

### Validation errors

```json
{
  "error": "validation_error",
  "message": "Request validation failed",
  "details": []
}
```

### Unexpected server errors

```json
{
  "error": "server_error",
  "message": "Internal server error"
}
```

Frontend apps should read message for display text and error for programmatic handling.

---

## Auth Rate Limit Contract

Auth-sensitive endpoints are currently limited to:

```text
5 attempts per 15 minutes
```

Affected endpoints:

- POST /api/v1/auth/login
- POST /api/v1/auth/email/verify
- POST /api/v1/auth/mfa/verify
- POST /api/v1/auth/mfa/setup/confirm
- POST /api/v1/auth/password/forgot
- POST /api/v1/auth/password/reset
- POST /api/v1/auth/invitations/accept
- POST /api/v1/auth/me/profile-update-challenge
- PATCH /api/v1/auth/me/identity

When the limit is exceeded, the API returns:

```json
{
  "error": "rate_limited",
  "message": "Too many attempts. Please try again later."
}
```

Frontend apps should show a friendly message and avoid retrying immediately.

Production note: the current limiter is in-memory. `X-Forwarded-For` is trusted only from configured trusted proxy IPs. Before multi-worker production deployment, replace it with Redis/shared-store rate limiting.

Local development note: while `DEBUG=True`, `POST /api/v1/auth/rate-limit/reset` clears the in-memory limiter for the running backend process. This route is hidden from OpenAPI and returns 404 when `DEBUG=False`.

---

## Router Capability Simulator Mode

`GET /api/v1/me/routers/{router_id}/capabilities` returns capability booleans plus:

- `integration_mode`: currently `simulator`
- `is_simulator`: currently `true`

Frontend apps should present device policy execution as simulated/demo behavior while this mode is active.

---

## OpenAPI Error Schema Contract

Swagger/OpenAPI now documents the same standard error response shape used at runtime.

Standard error responses use:

```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

Validation errors use:

```json
{
  "error": "validation_error",
  "message": "Request validation failed",
  "details": []
}
```

OpenAPI components added:

- APIErrorResponse
- APIValidationErrorResponse

Frontend-generated clients should use these schemas instead of FastAPI default detail-based validation errors.

### ISP Admin Automatic Intelligence Scheduler

PulseFi now supports a local/demo automatic intelligence scheduler.

Environment flags:
- `ENABLE_INTELLIGENCE_SCHEDULER`
- `INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES`

Behavior:
- When enabled, the backend periodically checks active ISPs.
- For each ISP, it checks active subscriptions.
- It generates missing daily predictions, recommendations, and alert checks from latest usage/device data.
- Existing prediction/recommendation records are reused to avoid duplicate rows.
- Unread/recent alert checks prevent duplicate high-usage, plan-risk, new-device, and policy-failure alert spam.
- Manual `POST /api/v1/isp-admin/intelligence/run` remains an admin/demo trigger; it is not the only way intelligence runs.
- The response includes `alerts_created` at run level and per item.

ML status:
- Current intelligence is a rules-based/heuristic MVP.
- Predictions use `model_version="rule_based_v1"`.
- Recommendations use `rule_based_recommendation_v1` service logic.
- There is no integrated trained ML training/inference pipeline yet, so do not label the current implementation as completed ML.

Production note:
- This scheduler is suitable for local/demo use.
- Before multi-worker production deployment, move scheduling to a single worker, cron, or job queue to avoid duplicate background runs.

### Step 45 Simulator Scenarios and Deterministic Explain Text

Full simulator request body now supports an optional `scenario` field:

```json
{
  "scenario": "near_plan_limit",
  "record_start": null,
  "record_end": null
}
```

Supported scenario values:
- `normal_usage`
- `high_usage`
- `near_plan_limit`
- `exceeded_plan`
- `new_device`
- `policy_failure`
- `heavy_device_usage`

Simulator responses include `scenario`; full simulator responses also include `policy_failure_alert_created`.

Alert and recommendation response models now include:
- `explanation`: deterministic text generated from existing alert/recommendation fields.

This is the current Explain-this MVP. It does not call an external AI service.

### Step 27D ISP Admin Intelligence Integration

Added ISP Admin recommendation viewing routes:
- `GET /api/v1/isp-admin/recommendations`
- `GET /api/v1/isp-admin/recommendations/{recommendation_id}`
- `POST /api/v1/isp-admin/intelligence/run`

Supported recommendation list filters:
- `status`
- `user_id`
- `subscription_id`
- `limit`
- `offset`

Frontend integration notes:
- ISP Admin recommendation queries are scoped to the authenticated admin's ISP.
- Non-owned recommendations return `404`.
- The real admin frontend must read the API base URL from `VITE_API_BASE_URL`.
- Local fallback remains `http://127.0.0.1:8000/api/v1`.
- `.env`, `.env.local`, `.env.development.local`, and other secret-bearing env files remain uncommitted.

### ISP Admin - ISP Admin Invitations

These endpoints allow an authenticated ISP Admin to invite another ISP Admin under the same ISP.

Important scoping rule:
- The request does not accept `isp_id`.
- The backend always uses `current_admin.isp_id`.
- An ISP Admin cannot invite an admin into another ISP.

#### Create ISP Admin invitation

`POST /api/v1/isp-admin/admin-invitations`

Auth:
- Bearer token
- Must be an active `isp_admin`

Request:

``json
{
  "email": "new.admin@example.com",
  "full_name": "New ISP Admin",
  "expires_in_days": 7
}
``

Response:

``json
{
  "id": "uuid",
  "email": "new.admin@example.com",
  "full_name": "New ISP Admin",
  "account_type": "admin",
  "admin_role": "isp_admin",
  "isp_id": "uuid",
  "invited_by_admin_id": "uuid",
  "expires_at": "datetime",
  "accepted_at": null,
  "revoked_at": null,
  "created_at": "datetime",
  "dev_invitation_token": "debug-only-token"
}
``

Notes:
- `dev_invitation_token` is returned only when `DEBUG=True`.
- In production, email delivery must be configured.

#### List ISP Admin invitations

`GET /api/v1/isp-admin/admin-invitations`

Optional query:
- `status=pending`
- `status=accepted`
- `status=revoked`
- `status=expired`
- `limit`
- `offset`

#### Revoke ISP Admin invitation

`PATCH /api/v1/isp-admin/admin-invitations/{invitation_id}/revoke`

Only pending invitations can be revoked.

### Network / RADIUS / Router Integration Direction

PulseFi should target local ISPs/resellers that receive bandwidth from an upstream provider but manage customers through their own RADIUS/API/router control point.

- RADIUS/API is the source for official customer usage, subscription state, plan/profile changes, suspend/reactivate actions, and billing-driven access control.
- Router/CPE adapters are the source for optional per-device visibility, live device rates, device counters, trust/untrust, bandwidth limit, and priority actions.
- Simulator endpoints represent this integration layer for demo and local development.
- Official subscription usage and estimated per-device usage must be labelled separately in frontend UX.
- ISP Admin alert views should focus on operational/admin-visible alerts, not every private App User alert.

See `docs/NETWORK_INTEGRATION_DIRECTION.md` for the full architecture note.

<!-- PULSEFI_MFA_API_SYNC_START -->
## MFA Login and Settings Contract Checkpoint - 2026-05-22

### Current MFA model

PulseFi supports multi-method MFA for Admin and App User accounts.

Account MFA state:

- `email_mfa_enabled`: Email MFA is active.
- `authenticator_mfa_enabled`: Authenticator-app MFA is active.
- `mfa_enabled`: legacy compatibility flag, synchronized from active MFA methods.
- `preferred_mfa_method`: default login MFA method. Valid values remain `email` or `authenticator`.

Backup codes are recovery credentials, not preferred MFA methods.

### Login UX contract

The frontend must not ask users to choose MFA method before password verification.

Correct flow:

1. User submits identifier/email and password.
2. Backend verifies password.
3. Backend starts MFA using the account's `preferred_mfa_method`.
4. MFA verification screen may show fallback actions only after password succeeds.

Fallback rules:

- Email fallback is available only when Email MFA is active.
- Backup-code fallback is available only when unused backup codes exist.
- Backup code entry should be shown as recovery, not as a preferred MFA method.

### Relevant auth endpoints

Existing / current endpoints:

- `POST /api/v1/auth/login`
  - Starts login.
  - Uses preferred MFA method by default.
  - API may accept an optional selected MFA method, but product UX should not expose a pre-login selector.

- `POST /api/v1/auth/mfa/verify`
  - Completes MFA login.
  - Accepts email OTP, authenticator code, or backup code if backup codes exist.

- `PATCH /api/v1/auth/mfa/challenge-method`
  - Switches an existing MFA challenge to another active MFA method.
  - Intended for post-password fallback such as "Send code to email."
  - Must not be used to show a pre-password method picker.

- `GET /api/v1/auth/me/mfa/status`
  - Returns active MFA methods and preferred method for the authenticated account.

- `POST /api/v1/auth/me/mfa/settings-challenge`
  - Starts verification before sensitive MFA settings actions.

- `PATCH /api/v1/auth/me/mfa/settings-action`
  - Applies MFA settings action only after valid verification.

### Pending contract work

Backup-code management still needs completed API/UI work:

- Generate backup codes.
- Show generated backup codes once.
- Store only hashed backup codes.
- Count unused backup codes.
- Regenerate backup codes after verification.
- Revoke old backup codes when regenerated.
- Surface `backup_codes_available` during MFA login only when unused backup codes exist.
<!-- PULSEFI_MFA_API_SYNC_END -->

---

## Step 40E MFA Login Fallback Contract Update - 2026-05-22

Admin/App User login MFA behavior:

- `POST /api/v1/auth/login` accepts only `account_type`, `identifier`, and `password` for normal login UX.
- The login page must not ask users to choose an MFA method before password verification.
- When MFA is required, the backend returns the preferred MFA challenge first.
- `MFARequiredResponse` now includes:
  - `active_methods`: list of active login MFA methods, currently `email` and/or `authenticator`
  - `backup_codes_available`: boolean showing whether unused recovery codes exist
- `PATCH /api/v1/auth/mfa/challenge-method` switches an active MFA challenge to another active method after password verification.
- Backup codes are recovery codes only and must not be treated as `preferred_mfa_method`.
- `preferred_mfa_method` remains limited to `email` or `authenticator`.
- `dev_email_code` may appear only in local development when `DEBUG=True`.
- Production must not expose OTP/dev codes.

Admin web behavior:

- Admin login asks only for identifier/email and password.
- MFA fallback actions appear only after password succeeds.
- â€œSend code to emailâ€ appears only when Email MFA is active.
- â€œUse authenticator appâ€ appears only when Authenticator MFA is active and not already the active challenge.
- â€œUse backup codeâ€ appears only when `backup_codes_available=true`.

---

## Step 40F MFA Backup-Code Contract Update - 2026-05-22

Backup-code endpoints:

- `GET /api/v1/auth/me/mfa/backup-codes/status`
  - Requires authenticated Admin/App User token.
  - Returns:
    - `account_type`
    - `backup_codes_available`
    - `available_backup_code_count`

- `PATCH /api/v1/auth/me/mfa/backup-codes/regenerate`
  - Requires authenticated Admin/App User token.
  - Requires a verified MFA settings challenge:
    - `challenge_token`
    - `code`
  - Revokes old unused backup codes.
  - Creates a fresh set of backup codes.
  - Stores only password-hashed backup-code values.
  - Returns raw backup codes one time only in `backup_codes`.

Security rules:

- Backup codes are recovery codes only.
- Backup codes must not become `preferred_mfa_method`.
- `preferred_mfa_method` remains limited to `email` or `authenticator`.
- Frontend must display generated backup codes as one-time-only secrets.
- Production must never expose OTP/dev email codes.

---

## Step 40H Admin-Only Continuation Note - 2026-05-22

Mobile App User MFA implementation is paused until the project reaches the mobile phase.

Current active work should remain backend/admin-web focused:

- Admin web uses post-password MFA fallback UX.
- Admin Settings supports backup-code status and verified generation/regeneration.
- Backend supports backup-code status/regeneration and login fallback availability.
- Mobile app changes should not continue unless explicitly resumed.

---

## Step 40H Admin Backup-Code Smoke Test Result - 2026-05-22

Manual admin web smoke test completed:

- Admin Settings backup-code status loads.
- Backup-code generation/regeneration works after verified MFA challenge.
- Old unused backup codes are revoked during regeneration.
- Raw generated backup codes are shown one time only.
- Copy-all backup-code UX works.
- Refreshing Settings hides raw codes and keeps only count/status.
- Mobile app work remains paused until the mobile phase.

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

### Step 42C router service-line validation

`POST /api/v1/isp-admin/routers` and `PATCH /api/v1/isp-admin/routers/{router_id}` may return `409 Conflict` when the selected `user_subscription_id` service line already has another router.

This does not block package reuse. Multiple independent service lines can use the same package/plan. The validation only prevents two independent routers from sharing one service-line row when their usage, policies, and service requests should stay separate.

### Step 42D actionable report data

Generated ISP Admin reports may now include actionable report sections inside `report_data`:

- `summary`: KPI-style report metrics.
- `insights`: list of admin-facing insight objects with `severity` and `message`.
- `tables`: report-specific row tables for admin review.

Usage reports may include:
- `top_service_lines_by_usage`
- `top_routers_by_usage`
- `recent_usage_records`

Alert reports may include:
- `recent_alerts`

Raw `report_data` remains available for technical inspection, but admin clients should render `summary`, `insights`, and `tables` as the primary user-facing report.

<!-- PULSEFI_EMAIL_DELIVERY_CONTRACT_START -->
## Email Delivery Configuration - Step 44E (2026-05-24)

PulseFi supports email delivery for:
- ISP Admin invitations.
- App User invitations.
- password reset links.
- verification/MFA-related email flows where enabled.

Deployment email status:
- Gmail SMTP is not reliable on the current Render deployment because outbound SMTP connection attempts failed with `OSError: [Errno 101] Network is unreachable`.
- SMTP connection failures should be handled as email-provider failures, not unhandled 500 crashes.
- HTTP email delivery through Resend is the active Step 44E direction.

Environment variables:
- `EMAIL_DELIVERY_ENABLED=True`
- `EMAIL_DELIVERY_PROVIDER=smtp|resend`
- `RESEND_API_KEY=<secret, Render only>`
- `BREVO_API_URL`
- `SMTP_FROM_EMAIL=<sender address>`
- `SMTP_FROM_NAME=PulseFi`
- `FRONTEND_ADMIN_URL=https://pulsefi-admin-web.vercel.app`

Notes:
- With `EMAIL_DELIVERY_PROVIDER=brevo`, old Gmail SMTP connection variables are ignored for sending.
- `SMTP_FROM_EMAIL` and `SMTP_FROM_NAME` are still used as sender identity fields.
- For quick Resend testing, use `SMTP_FROM_EMAIL=<verified Brevo sender email>`.
- A Gmail address such as `pulsefi.verify@gmail.com` should be used as a recipient unless a matching sender domain is verified in Resend.
- API keys and provider secrets must never be committed or shared in chat.
<!-- PULSEFI_EMAIL_DELIVERY_CONTRACT_END -->

---

## Step 44F - Platform Admin Team Invitations

Protected by `platform_admin` role only.

Endpoints:

- `POST /api/v1/platform-admin/platform-admin-invitations`
  - Creates a pending invitation for another Platform Admin.
  - Uses the same secure invitation-token flow as ISP Admin/App User invitations.
  - In `DEBUG=True`, response may include `dev_invitation_token` for deployed demo testing.
  - In production, email delivery must be configured.

- `GET /api/v1/platform-admin/platform-admin-invitations`
  - Lists Platform Admin invitations.
  - Optional query: `status=pending|accepted|revoked|expired`.

- `PATCH /api/v1/platform-admin/platform-admin-invitations/{invitation_id}/revoke`
  - Revokes a pending Platform Admin invitation.

- `GET /api/v1/platform-admin/platform-admins`
  - Lists active Platform Admin accounts.
  - Optional query: `status=active|inactive|suspended`.

Security notes:

- Platform Admin accounts are not public-registration accounts.
- First Platform Admin is deployment-bootstrap only.
- Additional Platform Admins are invited by an existing Platform Admin.
- Platform Admin invitations use `account_type="admin"`, `admin_role="platform_admin"`, and `isp_id=null`.

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

Current phase: **Step 50O complete - mobile UX pagination/service-request polish is complete; Step 50P immediate mobile behavior fixes are planned next; final full live smoke test remains deferred until all remaining project steps are finished.**

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



## Usage kind notes

For ISP Admin daily usage by user, `usage_kind` explains how the row should be interpreted:

- `official` / Service total: total usage counted for the user service line/router and suitable for plan/package usage display.
- `estimated` / Device estimate: simulator/CPE per-device usage breakdown used for device-level visibility.

Future simulator usage ingestion creates one official aggregate row with `device_id = null` plus estimated device rows for trusted connected devices.

- `GET /api/v1/me/usage/daily`

- `GET /api/v1/isp-admin/usage-records/daily`

- `GET /api/v1/isp-admin/usage-records/daily-by-user`

- Step 50H mobile usage cleanup is complete: Home no longer fails completely when usage summary fails, Usage now has a cleaner Monthly/Daily layout, Refresh labels were simplified, Official and Estimated totals are shown separately, and the user can choose which source the main usage graph displays.

- Step 50I mobile Insights cleanup is complete: Predictions and Recommendations are split into tabs, each list uses page controls like records/logs, and older user-facing insights are hidden from the mobile UI while remaining in backend/admin data.

- Step 50J admin Network Activity pagination is complete: ISP Admin Network tables now paginate Daily Usage by User, Recent Usage Records, Device Connection Logs, and Router Action Logs with compact table controls instead of long scrolling lists.
