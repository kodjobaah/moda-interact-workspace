---
id: ARCH-002
title: Render production gateway and infrastructure
status: in_progress
coordinator: moda_architect
created: 2026-08-29
updated: 2026-08-29
---

# ARCH-002: Render Production Gateway and Infrastructure

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

- establish the production public ingress boundary;
- minimise direct public exposure of application services;
- route public HTTP traffic through a thin infrastructure gateway;
- preserve Shopify and Meta webhook verification in the owning services;
- define Render service topology from actual repository capabilities;
- define Redis Cloud and PostgreSQL infrastructure wiring;
- preserve independent application/background scaling boundaries;
- document deployment, health, rollback, scaling and cost assumptions;
- validate infrastructure before integrated system testing.

Planning workload:

```text
Shopify inbound events ≈ 20,000/minute ≈ 333/second
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

Development/staging infrastructure may be replaced as necessary after required
configuration and system validation.

The exact deployment order must be established from actual service
prerequisites rather than copied from an example.

## Current Architecture

Accepted discovery establishes:

- the workspace superproject uses Git submodules for application/shared
  repositories;
- `moda-interact` and `moda-interact-background` consume
  `@modainteract/moda-interact-shared` through a sibling `file:` dependency;
- clean service-local Docker builds cannot currently resolve that sibling package;
- `moda-interact` and `moda-interact-messaging` have no health/readiness endpoint;
- `moda-interact-admin` has no health/readiness endpoint;
- `moda-interact-background` has liveness but not dependency readiness;
- all background worker classes currently start from one process and cannot be
  independently deployed/scaled;
- `moda-interact` currently runs Prisma migration and seed work on every replica
  startup;
- no OpenTelemetry implementation was found in the inspected deployable units;
- the gateway implementation itself remains downstream work.

### Shared package build decision

ARCH-002 selects **workspace-superproject build context** rather than introducing
a registry publication requirement.

Render supports repository-root Docker build context for monorepo services and
automatically clones Git submodules from a repository's root `.gitmodules`.

The target therefore keeps `moda-interact-shared` as a sibling build input and
updates infrastructure Docker/build configuration so app/background production
builds can consume the canonical shared package from the workspace checkout.

This decision is implemented by `ARCH-002-GATEWAY-005`.

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

Target direction, subject to GATEWAY-001 validation:

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
- Render Blueprint/topology;
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
- background worker instances;
- Redis Cloud capacity;
- PostgreSQL capacity.

Worker capacity should consider queue depth, queue lag, oldest-job age,
processing throughput, retry rate, worker concurrency and downstream provider
limits.

Planning values are ASSUMED until measured.

## Security

- minimise publicly exposed services;
- keep provider-specific signature verification in owning ingress services;
- preserve provider signature headers;
- preserve body semantics required for HMAC/signature verification;
- never commit secrets;
- use Render/provider secret mechanisms;
- use TLS where required;
- preserve tenant/authentication boundaries;
- do not log credentials or tokens.

## Observability

Infrastructure documentation/configuration should cover:

- gateway access/error logs;
- request/correlation identifiers;
- service health;
- upstream failures;
- worker health where applicable;
- queue capacity signals;
- deployment failures.

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
| ARCH-002-GATEWAY-002 | moda_gateway | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-GATEWAY-005 | moda_gateway | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-001 | moda_app | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-002 | moda_app | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-003 | moda_app | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-MESSAGING-001 | moda_messaging | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-MESSAGING-002 | moda_messaging | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-ADMIN-001 | moda_admin | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-ADMIN-002 | moda_admin | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-BACKGROUND-001 | moda_background | Ready | ARCH-002-GATEWAY-001 |
| ARCH-002-BACKGROUND-002 | moda_background | Pending | ARCH-002-BACKGROUND-001 |
| ARCH-002-BACKGROUND-003 | moda_background | Pending | ARCH-002-BACKGROUND-001 |
| ARCH-002-GATEWAY-006 | moda_gateway | Pending | ARCH-002-GATEWAY-002, ARCH-002-SHOPIFY-003, ARCH-002-MESSAGING-002, ARCH-002-ADMIN-002, ARCH-002-BACKGROUND-003 |
| ARCH-002-GATEWAY-003 | moda_gateway | Pending | ARCH-002-GATEWAY-002, ARCH-002-GATEWAY-005, ARCH-002-GATEWAY-006, ARCH-002-SHOPIFY-001, ARCH-002-SHOPIFY-002, ARCH-002-MESSAGING-001, ARCH-002-ADMIN-001, ARCH-002-BACKGROUND-001, ARCH-002-BACKGROUND-002 |
| ARCH-002-GATEWAY-004 | moda_gateway | Pending | ARCH-002-GATEWAY-003 |

After GATEWAY-001 review, `moda_architect` must:

1. create any concrete prerequisite tasks for owning agents;
2. add their fully-qualified IDs to downstream `depends_on`;
3. refine the architecture from inspected facts;
4. agree the implementation topology with the user;
5. only then mark appropriate downstream tasks Ready.

A system-test task is intentionally **not created yet**.

Once all required implementation, infrastructure and observability tasks are
Complete, `moda_architect` creates `ARCH-002-SYSTEM-TEST-001` for
`moda_system_test`.

## Open Questions

To be resolved by GATEWAY-001 and architect review:

- actual Render repository/build-context model;
- actual build/start commands;
- current health/readiness capabilities;
- current worker entrypoints;
- which worker classes require independent services;
- actual shared-package distribution/build strategy;
- exact private-service route contract;
- actual baseline Render plans and scaling limits;
- PostgreSQL production infrastructure choice;
- Redis Cloud region/TLS/connection assumptions.

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
