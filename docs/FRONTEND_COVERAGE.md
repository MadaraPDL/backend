# PulseFi Frontend Coverage Roadmap

Last updated: 2026-05-20

## Current Reality

The backend is ahead of the frontend.

The backend already supports:

- Platform Admin ISP management.
- Platform Admin ISP Admin invitation and account management.
- ISP Admin App User invitation and account management.
- ISP Admin subscription plan management.
- ISP Admin user subscription assignment and management.
- ISP Admin router management.
- ISP Admin simulator ingestion.
- ISP Admin usage records.
- ISP Admin alerts.
- ISP Admin analytics.
- ISP Admin reports.
- ISP Admin predictions and recommendations.
- ISP Admin router action logs.
- ISP Admin device connection logs.
- ISP Admin plan-change request review.
- App User mobile summary, subscriptions, routers, devices, usage, alerts, predictions, recommendations, plan-change requests, router capabilities, and device policies.
- Shared auth flows for login, MFA, invitation acceptance, email verification, password reset, profile-update challenge, and identity update.

The frontend/mobile apps currently expose the MVP flow, not every backend feature.

## Mobile App: Exposed Now

The mobile app currently exposes:

- Login and session restore.
- Home summary.
- Usage summary and recent records.
- Devices list.
- Device usage totals.
- Router mode/capability label.
- Capability-aware bandwidth limit actions.
- Capability-aware device priority actions.
- Device policy creation and execution.
- Alerts list.
- Mark alert as read.
- Predictions list.
- Recommendations list.
- Create plan-change request from recommendation.
- Plan-change request list.
- Profile account info.
- Logout.
- Light/dark theme toggle.
- Tab icons and dashboard-style dark theme polish.
- Dedicated Subscriptions/Plans screen inside the More tab.
- Subscription list, selected subscription details, status, limits, speed, price, auto-renew, start/end date, and monthly active total.
- Dedicated Routers screen inside the More tab.
- Router list, selected router details, simulator/demo mode, and capability support display.
- Device detail panel on the Devices screen.
- Device detail fetches device record and device usage totals from detail endpoints.
- Alert detail panel on the Alerts screen.
- Alert detail fetches the full alert record from the alert detail endpoint.

Current mobile API helpers include calls for:

- `GET /api/v1/auth/me`
- `GET /api/v1/me/summary`
- `GET /api/v1/me/subscriptions`
- `GET /api/v1/me/usage/summary`
- `GET /api/v1/me/usage/records`
- `GET /api/v1/me/devices`
- `GET /api/v1/me/devices/{device_id}`
- `GET /api/v1/me/usage/devices`
- `GET /api/v1/me/usage/devices/{device_id}`
- `GET /api/v1/me/routers/{router_id}/capabilities`
- `GET /api/v1/me/alerts`
- `GET /api/v1/me/alerts/{alert_id}`
- `PATCH /api/v1/me/alerts/{alert_id}/read`
- `GET /api/v1/me/predictions`
- `GET /api/v1/me/recommendations`
- `POST /api/v1/me/recommendations/{recommendation_id}/plan-change-request`
- `GET /api/v1/me/plan-change-requests`
- `GET /api/v1/me/device-policies`
- `POST /api/v1/me/device-policies`
- `PATCH /api/v1/me/device-policies/{policy_id}/execute`

## Mobile App: Missing or Incomplete

### High Priority

1. Dedicated Subscriptions screen - completed in mobile Step 31A/31B

Implemented frontend work:

- Added Subscriptions/Plans screen inside the More tab.
- Shows all subscriptions, not only the active one on Home.
- Shows plan name, data limit, speed, price, status, auto-renew, start/end date, and selected subscription details.
- Uses `GET /api/v1/me/subscriptions` and `GET /api/v1/me/subscriptions/{subscription_id}`.

2. Dedicated Routers screen - completed in mobile Step 32A

Implemented frontend work:

