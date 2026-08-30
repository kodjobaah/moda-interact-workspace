---
id: ARCH-002
title: Render test and production gateway and infrastructure
status: in_progress
coordinator: moda_architect
created: 2026-08-29
updated: 2026-08-30
---

# ARCH-002: Render Test and Production Gateway and Infrastructure

## Status

In Progress.

`ARCH-002-GATEWAY-001` is Complete and its deployment-prerequisite report is the
accepted source for current build/start/health/worker/dependency facts.

The architecture is now in implementation/dependency-remediation phase.

## Problem

Moda Interact currently consists of multiple independently owned application,
background and shared repositories, but the complete production Render ingress,
private-network, deployment and scaling topology must be made explicit and
version controlled.

Infrastructure required by the platform must not remain undocumented manual
configuration.

## Goals

- establish the public ingress boundary used by deployed test and production
  environments;
- minimise direct public exposure of application services;
- route public HTTP traffic through a thin infrastructure gateway;
- preserve Shopify and Meta webhook verification in the owning services;
- define two canonical Render Blueprints from actual repository capabilities;
- preserve the same logical service boundaries across test and production;
- use the cheapest practical test topology without weakening production
  architecture boundaries merely to obtain Free compute;
- define Redis Cloud and PostgreSQL infrastructure wiring with environment
  isolation;
- preserve independent application/background scaling boundaries;
- document deployment, health, rollback, scaling and cost assumptions;
- preserve a production ingress capacity target of approximately 22,000 Shopify
  webhook requests per minute;
- treat production machine sizing and instance counts as assumed/estimated until
  load testing provides measured evidence;
- validate infrastructure before integrated system testing.

Planning workload:

```text
Shopify inbound events ≈ 22,000/minute ≈ 367/second
```

This is raw ingress capacity, not recovery, WhatsApp, CommerceAgent or LLM
throughput.

## Non-Goals

- moving Shopify, recovery, messaging, billing or CommerceAgent business logic
  into the gateway;
- changing database schema from the gateway repository;
- inventing missing worker/application entrypoints inside `moda_gateway`;
- introducing a custom HTTP load balancer in front of BullMQ workers;
- treating planning capacity values as measured production capacity.

## Rollout / Migration

Classification:

**PRE-PRODUCTION / BREAKING ROLLOUT**

The target production gateway/private-service topology has not yet entered
production. Compatibility with a previous production gateway topology is not
required.

ARCH-002 uses two deployed Render environments:

```text
test
production
```

The intended rollout order is:

```text
implementation prerequisites
    ->
test Blueprint deployment
    ->
integration/system validation
    ->
load/capacity validation
    ->
production sizing review
    ->
production Blueprint deployment
```

Existing development/test stateless infrastructure may be replaced where the
assigned task permits it.

Durable state must not be destroyed merely because the architecture is
pre-production.

The exact deployment order must be established from actual service
prerequisites rather than copied from an example.

### Canonical Render Blueprints

The canonical ARCH-002 Render Blueprint files are:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

Together they are the version-controlled source of truth for the
architecture-managed Render topology.

The two Blueprints must manage distinct Render resources.

They model the same logical platform boundaries at different cost/capacity
levels.

### Test environment

The test environment exists for integration, deployment and system-test
validation.

It should:

- use the cheapest practical Render compute;
- use Free compute where Render supports the required service type;
- use the smallest practical paid compute where Free is unavailable;
- normally begin with one instance per service unless an accepted prerequisite
  requires otherwise;
- preserve private-service and background-worker boundaries;
- not make an internal/private service public merely to qualify for a Free plan;
- use test-only PostgreSQL/state;
- use test-only Redis/state;
- use test Shopify configuration/credentials;
- use test Meta/WhatsApp configuration/credentials;
- use test OpenTelemetry/OTLP configuration/credentials;
- contain no production data or production secret values;
- use `deployment.environment.name=test`.

### Production environment

The production environment uses production-isolated infrastructure and
credentials.

It should:

- preserve the approved public/private service boundary;
- use independently scalable HTTP services and worker pools;
- use production PostgreSQL/state;
- use production Redis/state;
- use production Shopify configuration/credentials;
- use production Meta/WhatsApp configuration/credentials;
- use production OpenTelemetry/OTLP configuration/credentials;
- use `deployment.environment.name=production`;
- preserve the capacity target of approximately 22,000 Shopify webhook requests
  per minute.

Initial production compute plans, minimum/maximum instance counts and autoscaling
settings are planning hypotheses.

They must be labelled **ASSUMED** or **ESTIMATED** until load testing
demonstrates measured capacity.

