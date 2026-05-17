# PulseFi Backend Review Package

Date: 2026-05-17

## Purpose

This document summarizes the PulseFi backend after Codex review fixes and final hardening before frontend integration.

PulseFi is a Final Year Project: a Smart Network Monitoring and Optimization System for ISP admins and app users.

## Current Backend Status

Completed major backend areas:

- Auth foundation
- MFA setup/login foundation
- Platform Admin flows
- ISP Admin user, plan, subscription, router, analytics, and report flows
- App User /me dashboard flows
- Usage ingestion and simulator records
- Alerts
- Predictions
- Recommendations
- Device network policy execution
- Router action logs
- Recommendation to plan change request flow
- ISP Admin plan change request review
- ISP Admin analytics summary
- Stored reports and expanded report types
- API contract snapshot
- Local demo seed helper
- Codex P1 fixes through Step 26E
- Remaining P2/P3 hardening through Step 26F

## Recent Completed Steps

Step 22 completed:

- App User can create a plan change request from upgrade/downgrade recommendations.
- ISP Admin can list, view, approve, and reject plan change requests.
- Approval updates the user subscription to the requested plan.
- Cross-ISP isolation is enforced through AppUser.isp_id.

Step 23 completed:

- ISP Admin analytics summary endpoint.
- Stored report generation, list, and detail endpoints.
- Expanded stored report types:
  - usage_report
  - device_report
  - alert_report
  - recommendation_report
  - network_performance_report

Step 24 completed so far:

- Backend readiness docs cleanup.
- API contract snapshot: docs/API_CONTRACT.md
- Local demo seed helper: scripts/seed_demo_data.py

Step 25 completed:

- Migration integrity hardening.
- Standard API error response foundation.
- Auth-sensitive rate limits tightened to 5 attempts per 15 minutes.
- API contract refreshed for standard errors and rate limits.
- Final docs/status alignment.

Step 26 completed:

- App User router responses hide admin-only router fields.
- OpenAPI documents the standard `error` / `message` / optional `details` response shape.
- ISP ownership paths for usage, ingestion, and analytics were hardened.
- Device policy request validation was tightened.
- Password reset tokens are invalidated account-wide.
- Email verification is rate-limited.
- MFA challenge counters are aligned to 5 attempts.
- Rate limiting trusts `X-Forwarded-For` only from configured trusted proxies.
- Stale plan-change approval now returns 409 Conflict.
- Enum-like model fields have check-constraint migration coverage.
- Router capability responses identify simulator/demo mode.

Demo accounts:

- Platform Admin: platform.demo@pulsefi-demo.com
- ISP Admin: isp.demo@pulsefi-demo.com
- App User: user.demo@pulsefi-demo.com
- Password: PulseFiDemo123!

These are local/demo credentials only.

## Important Security Rules

Codex should verify these especially:

1. ISP Admin endpoints must always use get_current_isp_admin.
2. Every ISP Admin query must be scoped by current_admin.isp_id.
3. App User /me endpoints must only use the authenticated App User from the JWT.
4. App User endpoints must not accept arbitrary target user IDs.
5. Router raw passwords must not be accepted or stored until encrypted credential storage is intentionally implemented.
6. Production config must reject weak SECRET_KEY, wildcard CORS when DEBUG=False, and missing DATA_ENCRYPTION_KEY when DEBUG=False.
7. Demo seed helper must refuse to run when DEBUG=False.

## Known Risks / Items to Review

Remaining items to keep in mind:

- Apply the new check-constraint migration with a migration/admin DB role, not the limited runtime `pulsefi_app` role.
- Use Redis/shared-store rate limiting before production multi-worker deployment.
- Configure real email delivery before production token/email flows.
- Keep router credential storage deferred until encrypted credential handling is intentionally added.
- Keep final frontend integration focused on the existing API contract unless a real blocker is found.

## Final Validation

Before frontend integration, run:

- .\venv\Scripts\python.exe -m pytest
- .\venv\Scripts\python.exe -m compileall app tests scripts
- .\venv\Scripts\python.exe -m alembic heads
- .\venv\Scripts\python.exe -m alembic current
- git diff --check

## Suggested Next Work

1. Run final validation.
2. Apply pending migration with the migration/admin DB role.
3. Start frontend integration.
4. Regenerate docs/API_CONTRACT.md if endpoint behavior changes during integration.
