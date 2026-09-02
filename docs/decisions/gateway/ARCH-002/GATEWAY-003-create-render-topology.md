---
id: ARCH-002-GATEWAY-003
architecture_id: ARCH-002
title: Create Render test and production deployment topology
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-02T20:52:26Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-002
  - ARCH-002-GATEWAY-005
  - ARCH-002-GATEWAY-006
  - ARCH-002-GATEWAY-007
  - ARCH-002-SHOPIFY-001
  - ARCH-002-SHOPIFY-002
  - ARCH-002-MESSAGING-001
  - ARCH-002-ADMIN-001
  - ARCH-002-ADMIN-008
  - ARCH-002-BACKGROUND-001
  - ARCH-002-BACKGROUND-002
enables:
  - ARCH-002-GATEWAY-004
created: 2026-08-29
updated: 2026-09-02
---

# Create Render Test and Production Deployment Topology

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Create two isolated, version-controlled Render deployment topologies using
capabilities accepted by the architect:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

Together these files are the canonical Render Blueprint sources of truth for
ARCH-002.

The test Blueprint must provide the lowest-cost practical environment that
preserves the production service boundaries closely enough for integration and
system testing.

The production Blueprint must provide the production-isolated topology and a
provisional capacity configuration designed around the architecture workload
target of approximately **22,000 Shopify webhook requests per minute**.

Production compute sizing must remain explicitly classified as
`ASSUMED`/`ESTIMATED` until load testing provides measured evidence.

## Context

The target logical topology is a public gateway with private application HTTP
services and BullMQ-distributed background workers.

The architecture now has two deployed Render environments:

```text
TEST
  -> integration/system validation
  -> lowest-cost practical compute
  -> isolated test state and credentials

PRODUCTION
  -> production traffic
  -> production-isolated state and credentials
  -> HA/scalable services where required
  -> capacity target validated by load testing
```

Actual service commands, ports, health paths, environment requirements and worker
entrypoints must come from architect-accepted prerequisite tasks and repository
inspection.

The Admin service must remain private. Public browser access is provided through
the gateway using the accepted host-routing contract from `GATEWAY-007`; the
production value is `admin.modainteract.com`. The Blueprint/deployment runbook
must wire the environment-specific Admin host/DNS/custom-domain requirement
without introducing a Next.js `/admin` base path.

The shared package production build boundary is npm-based and is validated by
`ARCH-002-GATEWAY-005`; the Blueprint must not require workspace-root build
context solely to resolve `@modainteract/moda-interact-shared`.

## Scope

The canonical Render Blueprints for ARCH-002 are owned by `moda_gateway` and
must be created or modified at:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

These files are inside the `moda-interact-gateway` repository, so no
cross-repository application implementation ownership is granted.

Configure/document where supported:

- public gateway service;
- private Shopify application service;
- private messaging ingress;
- private admin service;
- Admin public-host contract from GATEWAY-007 (`admin.modainteract.com` in production);
- actual supported worker services:
  - `moda-shopify-event-worker`;
  - `moda-recovery-worker`;
  - `moda-messaging-worker`;
- HTTP health checks;
- worker readiness/health behaviour supported by the accepted prerequisites;
- Render private service references;
- PostgreSQL infrastructure wiring;
- external Redis Cloud secret wiring;
- environment-variable declarations;
- deployment order;
- `moda-interact` pre-deploy migration wiring, with seed excluded from normal
  replica startup;
- environment-specific scaling/capacity classifications;
- environment-specific cost assumptions;
- OpenTelemetry/OTLP environment identity and secret placeholders.

### Test environment

`render.test.yaml` must:

- use the cheapest practical Render topology;
- use Free compute where Render supports the required service type and doing so
  does not distort the architecture;
- use the smallest practical paid compute where Free is unavailable, including
  private/background-worker service types as required;
- normally begin with one instance per service unless an accepted prerequisite
  requires otherwise;
- keep test PostgreSQL/state separate from production;
- keep test Redis/state separate from production;
- use test-only Shopify credentials/configuration;
- use test-only Meta/WhatsApp credentials/configuration;
- use test-only observability credentials/configuration;
- use `deployment.environment.name=test`;
- contain no production data or production secret values;
- remain suitable for integration and system-test validation.

Do not turn a production-private service into a public service merely to qualify
for a free plan.

### Production environment

`render.production.yaml` must:

- use production-isolated PostgreSQL, Redis, Shopify, Meta/WhatsApp and
  observability configuration;
- preserve the architecture-approved public/private boundary;
- configure HA/minimum instance counts where required by the accepted
  architecture;
- allow independently scalable worker pools;
- preserve the workload target of approximately **22,000 Shopify webhook
  requests per minute**;
- record initial compute plans, minimum/maximum instances and autoscaling choices
  as `ASSUMED` or `ESTIMATED` unless supported by measured load-test evidence;