No unmeasured hardware configuration may be described as proven to support the
22,000/minute target.

### Environment identity and isolation

Environment-specific Render resource names may use suffixes where useful, for
example:

```text
moda-interact-gateway-test
moda-interact-gateway-production
```

OpenTelemetry logical service identity remains environment-independent:

```text
service.namespace=moda-interact
service.name=<canonical-logical-service>
deployment.environment.name=test|production
```

Do not encode the environment into `service.name`.

Test and production must not share credentials or durable state merely for
convenience.

## Current Architecture

Accepted GATEWAY-001 discovery established the original deployment facts:

- the workspace superproject uses Git submodules for application/shared
  repositories;
- `moda-interact` and `moda-interact-background` originally consumed
  `@modainteract/moda-interact-shared` through a sibling `file:` dependency;
- clean service-local Docker builds could not resolve that sibling package;
- `moda-interact` and `moda-interact-messaging` had no health/readiness endpoint;
- `moda-interact-admin` had no health/readiness endpoint;
- `moda-interact-background` had liveness but not dependency readiness;
- all background worker classes originally started from one process and could
  not be independently deployed/scaled;
- `moda-interact` originally ran Prisma migration and seed work on every replica
  startup;
- no OpenTelemetry implementation was found in the inspected deployable units.

Subsequent ARCH-002 decisions/tasks may supersede an original discovery
constraint. The discovery report remains evidence of what was inspected at that
time; it is not authority to reintroduce a superseded design.

`ARCH-002-GATEWAY-002` has since implemented the thin public gateway and is
architect-accepted Complete.

The remaining deployment topology is downstream work.

### Shared package build decision

ARCH-002 now selects the **published npm package boundary** for production
dependency resolution.

The canonical cross-service package is:

```text
@modainteract/moda-interact-shared
```

The production dependency direction is:

```text
moda-interact-shared
    ->
versioned public npm artifact
    ->
moda-interact / moda-interact-background
```

Application repositories own their dependency declarations.

The bounded consumer tasks are:

```text
ARCH-002-SHOPIFY-004
ARCH-002-BACKGROUND-004
```

Those tasks replace the production `file:../moda-interact-shared` dependency
with an architect-approved exact npm package version and update their lockfiles.

`ARCH-002-GATEWAY-005` then validates that both consumers:

- resolve the package from npm;
- use compatible accepted package artifacts;
- perform clean service-local installs/builds;
- do not require a sibling `moda-interact-shared` checkout solely for production
  dependency resolution.

There is no speculative `ARCH-002-SHARED-001` dependency in this architecture.

If a consumer proves that the currently published npm artifact cannot satisfy
the required accepted exports/contracts, the owning task must return Blocked
with evidence. `moda_architect` may then create a bounded `moda_shared` task.

Do not silently fall back to workspace-root production build context or a
`file:` dependency.

Local development may continue to use workspace-oriented workflows where useful,
provided the committed production dependency/build model remains npm-based.

### Application startup decision

`moda-interact` replica startup must not automatically seed the database.

Target behaviour:

```text
build
  ->
pre-deploy migration (once per deploy)
  ->
replica start (application only)
```

Database seeding is a separate explicit initialization operation and is not part
of normal horizontally scaled replica startup.

### Background deployment decision

Do not prematurely create four entirely independent business pipelines.

The required initial deployment units are:

```text
moda-shopify-event-worker
    checkout + order event workers

moda-recovery-worker
    pending recovery materialization

moda-messaging-worker
    WhatsApp + current CommerceAgent workflow
```

This separates the major scaling domains without refactoring CommerceAgent into
a new queue boundary before capacity evidence requires it.

## Proposed Architecture

The same logical topology is deployed in both test and production.

The environments differ in compute/capacity, credentials, state and public
addresses — not in the fundamental service boundaries:

```text
                         INTERNET
                            |
                  Render public load balancer
                            |
                            v
                 moda-interact-gateway
                       2..N
                            |
                  Render private network
            +---------------+---------------+
            |               |               |
            v               v               v
      moda-interact   moda-messaging   moda-admin
      private HTTP     private HTTP     private HTTP
            |               |
            +-------+-------+
                    |
                 Redis Cloud
                    |
         BullMQ worker services
          +---------+---------+
          |         |         |
   Shopify-event  Recovery  Messaging/
      worker      worker   CommerceAgent
          \         |         /
                    |
                PostgreSQL
```

Only topology supported by actual application capabilities may be implemented.

## Request / Event Flow

### Shopify

