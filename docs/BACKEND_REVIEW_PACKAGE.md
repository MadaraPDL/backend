# PulseFi Backend Review Package

Date: 2026-05-16

## Purpose

This document prepares the PulseFi backend for a full Codex review before frontend integration.

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

Ask Codex to check:

- Whether any ISP Admin service accidentally misses ISP scoping.
- Whether any endpoint returns too much data.
- Whether any schema exposes sensitive fields.
- Whether old docs still mention outdated Step numbers.
- Whether tests cover enough ownership/isolation cases.
- Whether migrations can rebuild a fresh database from scratch.
- Whether .env.example or deployment docs need improvement.
- Whether router credential encryption is still incomplete.
- Whether report/analytics queries are efficient enough for demo.
- Whether OpenAPI/API contract is clear enough for frontend.

## Validation To Run Before Codex Review

Before using Codex, run:

- .\venv\Scripts\python.exe -m pytest
- .\venv\Scripts\python.exe -m compileall app tests scripts

## Recommended Codex Review Prompt

Use docs/CODEX_REVIEW_PROMPT.md.

## Suggested Next Work After Codex

After Codex review:

1. Fix P0/P1 backend issues.
2. Regenerate docs/API_CONTRACT.md if endpoints change.
3. Update memory/docs.
4. Start frontend integration.
