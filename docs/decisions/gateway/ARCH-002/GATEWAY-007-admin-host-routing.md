---
id: ARCH-002-GATEWAY-007
architecture_id: ARCH-002
title: Implement host-based admin gateway routing
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-002
  - ARCH-002-ADMIN-008
enables:
  - ARCH-002-GATEWAY-003
created: 2026-08-31
updated: 2026-08-31
---

# Implement Host-Based Admin Gateway Routing

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Replace the provisional `/admin/*` gateway mapping with the accepted production
admin host-routing contract so the root-based Next.js admin application can be
served through the public gateway while `moda-interact-admin` remains a private
Render HTTP service.

Production contract:

```text
admin.modainteract.com
    -> moda-interact-gateway
    -> moda_admin private upstream
```

## Context

`ARCH-002-GATEWAY-002` is architect-accepted Complete and intentionally retained
`/admin/* -> moda_admin` only as a provisional development mapping. Its Architect
Review recorded that `moda-interact-admin` has no `/admin` Next.js base path and
returned the base-path/host strategy to `moda_architect`.

ARCH-002 now resolves that question in favour of host-based routing. The admin
application remains rooted at `/`; no Next.js `basePath` or `assetPrefix` is
required by this architecture.

This is a bounded follow-up task and must not rewrite GATEWAY-002 completion
history.

## Scope

- add host-based routing for the Admin application at the gateway;
- use `admin.modainteract.com` as the production Admin hostname;
- make the test Admin hostname environment-configurable rather than hard-coding
  production identity into the test environment;
- route root paths, Next.js assets and Admin route handlers for the Admin host to
  the `moda_admin` private upstream;
- remove production reliance on the provisional `/admin/*` path-prefix mapping;
- ensure the Admin hostname cannot fall through to the Shopify application;
- ensure non-Admin hosts cannot reach the Admin upstream through the former
  `/admin/*` mapping in production configuration;
- preserve provider webhook/body/header behaviour implemented by GATEWAY-002;
- document the public Admin host environment/DNS contract consumed by
  GATEWAY-003;
- add gateway tests for the host-routing behaviour.

## Out of Scope

- implementing platform-admin authentication or authorisation;
- making `moda-interact-admin` a public Render service;
- modifying the Next.js admin application to introduce a `/admin` base path;
- implementing Grafana iframe/presentation behaviour;
- changing Shopify/Meta business verification;
- changing Redis/BullMQ worker topology;
- solving the remaining general production catch-all route-hardening question
  except where necessary to prevent Admin exposure.

## Requirements

Production public hostname:

```text
admin.modainteract.com
```

Deployment configuration must provide a non-secret Admin public-host contract,
for example an architecture-approved environment value such as:

```text
ADMIN_PUBLIC_HOST=<environment-specific-host>
```

The production value must resolve to:

```text
admin.modainteract.com
```

The exact test hostname may differ and is supplied by the test deployment.

For the configured Admin host:

```text
/...
    -> moda_admin
```

including:

```text
/
/_next/*
/observability
/api/*
```

where those paths exist in the Admin application.

The gateway must not require:

```text
/admin/*
```

for the production Admin contract.

Host routing must preserve gateway-level request/correlation identifiers and
forwarded headers already established by GATEWAY-002.

Unknown/non-Admin host handling must never route to `moda_admin` merely because a
request path begins with `/admin`.

The private upstream contract remains:

```text
moda_admin
```

as supplied by Render/private-service configuration.

## Work Items

- [ ] update gateway configuration/template for Admin host-based routing;
- [ ] add environment/configuration contract for the Admin public hostname;
- [ ] route Admin root paths and `/_next/*` assets correctly;
- [ ] eliminate production reliance on `/admin/* -> moda_admin`;
- [ ] prevent Admin-host fallthrough to `moda_interact`;
- [ ] prevent non-Admin hosts from reaching `moda_admin` through provisional
      path routing;
- [ ] preserve request/correlation and forwarded-header behaviour;
- [ ] add host-routing tests;
- [ ] document DNS/custom-domain requirements for GATEWAY-003;
- [ ] record any Render-specific host/custom-domain limitation discovered.

## Interfaces / Contracts

Produces the gateway contract consumed by:

```text
ARCH-002-GATEWAY-003
```

Public Admin hostname:

```text
production: admin.modainteract.com
test:       deployment-configured test Admin hostname
```

Private upstream:

```text
moda_admin
```

`ARCH-002-ADMIN-008` is the accepted final application-security gate for
platform-admin authentication and authorisation. Host routing is not an authentication mechanism.

## Dependencies

- `ARCH-002-GATEWAY-002`
- `ARCH-002-ADMIN-008`

## Enables

- `ARCH-002-GATEWAY-003`

## Acceptance Criteria

- [ ] production Admin traffic is defined by host routing at
      `admin.modainteract.com`;
- [ ] test Admin host identity is environment-configurable;
- [ ] Admin remains a private Render upstream rather than a directly public
      service;
- [ ] Admin root page and root-relative Next.js `/_next/*` assets route correctly;
- [ ] production routing does not depend on a Next.js `/admin` base path;
- [ ] non-Admin hosts cannot reach `moda_admin` through the old `/admin/*`
      mapping;
- [ ] Admin-host requests cannot fall through to `moda_interact`;
- [ ] existing Shopify/Meta provider verification routing remains compatible;
- [ ] request/correlation and forwarded-header behaviour is preserved;
- [ ] GATEWAY-003 receives a documented host/DNS/configuration contract.

## Validation

- [ ] NGINX/proxy syntax validation;
- [ ] gateway test suite;
- [ ] Admin host root routing test;
- [ ] Admin `/_next/*` routing test;
- [ ] Admin `/observability` routing test;
- [ ] non-Admin `/admin/*` isolation test;
- [ ] Admin-host no-Shopify-fallthrough test;
- [ ] request/correlation header regression test;
- [ ] Shopify/Meta routing regression tests;
- [ ] container build/start where required by repository validation.

## Implementation Notes

Keep the Admin service private. The browser reaches it only through the public
gateway.

Do not modify `moda-interact-admin` merely to make path-prefix routing fit; the
accepted architecture deliberately chooses host routing so the existing root
Next.js application model can remain intact.

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

None.

### Unresolved Issues

None recorded yet.

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
