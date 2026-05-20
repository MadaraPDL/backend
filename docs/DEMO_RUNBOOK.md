# PulseFi Demo Runbook

Last updated: 2026-05-20

## Repositories

- Backend: C:\PulseFi\backend
- Admin web: C:\PulseFi\pulsefi-admin-web
- Mobile app: C:\PulseFi\pulsefi-mobile-app

## LAN Demo Setup

For phone testing, backend must run on LAN.

Get PC LAN IP:

ipconfig | findstr /i "IPv4"

Use the Wi-Fi IPv4 address as YOUR_PC_LAN_IP.

## Start Backend on LAN

cd C:\PulseFi\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Backend API for LAN clients:

http://YOUR_PC_LAN_IP:8000/api/v1

Swagger:

http://YOUR_PC_LAN_IP:8000/docs

## Start Admin Web

For PC only:

cd C:\PulseFi\pulsefi-admin-web
npm.cmd run dev

Open:

http://localhost:5173

For phone/another device:

cd C:\PulseFi\pulsefi-admin-web
npm.cmd run dev -- --host 0.0.0.0

Open:

http://YOUR_PC_LAN_IP:5173

## Admin Web LAN Env

C:\PulseFi\pulsefi-admin-web\.env.development.local:

VITE_API_BASE_URL=http://YOUR_PC_LAN_IP:8000/api/v1

Restart Vite after changing this file.

## Mobile LAN Env

C:\PulseFi\pulsefi-mobile-app\.env:

EXPO_PUBLIC_API_BASE_URL=http://YOUR_PC_LAN_IP:8000/api/v1

Start mobile:

cd C:\PulseFi\pulsefi-mobile-app
npm.cmd start

Open with Expo Go.

## Backend CORS for LAN Admin Web

C:\PulseFi\backend\.env should include:

BACKEND_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://YOUR_PC_LAN_IP:5173"]

Restart backend after changing .env.

## Password Reset from Phone

Backend .env should use:

FRONTEND_ADMIN_URL=http://YOUR_PC_LAN_IP:5173

Then reset links should open like:

http://YOUR_PC_LAN_IP:5173/reset-password?token=...

Do not use localhost links on phone.

## Demo Flow

Platform Admin:
1. Login as Platform Admin.
2. Show platform overview.
3. Show ISP management.
4. Show ISP Admin invitations/accounts.

ISP Admin:
1. Login as ISP Admin.
2. Show overview.
3. Show users, invitations, plans, subscriptions, and routers.
4. Run full simulator ingestion.
5. Show generated devices, usage records, alerts, and router action logs.
6. Generate prediction/recommendation or run intelligence.
7. Show analytics/reports/monitoring.
8. Review App User plan-change request.

Mobile App User:
1. Login as App User.
2. Show Home usage/subscription summary.
3. Show Usage records.
4. Show Devices.
5. Confirm router mode/capability label.
6. Create custom download/upload bandwidth limit.
7. Execute pending policy.
8. Show Alerts and mark unread alert as read.
9. Show Insights predictions/recommendations.
10. Request plan change from recommendation.
11. Show Profile.
12. Toggle Light/Dark theme.
13. Logout and test session restore.

## Local MFA Recovery Note

For local demo only, if Platform Admin asks for 2FA even though MFA was never activated, check the admins table.

Safe local demo state for no 2FA:

mfa_enabled = false
mfa_required = false
mfa_secret = NULL
preferred_mfa_method = NULL

If mfa_required = true and mfa_enabled = false, login should show MFA setup, not normal 2FA verification.

Do not use manual DB MFA reset as a production solution.

## Reset Local Auth Rate Limits

When DEBUG=True:

curl.exe -X POST http://127.0.0.1:8000/api/v1/auth/rate-limit/reset

## Final Checks

Backend:

cd C:\PulseFi\backend
.\venv\Scripts\python.exe -m compileall app tests
.\venv\Scripts\python.exe -m pytest

Admin web:

cd C:\PulseFi\pulsefi-admin-web
npm.cmd run lint
npm.cmd run build

Mobile:

cd C:\PulseFi\pulsefi-mobile-app
npx.cmd tsc --noEmit --pretty false
npm.cmd start
