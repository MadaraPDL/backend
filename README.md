# Latest Backend Progress � Step 15 Complete

The Platform Admin backend MVP is complete and tested.

Completed Platform Admin features:
- Create/list/view/update ISPs.
- Invite ISP Admins.
- List ISP Admins under an ISP.
- View/update/deactivate/reactivate ISP Admin accounts.
- View platform dashboard summary metrics.
- List ISP Admin invitations.
- Filter ISP Admin invitations by pending, accepted, revoked, or expired.
- Revoke pending ISP Admin invitations.

Latest Platform Admin endpoints:
- `POST /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps/{isp_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}`
- `POST /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `GET /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admin-invitations/{invitation_id}/revoke`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `GET /api/v1/platform-admin/summary`

Current next backend step:
- Step 16: ISP Admin management endpoints.

Important access rule:
- Only Platform Admin can manage ISPs and ISP Admin accounts.
- ISP Admins cannot invite other ISP Admins and cannot manage other ISPs.
- ISP Admins will manage only their own ISP's users, plans, subscriptions, routers, reports, and analytics.

---
# Latest Backend Progress

The backend has moved beyond the older auth-testing phase.

Current completed backend progress:
- FastAPI backend foundation complete.
- PostgreSQL async SQLAlchemy setup complete.
- Core SQLAlchemy models complete.
- Auth models, schemas, services, and endpoints complete.
- Protected current-user route system complete.
- Platform Admin ISP management complete.
- Platform Admin ISP Admin invitation flow complete.
- Platform Admin ISP Admin account management complete.
- Platform Admin dashboard summary metrics complete.

Current next backend step:
- Step 15E: Platform Admin pending ISP Admin invitation management.

Latest Platform Admin endpoints:
- `POST /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps`
- `GET /api/v1/platform-admin/isps/{isp_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}`
- `POST /api/v1/platform-admin/isps/{isp_id}/admin-invitations`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins`
- `GET /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `PATCH /api/v1/platform-admin/isps/{isp_id}/admins/{admin_id}`
- `GET /api/v1/platform-admin/summary`

Important access rule:
- Only Platform Admin can manage ISPs and ISP Admins.
- ISP Admins cannot invite other ISP Admins and cannot manage other ISPs.
- ISP Admins will later manage only their own ISP's users, plans, subscriptions, routers, reports, and analytics.

---
# PulseFi Backend

PulseFi is a Smart Network Monitoring and Optimization System built for internet users and ISP administrators.

The project is designed as a deployable Final Year Project system, not just a simple prototype. Its goal is to help users understand their internet usage, help ISP admins manage users and plans, and add smart analysis features such as predictions, alerts, plan recommendations, and device-level optimization.

## Project Idea

PulseFi is a platform that connects users, ISP admins, subscriptions, routers, devices, usage data, alerts, predictions, recommendations, and reports into one smart system.

The main idea is:

A regular user should be able to open a mobile app and clearly understand:

- How much internet they used.
- Which subscription they are viewing.
- Which devices are connected to their network.
- How much each device is using when supported.
- Whether a new unknown device connected.
- Whether their usage is too high.
- Whether they may exceed their plan.
- Which plan may be better for them.
- Whether they should stay on their current plan.
- How to limit or prioritize a selected device.

At the same time, an ISP Admin should be able to open a web dashboard and manage:

- Users.
- Internet plans.
- User subscriptions.
- Routers.
- Usage records.
- Connected devices.
- Alerts.
- Recommendations.
- Reports.
- Network analytics.
- Router action logs.

A Platform Admin manages the higher-level system and creates or manages ISP-level access.

## Why PulseFi Exists

Many users do not clearly understand where their internet usage goes.

They may know their total plan limit, but they often do not know:

- Which device is consuming the most.
- Whether someone new connected to the network.
- Whether they are likely to exceed their plan.
- Whether their current plan is too small or too large.
- Whether a better plan exists.
- Whether a device should be limited or prioritized.

PulseFi solves this by combining monitoring, prediction, alerts, recommendations, and device optimization.

## Main User Types

### 1. Platform Admin

The Platform Admin is the highest-level admin.

The Platform Admin can:

- Manage ISPs.
- Create or invite ISP Admins.
- Manage platform-level access.
- Oversee the system at a high level.

The Platform Admin does not represent a normal internet customer. This role manages the platform itself.

### 2. ISP Admin

The ISP Admin represents an internet service provider.

The ISP Admin can:

- Manage app users.
- Invite users to create accounts.
- Manage subscription plans.
- Assign user subscriptions.
- Manage router information.
- Assign routers to user subscriptions.
- View usage records.
- View device records.
- View alerts.
- View prediction/recommendation summaries.
- Generate reports.
- View network performance analytics.
- View router action logs.
- Handle subscription upgrade/downgrade requests from users.

### 3. App User

The App User is the regular internet customer using the mobile app.

The App User can:

- Log in to the mobile app.
- View their subscription or subscriptions.
- View total internet usage.
- View connected devices.
- View per-device usage when supported by router capabilities.
- Receive high-usage alerts.
- Receive new-device-connected alerts.
- View future usage predictions.
- View plan recommendations.
- Request a subscription upgrade or downgrade.
- Select a device.
- Apply a bandwidth limit to a device.
- Prioritize a device.

## Main Features

## User Mobile App Features

The mobile app is for regular internet users.

### Dashboard

The user dashboard should show:

- Current subscription summary.
- Total usage.
- Remaining data if the plan has a limit.
- Usage trend.
- Alerts summary.
- Connected devices summary.
- Prediction summary.
- Recommendation summary.

If the user has only one subscription, the app should show it directly.

If the user has multiple subscriptions, the app should allow them to choose which subscription to view.

### Usage Monitoring

Users can view:

- Total usage.
- Daily/monthly usage records.
- Usage by subscription.
- Per-device usage when available.

### Device Monitoring

Users can view connected devices such as:

- Phones.
- Laptops.
- Tablets.
- Smart TVs.
- Gaming consoles.
- Unknown devices.

Device information may include:

- Device name.
- MAC address.
- IP address.
- Vendor/manufacturer if available.
- First seen time.
- Last seen time.
- Online/offline status.
- Usage amount when available.

### Alerts

Users can receive alerts such as:

- High usage alert.
- New device connected alert.
- Plan exceed risk alert.
- Router policy failed alert.

### Predictions

The system can predict future usage based on historical behavior.

Examples:

- Estimated usage by end of month.
- Risk of exceeding current plan.
- Usage trend increasing or decreasing.

The first MVP can use rule-based or statistical logic before adding more advanced ML.

### Recommendations

The system can recommend:

- Upgrade to a better plan.
- Downgrade to a smaller plan.
- Stay on the current plan.
- Reduce usage.
- Review high-consuming devices.

Recommendations should include:

- Reason.
- Confidence score.
- Related prediction when available.

### Device Optimization

Users can optimize selected devices by:

- Limiting bandwidth.
- Prioritizing a device.

Example:

A user may prioritize their work laptop or gaming device.

A user may limit an unknown device or a device using too much bandwidth.

This feature depends on router capability.

## ISP Admin Dashboard Features

The ISP Admin web dashboard should help the ISP manage users and network-related data.

### User Management

ISP Admins can:

- View users.
- Invite users.
- Create/manage user accounts through invitation flow.
- Update user status.
- View user subscriptions.
- View routers assigned to users.

### Plan Management

ISP Admins can:

- Create plans.
- Update plans.
- Deactivate plans.
- View plan details.
- Compare plan usage patterns.

Plans may include:

- Plan name.
- Speed.
- Data limit.
- Price.
- Description.
- ISP ownership.

### Subscription Management

ISP Admins can:

- Assign a plan to a user.
- View user subscriptions.
- Handle multiple subscriptions per user.
- Activate/deactivate subscriptions.
- Handle user upgrade/downgrade requests.

A user may have more than one active subscription, such as:

- Family subscription.
- Work subscription.
- Gaming subscription.

### Router Management

ISP Admins can:

- Add router information.
- Assign router to a subscription.
- View router capabilities.
- View router status.
- View router action logs.

Routers are linked to subscriptions, not just users, because one user may have multiple subscriptions.

One subscription may have multiple routers, such as:

- Main router.
- Repeater.
- Secondary router.

### Reports and Analytics

ISP Admins can generate or view:

- Usage reports.
- Device reports.
- Recommendation summaries.
- Network performance summaries.
- Router action logs.

## Platform Admin Dashboard Features

The Platform Admin dashboard is for managing the system at a higher level.

Platform Admins can:

- Create/manage ISPs.
- Invite ISP Admins.
- View ISP Admin accounts.
- Manage platform-level admin access.
- Deactivate or suspend ISPs/admins if needed.

## Router Integration Concept

PulseFi should not be designed as supporting only one router type forever.

In real deployment, users may already have different routers. Some routers may expose many features, while others expose only limited information.

Because of this, PulseFi should use a router adapter architecture.

## Router Adapter Architecture

A router adapter is a backend layer that communicates with a specific router type, protocol, or simulator.

The backend should not directly hard-code one router model everywhere.

Instead, it should use adapter logic so that different router integrations can be added over time.

## Router Feature Tiers

### Full Mode

Full mode means the router supports most required features:

- Total usage.
- Connected devices.
- Per-device usage.
- New-device detection.
- Bandwidth limiting.
- Device prioritization.

### Partial Mode

Partial mode means the router supports some features but not all.

For example, the router may support connected-device detection but not bandwidth limiting.

### Basic Mode

Basic mode means router-level integration is not available or is very limited.

In this mode, PulseFi can still support:

- Subscription-level usage.
- Predictions.
- Plan recommendations.
- ISP-side analytics.

But it may not support:

- Reliable per-device monitoring.
- Device-level bandwidth limiting.
- Device prioritization.

## MVP Router Plan

For the first deployable MVP:

- Build a simulator adapter for demo reliability.
- Support one first router integration family or protocol if possible.
- Use capability-based logic so unsupported features are hidden or disabled.

This makes the system realistic and deployable without pretending it supports every router from day one.

## Authentication and Security

PulseFi uses a secure invitation-based onboarding design.

## Invitation-Based Onboarding

The system should not use temporary passwords.

Instead:

1. Platform Admin invites ISP Admins.
2. ISP Admins invite regular app users.
3. The invited person receives an expiring setup link.
4. The invited person accepts the invitation.
5. The invited person sets their own password.
6. The invited person chooses their username.
7. The system verifies their email.

## Login

Users/admins can log in using:

- Email, or
- Username

The login request includes account type because admins and app users are stored in separate tables.

Account types:

- `admin`
- `app_user`

## Password Security

Passwords are hashed using Argon2 through `pwdlib[argon2]`.

Plain passwords are never stored.

## JWT Authentication

Access tokens are JWTs.

JWT payload includes:

- Subject/account ID.
- Account type.
- Issued-at time.
- Expiration time.

## Forgot Password

PulseFi includes a forgot-password flow.

The flow uses:

- Expiring reset tokens.
- Single-use reset links.
- Generic responses to avoid account enumeration.
- Password changed time to help invalidate older sessions.

## Email Verification

Email verification is included because emails are used for:

- Invitations.
- Password reset.
- Notifications.
- Recovery.
- Email-based MFA.

## MFA / 2FA

PulseFi supports multiple MFA methods.

Supported/planned methods:

- Authenticator app MFA.
- Email OTP MFA.
- Backup recovery codes.

Admin accounts should be strongly guided toward authenticator-app MFA.

Platform Admins and ISP Admins should have MFA required or strongly enforced.

Regular users may have optional MFA initially.

## Backup Recovery Codes

Backup codes are:

- Single-use only.
- Stored as hashes.
- Revoked/replaced when regenerated.
- Shown raw only once to the user.

## SMS Verification

SMS verification is deferred for now because it adds recurring production cost and is not necessary for the first release.

## Backend Technology

The backend uses:

- FastAPI
- PostgreSQL
- Async SQLAlchemy
- asyncpg
- Pydantic
- JWT
- Argon2 password hashing

## Backend Structure

Main structure:

- `app/main.py`
- `app/core/config.py`
- `app/core/security.py`
- `app/db/session.py`
- `app/db/base.py`
- `app/api/v1/router.py`
- `app/api/v1/endpoints/`
- `app/models/`
- `app/schemas/`
- `app/services/`

## Current Backend Status

Completed or mostly completed:

- Backend foundation.
- FastAPI setup.
- PostgreSQL connection setup.
- Health endpoint.
- Swagger documentation loading.
- Core SQLAlchemy models.
- Auth SQLAlchemy models.
- Auth schemas split into focused modules.
- Auth services split into focused modules.
- Auth endpoints split into focused modules.
- Swagger/OpenAPI loads successfully.

Current phase:

Step 13F — Test authentication endpoints through Swagger/Postman.

## Current Auth Endpoints

Current auth endpoints include:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/mfa/verify`
- `POST /api/v1/auth/invitations/accept`
- `POST /api/v1/auth/password/forgot`
- `POST /api/v1/auth/password/reset`
- `POST /api/v1/auth/email/verify`