- Added Routers screen inside the More tab.
- Shows all routers linked to the App User account.
- Shows selected router details, status, model, subscription link, simulator/demo mode, and updated date.
- Shows router capabilities for reading usage/devices and applying bandwidth/priority actions.
- Uses `GET /api/v1/me/routers`, `GET /api/v1/me/routers/{router_id}`, and `GET /api/v1/me/routers/{router_id}/capabilities`.

3. Detail screens

Backend endpoints already available:

- `GET /api/v1/me/predictions/{prediction_id}`
- `GET /api/v1/me/recommendations/{recommendation_id}`
- `GET /api/v1/me/plan-change-requests/{request_id}`
- `GET /api/v1/me/device-policies/{policy_id}`

Needed frontend work:

- Device detail panel is completed in mobile Step 33A.
- Alert detail panel is completed in mobile Step 33B.
- Still add tap-to-open detail screens or bottom sheets for predictions, recommendations, policies, and plan-change requests.
- Show full prediction, recommendation, policy, and request details.
- Keep details scoped to the logged-in App User only.

4. Manual plan-change request creation

Backend endpoint already available:

- `POST /api/v1/me/plan-change-requests`

Needed frontend work:

- Add a manual plan-change request form.
- Let the user choose subscription and target plan where possible.
- Keep recommendation-based request flow as the faster path.

### Medium Priority

5. Better policy history and execution feedback

Needed frontend work:

- Show policy detail.
- Show pending/applied/failed state clearly.
- Show failure reason.
- Show latest router action result if exposed to App User later.

6. Better filtering/search

Needed frontend work:

- Alerts filter by unread/status/severity.
- Usage records filter by date/limit.
- Devices filter by router/status/trusted/untrusted.
- Recommendations filter by status/type.

7. Mobile account/security screens

Backend flows already exist:

- MFA verify.
- MFA setup confirm.
- Profile-update challenge.
- Identity update.
- Forgot password.
- Reset password.
- Email verification.
- Invitation acceptance.

Needed frontend work:

- Decide which flows belong in mobile versus admin web.
- Add mobile MFA setup/management later.
- Add forgot/reset password mobile-friendly flow if needed.
- Add email/username update only through the backend challenge flow.

## Admin Web: Coverage Review Needed

The admin web should be reviewed against the API contract endpoint by endpoint.

### Platform Admin

Backend supports:

- Platform summary.
- ISP create/list/detail/update.
- ISP Admin invitation create/list/revoke.
- ISP Admin list/detail/update.

Coverage questions:

- Can the Platform Admin reach each workflow easily?
- Are detail/update views clear enough for demo?
- Are invitation tokens hidden unless backend DEBUG returns them?
- Is role routing still backend-derived?

### ISP Admin

Backend supports:

- Summary.
- App User invitations create/list/revoke.
- App User list/detail/update.
- Plans create/list/detail/update.
- Subscriptions create/list/detail/update.
- Routers create/list/detail/update.
- Full simulator ingestion action.
- Usage records list/detail.
- Device connection logs list/detail.
- Alerts list/detail.
- Analytics summary.
- Reports generate/list/detail.
- Predictions generate.
- Recommendations generate/list/detail.
- Router action logs list/detail.
- Plan-change requests list/detail/review.
- Intelligence run endpoint.

Coverage questions:

- Is each backend group visible in the dashboard?
- Are important details accessible, not only list rows?
- Can the ISP Admin run the full demo from dashboard without Swagger?
- Can the ISP Admin generate data, then see it reflected in mobile?
- Are all ISP Admin screens scoped to the logged-in admin ISP?

## Backend Work Still Deferred

Do not start these unless needed for demo or deployment:

- Real router credential storage.
- Raw router passwords.
- Production Redis/shared rate limiting.
- Production SMTP setup.
- Production deployment hardening.
- Push notifications.
- App store build.
- Advanced ML model replacement for demo/rules-based intelligence.

## Recommended Next Frontend Steps

1. Add Mobile detail screens for alerts/devices/insights/policies.
2. Add manual plan-change request flow.
3. Run admin web endpoint coverage review.
4. Add missing admin web detail panels/modals where needed.
5. Update SE diagrams.
6. Run full phone/admin demo smoke test.
