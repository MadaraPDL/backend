<!-- STEP_55F_PUSH_REPORT_ALIGNMENT_START -->
## Push Notifications MVP Report/Demo Alignment

PulseFi now includes a push notification MVP.

Accurate report/demo claim:

> PulseFi includes a push notification MVP where the mobile app registers an Expo push token, the backend stores it for the authenticated App User, and important events can dispatch safe generic push notifications. Notification taps route users to the relevant mobile screen.

Implemented push notification events:

- high usage / plan limit alerts,
- rapid high usage alerts,
- new device alerts,
- meaningful recommendation updates,
- approved/rejected service request updates.

Important limitations:

- Final live push smoke is still pending.
- A rebuilt APK/development build is required for Android remote push testing.
- Push delivery is best-effort and cannot be guaranteed.
- Expo push receipts are not yet stored or monitored.
- Firebase direct integration was not added.

Avoid claiming:

- push notifications are fully production-hardened,
- delivery is guaranteed,
- Firebase Cloud Messaging is directly integrated,
- push receipt lifecycle cleanup is implemented.
<!-- STEP_55F_PUSH_REPORT_ALIGNMENT_END -->

# PulseFi Report and Demo Alignment

## Purpose

This document keeps the PulseFi final report, presentation, and demo aligned with the real implemented system.

It should prevent overclaiming. Anything listed as implemented should exist in the backend, mobile app, or admin web. Anything not implemented yet should be described as future work or deferred scope.

## Current Implementation Status

### Backend

The backend is implemented with FastAPI, PostgreSQL, async SQLAlchemy, JWT authentication, role-based access, MFA support, invitation flows, password reset, ISP scoping, usage ingestion, predictions, recommendations, alerts, analytics, and admin/app-user APIs.

Important backend safety rules:

- ISP Admin data must stay scoped by the current admin ISP.
- Production debug tokens must not be exposed.
- Secrets, database URLs, API keys, JWT secrets, Render/Vercel/Neon/Brevo values must never be committed or shown.
- Router passwords must not be stored until encrypted credential storage exists.
- Existing rules-based intelligence remains the deployed fallback.

### Mobile App

The mobile app includes App User flows for usage, devices, alerts, insights, recommendations, service requests, account/package views, and the PulseFi Assistant chatbot-style MVP.

The Assistant is currently a local/contextual chatbot MVP. It does not call an external LLM and does not include client-side AI/API keys.

### Admin Web

The admin web supports Platform Admin and ISP Admin workflows, including login/session handling, dashboard views, ISP/admin/user management flows, router/network management views, intelligence/monitoring sections, and settings-related flows according to the current implemented scope.

### Machine Learning

Step 53A added a real offline ML MVP for next-day usage prediction.

The ML MVP includes:

- generated PulseFi-style demo usage records,
- supervised training for next-day usage prediction,
- MAE and RMSE evaluation,
- saved local artifacts under artifacts/ml/,
- deterministic tests under tests/ml/,
- dedicated documentation in docs/ML_MVP.md.

The current ML MVP is offline/demo-safe and is not wired into deployed backend runtime predictions.

## What We Can Honestly Claim

PulseFi can honestly claim:

- The system includes a deployed backend and connected admin/mobile app scope.
- The backend supports role-based APIs for Platform Admin, ISP Admin, and App User workflows.
- ISP Admins can manage and monitor their own ISP-scoped data.
- App Users can view usage, devices, alerts, insights, recommendations, and service request flows.
- PulseFi includes rules-based intelligence for predictions, recommendations, and alerts.
- PulseFi includes a real reproducible offline ML MVP for usage prediction.
- The ML MVP predicts next-day usage in GB using historical usage-style features.
- The ML MVP is evaluated using MAE and RMSE.
- Existing rules-based intelligence remains the safe deployed fallback.
- Push notifications are future work unless implemented later.
- Final full live smoke is deferred until remaining alignment and QA are ready.

## What We Should Not Claim Yet

Do not claim:

- The deployed backend is using the ML model in production.
- The mobile app calls an external LLM.
- Push notifications are implemented.
- Router admin password storage is implemented.
- The ML model was trained on real ISP production data.
- The ML model guarantees real-world prediction accuracy.
- Final full live smoke has been completed.

## Demo Script Outline

Recommended final demo order:

1. Show the landing/login flow.
2. Login as Platform Admin and show platform-level management.
3. Login as ISP Admin and show ISP-scoped dashboard sections.
4. Show app-user management, subscriptions, routers, monitoring, and intelligence areas.
5. Open the mobile app as an App User.
6. Show usage, devices, alerts, insights, recommendations, and service requests.
7. Show the PulseFi Assistant and explain it is contextual/local for MVP.
8. Show the ML MVP from the backend terminal:
   - generate demo dataset,
   - train usage prediction model,
   - evaluate model,
   - show MAE/RMSE metrics.
9. Explain that deployed runtime intelligence still uses safe rules-based fallback.
10. Explain future work: real ISP data training, optional backend ML integration, push notifications, and final full live smoke.

## ML Demo Commands

From the backend repo:

python scripts/ml/generate_demo_usage_dataset.py
python scripts/ml/train_usage_prediction_model.py
python scripts/ml/evaluate_usage_prediction_model.py

Metrics are saved in:

artifacts/ml/usage_prediction_metrics.json

Generated ML artifacts are local-only and gitignored.

## Final QA Still Deferred

Full final live smoke remains deferred until:

- report/presentation claims are aligned,
- mobile/admin/backend are confirmed clean,
- ML documentation is complete,
- remaining chosen scope is finalized.

## Recommended Next Work

Next safe tasks:

1. Keep ML offline/demo-only unless optional runtime loading is explicitly required.
2. Align final report and presentation wording with this document.
3. Prepare final live smoke checklist.
4. Only after that, perform final deployed backend/admin/mobile smoke testing.
