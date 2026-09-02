---
id: ARCH-002-GATEWAY-007
architecture_id: ARCH-002
title: Implement host-based admin gateway routing
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 25
executor: copilot
claimed_at: 2026-09-02T18:59:01Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-002
  - ARCH-002-ADMIN-008
enables:
  - ARCH-002-GATEWAY-003
created: 2026-08-31
updated: 2026-09-02
---

# Implement Host-Based Admin Gateway Routing

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Readiness decision

`moda_architect` re-evaluated the authoritative direct dependencies after
architect acceptance of `ARCH-002-ADMIN-008`.

```text
ARCH-002-GATEWAY-002  Complete
ARCH-002-ADMIN-008    Complete
```

`ARCH-002-GATEWAY-007` is therefore promoted:

```text
Pending -> Ready
```

This promotion does not start the task automatically.

The repository agent must stop at `review` and must not commit or push.
Developer publication remains user-owned.

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

- [x] update gateway configuration/template for Admin host-based routing;
- [x] add environment/configuration contract for the Admin public hostname;
- [x] route Admin root paths and `/_next/*` assets correctly;
- [x] eliminate production reliance on `/admin/* -> moda_admin`;
- [x] prevent Admin-host fallthrough to `moda_interact`;
- [x] prevent non-Admin hosts from reaching `moda_admin` through provisional
      path routing;
- [x] preserve request/correlation and forwarded-header behaviour;
- [x] add host-routing tests;
- [x] document DNS/custom-domain requirements for GATEWAY-003;
- [x] record any Render-specific host/custom-domain limitation discovered.

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

- [x] production Admin traffic is defined by host routing at
      `admin.modainteract.com`;
- [x] test Admin host identity is environment-configurable;
- [x] Admin remains a private Render upstream rather than a directly public
      service;
- [x] Admin root page and root-relative Next.js `/_next/*` assets route correctly;
- [x] production routing does not depend on a Next.js `/admin` base path;
- [x] non-Admin hosts cannot reach `moda_admin` through the old `/admin/*`
      mapping;
- [x] Admin-host requests cannot fall through to `moda_interact`;
- [x] existing Shopify/Meta provider verification routing remains compatible;
- [x] request/correlation and forwarded-header behaviour is preserved;
- [x] GATEWAY-003 receives a documented host/DNS/configuration contract.

## Validation

- [x] NGINX/proxy syntax validation;
- [x] gateway test suite;
- [x] Admin host root routing test;
- [x] Admin `/_next/*` routing test;
- [x] Admin `/observability` routing test;
- [x] non-Admin `/admin/*` isolation test;
- [x] Admin-host no-Shopify-fallthrough test;
- [x] request/correlation header regression test;
- [x] Shopify/Meta routing regression tests;
- [x] container build/start where required by repository validation.

## Implementation Notes

Keep the Admin service private. The browser reaches it only through the public
gateway.

