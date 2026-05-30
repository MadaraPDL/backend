<!-- STEP_55F_PUSH_SMOKE_CHECKLIST_START -->
## Push Notification Smoke Checklist

Run this only after rebuilding/installing the mobile APK or development build.

Do not expose secrets, push tokens, .env values, database URLs, API keys, JWT secrets, Expo credentials, Render/Vercel/Neon/Brevo secrets, or MFA codes.

Backend checks:

- Confirm backend is deployed after Step 55A/55C/55D.
- Confirm the `app_user_push_tokens` migration has applied.
- Login as an App User from the rebuilt mobile app.
- Confirm the mobile app can register a push token without showing it in the UI.
- Confirm token registration does not break login/session restore if permission is denied.

Mobile checks:

- Install rebuilt APK/development build.
- Login as App User.
- Accept notification permission.
- Close/background the app.
- Trigger one important event from backend/admin/simulator:
  - high usage / plan limit alert,
  - new device alert,
  - meaningful recommendation update,
  - approved/rejected service request update.
- Confirm a notification appears on device.
- Tap alert notification and confirm it opens Alerts.
- Tap recommendation notification and confirm it opens More > Predictions & recommendations.
- Tap service request update notification and confirm it opens More > Service requests.

Anti-spam checks:

- Repeat normal high usage within the normal alert repeat window and confirm duplicate notification spam does not occur.
- Confirm `stay_current` recommendations do not send push notifications.
- Confirm backend event still succeeds if push sending fails or no token exists.

Deferred/future checks:

- Expo receipt polling/storage is future work.
- Automated token cleanup from invalid receipt errors is future work.
- Direct Firebase integration is future work unless explicitly selected.
<!-- STEP_55F_PUSH_SMOKE_CHECKLIST_END -->

# PulseFi Final Live Smoke Checklist

## Purpose

This checklist defines the final deployed PulseFi smoke test scope before presentation/demo.

The final live smoke test is still deferred. This document only prepares the checklist.

## Safety Rules

- Do not expose or paste secrets.
- Do not print .env values.
- Do not use destructive production actions unless intentionally testing a reversible workflow.
- Do not create noisy or spammy production data.
- Keep DEBUG disabled in production.
- Confirm debug tokens are not exposed in production responses.
- Protect MFA codes and credentials.
- Do not store router passwords.

## Environments

Backend:

- Render deployed API
- Production DEBUG should be false
- OpenAPI should load if expected
- Health endpoint should respond

Admin web:

- Vercel deployed admin web
- Platform Admin login
- ISP Admin login
- MFA flow if enabled
- Session restore after refresh

Mobile:

- Expo / mobile deployed or test build flow
- App User login
- Usage, devices, alerts, insights, service requests
- PulseFi Assistant contextual/local chatbot MVP

## Backend Smoke Checks

- Health endpoint responds.
- OpenAPI loads if enabled.
- Auth login works for valid admin account.
- Invalid login fails safely.
- MFA-required account cannot bypass MFA.
- /auth/me returns correct role/session shape.
- Production invitation/reset responses do not expose debug tokens.
- ISP Admin endpoints stay scoped to the current ISP.
- App User endpoints stay scoped to the current App User.
- Intelligence endpoints do not crash.
- Existing rules-based predictions/recommendations/alerts still work.
- No ML runtime artifact is required for backend startup.

## Admin Web Smoke Checks

- Admin web loads from deployed URL.
- Login page renders correctly.
- Platform Admin can login.
- Platform Admin sees platform dashboard, not ISP dashboard.
- ISP Admin can login.
- ISP Admin sees ISP dashboard, not platform dashboard.
- Refresh keeps valid session.
- Logout clears session.
- Settings page opens correctly.
- Theme toggle works if present.
- No design-preview-only user role switch is visible in real app.
- No debug tokens appear in production UI.

## Mobile Smoke Checks

- App opens successfully.
- App User can login.
- Session restore works after app reload.
- Home shows selected router/service context.
- Usage screen loads official and estimated usage where available.
- Devices screen loads connected devices.
- Alerts screen loads and paginates alerts.
- Insights screen loads predictions and recommendations.
- Recommendation actions route correctly.
- Service requests screen works for current implemented scope.
- PulseFi Assistant opens from Home and More.
- Assistant answers with loaded context and does not pretend missing data exists.
- Keyboard input positioning remains fixed.

## ML Demo Checks

These checks are offline/local and not part of deployed runtime smoke:

- Run scripts/ml/generate_demo_usage_dataset.py.
- Run scripts/ml/train_usage_prediction_model.py.
- Run scripts/ml/evaluate_usage_prediction_model.py.
- Confirm metrics JSON includes MAE and RMSE.
- Confirm generated ML artifacts remain gitignored.
- Explain that deployed backend currently keeps rules-based intelligence as fallback.

## Deferred / Not Yet Claimed

- Push notifications remain future work.
- Production ML runtime integration remains future work unless explicitly added later.
- Router password storage remains deferred until encrypted credential storage exists.
- Final full live smoke has not been completed until this checklist is actually executed.

## Final Smoke Completion Criteria

Final live smoke can be marked complete only after:

- backend health/auth/core APIs pass deployed checks,
- admin web Platform Admin and ISP Admin flows pass,
- mobile App User core flows pass,
- Assistant core UX passes,
- production debug-token exposure is verified absent,
- no critical production regressions are found,
- report/presentation claims match implemented behavior.