- avoid claiming that a selected instance count has proven 22,000/minute
  capacity until load testing demonstrates it;
- use `deployment.environment.name=production`.

### Environment isolation

The two Blueprints must not manage the same Render service/resource.

Where environment-specific Render resource names are required, they may include
an environment suffix, for example:

```text
moda-interact-gateway-test
moda-interact-gateway-production
```

OpenTelemetry logical identity must remain stable:

```text
service.namespace=moda-interact
service.name=moda-interact-gateway
deployment.environment.name=test
```

or:

```text
service.namespace=moda-interact
service.name=moda-interact-gateway
deployment.environment.name=production
```

Do not encode the environment into the OpenTelemetry `service.name`.

## Out of Scope

- inventing worker commands;
- adding HTTP load balancers in front of BullMQ workers;
- provisioning Redis Cloud as Render Redis when architecture specifies external
  Redis Cloud;
- application schema/migration implementation;
- changing application business logic;
- modifying application package dependencies;
- publishing a shared npm package;
- committing secret values;
- claiming measured production capacity without measured load-test evidence;
- introducing a queue-aware autoscaling controller unless separately assigned by
  `moda_architect`.

## Requirements

Use Render-native service load balancing for ordinary HTTP services.

Use Redis/BullMQ for worker work distribution.

Worker pools must remain independently scalable:

```text
Redis Cloud / BullMQ
        |
        +--> moda-shopify-event-worker
        +--> moda-recovery-worker
        +--> moda-messaging-worker
```

A Shopify-event surge must not automatically require the messaging/CommerceAgent
worker pool to scale.

Planning instance counts and hardware selections must be labelled
`ASSUMED`/`ESTIMATED` unless measured.

The production capacity requirement is approximately:

```text
22,000 Shopify webhook requests per minute
```

Treat this as an acceptance/load-test target, not proof that an unmeasured
hardware configuration can sustain it.

Only actual required environment variables should be declared/documented.

Use the service-local production build model accepted by GATEWAY-005.

`moda-interact` and `moda-interact-background` must resolve:

```text
@modainteract/moda-interact-shared
```

from the architect-accepted published npm artifact.

Do not require workspace-root build context solely to make a sibling
`moda-interact-shared` checkout available.

`moda-interact-admin` may use Render's native Node runtime; ARCH-002 does not
require a Dockerfile solely for that service.

OpenTelemetry/OTLP declarations must consume GATEWAY-006's accepted environment
and transport model.

Test and production secret/state configuration must be independently
configurable.

Never commit secret values.

## Work Items

- [x] create/update `moda-interact-gateway/render.test.yaml`;
- [x] create/update `moda-interact-gateway/render.production.yaml`;
- [x] configure public gateway in both environments;
- [x] configure accepted private HTTP services in both environments;
- [x] configure the accepted worker services in both environments;
- [x] configure supported health/readiness behaviour;
- [x] configure internal service references;
- [x] wire Redis/PostgreSQL environment names securely;
- [x] preserve npm-based service-local build assumptions from GATEWAY-005;
- [x] wire test/production OpenTelemetry environment identity;
- [x] document test/production secret and state isolation;
- [x] document deployment order;
- [x] document test environment cost assumptions;
- [x] document production scaling/cost assumptions;
- [x] document the 22,000-webhooks/minute production capacity target;
- [x] classify every unmeasured production capacity claim as
      `ASSUMED`/`ESTIMATED`;
- [x] record validation.

## Interfaces / Contracts

Consumes:

- accepted public-gateway implementation;
- accepted deployment-prerequisite report;
- accepted npm-based service-local build validation from GATEWAY-005;
- accepted observability transport/environment model from GATEWAY-006;
- accepted application health/startup/worker prerequisite tasks.

Canonical ARCH-002 Blueprint files:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

## Dependencies

- `ARCH-002-GATEWAY-002`
- `ARCH-002-GATEWAY-005`
- `ARCH-002-GATEWAY-006`
- `ARCH-002-GATEWAY-007`
- `ARCH-002-SHOPIFY-001`
- `ARCH-002-SHOPIFY-002`
- `ARCH-002-MESSAGING-001`
- `ARCH-002-ADMIN-001`
- `ARCH-002-ADMIN-008`
- `ARCH-002-BACKGROUND-001`
- `ARCH-002-BACKGROUND-002`

## Enables

- `ARCH-002-GATEWAY-004`

## Acceptance Criteria

- [x] `moda-interact-gateway/render.test.yaml` represents the accepted test
      topology;
- [x] `moda-interact-gateway/render.production.yaml` represents the accepted
      production topology;
- [x] the two Blueprints manage distinct environment resources;
- [x] test and production secrets/state are independently configurable;
- [x] the test topology uses the cheapest practical compute without changing
      architecture boundaries merely to obtain Free instances;