Do not modify `moda-interact-admin` merely to make path-prefix routing fit; the
accepted architecture deliberately chooses host routing so the existing root
Next.js application model can remain intact.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-gateway/nginx/nginx.conf.template`
- `moda-interact-gateway/docker/entrypoint.sh`
- `moda-interact-gateway/tests/run-tests.sh`
- `moda-interact-gateway/README.md`
- `moda-interact-gateway/docs/gateway.md`
- `docs/decisions/gateway/ARCH-002/GATEWAY-007-admin-host-routing.md`

### Work Completed

Implemented dedicated NGINX host-based routing for `ADMIN_PUBLIC_HOST`, with
production set to `admin.modainteract.com` and a deployment-configured test
hostname. Admin root routes, `/_next/*`, `/observability` and `/api/*` now route
to the private `moda_admin` upstream without requiring a Next.js `/admin` base
path. The provisional `/admin` and `/admin/*` mapping is rejected on the
default/non-Admin host before the Shopify catch-all.

Preserved request/correlation IDs, forwarded headers, provider routing and
webhook behavior. Added the required host configuration contract and DNS/TLS/
OAuth documentation for GATEWAY-003.

### Validation Results

Passed `sh -n docker/entrypoint.sh` and `bash -n tests/run-tests.sh`.

Passed `tests/run-tests.sh`: `48 passed, 0 failed`. This includes container
build/start and rendered `nginx -t`, Admin root/`/_next/*`/`/observability`
routing, Admin-host header preservation, non-Admin `/admin/*` isolation, no
Admin-host Shopify fallthrough, Shopify/Meta routing and provider body/header
regressions.

The suite emitted the existing Docker legacy-builder deprecation warning. No
Render-specific custom-domain limitation was encountered; actual DNS, TLS and
OAuth custom-domain attachment remain deployment configuration consumed by
GATEWAY-003.

### Deviations

The test suite uses `admin.test.local` as the configurable Admin hostname. The
production contract remains `admin.modainteract.com` and is not hard-coded into
the test container invocation.

### Assumptions

Render provides the configured `ADMIN_PUBLIC_HOST` value and routes its public
custom domain/TLS to the gateway while `moda_admin` remains private. The Admin
application continues to serve root-relative paths.

### Unresolved Issues

None.

### Architectural Concerns

None. The task does not implement Admin authentication; it relies on the
accepted ADMIN-008 security boundary.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-GATEWAY-007` is architect-accepted.

Architect inspection confirms the accepted production routing contract:

```text
Host: admin.modainteract.com
    -> public Render gateway
    -> NGINX ADMIN_PUBLIC_HOST server
    -> private moda_admin upstream
```

The test deployment supplies its own non-production `ADMIN_PUBLIC_HOST`.

The Admin application remains rooted at `/`; no `/admin` Next.js `basePath` or
`assetPrefix` is required.

### Routing Boundary Reviewed

The NGINX template contains a dedicated Admin host server:

```text
server_name ${ADMIN_PUBLIC_HOST}

location /
    -> proxy_pass http://moda_admin
```

Therefore root-relative Admin routes such as:

```text
/
/_next/*
/observability
/api/*
```

remain valid behind the public gateway.

The default/non-Admin host explicitly rejects the provisional routing surface:

```text
/admin
/admin/*
    -> 404
```

before the Shopify catch-all.

Consequently:

```text
Admin host
    -> cannot fall through to moda_interact

non-Admin host + /admin/*
    -> cannot reach moda_admin
```

Host-based routing is therefore an exposure boundary, not an authentication
replacement. Application authentication and authorization remain owned by the
architect-accepted `ADMIN-008` security boundary.

### Header / Provider Compatibility

The Admin host server preserves the existing gateway forwarding contract:

```text
Host
X-Real-IP
X-Forwarded-For
X-Forwarded-Proto
X-Forwarded-Host
X-Request-Id
X-Correlation-Id
```

The default host retains the architect-accepted Shopify and Meta routes and raw
body/provider-header forwarding behavior.

No provider-specific verification logic has moved into the gateway.

### Environment Contract

The container entrypoint fails fast when any of these are missing:

```text
MODA_INTERACT_UPSTREAM
MODA_MESSAGING_UPSTREAM
MODA_ADMIN_UPSTREAM
ADMIN_PUBLIC_HOST
```

`ADMIN_PUBLIC_HOST` is non-secret deployment identity.

Accepted production value:

```text
admin.modainteract.com
```

Test uses an isolated environment-specific hostname.

### Validation Reviewed

Architect directly validated shell syntax:

```text
sh -n docker/entrypoint.sh
bash -n tests/run-tests.sh
PASS
```

The repository agent reports:

```text
tests/run-tests.sh
48 passed
0 failed
```

The suite includes:

```text
container build/start
rendered nginx -t
Admin root routing
Admin /_next/* routing
Admin /observability routing
Admin request/correlation header preservation
non-Admin /admin/* isolation
Admin-host no-Shopify-fallthrough
Shopify route regressions
Meta route regressions
provider body/header preservation
```

Docker is not available in the architect review environment, so the agent's
container execution result was reviewed against the submitted test harness
rather than rerun independently. The harness contains the claimed Admin-host
and regression assertions.

### Render DNS / TLS Clarification

One gateway documentation sentence describes TLS as being terminated by the
"gateway service".

The accepted architecture interpretation is:

```text
public DNS/custom domain
    -> Render-managed public edge / load balancer
       (TLS termination)
    -> moda-interact-gateway container
    -> private Admin upstream
```

This is consistent with the gateway's existing forwarded-protocol handling and
with the rest of its documentation.

Actual Render custom-domain, certificate/TLS, DNS and OAuth callback attachment
remain deployment wiring owned by `ARCH-002-GATEWAY-003`.

This wording drift does not change the implemented routing boundary and is not
a blocker for `GATEWAY-007`.

### Architecture Conformance

Accepted.

The task stayed inside `moda-interact-gateway` ownership and coordination
documentation. It did not modify the Admin application, introduce a Next.js
base path, make the Admin service directly public, or implement authentication
inside NGINX.

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Gateway implementation changes are ready for developer commit/push.

### Downstream Coordination

`ARCH-002-GATEWAY-007` is Complete.

Together with the already accepted `GATEWAY-005`, the remaining unresolved
direct prerequisites for `ARCH-002-GATEWAY-003` are now:

```text
ARCH-002-MESSAGING-001
ARCH-002-ADMIN-001
```

No downstream task is automatically promoted or started.

