# PulseFi Push Notifications MVP

## Status

Step 55A-55E are complete for the implemented MVP scope.

Push notifications are now implemented across backend and mobile, but final live push smoke testing is still pending until the final APK/development build is rebuilt and installed.

## What was implemented

### Step 55A - Backend push token storage

The backend now stores App User Expo push tokens.

Implemented backend endpoints:

- `POST /api/v1/app-user/me/push-tokens`
- `GET /api/v1/app-user/me/push-tokens`
- `DELETE /api/v1/app-user/me/push-tokens/{token_id}`

The token storage is scoped to the authenticated App User. App Users cannot list or disable another user's push tokens.

### Step 55B - Mobile push token registration

The mobile app now uses `expo-notifications` to:

- ask for notification permission,
- create the Android notification channel,
- read the EAS project ID,
- get the Expo push token,
- register the token with the backend after login/session restore.

If notification permission is denied or token registration fails, the mobile app continues normally.

### Step 55C - Backend Expo push sender service

The backend now has an Expo push sender service that can send notifications through Expo Push Service.

The sender service:

- validates Expo push token format,
- chunks outgoing messages,
- sends safe notification payloads,
- returns attempted/accepted/failed counts,
- treats delivery as best-effort.

### Step 55D - Backend event triggers

The backend now triggers push notifications for important events only:

- high usage / plan limit alerts,
- rapid high usage alerts,
- new device alerts,
- meaningful recommendation updates,
- approved/rejected service request updates.

Push notifications are intentionally generic. Notification bodies do not include sensitive details, admin responses, secrets, tokens, database URLs, or personally sensitive data.

Push sending is best-effort and must never break core backend behavior. If token lookup or Expo sending fails, the business event still succeeds.

### Step 55E - Mobile notification tap routing

The mobile app now routes notification taps:

- alert notifications open the Alerts tab,
- recommendation notifications open More > Predictions & recommendations,
- service request update notifications open More > Service requests.

The app also handles notification taps when opened from a killed/background state by checking the last notification response.

## Anti-spam behavior

Push notifications are tied to backend event creation. The backend already suppresses duplicate alert/recommendation records.

Important repeat windows:

- normal plan usage alerts are guarded by the existing 24-hour plan alert repeat window,
- rapid high usage alerts are guarded by the existing 30-minute rapid alert repeat window,
- same-state recommendations do not repeatedly notify,
- `stay_current` recommendations do not dispatch push notifications.

## Limitations

- Final live push smoke is still pending.
- A rebuilt APK/development build is required to test Android remote push behavior properly.
- Push notification receipt depends on Expo/device delivery and cannot be treated as guaranteed.
- No Firebase direct integration was added; this MVP uses Expo push notifications.
- Notification delivery receipts are not yet polled/stored.
- Push token cleanup based on Expo receipt errors is future work.

## Demo wording

Use this wording:

> PulseFi includes a push notification MVP. The mobile app registers an Expo push token, the backend stores it per App User, and important events such as high usage, new devices, recommendations, and service request updates can dispatch safe generic push notifications. Notification taps route users to the relevant app screen. Final live push delivery testing is done after rebuilding the APK.

Avoid saying:

- Push notifications are fully production-hardened.
- Delivery is guaranteed.
- Firebase Cloud Messaging is directly integrated.
- Push receipts are stored and monitored.

## Files involved

Backend:

- `app/models/app_user_push_token.py`
- `app/schemas/app_user/push_tokens.py`
- `app/services/app_user/push_token_service.py`
- `app/api/v1/endpoints/app_user/push_tokens.py`
- `app/services/notifications/expo_push_service.py`
- `app/services/notifications/push_dispatch_service.py`
- alert/recommendation/service-request trigger hooks

Mobile:

- `src/api/pushTokens.ts`
- `src/notifications/pushNotifications.ts`
- `App.tsx`
- `src/navigation/types.ts`
- `app.json`
- `package.json`
- `package-lock.json`

## Next required step

Rebuild the mobile APK/development build before final mobile push testing.

Final full live smoke remains deferred until APK rebuild and final deployment checks are ready.
