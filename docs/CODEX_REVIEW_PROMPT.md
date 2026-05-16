# Codex Review Prompt for PulseFi Backend

You are reviewing the PulseFi FastAPI backend repo.

Project: PulseFi, a Smart Network Monitoring and Optimization System for ISP admins and app users.

The backend uses:

- FastAPI
- PostgreSQL
- async SQLAlchemy
- Pydantic
- JWT auth
- MFA foundation
- Pytest

Read these files first:

- PULSEFI_MEMORY.md
- AGENTS.md
- ROADMAP.md
- README.md
- BACKEND_QUALITY_BACKLOG.md
- docs/API_CONTRACT.md
- docs/BACKEND_REVIEW_PACKAGE.md

Current status:

- Step 22 complete: recommendation to plan change request plus ISP Admin review.
- Step 23 complete: analytics and stored reports.
- Step 24 in final readiness phase: readiness docs, API contract, demo seed helper, review package.

Please perform a full backend improvement review before frontend integration.

Focus on:

1. Security and authorization.
2. ISP Admin cross-ISP isolation.
3. App User /me ownership isolation.
4. Auth and MFA correctness.
5. Demo and deployment readiness.
6. Migration and database reproducibility.
7. Test coverage gaps.
8. Endpoint/schema consistency for frontend.
9. Stale documentation.
10. Any high-priority backend bugs before frontend starts.

Important active rules:

- ISP Admin endpoints must use get_current_isp_admin.
- ISP Admin queries must be scoped by current_admin.isp_id.
- App User /me routes must only use the authenticated App User.
- Router raw passwords must not be accepted or stored until encrypted credential storage exists.
- Demo seed helper must refuse to run when DEBUG=False.

Do not make large feature expansions.

Return prioritized findings:

- P0 critical
- P1 high
- P2 medium
- P3 polish

For each issue, include:

- file path
- why it matters
- recommended fix
- whether it should be fixed before frontend
