---
id: ARCH-002-GATEWAY-004
architecture_id: ARCH-002
title: Validate gateway and Render infrastructure configuration
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 40
executor: copilot
claimed_at: 2026-09-02T00:00:00Z
attempt: 1
depends_on: 
  - ARCH-002-GATEWAY-003
enables: []
created: 2026-08-29
updated: 2026-09-02
---

# Validate Gateway and Render Infrastructure Configuration

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Validate ARCH-002 infrastructure artifacts before integrated system-test task
creation.

## Context

This is infrastructure validation. It does not own fixes in application
repositories.

## Scope

Validate where practical:

### Gateway

- reverse-proxy syntax;
- container build/start;
- health;
- routing;
- forwarded/provider headers;
- webhook-body compatibility;
- unavailable-upstream behaviour;
- Admin host-based routing;
- Admin/non-Admin host isolation;
- root-relative Next.js Admin asset routing.

### Render topology

- Blueprint syntax/configuration;
- service types/repository mappings;
- build/start commands;
- ports/health paths;
- environment declarations;
- private/public exposure;
- worker definitions;
- dependency assumptions.

### Redis/PostgreSQL

- required environment names;
- TLS/connectivity expectations;
- secret handling;
- region/network assumptions;
- ownership boundaries.

### Documentation

Verify prerequisite/topology/networking/scaling/deployment documentation is
consistent with implemented artifacts.

## Out of Scope

- repairing application business logic;
- destructively mutating Redis/PostgreSQL;
- creating system-test scenarios inside application repositories.

## Requirements

If validation discovers an application defect or missing capability:

1. record evidence;
2. do not modify the owning application implementation;
3. return the issue to `moda_architect`;
4. allow architect to reopen/create the owning task;
5. keep affected infrastructure/system validation blocked.

## Work Items

- [x] validate gateway configuration;
- [x] validate container build/start;
- [x] validate routing/header/body behaviour;
- [x] validate `admin.modainteract.com` production host routing contract;
- [x] validate test Admin hostname configurability;
- [x] validate Admin host/non-Admin host isolation and no Shopify fallthrough;
- [x] validate root-relative Admin `/_next/*` asset routing;
- [x] validate Blueprint/topology;
- [x] validate public/private exposure;
- [x] validate real worker commands;
- [x] validate Redis/PostgreSQL wiring expectations;
- [x] validate no secrets committed;
- [x] validate deployment runbook;
- [x] record evidence.

## Interfaces / Contracts

Consumes the infrastructure artifacts produced by GATEWAY-002 and GATEWAY-003.

## Dependencies

- `ARCH-002-GATEWAY-003`

## Enables

None directly.

After architect acceptance and after every required implementation task is
Complete, `moda_architect` creates `ARCH-002-SYSTEM-TEST-001`.

## Acceptance Criteria

- [x] gateway configuration validates;
- [x] gateway container builds/starts;
- [x] health succeeds;
- [x] approved routes target intended services;
- [x] production `admin.modainteract.com` targets only the private Admin upstream;
- [x] non-Admin hosts cannot reach the Admin upstream through the provisional
      `/admin/*` path;
- [x] Admin host root and `/_next/*` requests resolve through the gateway without
      requiring a Next.js `/admin` base path;
- [x] required headers/body behaviour are preserved;
- [x] upstream failure behaviour is predictable;
- [x] Render configuration is internally consistent;
- [x] service commands/ports/health paths match accepted prerequisites;
- [x] worker definitions match real entrypoints;
- [x] Redis/PostgreSQL expectations are documented;
- [x] public/private exposure matches ARCH-002;
- [x] no secrets are committed;
- [x] validation evidence is ready for architect review.

## Validation

- [x] infrastructure test suite;
- [x] proxy configuration validation;
- [x] container validation;
- [x] Render topology validation where practical;
- [x] documentation consistency review.

## Implementation Notes

Do not create the system-test task from this repository agent. After this task
is accepted, `moda_architect` evaluates all implementation dependencies and
creates the system-test task.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-gateway/docs/render-topology.md` was updated with bounded
rollback and environment-recreation guidance. The gateway Dockerfile,
entrypoint, NGINX template, tests, observability validator, and both Render
Blueprints were reviewed without implementation changes.

### Work Completed

Validated the accepted public gateway, private Shopify/Messaging/Admin HTTP
services, three independent workers, Render PostgreSQL, external Redis Cloud,
direct OTLP/Loki observability, Admin host routing, and capacity
classifications. The Admin custom-domain `GET /health` correction is present
and tested. No application repository was modified.

### Validation Results

`tests/run-tests.sh`: PASS, 49 passed, 0 failed, including gateway build/start,
health, routing, headers, webhook body preservation, failure behavior,
timeouts, and Admin-host health liveness.

`tests/validate-observability-config.sh`: PASS.

AJV Draft 2020-12 validation: both `render.test.yaml` and
`render.production.yaml` valid; only the known ignored optional `uri` format
warning was emitted.

Focused topology assertions: PASS for YAML parsing, resource types/plans,
repository URLs, public/private/worker boundaries, service references,
test/production isolation, PostgreSQL and Redis wiring, worker commands,
Admin-host health reservation, and secret scanning. Source contract checks and
`git diff --check` also passed.

### Deviations

The Render Blueprint schema supports `healthCheckPath` for the public gateway;
private `/health` and `/ready` routes remain deployment/system-test checks.
Live Render validation was not performed because this task does not deploy or
use production credentials.

### Assumptions

Production plans/counts and the approximately 22,000 Shopify webhooks/minute
target remain assumed/estimated, not measured capacity. Actual Render access,
plan availability, private networking, DNS/TLS, credentials, migrations,
readiness, and provider connectivity require environment validation.

### Unresolved Issues

Live Render validation remains outstanding: credential population, repository
access, plan availability, private networking, DNS/TLS/custom-domain
verification, migrations/readiness, external Redis connectivity, rollback
execution, and capacity/load evidence.

### Architectural Concerns

No architectural defect was found. GATEWAY-004 does not alter application
repositories, queue semantics, database schema ownership, or the accepted
ARCH-002 topology.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-GATEWAY-004` is architect-accepted.

