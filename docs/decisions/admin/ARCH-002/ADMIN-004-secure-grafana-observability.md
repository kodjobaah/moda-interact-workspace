---
id: ARCH-002-ADMIN-004
architecture_id: ARCH-002
title: Add secure private Grafana Cloud observability access
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-ADMIN-008
  - ARCH-002-GATEWAY-006
enables:
  - ARCH-002-SYSTEM-TEST-001
created: 2026-08-31
updated: 2026-08-31
---

# Add Secure Private Grafana Cloud Observability Access

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Presentation amendment:

`docs/architecture/ARCH-002-grafana-cloud-free-access-amendment.md`

Coordinator:

`moda_architect`

## Objective

Replace the current static Grafana dashboard visual in the Admin observability
page with secure navigation to the private Grafana Cloud environment used by
Moda platform administrators.

The current architecture uses Grafana Cloud Free and does not require private
silent iframe embedding. Grafana remains separately authenticated by Grafana
Cloud.

## Context

The current Admin application contains `/observability` and displays the static
`public/grafana-dashboard.png` image.

ARCH-002 separately owns:

```text
ADMIN-002   Admin OpenTelemetry instrumentation
GATEWAY-006 observability backend/transport/environment wiring
ADMIN-008   accepted platform-admin security boundary
```

This task owns only the Admin presentation/navigation boundary after those
prerequisites are available.

Operational telemetry is internal Moda Interact control-plane data. It must not
become public or anonymous merely to improve embedding convenience.

## Scope

- replace the static Grafana screenshot with a real observability access page;
- require the accepted `ADMIN-008` platform-admin authorisation boundary;
- provide explicit links to the private Grafana Cloud platform dashboard and,
  where configured, Logs, Traces and Metrics destinations;
- open Grafana destinations as external authenticated navigation rather than an
  iframe;
- display the resolved deployment environment clearly enough to distinguish
  test from production operations;
- consume only non-secret Grafana URL configuration in the Admin UI;
- validate configured destinations before rendering them;
- provide a safe "not configured" / unavailable state when Grafana navigation
  is not configured;
- preserve normal Admin functionality when Grafana is unavailable;
- document the environment/configuration contract for Render and system tests.

## Out of Scope

- Grafana iframe embedding;
- Grafana Cloud Enterprise/OEM authenticated embedding;
- a custom Grafana authentication/reverse-proxy bridge;
- public or anonymously shared Grafana dashboards;
- Grafana service-account/API credentials in the browser;
- implementing OpenTelemetry SDK instrumentation;
- OTLP/Loki backend provisioning;
- editing Grafana datasource or dashboard contents from Admin;
- tenant-facing analytics/reporting;
- gateway host routing;
- changing application business telemetry semantics.

## Requirements

The access invariant is:

```text
platform-admin authorisation
    -> Admin /observability
    -> explicit private Grafana Cloud link
    -> Grafana Cloud authentication/authorisation
```

Never:

```text
public/anonymous Grafana dashboard
    -> Admin link or iframe convenience
```

The implementation must:

- consume the accepted `ADMIN-008` platform-admin guard;
- never treat possession of a Grafana URL as authentication;
- never include Grafana credentials, service-account tokens, API tokens,
  passwords, cookies or authorization headers in rendered HTML/configuration;
- use deployment-specific non-secret URLs;
- ensure production and test navigation cannot be silently confused;
- validate URL protocols and reject unsafe/malformed configured destinations;
- prefer HTTPS destinations outside local development;
- use safe external-link behaviour (`target="_blank"` with
  `rel="noopener noreferrer"` or equivalent);
- fail locally/boundedly when configuration is absent or Grafana is unavailable;
- not make Grafana availability an Admin application correctness dependency;
- ensure Shopify merchant/tenant users cannot reach the internal observability
  page through the platform-admin boundary.

## Configuration Contract

Canonical non-secret Admin variables:

```text
GRAFANA_BASE_URL
GRAFANA_PLATFORM_DASHBOARD_URL
GRAFANA_LOGS_URL              # optional
GRAFANA_TRACES_URL            # optional
GRAFANA_METRICS_URL           # optional
```

`DEPLOYMENT_ENVIRONMENT_NAME` continues to identify:

```text
development
test
production
```

Test and production Render services must be configured with their intended
Grafana destinations independently.

No secret Grafana credential belongs in these variables.

## Work Items

- [ ] inspect the current `/observability` page and static screenshot usage;
- [ ] consume the accepted platform-admin page guard from `ADMIN-008`;
- [ ] implement a server-side Grafana navigation configuration helper;
- [ ] validate configured URLs and environment identity;
- [ ] replace the screenshot with dashboard/logs/traces/metrics access cards;
- [ ] add a clear environment indicator;
- [ ] implement safe external-link attributes;
- [ ] implement missing/unavailable configuration state;
- [ ] remove runtime dependence on `public/grafana-dashboard.png`;
- [ ] document Render test/production URL configuration;
- [ ] add regression tests covering access, configuration and secret safety.

## Interfaces / Contracts

Consumes:

```text
ARCH-002-ADMIN-008
    accepted platform-admin security boundary

ARCH-002-GATEWAY-006
    accepted Grafana/observability backend and environment wiring
```

Produces the Admin observability access surface validated by:

```text
ARCH-002-SYSTEM-TEST-001
```

No authenticated Grafana proxy contract is produced by this task.

## Dependencies

- `ARCH-002-ADMIN-008`
- `ARCH-002-GATEWAY-006`

## Enables

- `ARCH-002-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] `/observability` is accessible only to authorised platform administrators;
- [ ] the static dashboard screenshot is no longer the operational presentation;
- [ ] the page provides configured private Grafana Cloud navigation;
- [ ] Grafana remains privately authenticated and is not anonymous/public;
- [ ] no iframe or public-dashboard workaround is introduced;
- [ ] no Grafana credential/token/password is present in browser-visible source,
      logs or committed configuration;
- [ ] configured URLs are validated before use;
- [ ] test and production destinations remain distinguishable and independently
      configurable;
- [ ] external links use safe new-window semantics;
- [ ] missing Grafana configuration produces a bounded page-level unavailable
      state;
- [ ] Grafana unavailability does not break unrelated Admin functionality;
- [ ] merchant/tenant-facing users cannot access the internal operational page;
- [ ] deployment configuration and security assumptions are documented.

## Validation

- [ ] repository tests;
- [ ] typecheck/lint as applicable;
- [ ] production build;
- [ ] authorised observability-page test;
- [ ] anonymous/non-admin rejection test;
- [ ] configured dashboard-link render test;
- [ ] malformed/unsafe URL rejection test;
- [ ] missing configuration state test;
- [ ] external-link security attribute review;
- [ ] browser-visible secret/credential review;
- [ ] test/production configuration-isolation review;
- [ ] verify `public/grafana-dashboard.png` is no longer required by the live page.

## Implementation Notes

The Admin page is a navigation surface, not a Grafana authentication proxy.

A second Grafana login/session is acceptable under the current Grafana Cloud
Free architecture. Do not add application complexity or weaken telemetry
privacy merely to remove that login.

Reference code is provided in:

`docs/decisions/admin/ARCH-002/ADMIN-004-reference/`

It is an implementation accelerator only. `moda_admin` must inspect the accepted
`ADMIN-008` implementation and adapt the guard import/path rather than copying
blindly.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Grafana Cloud remains private and separately authenticated.

### Unresolved Issues

Exact Grafana dashboard/Explore URLs are deployment configuration and may not be
known until `GATEWAY-006` is accepted.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
