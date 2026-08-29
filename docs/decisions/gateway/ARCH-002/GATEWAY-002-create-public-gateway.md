---
id: ARCH-002-GATEWAY-002
architecture_id: ARCH-002
title: Create public Moda Interact gateway
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 20
executor: codex
claimed_at: 2026-08-29T17:54:00+01:00
attempt: 1
depends_on: 
  - ARCH-002-GATEWAY-001
enables: 
  - ARCH-002-GATEWAY-003
created: 2026-08-29
updated: 2026-08-29
---

# Create Public Moda Interact Gateway

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Create the thin public reverse-proxy gateway using only route/upstream
capabilities established by the architect-accepted prerequisite report.

## Context

GATEWAY-001 is Complete.

The thin gateway implementation can proceed independently of the application
health/startup/worker remediation tasks because routing/header/body/error
behaviour can be implemented and tested against controlled upstream fixtures.

Deployment topology remains gated later by GATEWAY-003.

## Scope

Within authorised infrastructure scope create equivalent artifacts for:

- minimal gateway container;
- reverse-proxy configuration;
- environment/config validation;
- routing/header/body/health tests;
- infrastructure documentation.

Expected responsibilities include:

- route matching;
- reverse proxying;
- request/correlation IDs;
- forwarded/provider headers;
- request-size/connection/timeouts;
- access/error logging;
- security headers;
- approved rate limiting;
- health handling;
- private-service routing.

## Out of Scope

- Shopify/recovery/messaging business logic;
- provider signature verification itself;
- database queries/business semantics;
- queue business semantics;
- CommerceAgent/LLM/billing logic;
- implementing missing upstream application capabilities.

## Requirements

Only architect-approved routes may be exposed.

Provider verification remains in owning ingress services.

The gateway must preserve headers and body behaviour required by Shopify and
Meta signature verification.

No secrets may be embedded in image/configuration.

## Work Items

- [x] implement minimal production gateway image;
- [x] implement route/upstream configuration;
- [x] implement environment/config validation;
- [x] implement health handling;
- [x] implement routing tests;
- [x] implement header-forwarding tests;
- [x] implement webhook-body compatibility tests;
- [x] implement upstream-error tests;
- [x] create/update gateway documentation;
- [x] record validation.

## Interfaces / Contracts

Consumes the architect-accepted GATEWAY-001 deployment prerequisite report and
any concrete prerequisite tasks added by `moda_architect`.

## Dependencies

- `ARCH-002-GATEWAY-001`
- any additional **fully-qualified** task IDs added by `moda_architect` after
  GATEWAY-001 review.

## Enables

- `ARCH-002-GATEWAY-003`

## Acceptance Criteria

- [x] thin public gateway is implemented;
- [x] only approved routes are exposed;
- [x] accepted private-service targets are used;
- [x] provider-signature headers are preserved;
- [x] webhook body behaviour remains verification-compatible;
- [x] gateway health is cheap and testable;
- [x] upstream failures are predictable;
- [x] secrets are not embedded;
- [x] gateway configuration validates;
- [x] container builds/starts;
- [x] no application business logic moved into gateway.

## Validation

- [x] reverse-proxy syntax validation;
- [x] gateway container build;
- [x] gateway container startup;
- [x] gateway test suite;
- [x] environment/config validation.

## Implementation Notes