```text
Shopify / merchant browser
    -> Render public ingress
    -> moda-interact-gateway
    -> moda-interact private service
    -> Shopify authentication / HMAC verification / application logic
```

### Meta / WhatsApp

```text
Meta
    -> Render public ingress
    -> moda-interact-gateway
    -> moda-interact-messaging private service
    -> Meta verification / ingress logic
```

The gateway must preserve headers and request-body behaviour required by
downstream signature verification.

## Repository Responsibilities

### moda_gateway

Owns:

- gateway/reverse-proxy implementation;
- infrastructure Docker configuration;
- canonical Render Blueprints/topology (`render.test.yaml` and `render.production.yaml`);
- private-service routing;
- infrastructure health configuration;
- infrastructure environment wiring;
- scaling/autoscaling configuration where supported;
- deployment documentation;
- infrastructure validation;
- infrastructure observability.

May inspect other repositories to determine deployment requirements.

Must not silently implement missing business/application capabilities.

### application repository agents

Own application capabilities required by infrastructure, including health
endpoints, worker entrypoints and application startup behaviour where those
capabilities do not already exist.

### moda_system_test

Will validate the integrated topology only after implementation and
infrastructure dependencies are Complete.

## Contracts

Infrastructure routing contracts must be derived from the accepted deployment
prerequisite report.

Examples include:

- upstream service host/port variables;
- health/readiness paths;
- public route mappings;
- provider-signature header forwarding;
- environment-variable names.

Do not invent cross-service configuration contracts independently in gateway
and application repositories.

## Consistency and Transactions

No new business transaction model is introduced by ARCH-002.

Gateway failure must not be interpreted as successful application acceptance.

Business consistency remains owned by the corresponding application
architecture.

## Ordering

Gateway HTTP routing does not impose business-event ordering.

BullMQ workers must not be HTTP load-balanced. Redis/BullMQ remains responsible
for background work distribution.

## Failure Handling

Infrastructure must define observable behaviour for:

- unavailable private upstreams;
- gateway configuration failure;
- health/readiness failure;
- Redis connectivity failure;
- PostgreSQL connectivity failure;
- invalid/missing environment configuration;
- deployment rollback.

Application defects discovered during infrastructure work must be returned to
`moda_architect`.

## Scalability

Relevant scaling boundaries must be treated independently:

- public gateway instances;
- Shopify application instances;
- messaging ingress instances;
- admin instances where applicable;
- `moda-shopify-event-worker` instances;
- `moda-recovery-worker` instances;
- `moda-messaging-worker` instances;
- Redis Cloud capacity;
- PostgreSQL capacity.

Background worker work distribution remains:

