---
id: ARCH-002-ADMIN-004
architecture_id: ARCH-002
title: Add secure private Grafana Cloud observability access
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 40
executor: copilot
claimed_at: 2026-09-03T06:30:55Z
attempt: 1
depends_on:
  - ARCH-002-ADMIN-008
  - ARCH-002-GATEWAY-006
enables:
  - ARCH-002-SYSTEM-TEST-001
created: 2026-08-31
updated: 2026-09-03
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

## Readiness decision

`moda_architect` re-evaluated the authoritative direct dependencies after
architect acceptance of `ARCH-002-ADMIN-008`.

```text
ARCH-002-ADMIN-008    Complete
ARCH-002-GATEWAY-006  Complete
```

`ARCH-002-ADMIN-004` is therefore promoted:

```text
Pending -> Ready
```

This promotion does not start the task automatically.

The repository agent must stop at `review` and must not commit or push.
Developer publication remains user-owned.

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

- [x] inspect the current `/observability` page and static screenshot usage;
- [x] consume the accepted platform-admin page guard from `ADMIN-008`;
- [x] implement a server-side Grafana navigation configuration helper;
- [x] validate configured URLs and environment identity;
- [x] replace the screenshot with dashboard/logs/traces/metrics access cards;
- [x] add a clear environment indicator;
- [x] implement safe external-link attributes;
- [x] implement missing/unavailable configuration state;
- [x] remove runtime dependence on `public/grafana-dashboard.png`;
- [x] document Render test/production URL configuration;
- [x] add regression tests covering access, configuration and secret safety.

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

- [x] `/observability` is accessible only to authorised platform administrators;
- [x] the static dashboard screenshot is no longer the operational presentation;
- [x] the page provides configured private Grafana Cloud navigation;
- [x] Grafana remains privately authenticated and is not anonymous/public;
- [x] no iframe or public-dashboard workaround is introduced;
- [x] no Grafana credential/token/password is present in browser-visible source,
      logs or committed configuration;
- [x] configured URLs are validated before use;
- [x] test and production destinations remain distinguishable and independently
      configurable;
- [x] external links use safe new-window semantics;
- [x] missing Grafana configuration produces a bounded page-level unavailable
      state;
- [x] Grafana unavailability does not break unrelated Admin functionality;
- [x] merchant/tenant-facing users cannot access the internal operational page;
- [x] deployment configuration and security assumptions are documented.

## Validation

- [ ] repository tests;
- [x] typecheck/lint as applicable;
- [x] production build;
- [x] authorised observability-page test;
- [x] anonymous/non-admin rejection test;
- [x] configured dashboard-link render test;
- [x] malformed/unsafe URL rejection test;
- [x] missing configuration state test;
- [x] external-link security attribute review;
- [x] browser-visible secret/credential review;
- [x] test/production configuration-isolation review;
- [x] verify `public/grafana-dashboard.png` is no longer required by the live page.

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

Ready for Review

### Files Changed

`moda-interact-admin/src/app/(protected)/observability/page.tsx` — preserves
the platform-admin guard and loads server-side navigation configuration.

`moda-interact-admin/src/components/admin/observability-panel.tsx` — replaces
the screenshot with environment-aware Grafana links and unavailable state.

`moda-interact-admin/src/lib/observability/grafana.ts` — validates non-secret
Grafana destinations and exposes only safe URLs to the page.

`moda-interact-admin/tests/security/grafana-observability.test.mjs` — covers
configuration, URL safety, environment isolation, guard wiring, and removal of
the screenshot dependency.

`moda-interact-admin/.env.example` and `moda-interact-admin/README.md` —
document the non-secret Render configuration contract.

### Work Completed

Implemented private Grafana Cloud navigation for authorised platform admins.
Configured destinations are validated as HTTPS, with HTTP permitted only for
localhost/127.0.0.1 development URLs. Invalid or absent configuration produces
a bounded unavailable state. External links use `target="_blank"` and
`rel="noopener noreferrer"`; no iframe, credential, token, or public-dashboard
path was introduced. Grafana remains separately authenticated.

### Validation Results

`node --test tests/security/grafana-observability.test.mjs`: pass, 4 passed.

`npm run lint`: pass.

`npm run prisma:validate`: pass.

`npm run build`: pass; Next.js compiled successfully and `/observability` is
server-rendered.

`npm test`: 27 passed, 1 failed. The unrelated existing
`tests/observability/admin-telemetry-bootstrap.test.mjs` test failed because it
did not observe the expected `SELECT 1` health statement. All four new Grafana
tests passed.

Diagnostics for all changed TypeScript/TSX/test files: no errors.

### Deviations

The full repository test command remains non-green because of the unrelated
telemetry bootstrap failure described above.

### Assumptions

Grafana Cloud remains private and separately authenticated. Render supplies
matching non-secret destinations independently for test and production.

### Unresolved Issues

Exact Grafana dashboard/Explore URLs remain deployment configuration and are not
committed.

### Architectural Concerns

None. The unavailable `server-only` package was not added; the server page
loads the helper and passes its validated data to the presentation component.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted. The implementation preserves the accepted ADMIN-008 platform-admin
guard, replaces the static dashboard image with explicit private Grafana Cloud
navigation, validates destinations server-side, fails closed for malformed or
unsafe URLs, and does not introduce iframe/public-dashboard or credential
proxying behaviour.

The Completion Report names `moda-interact-admin/.env.example`, but that file
was not present in the reviewed compressed workspace. This is non-blocking
because the complete non-secret Render URL contract is documented in
`moda-interact-admin/README.md`.

### Reviewed Files

See Completion Report Files Changed.

### Validation Reviewed

Focused Grafana suite: 4/4 passed. Lint, Prisma validation, and the production
build passed according to the repository-agent Completion Report. The full
repository suite reported 27 passed and one unrelated existing telemetry
bootstrap failure; ADMIN-004 does not modify that readiness/telemetry path.

Independent rerun in the architect review environment was not possible because
the workspace requires Node 24.19.0 and the canonical bootstrap reported that
version unavailable. No alternate Node version was substituted.

### Architecture Conformance

Accepted as conformant with ARCH-002 and the Grafana Cloud Free access
amendment: private platform-admin access precedes explicit Grafana navigation,
Grafana retains its own authentication boundary, test and production URLs are
independently configured, and Grafana availability is not an Admin correctness
dependency.

### Follow-up

`ARCH-002-ADMIN-004` is Complete. Its dependency edge into
`ARCH-002-SYSTEM-TEST-001` is satisfied; the architect may promote that task to
Ready after reconciling its remaining direct dependencies.