- [x] production capacity configuration preserves the 22,000-webhooks/minute
      target without presenting assumptions as measured capacity;
- [x] public/private exposure matches architecture in both environments;
- [x] `moda-interact-admin` remains a private Render service;
- [x] production Admin public-host configuration resolves the accepted
      `admin.modainteract.com` gateway contract without requiring a Next.js
      `/admin` base path;
- [x] test Admin host/configuration is isolated from production;
- [x] worker definitions use real supported entrypoints;
- [x] worker pools are independently scalable;
- [x] no HTTP load balancer fronts BullMQ workers;
- [x] Redis Cloud remains external where required;
- [x] PostgreSQL schema ownership remains with `moda_database`;
- [x] no secrets are committed;
- [x] health/readiness paths match actual services;
- [x] environment declarations match actual requirements;
- [x] npm-based service-local build assumptions from GATEWAY-005 are preserved;
- [x] OpenTelemetry resource identity distinguishes `test` and `production`
      without changing canonical logical `service.name`;
- [x] deployment order is documented;
- [x] scaling/cost claims are correctly classified.

## Validation

- [x] validate both Render Blueprint/config files where practical;
- [x] verify no resource is managed by both Blueprints;
- [x] service mapping review;
- [x] command/port/health cross-check;
- [x] worker entrypoint cross-check;
- [x] npm/service-local build assumption cross-check;
- [x] test/production environment-variable isolation review;
- [x] test/production Redis/PostgreSQL isolation review;
- [x] OpenTelemetry resource/environment review;
- [x] secret scan/review;
- [x] test topology cost review;
- [x] production capacity classification review;
- [x] topology documentation review.

## Implementation Notes

This task may only use worker/service decomposition actually supported by
accepted application prerequisites.

The test and production files intentionally model the same logical system at
different capacity/cost levels. Do not solve test-cost concerns by changing a
private service into a public service or merging independently scalable worker
pools.

Production sizing is an initial deployment hypothesis until load tests validate
the 22,000-webhooks/minute target.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/docs/render-topology.md`
- `moda-interact-gateway/README.md`
- `docs/decisions/gateway/ARCH-002/GATEWAY-003-create-render-topology.md`

### Work Completed

- Added isolated test and production Render Blueprints, each with one public
  gateway, three private HTTP services, three independent background workers,
  one Render PostgreSQL resource, and an environment-specific observability
  group.
- Wired gateway upstreams through Render private `hostport` references, kept
  Redis Cloud external, and used environment-specific PostgreSQL references.
- Wired the Shopify migration as `preDeployCommand: npm run migrate`; no seed
  command is part of replica startup.
- Declared the source-confirmed Docker/native runtimes and the three accepted
  worker entrypoints.
- Added production `admin.modainteract.com` gateway domain/host wiring and kept
  Admin private without a Next.js base path.
- Retained the applied correction that reserves `GET /health` as gateway-local
  liveness in both the default server and the `ADMIN_PUBLIC_HOST` server. This
  prevents Render custom-domain health checks from falling through to
  `moda_admin`.
- Documented runtime contracts, readiness behaviour, secrets/state isolation,
  deployment order, Render-only checks, and cost/capacity classifications.

### Validation Results

- Both files parsed successfully as YAML and contained seven services.
- Both files passed Render's published Draft 2020-12 JSON Schema using
  `ajv-cli@5` with no deployment or credentials.
- Structural validation passed: one public web service, three private services,
  three workers, one database, valid internal references, no Render Redis,
  no private/worker `healthCheckPath`, and no shared resource names.
- `tests/run-tests.sh` passed gateway health, application/messaging/Admin
  routing, forwarding, webhook-body integrity, sensitive-query checks, and the
  Admin-host `/health` gateway-liveness regression test (49 passed, 0 failed).
- `tests/validate-observability-config.sh` passed.
- `git diff --check` passed.
- VS Code diagnostics reported no errors in either Blueprint or the runbook.
- Credential-pattern scan returned no matches; `git diff --check` passed.

### Deviations

- The applied correction keeps `/health` gateway-local in the `ADMIN_PUBLIC_HOST`
  server as well as the default server. This is required because Render may
  send a custom-domain health check with `Host: admin.modainteract.com`; it must
  not proxy to the private Admin service.
- Render's current Blueprint schema restricts `healthCheckPath` to public web
  services. Private Shopify, Messaging, and Admin `/health` and `/ready` routes
  remain documented for deployment/system checks rather than declared as
  invalid private-service Blueprint health checks.

### Assumptions

- Test private services/workers use `0.5c-512mb`, the current smallest supported
  compute plan; the public gateway and PostgreSQL use Free plans.
- Production plans and counts are `ASSUMED` initial hypotheses. The
  22,000-webhooks/minute figure is an `ESTIMATED` load-test target, not measured
  capacity.

### Unresolved Issues

- Credential-aware Render CLI/API validation, repository access, plan/workspace
  availability, secret population, private networking, DNS/TLS, migrations,
  readiness, and production capacity require isolated Render environments and
  remain deployment-time validation. No Render deployment was performed.

### Architectural Concerns

- Render supports native health checks only for the public web service in this
  topology. Operational validation must explicitly probe private readiness and
  worker readiness commands after deployment.
- Production capacity remains unknown until GATEWAY-004 load testing; that task
  was not started.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-GATEWAY-003` is architect-accepted.