```text
Redis Cloud / BullMQ
    ->
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

BullMQ/Redis distributes jobs across existing worker processes.

Render/infrastructure controls how many worker processes/instances exist.

Because Render background workers do not receive inbound network traffic,
ARCH-002 does not require an HTTP readiness endpoint for worker services.
BACKGROUND-002 instead provides bounded dependency preflight before queue
consumption plus a deterministic non-network readiness/diagnostic command for
infrastructure/system validation.

Worker capacity should consider:

- queue depth;
- queue lag;
- oldest-job age;
- processing throughput;
- retry rate;
- worker concurrency;
- Redis operations per job;
- downstream provider limits.

CPU/memory alone must not be treated as proof that a worker queue is keeping up.

Test should begin with the cheapest practical capacity while preserving the
architecture.

Production must preserve the raw Shopify ingress target:

```text
≈ 22,000 webhook requests/minute
≈ 367 requests/second
```

Production instance plans/counts are **ASSUMED/ESTIMATED** until measured load
testing validates them.

The architecture may later add queue-aware autoscaling only through a separate
approved task if measurements justify it.

## Security

- minimise publicly exposed services;
- keep provider-specific signature verification in owning ingress services;
- preserve provider signature headers;
- preserve body semantics required for HMAC/signature verification;
- never commit secrets;
- use Render/provider secret mechanisms;
- use TLS where required;
- preserve tenant/authentication boundaries;
- do not log credentials or tokens;
- isolate test and production credentials;
- isolate test and production Redis/PostgreSQL state;
- do not place production data in the test environment;
- do not weaken service exposure merely to reduce test-environment cost.

## Observability

Infrastructure documentation/configuration should cover:

- gateway access/error logs;
- request/correlation identifiers;
- service health;
- upstream failures;
- worker health where applicable;
- queue capacity signals;
- deployment failures;
- OpenTelemetry/OTLP infrastructure wiring;
- test/production telemetry isolation.

Canonical resource identity includes:

```text
service.namespace=moda-interact
service.name=<canonical-logical-service>
deployment.environment.name=<environment>
```

For deployed ARCH-002 environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

Test and production OTLP credentials must be independently configurable.

If one observability backend is shared, production dashboards/alerts must filter
explicitly for the production deployment environment.

Observability must not become a correctness dependency for webhook
acknowledgement, BullMQ processing, recovery, WhatsApp/CommerceAgent processing
or database commits.

## Infrastructure Assessment

Infrastructure implementation is required.

The architecture therefore uses bounded `moda_gateway` tasks under:

```text
docs/decisions/gateway/ARCH-002/
```

Missing application capabilities discovered by GATEWAY-001 are created later
as owner-specific tasks by `moda_architect`.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|------|-------|--------|------------|
| ARCH-002-GATEWAY-001 | moda_gateway | Complete | - |
| ARCH-002-GATEWAY-002 | moda_gateway | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-001 | moda_app | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-002 | moda_app | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-003 | moda_app | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-004 | moda_app | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-MESSAGING-001 | moda_messaging | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-MESSAGING-002 | moda_messaging | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-ADMIN-001 | moda_admin | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-ADMIN-002 | moda_admin | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-BACKGROUND-001 | moda_background | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-BACKGROUND-002 | moda_background | Pending | ARCH-002-BACKGROUND-001 |
| ARCH-002-BACKGROUND-003 | moda_background | Pending | ARCH-002-BACKGROUND-001 |
| ARCH-002-BACKGROUND-004 | moda_background | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-GATEWAY-005 | moda_gateway | Pending | ARCH-002-GATEWAY-001, ARCH-002-SHOPIFY-004, ARCH-002-BACKGROUND-004 |
| ARCH-002-GATEWAY-006 | moda_gateway | Pending | ARCH-002-GATEWAY-002, ARCH-002-SHOPIFY-003, ARCH-002-MESSAGING-002, ARCH-002-ADMIN-002, ARCH-002-BACKGROUND-003 |
| ARCH-002-GATEWAY-003 | moda_gateway | Pending | ARCH-002-GATEWAY-002, ARCH-002-GATEWAY-005, ARCH-002-GATEWAY-006, ARCH-002-SHOPIFY-001, ARCH-002-SHOPIFY-002, ARCH-002-MESSAGING-001, ARCH-002-ADMIN-001, ARCH-002-BACKGROUND-001, ARCH-002-BACKGROUND-002 |
| ARCH-002-GATEWAY-004 | moda_gateway | Pending | ARCH-002-GATEWAY-003 |
| ARCH-002-SYSTEM-TEST-001 | moda_system_test | Pending | ARCH-002-GATEWAY-004 |

`ARCH-002-GATEWAY-003` remains Pending.

Before it becomes Ready:

1. every declared prerequisite must be Complete;
2. GATEWAY-005 must prove service-local npm-based app/background builds;
3. GATEWAY-006 must establish the accepted OTLP/environment wiring model;
4. application health/startup/worker prerequisites must be accepted;
5. the two canonical Blueprint files defined by this architecture must remain the
   task target.

`ARCH-002-SYSTEM-TEST-001` already exists as the integrated validation task.

Its durable dependency is `ARCH-002-GATEWAY-004`, the final infrastructure
validation gate. GATEWAY-004 is expected to become Complete only after
GATEWAY-003 and all transitive application/build/observability prerequisites are
architect-accepted.

SYSTEM-TEST-001 performs full functional validation in the isolated test
environment, validates production configuration/isolation, and requires measured
capacity evidence before ARCH-002 claims the approximately 22,000-webhooks/minute
production target.

The cheap test environment is not production-capacity evidence.

The architecture must not mark system testing Ready merely because the gateway
itself is deployable.

## Open Questions

Remaining implementation/measurement questions include:

- exact test-environment Render plans after the gateway agent validates the
  service types supported by the current Render Blueprint model;
- actual production HTTP instance plans/minimums/maximums;
- measured gateway/application capacity at the 22,000-webhooks/minute target;
- measured worker throughput and queue-lag behaviour;
- whether queue-aware autoscaling is justified after measurement;
- PostgreSQL production infrastructure sizing/choice;
- Redis Cloud production tier/region/TLS/connection capacity;
- final production admin route/base-path or host-routing contract;
- final production public-route hardening for the development catch-all gateway
  route.

The following are no longer open architecture questions:

- shared-package production distribution: published npm artifact;
- canonical Blueprint model: separate test and production files;
- initial worker deployment units: Shopify event, recovery, messaging;
- replica startup: seed excluded from normal application startup.

## Relationship to ARCH-001

ARCH-001 remains the Shopify checkout-recovery architecture.

Any ARCH-001 gateway task is limited to deployability requirements of that
initiative.

ARCH-002 owns the broader platform-wide production ingress/networking/topology.

ARCH-002 discovery should reuse accepted ARCH-001 deployment findings and must
not duplicate or silently override them.

## Change History

### 2026-08-29

Reformatted the original ARCH-002 gateway bundle to the current
`moda_architect` coordination protocol:

- added canonical YAML frontmatter;
- made GATEWAY-001 the only immediately executable discovery task;
- removed placeholder dependencies from YAML;
- deferred system-test task creation until dependencies are Complete;
- documented relationship with ARCH-001;
- retained the original gateway/private-service target as a proposed topology
  subject to repository discovery.

### 2026-08-29 — GATEWAY-001 accepted

- accepted the deployment-prerequisite discovery baseline;
- selected workspace-superproject build context for the shared package rather
  than introducing registry publication;
- required migrations to move out of replica startup and prohibited automatic
  seed-on-every-replica startup;
- selected three initial independently deployable background worker pools:
  Shopify events, recovery, and messaging/CommerceAgent;
- decomposed health/readiness and OpenTelemetry work by repository ownership;
- kept GATEWAY-002 independently executable;
- kept GATEWAY-003 pending on concrete deployability/observability prerequisites;
- retained `moda-interact-gateway/render.yaml` as the canonical Render Blueprint.

### 2026-08-29 — GATEWAY-002 accepted and deployment model refined

- accepted `ARCH-002-GATEWAY-002` as Complete after gateway security correction
  and validation;
- superseded the earlier workspace-superproject production build-context
  decision with the published npm package boundary for
  `@modainteract/moda-interact-shared`;
- introduced `ARCH-002-SHOPIFY-004` and `ARCH-002-BACKGROUND-004` as the
  consumer-owned npm dependency tasks;
- removed the speculative `ARCH-002-SHARED-001` dependency from GATEWAY-005;
- defined two canonical Render Blueprint files:
  `moda-interact-gateway/render.test.yaml` and
  `moda-interact-gateway/render.production.yaml`;
- required test and production to use isolated state/secrets;
- defined test as the cheapest practical topology that preserves production
  service boundaries;
- raised the production raw Shopify ingress capacity target to approximately
  22,000 webhooks/minute (~367/second);
- required unmeasured production hardware/instance sizing to remain
  ASSUMED/ESTIMATED until load testing validates capacity;
- preserved the three independent background worker deployment units;
- recorded that `ARCH-002-SYSTEM-TEST-001` exists and remains Pending until its
  implementation/infrastructure/observability prerequisites are Complete.

### 2026-08-29 — application/runtime prerequisite tasks refined

- defined deterministic `/health` and `/ready` contracts for Shopify and
  messaging private HTTP services;
- clarified that Render background workers do not receive inbound traffic and
  therefore use bounded dependency preflight plus a non-network readiness
  command rather than an HTTP readiness contract;
- required graceful shutdown and strict worker-entrypoint isolation for the
  three independently scalable background worker services;
- made Shopify, messaging and worker OpenTelemetry tasks explicitly preserve
  stable service names across isolated test and production environments;
- added bounded telemetry/cardinality and secret-handling requirements;
- rewrote `ARCH-002-SYSTEM-TEST-001` into the current coordination format;
- made the test environment the primary functional integration environment;
- separated cheap test-environment correctness from production capacity
  validation;
- required measured evidence before claiming approximately 22,000 Shopify
  webhooks/minute production capacity.

### 2026-08-29 — remaining ARCH-002 tasks and indexes reconciled

- defined deterministic `/health` and `/ready` contracts for the internal admin
  service without conflating those operational routes with the unresolved
  production admin base-path/host-routing decision;
- made admin OpenTelemetry explicitly test/production-aware and strengthened
  cross-tenant/database telemetry data-safety requirements;
- retained SHOPIFY-004 and BACKGROUND-004 as the consumer-owned exact npm package
  migration tasks and required current-artifact compatibility validation;
- reconciled Shopify, messaging, background, admin, gateway and system-test
  ARCH-002 indexes with the current dependency graph;
- recorded GATEWAY-002 as Complete, GATEWAY-005/GATEWAY-003 as Pending, and
  SYSTEM-TEST-001 as Pending on GATEWAY-004;
- removed stale index references to the old single `render.yaml`,
  workspace-root production build model and not-yet-created system-test task.
