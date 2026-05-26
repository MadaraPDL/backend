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
- `RESEND_API_URL=https://api.resend.com/emails`
- `SMTP_FROM_EMAIL=<sender address>`
- `SMTP_FROM_NAME=PulseFi`
- `FRONTEND_ADMIN_URL=https://pulsefi-admin-web.vercel.app`

Notes:
- With `EMAIL_DELIVERY_PROVIDER=resend`, old Gmail SMTP connection variables are ignored for sending.
- `SMTP_FROM_EMAIL` and `SMTP_FROM_NAME` are still used as sender identity fields.
- For quick Resend testing, use `SMTP_FROM_EMAIL=onboarding@resend.dev`.
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

### Live deployment configuration

The deployed backend is configured for automatic intelligence:

- `ENABLE_INTELLIGENCE_SCHEDULER=True`
- `INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES=15`

This means scheduled intelligence should periodically check active subscriptions. However, PulseFi should not depend only on the scheduler for simulator/demo behavior. New usage ingestion should also trigger immediate alert/intelligence checks.

### Step 46 - Usage visibility, alert correctness, simulator intelligence, and mobile simplification

Status: active / in progress.

#### Step 46A - Shared usage summary backend

Status: implemented.

PulseFi now needs one shared usage summary contract used by ISP Admin and App User/mobile.

Required fields:

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

Important rule:

- `usage_summaries` is not a database column.
- It is a calculated API response built from existing `user_subscriptions`, `subscription_plans`, and `usage_records`.

#### Step 46B - ISP Admin selected-user plan usage

Status: implemented and live-tested after backend deploy.

The ISP Admin Users table should stay compact. It should not contain too many usage columns.

Correct UX:

- Users table is for finding/selecting users.
- Selected user panel shows details.
- Selected user panel shows one circular usage card per subscription/service line/plan.
- If the user has multiple subscriptions, each subscription must have its own usage card and its own used/limit display.

Expected selected-user usage display:

- plan name
- subscription label
- status
- used / plan limit
- usage percentage
- remaining data
- today usage
- monthly/current-cycle usage
- total usage

#### Step 46C - App User mobile usage visibility

Status: planned / next mobile work.

The App User mobile app must not show only total consumption without context.

Required mobile usage display:

- used / plan limit
- remaining GB
- today usage
- this month / current-cycle usage
- total usage
- unlimited-plan handling

The Home screen should show only a small summary. Detailed usage belongs in the Usage tab.

#### Step 46D - Automatic usage alert tiers

Status: being corrected and tested.

PulseFi alert generation must be automatic after usage ingestion.

Plan usage tiers:

- `50%+` of plan: create `Usage warning`
- `80%+` of plan: create `High internet usage`
- `100%+` of plan: create `Plan usage limit reached`

Important implementation rule:

- Do not add a new DB alert type for rapid usage unless a safe migration is prepared.
- For now, use existing `alert_type="high_usage"` with different alert titles:
  - `Usage warning`
  - `High internet usage`
  - `Rapid high internet usage`
- `Plan usage limit reached` should use `alert_type="plan_exceed_risk"`.

Duplicate protection should be title-specific, not only alert-type-specific. Otherwise one unread `high_usage` alert blocks `Usage warning`, `High internet usage`, and `Rapid high internet usage`.

#### Step 46E - Rapid high-usage alerts

Status: planned/in progress.

Rapid high usage must trigger even when the user is not near the monthly plan limit.

Required rapid rules:

- `5 GB+` in the last 24 hours should trigger `Rapid high internet usage`.
- `2 GB+` in about one hour should trigger `Rapid high internet usage`.

Example:

- A user consuming `6.73 GB` quickly on a `10 GB` plan should receive a rapid usage alert even if the cycle percentage is below the high-usage threshold.

This must be based on actual recent usage records, not only the simulator scenario name.

#### Step 46F - Full simulator immediate checks

Status: in progress.

After full simulation creates usage/device data, backend should immediately run:

- usage alert checks
- new-device alert checks
- prediction/intelligence checks
- recommendation checks

The user/admin should not need to wait for the 15-minute scheduler tick during demo testing.

The simulator response should expose useful counts:

- usage alerts created
- new device alerts created
- total alerts created
- intelligence alerts created
- predictions created
- recommendations created

#### Step 46G - Mobile alert auto-refresh

Status: planned / needed before push notifications.