The task file's YAML `depends_on` must be amended by `moda_architect` with any
new prerequisite task IDs before this task is moved from Pending to Ready.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-gateway/Dockerfile`
- `moda-interact-gateway/nginx/nginx.conf.template`
- `moda-interact-gateway/docker/entrypoint.sh`
- `moda-interact-gateway/tests/run-tests.sh`
- `moda-interact-gateway/tests/fixtures/upstream.py`
- `moda-interact-gateway/tests/payloads/shopify-checkout-create.json`
- `moda-interact-gateway/README.md`
- `moda-interact-gateway/docs/gateway.md`
- `moda-interact-gateway/docs/GATEWAY-002-completion-report.md`
- `docs/decisions/gateway/ARCH-002/GATEWAY-002-create-public-gateway.md`

### Work Completed

Thin public reverse-proxy gateway implemented per ARCH-002:

- NGINX **`nginx:1.30.4-alpine`** gateway image (corrected from
  `nginx:1.27-alpine`; fixed stable line for CVE-2026-42533, which affects
  `map`-with-regex through 1.31.2).
- `nginx/nginx.conf.template` as the single source of truth for routing:
  - Shopify webhooks `/webhooks`, `/webhooks/*` -> `moda_interact`;
  - Shopify OAuth `/auth/*` -> `moda_interact`;
  - Meta `/webhook/whatsapp` -> `moda_messaging`;
  - `/admin/*` -> `moda_admin` (intended mapping only; contract not
    established — see Architectural Concerns);
  - default `/` -> `moda_interact` (pre-production development catch-all;
    documented as a non-blocking note to tighten before cutover);
  - `GET /health` served by the gateway itself (no upstream dependency).
- Request/correlation IDs (`X-Request-Id` preserved or generated, mirrored as
  `X-Correlation-Id`, echoed on responses).
- Forwarded headers (`X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`,
  `X-Real-IP`, `Host`) with Render load-balancer inbound values preferred.
- Provider verification compatibility: raw webhook bodies and
  `X-Shopify-*` / `X-Hub-*` headers passed through untouched; no
  parse/re-serialise anywhere.
- Request-size limit (`CLIENT_MAX_BODY_SIZE`, default `10m` -> `413`),
  connect/send/read timeouts (defaults `5s`/`60s`/`60s` -> `504`).
- Security headers (`X-Content-Type-Options`, `Referrer-Policy`,
  `X-XSS-Protection`); no frame-blocking headers (Shopify iframe embedding).
- Environment/config validation: entrypoint fails fast when required upstream
  env vars are missing; rendered config validated with `nginx -t` before start.
- Sensitive-query logging correction (architect review item 1): the access log
  records `$uri` (path only), never `$request_uri`, and never the `Referer`
  header; query strings are still forwarded to upstream unchanged.
- No secrets embedded in image or configuration (all values injected via
  environment at runtime).

Round 2 (architect review — sensitive error-log disclosure on upstream
failure):

- Added a second logging layer: the sensitive query-bearing locations
  (`location /auth/` and `location = /webhook/whatsapp`) now override
  `error_log` to `/dev/null crit`, so NGINX core error records — which include
  the complete request line and upstream URL, including query parameters —
  cannot disclose the Shopify OAuth `code` or the Meta `hub.verify_token` when
  an upstream request fails. The override is bounded to those routes; error
  logging everywhere else is unchanged, and the safe structured access log
  (path, HTTP status, upstream address/status, request ID) is retained for
  these routes. Genuine `crit`+ conditions are still reported.
- The proxied query string is untouched: `proxy_pass` still forwards the
  original request URI (path + query) to the owning upstream unchanged.
- Extended the suite with upstream-failure tests for both sensitive routes:
  each upstream is stopped, the sensitive request is sent with a unique
  per-run secret, the gateway returns the expected 5xx, the unique secret is
  asserted absent from complete `docker logs` (stdout + stderr), and the
  path-only access-log failure entry with HTTP status is still present.

### Validation Results

Full integration suite rerun in the implementation environment with the
corrected `nginx:1.30.4-alpine` image after the Round-2 correction:

```text
Gateway test suite complete: 44 passed, 0 failed
```

Covered by the suite:

- health (`GET /health` + `X-Request-Id`);
- routing to private-service upstreams (`webhooks/*`, `/auth/*`, default,
  `/webhook/whatsapp`, `/admin/*` fixture routing);
- request/correlation IDs and forwarded headers;
- security headers;
- Shopify HMAC + raw-body preservation and `X-Shopify-*` header preservation;
- Meta HMAC + raw-body preservation and `X-Hub-*` header preservation;
- sensitive-query logging (healthy upstreams): Shopify OAuth `code` and Meta
  `hub.verify_token` forwarded unchanged to upstreams AND absent from gateway
  logs, with path-only access-log entries still present;
- sensitive-query logging on upstream failure (Round 2): with the app upstream
  and then the messaging upstream stopped, `/auth/callback?code=<unique>` and
  `/webhook/whatsapp?hub.verify_token=<unique>` return the expected 5xx, the
  unique secrets are absent from complete `docker logs` (stdout + stderr), and
  the path-only failure entries with HTTP status remain in the access log;
- upstream failure -> predictable 5xx and recovery after upstream restart;
- request-size limit (`413`);
- upstream timeout (`504`);
- environment/config validation (missing upstream env fails fast; `nginx -t`
  passes on the rendered config).

Static checks:

```text
sh -n docker/entrypoint.sh
bash -n tests/run-tests.sh
```

### Deviations

- Reverse-proxy implementation: NGINX (architect-ratified in the GATEWAY-002
  review); `nginx:1.30.4-alpine` fixed stable line.
- No rate limiting enabled: no approved policy exists for the high-volume
  Shopify ingress path (architect-ratified "no gateway rate limiting yet").
- No global frame-blocking headers: the Shopify app must remain embeddable in
  the Shopify admin iframe (architect-ratified).
- `/admin/*` mapping retained as the intended private-service boundary only;
  it is not claimed as a proven admin base-path contract (see Architectural
  Concerns).

### Assumptions

- The architect-accepted GATEWAY-001 deployment-prerequisite report remains the
  route/upstream source of truth; `/admin/*` is an intended mapping, not a
  claim derived from GATEWAY-001.
- Render injects upstream `host:port` via the documented environment
  variables; `render.yaml` topology is GATEWAY-003 scope and was not created
  here.
- No application health/readiness behaviour was added or changed in other
  repositories; missing health/readiness capabilities remain with their owning
  services (GATEWAY-001 findings).

### Unresolved Issues

- Admin routing/base-path contract is not established (see Architectural
  Concerns) — must be resolved by `moda_architect` before the admin service can
  be served behind the gateway.
- Production Render addressing/restart behaviour is not asserted from Docker
  fixture behaviour; GATEWAY-003 must use Render private-service
  `hostport`/service-level references as the canonical addressing mechanism.
- Default `/` catch-all is a pre-production development convenience that should
  be tightened before production cutover (documented, non-blocking).

### Architectural Concerns

```
Architectural Concern:
moda-interact-admin does not yet support a /admin/* base-path contract. The
gateway's /admin/ location is an intended private-service mapping only.
Evidence: moda-interact-admin/next.config.ts has no basePath/assetPrefix; the
App Router exposes only / (src/app/page.tsx) and /api/health/database; there
is no src/app/admin/ directory; Next.js assets are root-relative (/_next/...).
The base-path/host strategy decision is returned to moda_architect.
Owner: moda_admin + moda_gateway (architect decision required)
Architect follow-up required: yes
```

```
Architectural Concern:
Production Render addressing after upstream redeploys must be established from
Render-specific evidence (private-service hostport/service-level references),
not inferred from Docker fixture restart behaviour.
Owner: moda_gateway (GATEWAY-003)
Architect follow-up required: yes
```

```
Architectural Concern:
The default / catch-all forwards unmatched paths to moda-interact as a
pre-production development convenience. The public route surface must be
reviewed and tightened before production cutover so unknown/unapproved paths
are rejected at the gateway boundary.
Owner: moda_gateway + moda_architect
Architect follow-up required: yes (pre-production)
```

## Architect Review

### Review Status

Accepted

### Review Notes

GATEWAY-002 is accepted.

The Round-2 correction closes the remaining sensitive-query logging defect.

The implementation now applies two bounded protections:

1. the structured access log records `$uri` rather than `$request_uri` and does
   not log the full Referer header; and
2. the two known sensitive query-bearing ingress locations suppress ordinary
   NGINX core error-log records that would otherwise include the full request
   line/upstream URL on an upstream failure:

```nginx
location /auth/ {
    error_log /dev/null crit;
    proxy_pass http://moda_interact;
}

location = /webhook/whatsapp {
    error_log /dev/null crit;
    proxy_pass http://moda_messaging;
}
```

The original query string continues to be forwarded unchanged to the owning
upstream.

The submitted suite reports:

```text
Gateway test suite complete: 44 passed, 0 failed
```

and now includes unique-secret failure-path assertions against complete
`docker logs` for both Shopify OAuth and Meta verification.

Architect-side reproduction using the submitted rendered NGINX configuration
confirmed:

```text
/auth/callback?code=<unique-secret>
    -> 502 with unavailable upstream
    -> path-only access-log entry
    -> secret absent from stdout/stderr

/webhook/whatsapp?hub.verify_token=<unique-secret>
    -> 502 with unavailable upstream
    -> path-only access-log entry
    -> secret absent from stdout/stderr
```

The implementation remains a thin infrastructure boundary and does not move
provider verification, Shopify business logic, messaging business logic or
BullMQ processing into the gateway.

The following previously ratified decisions remain accepted:

- NGINX is the ARCH-002 reverse proxy;
- `nginx:1.30.4-alpine` is accepted for this task;
- no gateway rate limiting is required yet;
- background BullMQ workers are infrastructure-managed but are not HTTP
  reverse-proxy upstreams;
- the broad `location / -> moda_interact` catch-all may remain during
  pre-production development and must be tightened before production cutover;
- `/admin/*` remains an intended development mapping only and is not accepted
  as a proven production admin base-path contract.

One documentation wording issue is non-blocking: `error_log /dev/null crit`
does not "report" crit-and-above records for those locations; such records are
written to `/dev/null`. The required security behaviour is nevertheless
correct and independently reproduced. Correct that wording during the next
gateway-owned documentation update.

### Reviewed Files

- `moda-interact-gateway/Dockerfile`
- `moda-interact-gateway/nginx/nginx.conf.template`
- `moda-interact-gateway/docker/entrypoint.sh`
- `moda-interact-gateway/README.md`
- `moda-interact-gateway/docs/gateway.md`
- `moda-interact-gateway/docs/GATEWAY-002-completion-report.md`
- `moda-interact-gateway/tests/run-tests.sh`
- `moda-interact-gateway/tests/fixtures/*`
- `moda-interact-gateway/tests/payloads/*`
- `docs/decisions/gateway/ARCH-002/GATEWAY-002-create-public-gateway.md`

### Validation Reviewed

Submitted implementation evidence:

```text
Gateway test suite complete: 44 passed, 0 failed
```

Architect-side static validation:

```text
sh -n docker/entrypoint.sh
PASS

bash -n tests/run-tests.sh
PASS

render submitted nginx template + nginx -t
PASS
```

Architect-side NGINX runtime reproduction with unavailable app/messaging
upstreams:

```text
Shopify OAuth failure -> 502
OAuth secret absent from stdout/stderr
path-only access record present

Meta verification failure -> 502
Meta verification secret absent from stdout/stderr
path-only access record present
```

Docker is not available in the architect review environment, so the submitted
44-test Docker suite was not independently rerun. The specific Round-2
security behaviour was independently reproduced with NGINX itself.

### Architecture Conformance

Accepted.

The implementation conforms to the approved GATEWAY-002 thin-public-ingress
boundary for the current pre-production stage.

### Follow-up

- `ARCH-002-GATEWAY-002` transitions `review -> complete`.
- Evaluate `ARCH-002-GATEWAY-003`; it remains Pending until every declared
  prerequisite is Complete.
- Before GATEWAY-003 executes, `moda_architect` must reconcile the newly agreed
  two-environment deployment model (`test` and `production`) and its canonical
  Blueprint filenames.
- Resolve the admin base-path/host-routing contract before production cutover.
- Tighten the development catch-all public route before production cutover.
- Correct the minor `crit+` documentation wording during the next
  gateway-owned documentation update.

No further correction cycle is required for GATEWAY-002.
