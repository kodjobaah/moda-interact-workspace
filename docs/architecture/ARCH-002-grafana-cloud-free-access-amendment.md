# ARCH-002 Amendment — Grafana Cloud Free Admin Access

Date: 2026-08-31

## Decision

Moda Interact currently uses a basic Grafana Cloud Free account.

ARCH-002 therefore does **not** require private silent iframe embedding for the
Admin observability experience at this stage.

The accepted presentation model is:

```text
Moda platform administrator
        |
        v
admin.modainteract.com/observability
        |
        | authenticated by Moda Admin
        v
private observability navigation page
        |
        | explicit external link
        v
Grafana Cloud
        |
        | Grafana's own authentication/session
        v
private Grafana dashboards / Explore
```

The operational telemetry remains private. The Admin application must never
switch a Grafana dashboard to public/anonymous sharing merely to avoid a second
login or to make iframe embedding possible.

## Why

The previous `ARCH-002-ADMIN-004` design allowed an iframe only where the
selected Grafana account supported architecture-conformant private authenticated
embedding.

That capability is not part of the currently selected basic Grafana Cloud Free
operating model. Building a custom Grafana authentication proxy or purchasing an
Enterprise/OEM arrangement is not justified merely to remove a second login from
an internal control-plane application.

## Current boundary

```text
Moda Admin authentication     -> Auth.js / Google + PlatformAdmin
Grafana authentication        -> Grafana Cloud account/session
Moda authorisation            -> controls access to /observability
Grafana authorisation         -> controls access inside Grafana Cloud
```

The two identity/session boundaries remain independent.

## Configuration

Admin may consume non-secret, deployment-specific URLs such as:

```text
GRAFANA_BASE_URL
GRAFANA_PLATFORM_DASHBOARD_URL
GRAFANA_LOGS_URL
GRAFANA_TRACES_URL
GRAFANA_METRICS_URL
```

These values are navigation destinations, not credentials.

Test and production Render services must receive environment-appropriate URLs.
No Grafana password, service-account token, API token or authorization header is
placed in browser-visible configuration or committed to source control.

## Development behaviour

Grafana access is not a local Admin correctness dependency.

If Grafana URL configuration is absent in development, `/observability` should
render a bounded "not configured" state while the rest of Admin continues to
work.

## Deferred alternatives

The following remain valid future architecture changes if cost/UX requirements
justify them:

- Grafana Cloud authenticated embedding under a suitable commercial agreement;
- an architecture-reviewed authenticated proxy/embedding bridge;
- self-managed Grafana with an approved authentication model.

None is required by the current ARCH-002 implementation.

## Task impact

`ARCH-002-ADMIN-004` is narrowed to secure authenticated **access/navigation**
to private Grafana Cloud rather than iframe embedding.

No new `GATEWAY-008` Grafana proxy task is required.

`ARCH-002-ADMIN-004` continues to depend on:

```text
ARCH-002-ADMIN-008
ARCH-002-GATEWAY-006
```

and continues to enable:

```text
ARCH-002-SYSTEM-TEST-001
```
