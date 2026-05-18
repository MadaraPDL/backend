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
| PATCH | `/api/v1/me/device-policies/{policy_id}/execute` | Mobile App | App User JWT | `None` | 200, 422 | Execute My Device Policy Endpoint |
| GET | `/api/v1/me/devices` | Mobile App | App User JWT | `None` | 200, 422 | List My Devices Endpoint |
| GET | `/api/v1/me/devices/{device_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Device Endpoint |
| GET | `/api/v1/me/plan-change-requests` | Mobile App | App User JWT | `None` | 200, 422 | List My Plan Change Requests Endpoint |
| POST | `/api/v1/me/plan-change-requests` | Mobile App | App User JWT | `MyPlanChangeRequestCreate` | 201, 422 | Create My Plan Change Request Endpoint |
| GET | `/api/v1/me/plan-change-requests/{request_id}` | Mobile App | App User JWT | `None` | 200, 422 | Get My Plan Change Request Endpoint |
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

### Deployment / CORS

- Frontend origins must be configured in `BACKEND_CORS_ORIGINS`.
- Wildcard CORS is blocked when `DEBUG=False`.

### Invitation Email Delivery

- `POST /api/v1/platform-admin/isps/{isp_id}/admin-invitations` sends the ISP Admin invitation email through the configured SMTP transport when `EMAIL_DELIVERY_ENABLED=True`.
- `POST /api/v1/isp-admin/user-invitations` sends the App User invitation email through the configured SMTP transport when `EMAIL_DELIVERY_ENABLED=True`.
- SMTP configuration uses `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`, `SMTP_USE_TLS`, and `SMTP_USE_SSL`.
- Invitation accept links are built from `FRONTEND_ADMIN_URL`.
- `dev_invitation_token` is a local development helper and is only populated when `DEBUG=True`; production responses must not expose invitation tokens.
- The frontend should remove `token` from `/accept-invitation` URLs immediately after reading it and submit the token only in the `POST /api/v1/auth/invitations/accept` request body.

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
- It generates missing daily predictions and recommendations.
- Existing prediction/recommendation records are reused to avoid duplicate rows.

Production note:
- This scheduler is suitable for local/demo use.
- Before multi-worker production deployment, move scheduling to a single worker, cron, or job queue to avoid duplicate background runs.

### Step 27D ISP Admin Intelligence Integration

Added ISP Admin recommendation viewing routes:
- `GET /api/v1/isp-admin/recommendations`
- `GET /api/v1/isp-admin/recommendations/{recommendation_id}`

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