The final submission preserves the approved ARCH-002 deployment boundaries and
includes the requested custom-domain health correction.

### Blueprint Topology Reviewed

Both canonical Blueprint files are present:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

Architect inspection confirms each environment declares:

```text
1 public web gateway
3 private HTTP services
3 independent background workers
1 Render PostgreSQL resource
1 environment-specific observability group
```

The public/private boundary remains:

```text
PUBLIC
  moda-interact-gateway

PRIVATE
  moda-interact
  moda-interact-messaging
  moda-interact-admin

NO INBOUND HTTP
  moda-shopify-event-worker
  moda-recovery-worker
  moda-messaging-worker
```

Redis remains external Redis Cloud configuration rather than a Render-managed
Redis/Key Value resource.

### Environment Isolation Reviewed

Test and production use distinct:

```text
service/resource names
PostgreSQL resources
observability groups
secret placeholders
Redis credential inputs
provider credential inputs
deployment.environment.name
```

No production secret value is committed.

Canonical OpenTelemetry logical service identity remains source-owned and is
not environment-suffixed.

### Admin Host / Gateway Health Correction Reviewed

Production attaches:

```text
admin.modainteract.com
```

to the public gateway.

The corrected NGINX Admin-host server now reserves:

```text
GET /health
```

as gateway-local liveness and returns:

```json
{"status":"ok","service":"moda-interact-gateway"}
```

instead of proxying that request to `moda_admin`.

The regression suite contains an explicit Admin-host health request and proves
the gateway response is returned.

Normal Admin-host routes still proxy to the private Admin service.

### Capacity Classification Reviewed

The approximately:

```text
22,000 Shopify webhooks/minute
~367 requests/second
```

target is documented as an estimated/unmeasured load-test target.

Initial production instance counts and plan choices remain explicitly
`ASSUMED`; they are not represented as measured capacity.

Shopify ingress, recovery, WhatsApp and CommerceAgent workloads remain separate
scaling domains.

### Independent Architect Checks

Against the submitted bundle the architect independently confirmed:

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

credential-pattern scan
  no obvious committed credential matches
```

The architect execution environment did not provide Docker, so the full Docker
gateway suite was not re-executed independently in this review.

### Repository-Agent Validation Reviewed

The Completion Report records:

```text
gateway integration suite
  49 passed
  0 failed

observability configuration validation
  PASS

Render published Blueprint JSON-schema validation
  PASS for test
  PASS for production

git diff --check
  PASS

credential-pattern scan
  no matches
```

The completion report also correctly leaves credential-aware Render deployment,
DNS/TLS, private-network connectivity, real secret population, real database
migration/readiness and measured production capacity to later deployment/system
validation.

### Architecture Conformance

Accepted.

No application repository ownership was crossed.

No HTTP load balancer was introduced for BullMQ workers.

No OpenTelemetry Collector was introduced.

No production deployment was performed.

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Accepted Gateway changes are ready for developer commit/push.

### Downstream Coordination

`ARCH-002-GATEWAY-003` is Complete.

The authoritative `ARCH-002-GATEWAY-004` task has exactly one direct dependency:

```text
ARCH-002-GATEWAY-003
```

That dependency is now Complete.

Therefore:

```text
ARCH-002-GATEWAY-004
pending -> ready
```

No task is automatically claimed or started.

## Architect Readiness Review

### Status

Ready

### Dependency Re-evaluation

The architect re-evaluated the authoritative `depends_on` list on 2026-09-02.

All declared direct prerequisites are architect-accepted Complete:

```text
ARCH-002-GATEWAY-002
ARCH-002-GATEWAY-005
ARCH-002-GATEWAY-006
ARCH-002-GATEWAY-007
ARCH-002-SHOPIFY-001
ARCH-002-SHOPIFY-002
ARCH-002-MESSAGING-001
ARCH-002-ADMIN-001
ARCH-002-ADMIN-008
ARCH-002-BACKGROUND-001
ARCH-002-BACKGROUND-002
```

No declared direct dependency remains unresolved.

`ARCH-002-GATEWAY-003` is therefore eligible for execution and is promoted:

```text
pending -> ready
```

No executor has been claimed.

No downstream task is started automatically.
