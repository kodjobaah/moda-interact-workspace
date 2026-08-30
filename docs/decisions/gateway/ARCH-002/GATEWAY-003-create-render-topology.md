---
id: ARCH-002-GATEWAY-003
architecture_id: ARCH-002
title: Create Render test and production deployment topology
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-002
  - ARCH-002-GATEWAY-005
  - ARCH-002-GATEWAY-006
  - ARCH-002-SHOPIFY-001
  - ARCH-002-SHOPIFY-002
  - ARCH-002-MESSAGING-001
  - ARCH-002-ADMIN-001
  - ARCH-002-BACKGROUND-001
  - ARCH-002-BACKGROUND-002
enables:
  - ARCH-002-GATEWAY-004
created: 2026-08-29
updated: 2026-08-29
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
- private admin service where deployed;
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

- [ ] create/update `moda-interact-gateway/render.test.yaml`;
- [ ] create/update `moda-interact-gateway/render.production.yaml`;
- [ ] configure public gateway in both environments;
- [ ] configure accepted private HTTP services in both environments;
- [ ] configure the accepted worker services in both environments;
- [ ] configure supported health/readiness behaviour;
- [ ] configure internal service references;
- [ ] wire Redis/PostgreSQL environment names securely;
- [ ] preserve npm-based service-local build assumptions from GATEWAY-005;
- [ ] wire test/production OpenTelemetry environment identity;
- [ ] document test/production secret and state isolation;
- [ ] document deployment order;
- [ ] document test environment cost assumptions;
- [ ] document production scaling/cost assumptions;
- [ ] document the 22,000-webhooks/minute production capacity target;
- [ ] classify every unmeasured production capacity claim as
      `ASSUMED`/`ESTIMATED`;
- [ ] record validation.

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
- `ARCH-002-SHOPIFY-001`
- `ARCH-002-SHOPIFY-002`
- `ARCH-002-MESSAGING-001`
- `ARCH-002-ADMIN-001`
- `ARCH-002-BACKGROUND-001`
- `ARCH-002-BACKGROUND-002`

## Enables

- `ARCH-002-GATEWAY-004`

## Acceptance Criteria

- [ ] `moda-interact-gateway/render.test.yaml` represents the accepted test
      topology;
- [ ] `moda-interact-gateway/render.production.yaml` represents the accepted
      production topology;
- [ ] the two Blueprints manage distinct environment resources;
- [ ] test and production secrets/state are independently configurable;
- [ ] the test topology uses the cheapest practical compute without changing
      architecture boundaries merely to obtain Free instances;
- [ ] production capacity configuration preserves the 22,000-webhooks/minute
      target without presenting assumptions as measured capacity;
- [ ] public/private exposure matches architecture in both environments;
- [ ] worker definitions use real supported entrypoints;
- [ ] worker pools are independently scalable;
- [ ] no HTTP load balancer fronts BullMQ workers;
- [ ] Redis Cloud remains external where required;
- [ ] PostgreSQL schema ownership remains with `moda_database`;
- [ ] no secrets are committed;
- [ ] health/readiness paths match actual services;
- [ ] environment declarations match actual requirements;
- [ ] npm-based service-local build assumptions from GATEWAY-005 are preserved;
- [ ] OpenTelemetry resource identity distinguishes `test` and `production`
      without changing canonical logical `service.name`;
- [ ] deployment order is documented;
- [ ] scaling/cost claims are correctly classified.

## Validation

- [ ] validate both Render Blueprint/config files where practical;
- [ ] verify no resource is managed by both Blueprints;
- [ ] service mapping review;
- [ ] command/port/health cross-check;
- [ ] worker entrypoint cross-check;
- [ ] npm/service-local build assumption cross-check;
- [ ] test/production environment-variable isolation review;
- [ ] test/production Redis/PostgreSQL isolation review;
- [ ] OpenTelemetry resource/environment review;
- [ ] secret scan/review;
- [ ] test topology cost review;
- [ ] production capacity classification review;
- [ ] topology documentation review.

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

None beyond those explicitly stated by the task.

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