## Next Backend Step

The next backend step is to test the auth endpoints.

After auth testing, the next major step is:

Step 14 — Protected route system and current user endpoint.

This includes:

- `get_current_account`
- `get_current_admin`
- `get_current_app_user`
- role checks
- `GET /api/v1/auth/me`

## Development Commands

Run the backend from the project root:

`.\venv\Scripts\python.exe -m uvicorn app.main:app --reload`

Swagger:

`http://127.0.0.1:8000/docs`

Root endpoint:

`/`

Health endpoint:

`/api/v1/health`

Basic import test:

`.\venv\Scripts\python.exe -c "from app.main import app; print('App imported successfully')"`

API router import test:

`.\venv\Scripts\python.exe -c "from app.api.v1.router import api_router; print('API router imported successfully')"`

## Deployment Goal

PulseFi should be deployable by presentation time.

The MVP should prioritize:

- Reliable backend.
- Clear user/admin flows.
- Working authentication.
- Working database.
- Demo-friendly router simulator.
- Usage data flow.
- Alerts.
- Predictions/recommendations.
- Reports.
- Frontend integration.

Router support should be realistic:

- Do not claim universal router support from day one.
- Use simulator + first supported router/protocol.
- Use feature capabilities to decide which features are available.

## Project Philosophy

PulseFi should be:

- Practical.
- Deployable.
- Clear to explain.
- Secure.
- Modular.
- Expandable.
- Realistic for an FYP.
- Strong enough to become a real product later.