Backend alert creation can be automatic, but mobile display is not instant unless the app refreshes or receives push events.

Required mobile behavior:

- refresh alerts when opening the Alerts tab
- refresh Home unread-alert count when opening Home
- refresh alerts when the app returns from background
- optionally poll every 15-30 seconds while Alerts is open
- keep pull-to-refresh

This is not full push notifications. It is a lightweight auto-refresh improvement.

#### Step 46H - Event-driven non-spam intelligence

Status: planned / next backend correction.

Best architecture:

- after each usage record is created, run intelligence for that subscription
- compare the new recommendation state against the latest existing recommendation state
- only create/push a recommendation when the state changes
- keep periodic intelligence as a safety sweep, but avoid spam

Recommendation state comparison should include:

- `recommendation_type`
- `recommendation_plan_id`
- `risk_level`

Expected behavior:

- `stay_current` -> `stay_current`: do not create/push duplicate recommendation
- `stay_current` -> `upgrade_plan`: create recommendation
- `upgrade_plan` to same plan -> same plan: do not duplicate
- `upgrade_plan` to one plan -> `upgrade_plan` to different plan: create new recommendation
- `upgrade_plan` -> `monitor_usage`: create new recommendation
- `upgrade_plan` -> `stay_current`: do not spam; optionally record a non-push status later

The manual `Run intelligence now` button should remain for admin/demo testing, but normal behavior should be event-driven after usage ingestion.

#### Step 46I - Mobile app simplification

Status: planned.

The mobile app is too crowded and should be reorganized into:

- Home
- Usage
- Devices
- Alerts
- Profile

Home should only show:

- plan usage summary
- today usage
- most important active alert
- latest meaningful recommendation
- quick counts

Usage tab should contain:

- daily usage
- monthly/current-cycle usage
- total usage
- per-plan/subscription usage

Devices tab should contain:

- connected devices
- device details
- device policies/actions
- new-device state

Alerts tab should contain:

- alerts
- recommendation/explanation entry points

Profile tab should contain:

- account info
- plan/service-line info
- MFA/security
- logout
- settings

### Step 47 - Real ML prediction pipeline

Status: planned.

Current intelligence is rules-based/heuristic MVP, not a trained ML pipeline.

Step 47 should add a lightweight supervised ML pipeline to predict whether a user will exceed their plan before the cycle ends.

Planned inputs:

- current cycle usage
- plan limit
- days elapsed in cycle
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

Target implementation:

- add ML dependencies such as `numpy`, `pandas`, `scikit-learn`, and `joblib`
- train first model from simulator/historical usage records
- save/load model artifact
- keep rule-based fallback when model artifact is missing
- store prediction results in the existing predictions flow

### Step 48 - Focused chatbot / AI explainer

Status: planned after Step 46 and Step 47.

Do not build a generic chatbot first. The useful version is a focused PulseFi assistant that explains alerts and recommendations.

Examples:

- Explain this alert.
- Why is this user high risk?
- Why did PulseFi recommend this plan?
- What should the user do next?

Security rule:

- The explainer should receive only scoped alert/recommendation/usage summary/plan context.
- It must not receive secrets, passwords, API keys, MFA codes, raw tokens, router credentials, or unrestricted database content.

### Step 49 - Push notifications

Status: deferred until alert generation and mobile alert refresh are correct.

Required pieces:

- mobile push token registration
- notification preferences
- backend push dispatch service
- Expo push notification integration
- alert/recommendation notification triggers
- tests for token registration and dispatch behavior

Push notifications should come after Step 46 because notifications depend on correct alert/recommendation generation.

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
- usage summary cards
- alert tiers
- rapid high-usage alerts
- recommendation state-change behavior
- mobile alert auto-refresh
- ML predictions after Step 47
- Platform Admin flows
- ISP Admin flows
- App User mobile flows

### SE documentation note

The SE diagrams/docs should be updated after these implementation steps stabilize.

Required future SE updates:

- Use Case Diagram: usage summaries, rapid alerts, profile tab, ML predictions, chatbot, push notifications
- DFD Level 1: usage ingestion -> alert generation -> intelligence -> recommendations -> mobile/admin display
- Component Diagram: usage summary service, alert service, intelligence service, future ML module, future notification service
- Mobile screen map: Home, Usage, Devices, Alerts, Profile
- API/Feature coverage matrix: usage summaries, alert tiers, recommendation refresh, auto-refresh/push status

