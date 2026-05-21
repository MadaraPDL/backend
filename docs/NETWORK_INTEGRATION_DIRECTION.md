# PulseFi Network Integration Direction

This document records the updated real-world network direction for PulseFi after ISP workflow discussion.

## Confirmed model

PulseFi should target local ISPs/resellers that receive bandwidth from an upstream provider but manage customers through their own server/router/RADIUS/API control point.

Typical structure:

```text
Upstream provider gives bandwidth
        ?
Local ISP server/router/RADIUS controls customers
        ?
Customers
        ?
PulseFi backend, admin web, and mobile app
```

If the customer is connected directly to the upstream company with no local ISP control point, PulseFi cannot automatically manage usage, subscriptions, speed, suspend/reactivate, or plans unless the upstream provider exposes an API.

## RADIUS direction

RADIUS is the preferred source for official customer usage and subscription/account control.

RADIUS commonly handles AAA:

- Authentication: is the customer allowed to connect?
- Authorization: what profile, speed, quota, or rules does the customer get?
- Accounting: how much upload/download usage did the customer consume?

PulseFi can integrate with RADIUS directly or through an ISP API connected to RADIUS.

Examples:

- Approve plan change in PulseFi ? ISP API updates RADIUS group/profile.
- Suspend unpaid user in PulseFi ? ISP API disables RADIUS user or moves user to suspended profile.
- Sync official usage ? PulseFi imports RADIUS accounting usage.

## Official usage vs per-device usage

PulseFi must separate two usage types.

### Official subscription usage

Source: RADIUS accounting or ISP API.

Used for:

- Mobile total usage.
- Plan quota usage.
- Billing and subscription status.
- Official usage history.

This is customer/subscription-level usage.

### Per-device usage

Source: customer router/CPE/router adapter when supported.

Used for:

- Phone/TV/laptop breakdown.
- Device trust/untrust.
- Device-level bandwidth limit.
- Device-level priority.
- Device-level alerts.

RADIUS usually sees the customer/session, not every home device behind NAT. Per-device usage requires a customer router/CPE or network device that can see individual devices.

## Router live-rate polling

Some routers show only live per-device usage rate, not historical total usage per device.

If the router exposes current upload/download rate, PulseFi can estimate usage by polling repeatedly:

```text
interval_usage_mb = (download_mbps + upload_mbps) * seconds_between_polls / 8
device_total = previous_device_total + interval_usage_mb
```

Example:

```text
TV current rate = 8 Mbps
polling interval = 10 seconds
estimated usage = 8 * 10 / 8 = 10 MB
```

This is an estimate, not official billing usage. If PulseFi is offline while the router only exposes live rates, usage during that offline period is missed.

## Router byte counters

If the router exposes cumulative byte counters, PulseFi should prefer delta accounting:

```text
delta = current_router_counter - last_saved_router_counter
stored_total = stored_total + delta
last_saved_router_counter = current_router_counter
```

If the counter goes backwards, the router likely rebooted or reset counters. PulseFi should treat that as a new baseline instead of creating negative usage.

## Router adapter direction

PulseFi should keep an adapter architecture.

Current/demo adapter:

- Simulator adapter.

Future adapters:

- RADIUS API adapter.
- MikroTik/PPPoE adapter.
- TP-Link/CPE adapter where safely possible.
- SNMP/TR-069/vendor API adapter if supported.
- CSV/manual import adapter for fallback.

Router admin panels prove that data may exist, but production integration should prefer APIs, counters, SNMP, RADIUS accounting, or vendor-supported mechanisms instead of fragile HTML scraping.

## Billing/subscription direction

ISP Admin should see who paid and who did not pay through Billing/Subscription Center, not through private App User alerts.

Future billing workflow:

```text
Invoice overdue
        ?
PulseFi marks subscription suspended
        ?
PulseFi calls ISP API/RADIUS adapter if available
        ?
RADIUS disables user or moves user to suspended profile
```

If no API exists, PulseFi should show external/manual action required.

## Alert visibility direction

ISP Admin should not see every private App User alert.

Recommended rule:

- App User sees personal usage/device/recommendation/plan-request alerts.
- ISP Admin sees operational/network/support alerts only.

Future backend should add alert visibility, such as `alert_visibility: app_user / isp_admin / both` or `is_admin_visible: true/false`.

## Demo positioning

For the final-year project demo, simulator endpoints represent the ISP network integration layer:

```text
Simulator stands in for RADIUS/API/router data
        ?
PulseFi backend
        ?
Admin web and mobile app
```

The project should be explained honestly:

- RADIUS/API is the official subscription and usage direction.
- Router/CPE integration is for optional per-device visibility/actions.
- Simulator is used because real ISP API credentials and router integrations are environment-specific.