This task remained a bounded infrastructure-validation task and did not
redesign the accepted `GATEWAY-003` topology.

### Infrastructure Validation Reviewed

The accepted topology remains:

```text
PUBLIC
  moda-interact-gateway

PRIVATE HTTP
  moda-interact
  moda-interact-messaging
  moda-interact-admin

NO INBOUND HTTP
  moda-shopify-event-worker
  moda-recovery-worker
  moda-messaging-worker

STATE / EXTERNAL DEPENDENCIES
  Render PostgreSQL
  external Redis Cloud
```

Both canonical Blueprint sources remain:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

### Independent Architect Checks

Against the submitted bundle, the architect independently confirmed:

```text
render.test.yaml
  YAML parse PASS
  7 services
  1 database
  1 env-var group

render.production.yaml
  YAML parse PASS
  7 services
  1 database
  1 env-var group

tests/run-tests.sh
  shell syntax PASS

tests/validate-observability-config.sh
  shell syntax PASS

docker/entrypoint.sh
  shell syntax PASS

tests/validate-observability-config.sh
  execution PASS
```

The expected service-type split is present in both environments:

```text
1 web
3 pserv
3 worker
```

The architect environment does not provide Docker, so the full containerized
gateway integration suite could not be independently re-executed.

### Repository-Agent Validation Reviewed

The Completion Report records:

```text
tests/run-tests.sh
  49 passed
  0 failed

tests/validate-observability-config.sh
  PASS

AJV Draft 2020-12 Render Blueprint schema validation
  test PASS
  production PASS

focused topology assertions
  PASS

source contract checks
  PASS

git diff --check
  PASS

credential-pattern scan
  PASS
```

The reported Docker gateway suite covers:

```text
container build/start
gateway liveness
application routing
Meta/WhatsApp routing
Admin host routing
Admin/non-Admin isolation
root-relative Next.js assets
forwarded/request/correlation headers
raw webhook body preservation
provider signature headers
upstream failure behavior
timeouts
request-size behavior
sensitive-query logging
Admin-host gateway-local /health
```

### Documentation / Operations Reviewed

`docs/render-topology.md` now documents bounded deployment, rollback and
environment recreation behavior.

It correctly preserves:

```text
test before production
environment-specific credentials/state
PostgreSQL migration sequencing
worker dependency preflight
private service readiness
gateway health/routing validation
custom-domain DNS/TLS validation
no ordinary rollback destruction of durable state
```

### Capacity Classification

The approximately:

```text
22,000 Shopify webhooks/minute
~367 requests/second
```

target remains an estimated workload target, not measured capacity.

Production plans and replica counts remain assumed starting hypotheses.

Recovery, WhatsApp and CommerceAgent workloads are not inferred from raw
Shopify ingress throughput.

### Security / Secret Handling

No production credential value was identified in the submitted Blueprint or
gateway configuration.

Synthetic values inside gateway test fixtures are test-only evidence and are
not production secrets.

### Deferred Live Validation

The following remain correctly deferred to isolated Render/system validation:

```text
Render repository access
actual plan availability
real private networking
DNS/TLS/custom-domain verification
credential population
database migration/readiness
external Redis connectivity
rollback execution
measured load/capacity evidence
```

These are not defects in `GATEWAY-004`; the task explicitly does not perform a
production deployment.

### Architecture Conformance

Accepted.

No application repository was modified.

No schema ownership, queue semantics or provider business behavior was moved
into the gateway.

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Accepted Gateway validation/documentation changes are ready for developer
commit/push.

### Downstream Coordination

`ARCH-002-GATEWAY-004` is Complete.

The infrastructure gate required by the ARCH-002 system-test phase is therefore
satisfied.

Existing system-test preparation tasks remain authoritative:

```text
ARCH-002-SYSTEM-TEST-003
  isolated ephemeral Redis infrastructure

ARCH-002-SYSTEM-TEST-004
  WhatsApp Cloud API emulator infrastructure
```

`SYSTEM-TEST-001` and `SYSTEM-TEST-002` must not be promoted solely because
`GATEWAY-004` is Complete. Their complete explicit `depends_on` lists must be
re-evaluated after the remaining prerequisites are architect-accepted.

No downstream task is automatically started.

## Architect Readiness Review

### Status

Ready

### Dependency Re-evaluation

The authoritative task declares one direct dependency:

```text
ARCH-002-GATEWAY-003
```

`ARCH-002-GATEWAY-003` is architect-accepted Complete.

Therefore this task is promoted:

```text
pending -> ready
```

No executor has been claimed.

No implementation work has been started by this coordination update.
