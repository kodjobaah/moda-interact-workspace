---
id: ARCH-002
title: Render test and production gateway and infrastructure
status: in_progress
coordinator: moda_architect
created: 2026-08-29
updated: 2026-09-03
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
            |               |               |
            +-------+-------+               |
                    |                       |
                 Redis Cloud                |
                    |                       |
         BullMQ worker services             |
          +---------+---------+             |
          |         |         |             |
          v         v         v             |
   Shopify-event  Recovery  Messaging/      |
      worker      worker   CommerceAgent     |
          |         |         |             |
          +---------+---------+-------------+
                    |
                PostgreSQL
```

Background workers are private Render Background Worker deployments. They are
not HTTP upstreams and are not routed through the gateway. Redis/BullMQ
coordinates work distribution to the three independently scalable worker pools.

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

### Admin control plane

Production browser contract:

```text
Administrator
    -> admin.modainteract.com
    -> Render public ingress
    -> moda-interact-gateway
    -> moda-interact-admin private service
    -> platform-admin authentication / authorisation
```

The Admin application remains rooted at `/`. ARCH-002 selects host-based routing
instead of introducing a Next.js `/admin` base path.

The production Admin hostname is:

```text
admin.modainteract.com
```

The test Admin hostname is deployment-configured and must remain isolated from
production.

The Admin service itself remains private on Render. Gateway routing is not an
authentication mechanism; `moda-interact-admin` must independently enforce the
platform-admin boundary.

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

### moda_admin

Owns the platform-admin application security boundary and internal operational
presentation. The Admin service remains a private Render HTTP service.

`moda_admin` does not own public host routing, Render topology or observability
transport infrastructure.

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
- do not weaken service exposure merely to reduce test-environment cost;
- keep `moda-interact-admin` private on Render and expose browser traffic only
  through the gateway host-routing contract;
- require application-level platform-admin authentication and server-side
  authorisation for privileged Admin functionality;
- do not treat gateway routing/private networking as a substitute for Admin
  authorisation;
- do not make Grafana operational dashboards anonymous/public merely to enable
  iframe embedding;
- keep Admin and Grafana credentials/session material out of logs/telemetry.

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

The Admin `/observability` page is the internal operational presentation
boundary. The intended live Grafana presentation may use an iframe only when the
selected Grafana capability supports private authenticated embedding. Anonymous
or publicly shared dashboard access is not architecture-conformant. If secure
embedding is unavailable, the implementation task must return Blocked to
`moda_architect` rather than weakening dashboard access.

Observability must not become a correctness dependency for webhook
acknowledgement, BullMQ processing, recovery, WhatsApp/CommerceAgent processing
or database commits.

### Third-Party Telemetry Trust Boundary

ARCH-002 distinguishes between Moda-owned telemetry and telemetry emitted by
supported third-party frameworks and OpenTelemetry instrumentation libraries.

#### Moda-owned telemetry

Telemetry explicitly created or enriched by Moda Interact application code is
subject to Moda's observability safety requirements.

Moda-owned telemetry must:

- avoid secrets, credentials and sensitive payload content;
- use bounded metric dimensions;
- avoid unbounded customer, tenant, conversation, message or provider identifiers
  where prohibited by the relevant telemetry contract;
- preserve application correctness when telemetry recording or export fails.

#### Third-party telemetry

Telemetry generated by supported frameworks, runtime libraries and standard
OpenTelemetry instrumentation is treated as trusted operational telemetry.

Examples include telemetry generated by:

- Next.js;
- OpenTelemetry HTTP instrumentation;
- OpenTelemetry Undici/fetch instrumentation;
- Prisma instrumentation;
- BullMQ/OpenTelemetry integrations;
- other architecture-approved instrumentation libraries.

Moda Interact does not rewrite, sanitize, reinterpret or patch attributes owned
by those third-party telemetry producers solely to conform them to Moda-owned
telemetry conventions.

Third-party telemetry may be exported unchanged to the configured internal
observability backend and displayed in Grafana.

Moda's sensitive-data and bounded-attribute guarantees apply to telemetry
explicitly created or enriched by Moda-owned application code, not to arbitrary
attributes emitted by trusted third-party instrumentation.

Third-party operational telemetry remains subject to the internal observability
access boundary and must not be exposed through tenant-facing or public
interfaces.


### Framework-First Telemetry Reuse

Trusted third-party telemetry should be reused rather than duplicated.

Before ARCH-002 creates or accepts Moda-owned technical telemetry, the owning
agent and `moda_architect` must establish whether the enabled Next.js/runtime/
OpenTelemetry/shared instrumentation already emits an operationally equivalent
signal.

If it does, that standard signal is the architecture-approved source for the
technical lifecycle and may be queried/displayed directly in Grafana. Moda must
not add a parallel metric/span solely to rename, re-bucket, relabel or maintain
a second route taxonomy for the same request/job/client lifecycle.

Generic HTTP request count, duration, status, method and route telemetry are
framework/runtime concerns when supplied by the approved instrumentation. A new
application route must not require edits to a custom Moda request-metric schema
merely to remain observable.

Moda-owned telemetry is reserved for additional Moda-specific semantic meaning
that generic instrumentation cannot know, or for a documented operational
property that existing telemetry does not supply with sufficient accuracy or
signal semantics.

When a task is discovered to duplicate an existing approved telemetry
capability, `moda_architect` must narrow or supersede the task rather than
requiring the duplicate implementation to be completed.

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
| ARCH-002-SHOPIFY-002 | moda_app | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-003 | moda_app | Superseded | SHOPIFY-006/007 |
| ARCH-002-SHOPIFY-004 | moda_app | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-SHOPIFY-006 | moda_app | Complete | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-SHOPIFY-007 | moda_app | Complete | ARCH-002-SHOPIFY-006 |
| ARCH-002-SHOPIFY-008 | moda_app | Complete | ARCH-002-SHOPIFY-002 |
| ARCH-002-MESSAGING-001 | moda_messaging | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-MESSAGING-002 | moda_messaging | Superseded | MESSAGING-003/004/005 |
| ARCH-002-MESSAGING-003 | moda_messaging | Complete | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-MESSAGING-004 | moda_messaging | Complete | ARCH-002-MESSAGING-003 |
| ARCH-002-MESSAGING-005 | moda_messaging | Complete | ARCH-002-MESSAGING-003 |
| ARCH-002-ADMIN-001 | moda_admin | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-ADMIN-002 | moda_admin | Superseded | ADMIN-009/010 |
| ARCH-002-DATABASE-001 | moda_database | Complete | - |
| ARCH-002-ADMIN-003 | moda_admin | Complete | ARCH-002-DATABASE-001 |
| ARCH-002-ADMIN-005 | moda_admin | Complete | ARCH-002-ADMIN-003 |
| ARCH-002-ADMIN-006 | moda_admin | Complete | ARCH-002-ADMIN-003 |
| ARCH-002-ADMIN-007 | moda_admin | Complete | ARCH-002-ADMIN-005, ARCH-002-ADMIN-006, ARCH-002-SHARED-005 |
| ARCH-002-ADMIN-008 | moda_admin | Complete | ARCH-002-ADMIN-003, ARCH-002-ADMIN-005, ARCH-002-ADMIN-006, ARCH-002-ADMIN-007 |
| ARCH-002-ADMIN-004 | moda_admin | Complete | ARCH-002-ADMIN-008, ARCH-002-GATEWAY-006 |
| ARCH-002-ADMIN-009 | moda_admin | Complete | ARCH-002-GATEWAY-001, ARCH-002-SHARED-010 |
| ARCH-002-ADMIN-010 | moda_admin | Superseded | Duplicate of standard framework/OpenTelemetry HTTP request telemetry |
| ARCH-002-ADMIN-011 | moda_admin | Complete | ARCH-002-ADMIN-005 |
| ARCH-002-BACKGROUND-001 | moda_background | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-BACKGROUND-002 | moda_background | Complete | ARCH-002-BACKGROUND-001 |
| ARCH-002-BACKGROUND-003 | moda_background | Superseded | Replaced by BACKGROUND-005/006/007/008/009 |
| ARCH-002-BACKGROUND-004 | moda_background | Complete | ARCH-002-GATEWAY-001 |
| ARCH-002-GATEWAY-005 | moda_gateway | Complete | ARCH-002-GATEWAY-001, ARCH-002-SHOPIFY-004, ARCH-002-BACKGROUND-004 |
| ARCH-002-GATEWAY-006 | moda_gateway | Complete | ARCH-002-GATEWAY-002, ARCH-002-SHOPIFY-006, ARCH-002-MESSAGING-003, ARCH-002-ADMIN-009, ARCH-002-BACKGROUND-005 |
| ARCH-002-GATEWAY-007 | moda_gateway | Complete | ARCH-002-GATEWAY-002, ARCH-002-ADMIN-008 |
| ARCH-002-GATEWAY-008 | moda_gateway | Complete | ARCH-002-GATEWAY-003, ARCH-002-ADMIN-004, ARCH-002-ADMIN-009 |
| ARCH-002-GATEWAY-009 | moda_gateway | Pending | ARCH-002-GATEWAY-003, ARCH-002-GATEWAY-008, ARCH-002-GATEWAY-010 |
| ARCH-002-GATEWAY-010 | moda_gateway | Ready | ARCH-002-GATEWAY-008 |
| ARCH-002-GATEWAY-003 | moda_gateway | Complete | ARCH-002-GATEWAY-002, ARCH-002-GATEWAY-005, ARCH-002-GATEWAY-006, ARCH-002-GATEWAY-007, ARCH-002-SHOPIFY-001, ARCH-002-SHOPIFY-002, ARCH-002-MESSAGING-001, ARCH-002-ADMIN-001, ARCH-002-ADMIN-008, ARCH-002-BACKGROUND-001, ARCH-002-BACKGROUND-002 |
| ARCH-002-GATEWAY-004 | moda_gateway | Complete | ARCH-002-GATEWAY-003 |
| ARCH-002-SYSTEM-TEST-001 | moda_system_test | Pending | ARCH-002-SYSTEM-TEST-002, ARCH-002-SYSTEM-TEST-006, ARCH-002-SYSTEM-TEST-007, ARCH-002-SYSTEM-TEST-008 |
| ARCH-002-SYSTEM-TEST-002 | moda_system_test | Complete | ARCH-002-SHOPIFY-007, ARCH-002-BACKGROUND-007, ARCH-002-BACKGROUND-009, ARCH-002-MESSAGING-004, ARCH-002-MESSAGING-005, ARCH-002-ADMIN-009, ARCH-002-GATEWAY-006, ARCH-002-GATEWAY-004, ARCH-002-SYSTEM-TEST-003, ARCH-002-SYSTEM-TEST-004, ARCH-002-SYSTEM-TEST-005 |
| ARCH-002-SYSTEM-TEST-003 | moda_system_test | Complete | - |
| ARCH-002-SYSTEM-TEST-004 | moda_system_test | Complete | ARCH-002-BACKGROUND-010 |
| ARCH-002-SYSTEM-TEST-005 | moda_system_test | Complete | - |
| ARCH-002-SYSTEM-TEST-006 | moda_system_test | Complete | ARCH-002-GATEWAY-004, ARCH-002-ADMIN-004, ARCH-002-SHOPIFY-008, ARCH-002-GATEWAY-008, ARCH-002-GATEWAY-009, ARCH-002-GATEWAY-010 |
| ARCH-002-SYSTEM-TEST-007 | moda_system_test | Complete | ARCH-002-GATEWAY-004 |
| ARCH-002-SYSTEM-TEST-008 | moda_system_test | Pending | ARCH-002-SYSTEM-TEST-002, ARCH-002-SYSTEM-TEST-006, ARCH-002-SYSTEM-TEST-007, ARCH-002-SYSTEM-TEST-009 |
| ARCH-002-SYSTEM-TEST-009 | moda_system_test | Pending | ARCH-002-GATEWAY-010, ARCH-002-SYSTEM-TEST-007 |

`ARCH-002-GATEWAY-003` and `ARCH-002-GATEWAY-004` are Complete.

The current system-validation frontier is intentionally decomposed by environment and evidence boundary:

```text
ARCH-002-SYSTEM-TEST-002   Complete local deterministic observability/integration
ARCH-002-SHOPIFY-008       Complete fix Shopify Render Docker build
ARCH-002-GATEWAY-008       Complete fix Admin Render build dependencies
ARCH-002-GATEWAY-010       Ready   rename deployment config groups
ARCH-002-GATEWAY-009       Pending codify test gateway custom domains
ARCH-002-SYSTEM-TEST-006   Complete deployed Render test topology
ARCH-002-SYSTEM-TEST-007   Complete production Blueprint/readiness
              \             |             /
               \            |            /
                +------> ARCH-002-SYSTEM-TEST-008 Pending
                         production-sized capacity gate
                                   |
                                   v
                         ARCH-002-SYSTEM-TEST-001 Pending
                         final evidence aggregation
```

`SYSTEM-TEST-002` is architect-accepted Complete. Its local deterministic
evidence includes cross-service trace continuity, worker/GenAI metrics,
telemetry-backend failure isolation, Admin Prisma telemetry against isolated
PostgreSQL, and bounded synthetic WhatsApp timing evidence.

`SYSTEM-TEST-006` is architect-accepted Complete for the current Render
deployment-topology milestone. The remaining Meta verification GET `403` is
explicitly deferred to the later WhatsApp/Messaging integration validation and
is not recorded as a passing assertion. The next active Render investigation is
the Shopify checkout -> queue -> background-worker processing path. No further
probe implementation work is currently required.

The local ephemeral Redis/PostgreSQL/WhatsApp fixtures belong to
`SYSTEM-TEST-002`. They are not direct dependencies of deployed Render test
validation and must not be represented as infrastructure consumed by Render
services.

`SYSTEM-TEST-006` validates the actual deployed Render test boundary and must
return Blocked if mandatory live test-environment inputs are unavailable rather
than substituting local processes.

`SYSTEM-TEST-007` statically validates the actual current production/test
Blueprint and gateway-readiness configuration without requiring live production.

`SYSTEM-TEST-007` is architect-accepted Complete. `SYSTEM-TEST-006` remains Blocked on the five live Render test inputs.

`SYSTEM-TEST-008` becomes Ready only after SYSTEM-TEST-002/006/007 are accepted.
It records the approximately 22,000-webhooks/minute production ingress capacity
gate as exactly `PROVEN` or `UNMET`; the cheap Render test environment cannot
produce `PROVEN` production-capacity evidence.

`SYSTEM-TEST-001` is now a final evidence-aggregation task. It becomes Ready only
after SYSTEM-TEST-002/006/007/008 are architect-accepted Complete and must not
repeat their implementation or broad validation work.

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
- final production public-route hardening for the development catch-all gateway
  route.

The following are no longer open architecture questions:

- shared-package production distribution: published npm artifact;
- canonical Blueprint model: separate test and production files;
- initial worker deployment units: Shopify event, recovery, messaging;
- replica startup: seed excluded from normal application startup;
- production Admin route model: `admin.modainteract.com` host routing through the
  gateway to the private Admin service; no Next.js `/admin` base path.

## Relationship to ARCH-001

ARCH-001 remains the Shopify checkout-recovery architecture.

Any ARCH-001 gateway task is limited to deployability requirements of that
initiative.

ARCH-002 owns the broader platform-wide production ingress/networking/topology.

ARCH-002 discovery should reuse accepted ARCH-001 deployment findings and must
not duplicate or silently override them.

## Change History

### 2026-09-03 — Deployment environment-group resource naming

- live Render deployment evidence established that the shared environment group
  is deployment configuration, not an observability-only runtime resource;
- feature-oriented names `moda-observability-test` and
  `moda-observability-production` are therefore deprecated as infrastructure
  resource names;
- canonical names are `moda-interact-test-config` and
  `moda-interact-production-config`;
- created `ARCH-002-GATEWAY-010` to establish the canonical Blueprint resource
  names and all gateway-owned references for clean recreation;
- the previous Blueprint instance and test Environment Group were deleted before
  implementation, so the operational path is now clean recreation rather than a
  live rename;
- `GATEWAY-009` waits for `GATEWAY-010` so custom-domain work applies to the
  final recreated Blueprint state;
- created `ARCH-002-SYSTEM-TEST-009` to update the accepted static readiness
  validator to the new concrete resource names;
- `SYSTEM-TEST-008` now also waits for SYSTEM-TEST-009.


### 2026-09-03 — Render test custom domains

- the Render test gateway is live at
  `moda-interact-gateway-test.onrender.com`;
- Cloudflare DNS-only CNAME records were created for
  `admin-test.modainteract.com` and `app-test.modainteract.com`, both targeting
  the test gateway;
- created `ARCH-002-GATEWAY-009` to codify those two custom domains directly on
  the canonical `render.test.yaml` web-service declaration;
- production custom domains remain out of scope pending explicit production
  hostname decisions;
- `SYSTEM-TEST-006` remains Blocked until the Blueprint is synchronized,
  domains are verified/TLS-enabled, test services are healthy and live test
  inputs are supplied.


### 2026-09-03 — Render test Admin build failure

- deployment of `moda-interact-admin-test` reached the Next/PostCSS build but
  failed because `@tailwindcss/postcss` was unavailable;
- the Admin repository already declares the package as a build-time
  `devDependency`;
- the canonical Blueprints run plain `npm ci` while supplying
  `NODE_ENV=production`, creating a Render build dependency mismatch;
- created and architect-accepted `ARCH-002-GATEWAY-008`, using explicit
  dev-inclusive locked dependency installation for both test and production
  Admin build commands;
- no Admin source/dependency reclassification was required;
- the corrected Admin test service must now be redeployed;
- deployed topology validation `SYSTEM-TEST-006` remains Blocked until the
  Admin test service is healthy and its live environment inputs are available.


### 2026-09-03 — Render test Shopify build failure

- deployment of `moda-interact-test` exposed a Docker build dependency-order
  defect: the image runs production-only `npm ci --omit=dev` before the
  Vite/React Router build, while `@tailwindcss/vite` and related build tooling
  are development dependencies;
- created `ARCH-002-SHOPIFY-008` as a bounded `moda_app` task;
- required the correction to preserve Render's accepted
  `preDeployCommand: npm run migrate` lifecycle;
- added `SHOPIFY-008` as a dependency of deployed Render validation
  `SYSTEM-TEST-006`;
- `SHOPIFY-008` is architect-accepted Complete; a fresh Render deployment of
  `moda-interact-test` must now use the corrected image contract;
- `SYSTEM-TEST-006` remains Blocked until that deployment is healthy and the
  five live test inputs are available.


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


### 2026-08-31 — Admin Render/control-plane routing and Grafana presentation

- confirmed `moda-interact-admin` remains a private Render HTTP service rather
  than a separate Vercel/public application deployment;
- resolved the production Admin browser contract as
  `admin.modainteract.com -> moda-interact-gateway -> private moda-interact-admin`;
- selected host-based routing and explicitly rejected requiring a Next.js
  `/admin` base path;
- added `ARCH-002-ADMIN-003` for platform-admin authentication/authorisation;
- added `ARCH-002-GATEWAY-007` as a bounded follow-up to replace the provisional
  GATEWAY-002 `/admin/*` mapping without reopening the accepted task;
- added `ARCH-002-ADMIN-004` for secure live Grafana presentation after Admin
  security and observability transport are available;
- prohibited anonymous/public Grafana sharing merely to support iframe
  embedding;
- updated GATEWAY-003/GATEWAY-004 and SYSTEM-TEST-001 dependencies/assertions;
- clarified in the primary topology diagram that the three BullMQ worker pools
  are private background worker deployments behind Redis rather than HTTP
  gateway upstreams.

<!-- ARCH-002-SHARED-LOGGING-AMENDMENT:START -->
## Shared Structured Logging Amendment

Generic structured application logging is owned by:

```text
ARCH-002-SHARED-002
@modainteract/moda-interact-shared/logging
```

`ARCH-002-SHOPIFY-003` is Blocked until that shared task is architect-accepted.

Service-specific OpenTelemetry remains in the owning runtime repository.
Generic logging must not automatically create metrics/spans.

Durable design:

`docs/architecture/ARCH-002-shared-logging-amendment.md`

Consumer guide:

`docs/observability/shared-logging.md`

<!-- ARCH-002-SHARED-LOGGING-AMENDMENT:END -->


### 2026-08-31 — Admin security decomposition

See `docs/architecture/ARCH-002-admin-security-amendment.md`. The former broad ADMIN-003 security task is decomposed into DATABASE-001 and ADMIN-003/005/006/007/008. Development auth bypass is allowed only for the development deployment environment and never in a production Node process.

## Shared observability runtime amendment

See `docs/architecture/ARCH-002-shared-observability-runtime-amendment.md` and
the durable consumer contract at
`docs/observability/shared-observability-runtime.md`.


### 2026-08-31 — Shared observability release `0.4.0` and granular consumer rollout

`ARCH-002-SHARED-010` is architect-accepted Complete. The exact consumer release
is `@modainteract/moda-interact-shared@0.4.0`.

The former broad SHOPIFY-003, MESSAGING-002 and ADMIN-002 observability tasks are
Superseded by granular consumer tasks:

- SHOPIFY-006 -> SHOPIFY-007
- MESSAGING-003 -> MESSAGING-004 and MESSAGING-005
- ADMIN-009 (ADMIN-010 superseded: standard HTTP request telemetry is reused)

BACKGROUND-003 is Superseded. The accepted background observability gates are
BACKGROUND-007 for worker operational metrics and BACKGROUND-009 for the final
GenAI operational metrics chain.

GATEWAY-006 depends on deployable runtime/exporter contracts rather than superseded
broad tasks and is architect-accepted Complete. SYSTEM-TEST-002 consumes the
granular semantic telemetry gates plus the accepted observability transport model,
but integrated observability validation must also wait for the infrastructure
validation gate that establishes the integrated test topology.


### 2026-09-02 — Observability coordination reconciliation

`ARCH-002-SYSTEM-TEST-002` remains Pending on SHOPIFY-007, MESSAGING-004,
MESSAGING-005, ADMIN-009, BACKGROUND-007, BACKGROUND-009, GATEWAY-006 and
GATEWAY-004. GATEWAY-004 is required because SYSTEM-TEST-002 validates the
integrated test topology rather than only repository-local telemetry.
Superseded ADMIN-010 and BACKGROUND-003 must not satisfy active dependencies.


### 2026-09-02 — GATEWAY-006 dependency reconciliation

- reduced GATEWAY-006 direct dependencies to accepted deployable runtime/exporter
  contracts: GATEWAY-002, SHOPIFY-006, MESSAGING-003, ADMIN-009 and
  BACKGROUND-005;
- kept semantic telemetry tasks out of the transport-configuration critical path;
- retained SHOPIFY-007, MESSAGING-004, MESSAGING-005, BACKGROUND-007 and
  BACKGROUND-009 as SYSTEM-TEST-002 integration prerequisites;
- recorded GATEWAY-006 as enabling GATEWAY-003, ADMIN-004 and SYSTEM-TEST-002.

### 2026-09-02 — Post-GATEWAY-006 dependency re-evaluation

`ARCH-002-GATEWAY-006` is architect-accepted Complete.

The authoritative `GATEWAY-003` task remains **Pending**. Its currently
unresolved direct prerequisites are:

```text
ARCH-002-GATEWAY-005
ARCH-002-GATEWAY-007
ARCH-002-MESSAGING-001
ARCH-002-ADMIN-001
ARCH-002-ADMIN-008
```

The current executable frontier is:

```text
ARCH-002-DATABASE-001
ARCH-002-SHOPIFY-004
ARCH-002-SHOPIFY-005
ARCH-002-MESSAGING-001
ARCH-002-ADMIN-001
```

`ARCH-002-DATABASE-001` is architect-accepted Complete and its accepted
implementation has been published at `moda-interact-database@9a286b7`.
`ADMIN-003` is therefore Ready and is now the next task on this critical path:

```text
DATABASE-001  Complete @ 9a286b7
    -> ADMIN-003  Complete
        -> ADMIN-005
            -> ADMIN-006
                -> ADMIN-007
                    -> ADMIN-008
                        -> GATEWAY-007
                            -> GATEWAY-003
```

`SHOPIFY-004` remains an important independent blocker because it enables
`GATEWAY-005`. `MESSAGING-001` and `ADMIN-001` are direct GATEWAY-003
prerequisites. `SHOPIFY-005` is executable but is not currently a declared
GATEWAY-003 dependency.

`SYSTEM-TEST-002` is not promoted merely because its former telemetry-only
dependencies are Complete. Its objective requires validation across the
integrated test topology, and ARCH-002 rollout places integration/system
validation after the test Blueprint/infrastructure gate. It therefore also
depends on `ARCH-002-GATEWAY-004`.


### 2026-09-02 — DATABASE-001 architect acceptance

- accepted `ARCH-002-DATABASE-001` as Complete;
- retained `ARCH-002-ADMIN-003` as Pending until the accepted database changes
  are committed/pushed by the developer and therefore available as a real
  submodule target;
- once publication is confirmed, `ADMIN-003` becomes the next task on the
  platform-admin security critical path.


### 2026-09-02 — DATABASE-001 publication gate satisfied

Developer publication confirmed:

```text
moda-interact-database
main
9a286b7 feat(database): added admin tables
origin/main
working tree clean
```

Consequences:

- `ARCH-002-DATABASE-001` remains Complete;
- `ARCH-002-ADMIN-003` is promoted `Pending -> Ready`;
- `ADMIN-003` must pin its nested database submodule to `9a286b7`;
- no downstream Admin task is promoted automatically.


### 2026-09-02 — ADMIN-003 architect acceptance

`ARCH-002-ADMIN-003` is architect-accepted Complete.

Accepted implementation properties:

```text
Google/Auth.js identity
verified Google email
PlatformAdmin allow-list
providerSubject binding/mismatch enforcement
bounded JWT session
fail-closed development-only bypass
local identity-only provisioning CLI
nested database gitlink -> 9a286b7
```

Final focused Admin validation includes:

```text
npm test
10 passed
0 failed
```

The repository agent did not commit or push.

The developer/user owns Admin repository publication after architect
acceptance.

No downstream task is promoted or started automatically by this acceptance.
The ARCH-002 executable frontier must be re-evaluated separately.


### 2026-09-02 — ADMIN-005 architect acceptance

`ARCH-002-ADMIN-005` is architect-accepted Complete.

Accepted boundary:

```text
privileged page
    -> direct page guard
    -> privileged data helper
    -> direct read guard
    -> Prisma
```

The protected route-group layout remains defence in depth rather than the sole
authorization control.

Current public auth/login/health routes remain outside that protected route
group.

The repository agent did not commit or push. The developer/user owns
publication after architect acceptance.

No downstream task is promoted or started automatically by this acceptance.


### 2026-09-02 — ADMIN-006 architect acceptance

`ARCH-002-ADMIN-006` is architect-accepted Complete.

The existing tenant mutation now enforces the platform-admin authorization
boundary before input handling or Prisma writes.

Current Admin source inventory found no additional privileged custom
server-action/API boundaries. Auth.js and bounded health routes remain public.

The repository agent did not commit or push. The developer/user owns
publication after architect acceptance.

No downstream task is promoted or started automatically by this acceptance.


### 2026-09-02 — ADMIN-007 ready

All explicit direct dependencies are architect-accepted Complete:

```text
ARCH-002-ADMIN-005
ARCH-002-ADMIN-006
ARCH-002-SHARED-005
```

`ARCH-002-ADMIN-007` is promoted `Pending -> Ready`.

This promotion does not start the task automatically and does not promote
`ADMIN-008`.


### 2026-09-02 — ADMIN-007 architect acceptance

`ARCH-002-ADMIN-007` is architect-accepted Complete.

The accepted Admin security-audit layer emits bounded domain events through the
shared logging facade without introducing a repository-local generic
logger/redaction/exporter stack.

The current Admin package remains pinned to the later accepted shared release:

```text
@modainteract/moda-interact-shared@0.4.0
```

which retains the shared logging capability.

The repository agent did not commit or push. The developer/user owns
publication after architect acceptance.

No downstream task is promoted or started automatically by this acceptance.


### 2026-09-02 — ADMIN-008 ready

All explicit direct dependencies are architect-accepted Complete:

```text
ARCH-002-ADMIN-003
ARCH-002-ADMIN-005
ARCH-002-ADMIN-006
ARCH-002-ADMIN-007
```

`ARCH-002-ADMIN-008` is promoted `Pending -> Ready`.

It is the final Admin application security/deployment validation gate before
`GATEWAY-007`, `GATEWAY-003`, and `ADMIN-004` may consume the accepted Admin
security boundary.

Repository-agent Git publication remains prohibited; the developer/user owns
commit and push after architect review.


### 2026-09-02 — ADMIN-008 attempt 2 ready

Attempt 1 confirmed the intended code shape but did not provide executable
coverage for several required final-gate matrix cases.

`ARCH-002-ADMIN-008` is returned:

```text
Review -> Ready
```

for attempt 2.

Downstream gates remain closed:

```text
ARCH-002-GATEWAY-007
ARCH-002-GATEWAY-003
ARCH-002-ADMIN-004
```

Acceptance requires focused security validation of the identity, revocation,
direct-mutation, environment and deployment matrix.

Repository-agent commit/push remains prohibited; the developer/user owns
publication after architect acceptance.


### 2026-09-02 — ADMIN-008 architect accepted

`ARCH-002-ADMIN-008` is Complete after four implementation/validation attempts.

The final accepted Admin security boundary has executable evidence for:

```text
environment bypass/fail-closed rules
Google verified/allow-listed identity rules
provider-subject binding and race handling
current-record revocation with an existing session
privileged page/read/mutation boundaries
guard-before-mutation behavior
bounded public health/readiness routes
hosted cookie/session security contract
bounded Admin security audit fields
test/production OAuth and environment isolation
```

This satisfies the `ADMIN-008` dependency edge for downstream tasks, but no
downstream status is changed by this acceptance record.

Developer publication of the accepted Admin module and parent-workspace
submodule pointer should occur before the next downstream task is started.

### 2026-09-02 — Post-ADMIN-008 dependency re-evaluation

`ARCH-002-ADMIN-008` is architect-accepted Complete.

A fresh evaluation of the authoritative individual task frontmatter produces
the following executable frontier:

```text
ARCH-002-SHOPIFY-004     Ready
ARCH-002-SHOPIFY-005     Ready
ARCH-002-MESSAGING-001   Ready
ARCH-002-ADMIN-001       Ready
ARCH-002-GATEWAY-007     Ready   <- newly unblocked
ARCH-002-ADMIN-004       Ready   <- newly unblocked
```

`ARCH-002-GATEWAY-003` remains Pending.

Its unresolved direct prerequisites are now:

```text
ARCH-002-GATEWAY-005
ARCH-002-GATEWAY-007
ARCH-002-MESSAGING-001
ARCH-002-ADMIN-001
```

The `ADMIN-008` dependency edge is satisfied.

`GATEWAY-005` remains Pending on:

```text
ARCH-002-SHOPIFY-004
```

because its other direct dependencies are already Complete.

The topology critical path now converges as:

```text
SHOPIFY-004 -> GATEWAY-005 ---+
GATEWAY-007 ------------------+
MESSAGING-001 ----------------+--> GATEWAY-003 -> GATEWAY-004
ADMIN-001 --------------------+
```

Separately:

```text
ADMIN-004 ---------------------------> SYSTEM-TEST-001
GATEWAY-004 -------------------------+-> SYSTEM-TEST-001
GATEWAY-004 + telemetry prerequisites -> SYSTEM-TEST-002
```

`SYSTEM-TEST-002` remains Pending. Its body and system-test index already state
that `GATEWAY-004` is a direct infrastructure dependency; its YAML frontmatter
is reconciled in this update to include that missing dependency explicitly.

For strictly sequential execution, `ARCH-002-SHOPIFY-004` is the recommended
next critical-path task because it is the only currently Ready task that
unlocks another unresolved direct `GATEWAY-003` prerequisite
(`ARCH-002-GATEWAY-005`).

No Ready task is started automatically.


### 2026-09-02 — GATEWAY-005 architect accepted

`ARCH-002-GATEWAY-005` is Complete.

The accepted service-local production shared-package boundary is:

```text
moda-interact
  -> exact @modainteract/moda-interact-shared@0.4.0
  -> npm registry

moda-interact-background
  -> exact @modainteract/moda-interact-shared@0.5.0
  -> npm registry
```

The Background version differs from the historical `BACKGROUND-004` acceptance
because later architect-accepted GenAI observability work advanced that consumer
to `0.5.0`. The current effective accepted state has been validated without a
sibling shared checkout.

`ARCH-002-GATEWAY-003` remains Pending.

Its unresolved direct prerequisites are now:

```text
ARCH-002-GATEWAY-007
ARCH-002-MESSAGING-001
ARCH-002-ADMIN-001
```

The longest `SHOPIFY-004 -> GATEWAY-005` prerequisite chain has therefore been
cleared.

The remaining three branches are each one accepted task away from
`GATEWAY-003`:

```text
GATEWAY-007 ---+
MESSAGING-001 -+--> GATEWAY-003
ADMIN-001 -----+
```

No downstream task is started automatically.


### 2026-09-02 — GATEWAY-007 architect accepted

`ARCH-002-GATEWAY-007` is Complete.

The accepted Admin public ingress contract is host-based:

```text
admin.modainteract.com
    -> Render-managed public edge / TLS
    -> moda-interact-gateway
    -> private moda-interact-admin
```

The Admin Next.js application remains rooted at `/`.

The default/non-Admin host rejects:

```text
/admin
/admin/*
```

rather than proxying them to the Admin service.

With both `GATEWAY-005` and `GATEWAY-007` accepted, only two unresolved direct
prerequisites remain before `GATEWAY-003`:

```text
ARCH-002-MESSAGING-001
ARCH-002-ADMIN-001
```

The remaining convergence is therefore:

```text
MESSAGING-001 ---+
                 +--> GATEWAY-003 -> GATEWAY-004
ADMIN-001 -------+
```

No downstream task is started automatically.


### 2026-09-02 — Isolated system-test dependency infrastructure

ARCH-002 adds two test-harness prerequisite tasks:

```text
ARCH-002-SYSTEM-TEST-003
  Add isolated ephemeral Redis test infrastructure

ARCH-002-SYSTEM-TEST-004
  Add WhatsApp Cloud API emulator test infrastructure
```

Both are owned by `moda_system_test` and are Ready independently.

The accepted test dependency model is:

```text
SYSTEM TEST
   |
   +--> ephemeral per-run Redis container
   |
   +--> @whatsapp-cloudapi/emulator test instance
```

This is intentionally different from production:

```text
PRODUCTION
   |
   +--> Redis Cloud
   |
   +--> real Meta / WhatsApp Cloud API
```

`SYSTEM-TEST-001` and `SYSTEM-TEST-002` now depend directly on both new
test-infrastructure tasks in addition to their existing implementation and
gateway prerequisites.

The Redis fixture must be isolated, dynamically addressed, clean per run and
destroyed after execution.

The WhatsApp fixture must support deterministic outbound API calls, signed
inbound webhooks, duplicate delivery and status webhooks without sending to
real WhatsApp users.

The emulator is not accepted as proof of full Meta production compatibility,
Meta latency or production capacity.

If source inspection finds that Moda's outbound WhatsApp client cannot accept
an injected emulator base URL, the system-test task must return Blocked and the
architect will create the missing capability task for the owning repository.

Current test-preparation graph:

```text
SYSTEM-TEST-003 Ready ---+
                         +--> SYSTEM-TEST-001 Pending
SYSTEM-TEST-004 Ready ---+        ^
                                  |
                         GATEWAY-004 + ADMIN-004


SYSTEM-TEST-003 Ready ---+
                         +--> SYSTEM-TEST-002 Pending
SYSTEM-TEST-004 Ready ---+        ^
                                  |
                         GATEWAY-004 + telemetry prerequisites
```

These tasks do not change the remaining `GATEWAY-003` implementation
prerequisites and are not started automatically.


### 2026-09-02 — MESSAGING-001 architect accepted

`ARCH-002-MESSAGING-001` is Complete.

The accepted Messaging deployment-health contract is:

```text
GET /health
  -> dependency-free liveness

GET /ready
  -> bounded Redis PING readiness
```

Repository-level tests use an injected probe for deterministic failure/timeout
coverage. Real Redis connectivity and outage validation are delegated to the
isolated ephemeral Redis system-test infrastructure in
`ARCH-002-SYSTEM-TEST-003`.

The corrected React Router mapping uses distinct route modules for `/health`
and `/ready`.

The critical `GATEWAY-003` convergence is now:

```text
ARCH-002-ADMIN-001
        |
        v
ARCH-002-GATEWAY-003
        |
        v
ARCH-002-GATEWAY-004
```

`ARCH-002-ADMIN-001` is the only unresolved direct prerequisite for
`GATEWAY-003`.

No downstream task is started automatically.


### 2026-09-02 — ADMIN-001 architect accepted

`ARCH-002-ADMIN-001` is Complete.

The accepted Admin operational endpoint contract is:

```text
GET /health
  -> dependency-free process liveness

GET /ready
  -> bounded PostgreSQL `SELECT 1` readiness
```

The architect independently re-ran the focused behavioral health/readiness
suite and observed:

```text
5 passed
0 failed
```

`ADMIN-001` was the final known unresolved direct prerequisite of
`ARCH-002-GATEWAY-003`.

The accepted dependency graph therefore has no known unresolved direct
`GATEWAY-003` prerequisite.

Before changing `GATEWAY-003` from Pending to Ready, `moda_architect` must
inspect the authoritative current task file and re-evaluate only its explicit
`depends_on` list.

No downstream task is started automatically.


### 2026-09-02 — GATEWAY-003 Ready

The authoritative `ARCH-002-GATEWAY-003` direct dependency list was
re-evaluated after architect acceptance of `ADMIN-001`.

Every declared prerequisite is Complete.

The task is promoted:

```text
ARCH-002-GATEWAY-003
  Pending -> Ready
```

This coordination change does not claim the task and does not start
`GATEWAY-004`.


### 2026-09-02 — GATEWAY-003 architect accepted

`ARCH-002-GATEWAY-003` is Complete.

The accepted canonical Render topology is represented by:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

Both environments preserve the same service boundaries while isolating names,
state, credentials and telemetry environment identity.

The corrected public gateway reserves `/health` as gateway-local liveness even
when Render supplies the verified Admin custom domain as the Host header.

Production sizing remains an assumed starting hypothesis pending measured load
evidence.

The next infrastructure gate is now:

```text
ARCH-002-GATEWAY-004
  Ready
```

No downstream task is automatically claimed.


### 2026-09-02 — GATEWAY-004 architect accepted

`ARCH-002-GATEWAY-004` is Complete.

The ARCH-002 gateway/Render infrastructure chain is architect-accepted through
configuration validation.

Local/container evidence validates the accepted topology and gateway behavior;
credential-aware live Render validation, DNS/TLS, real private networking,
external dependency connectivity and measured capacity remain system/deployment
validation concerns.

The system-test preparation graph remains:

```text
SYSTEM-TEST-003 Ready ---+
                         +--> SYSTEM-TEST-001 Pending
SYSTEM-TEST-004 Ready ---+        ^
                                  |
                         ADMIN-004 + accepted infrastructure


SYSTEM-TEST-003 Ready ---+
                         +--> SYSTEM-TEST-002 Pending
SYSTEM-TEST-004 Ready ---+        ^
                                  |
                         accepted infrastructure + telemetry prerequisites
```

No system-test task is automatically started or promoted without re-reading its
authoritative direct dependency list.


### 2026-09-02 — SYSTEM-TEST-003 architect accepted

`ARCH-002-SYSTEM-TEST-003` is Complete.

The accepted system-test Redis boundary is:

```text
system-test run
    -> dedicated ephemeral Redis 7 Alpine container
    -> dynamic mapped host port
    -> bounded PING readiness
    -> generated REDIS_URL
    -> outage/restart/clean-state controls
    -> teardown
```

This is test-only infrastructure and does not replace production Redis Cloud.

The next independently executable system-test infrastructure task remains:

```text
ARCH-002-SYSTEM-TEST-004
  Ready
```

Integrated `SYSTEM-TEST-001` and `SYSTEM-TEST-002` remain Pending until all of
their explicit direct prerequisites are Complete.


### 2026-09-02 — SYSTEM-TEST-004 consumer preflight blocker

`ARCH-002-SYSTEM-TEST-004` correctly stopped during its required outbound
consumer capability preflight.

Current Background outbound behavior contains a hard-coded Meta Graph API base:

```text
https://graph.facebook.com/v25.0
```

so a real Moda outbound request cannot be directed to the architecture-owned
WhatsApp emulator without an owning-repository configuration seam.

The architect creates:

```text
ARCH-002-BACKGROUND-010
  Make outbound WhatsApp API base URL configurable
  status: Ready
```

The production default must remain unchanged.

The dependency is now:

```text
BACKGROUND-010 Ready
        |
        v
SYSTEM-TEST-004 Blocked
        |
        +--------------------+
        |                    |
        v                    v
SYSTEM-TEST-001        SYSTEM-TEST-002
   Pending                 Pending
```

No test-only network interception is approved.

`SYSTEM-TEST-004` may resume only after `BACKGROUND-010` is
architect-accepted Complete and the architect changes it `blocked -> ready`.


### 2026-09-02 — BACKGROUND-010 accepted; SYSTEM-TEST-004 unblocked

`ARCH-002-BACKGROUND-010` is Complete.

The Background outbound WhatsApp client now supports a configurable provider
base URL while preserving the existing production Meta v25.0 default.

The prior system-test blocker is resolved:

```text
BACKGROUND-010 Complete
        |
        v
SYSTEM-TEST-004 Ready
```

`SYSTEM-TEST-004` may now be claimed as a new execution attempt.

Integrated `SYSTEM-TEST-001` and `SYSTEM-TEST-002` remain Pending until all of
their explicit direct prerequisites are Complete.


### 2026-09-02 — SYSTEM-TEST-004 architect accepted

`ARCH-002-SYSTEM-TEST-004` is Complete.

The architecture now has both isolated test-provider dependencies:

```text
SYSTEM-TEST-003 Complete
  -> ephemeral Redis

SYSTEM-TEST-004 Complete
  -> WhatsApp Cloud API emulator
```

The WhatsApp fixture uses synthetic provider identity and can exercise the
real Background outbound client through `WHATSAPP_API_BASE_URL` without
cross-repository interception.

The direct dependency graph now permits:

```text
SYSTEM-TEST-002 Ready
```

because all of its explicit dependencies are Complete.

`SYSTEM-TEST-001` remains Pending only on its remaining explicit prerequisite:

```text
ARCH-002-ADMIN-004
```

No integrated system-test task is automatically claimed.


### 2026-09-03 — ADMIN-004 architect accepted; SYSTEM-TEST-001 ready

`ARCH-002-ADMIN-004` is Complete after architect review of the actual Admin
implementation. The accepted boundary keeps `/observability` behind the
platform-admin guard and navigates explicitly to separately authenticated,
private Grafana Cloud destinations using validated non-secret URLs.

Its final direct dependency edge into integrated topology validation is now
satisfied. Together with the already accepted GATEWAY-004, SYSTEM-TEST-003, and
SYSTEM-TEST-004 tasks:

```text
ARCH-002-SYSTEM-TEST-001
  pending -> ready
```

`ARCH-002-SYSTEM-TEST-002` also remains Ready. Neither system-test task is
automatically claimed. ARCH-002 remains In Progress until the required
integrated validation/capacity gates are reviewed and accepted.


### 2026-09-03 — SYSTEM-TEST-002 attempt 1 blocked; ADMIN-009 validation correction

`ARCH-002-SYSTEM-TEST-002` correctly stopped at the Admin owning-repository
validation boundary after its preceding observability and WhatsApp checks
passed.

The failing ADMIN-009 bootstrap assertion requires a literal `SELECT 1` value in
`db.statement` or `db.query.text`. That is stricter than the architecture-owned
contract. ARCH-002 and accepted SHARED-008 require Prisma instrumentation to
emit Prisma spans when enabled; they do not require third-party Prisma
instrumentation to expose SQL text.

This is classified as validation-contract drift inside the original ADMIN-009
scope, not a new architecture requirement and not yet evidence of an Admin
runtime defect. Under the Changes Requested path:

```text
ARCH-002-ADMIN-009
  complete -> in_progress

ARCH-002-SYSTEM-TEST-002
  ready -> blocked
```

`moda_admin` must correct the focused bootstrap validation so Prisma span
emission proves the instrumentation boundary without requiring SQL-text
attributes. If SQL text is present it remains subject to the existing safety
checks. The correction must not add custom SQL telemetry or a second Prisma
instrumentation mechanism.

`ARCH-002-GATEWAY-006` remains Complete because this correction does not change
Admin runtime/exporter configuration or OTLP/environment wiring.

The valid SYSTEM-TEST-002 attempt-1 runner/evidence is preserved. After
ADMIN-009 is architect-accepted Complete again, SYSTEM-TEST-002 may return to
Ready for attempt 2. SYSTEM-TEST-001 remains independently Ready.


### 2026-09-03 — Add local ephemeral PostgreSQL prerequisite for SYSTEM-TEST-002

The attempt-1 `SYSTEM-TEST-002` blocker also established a local harness gap:
the deterministic system-test runner provisions isolated Redis and a WhatsApp
emulator but did not provision PostgreSQL for the Admin production-bootstrap
boundary. Both deployed ARCH-002 environments include PostgreSQL.

The architecture therefore creates:

```text
ARCH-002-SYSTEM-TEST-005
  Add isolated ephemeral PostgreSQL test infrastructure
  status: Ready
```

`SYSTEM-TEST-005` owns a reusable disposable PostgreSQL 17 lifecycle for local
integration/system tests: unique container, dynamic host port, bounded database
readiness, generated `DATABASE_URL`, clean state and guaranteed teardown. It does
not replace the Render PostgreSQL resource used by deployed `SYSTEM-TEST-001`
validation.

`ARCH-002-SYSTEM-TEST-002` gains `SYSTEM-TEST-005` as a direct dependency. Its
next attempt must run the Admin production bootstrap against the accepted
ephemeral PostgreSQL fixture so the healthy readiness/Prisma instrumentation
path is exercised. It must still avoid requiring literal SQL text from
third-party Prisma/OpenTelemetry instrumentation.

The integrated frontier is now:

```text
ADMIN-009 Complete ----------+
                             +--> SYSTEM-TEST-002 Blocked
SYSTEM-TEST-005 Ready -------+

SYSTEM-TEST-001 Ready
```

ADMIN-009 and SYSTEM-TEST-005 are independently executable by their owning
logical agents. Neither is automatically claimed.

### 2026-09-03 — ADMIN-009 attempt 2 accepted

`ARCH-002-ADMIN-009` is architect-accepted Complete after correcting only the over-specific Prisma SQL-text validation contract. Production runtime configuration is unchanged; the focused test continues to require emitted Prisma spans while treating `db.statement`/`db.query.text` as optional third-party attributes.

The remaining local-harness gate for `ARCH-002-SYSTEM-TEST-002` is now:

```text
ARCH-002-SYSTEM-TEST-005  Ready
        |
        v
ARCH-002-SYSTEM-TEST-002  Blocked
```

After SYSTEM-TEST-005 is architect-accepted Complete, SYSTEM-TEST-002 may be returned to Ready for attempt 2 using its preserved attempt-1 runner/evidence.


### 2026-09-03 — SYSTEM-TEST-005 attempt 2 accepted; SYSTEM-TEST-002 unblocked

`ARCH-002-SYSTEM-TEST-005` is architect-accepted Complete. The reusable local
PostgreSQL 17 fixture preserves dynamic host ports, isolated state/credentials,
bounded readiness and guaranteed teardown, and attempt 2 adds the missing proof
that an external consumer process can connect through the generated host
`DATABASE_URL` and execute bounded `SELECT 1`.

`pg@8.16.3` is test-only infrastructure and does not move application schema or
Prisma ownership into `moda-interact-system-test`.

Together with the accepted `ARCH-002-ADMIN-009` validation correction, every
direct dependency of `ARCH-002-SYSTEM-TEST-002` is now Complete. Therefore:

```text
SYSTEM-TEST-002
  blocked -> ready
  next claim: attempt 2
```

The valid attempt-1 observability/WhatsApp runner and evidence must be reused.
The resumed task adds the accepted PostgreSQL fixture to the Admin bootstrap
path rather than rewriting the scenario. `SYSTEM-TEST-001` remains independently
Ready against the deployed Render test topology.

### 2026-09-03 — System-validation plan decomposed for deterministic execution

The former broad `ARCH-002-SYSTEM-TEST-001` mixed three distinct execution
environments and duplicated evidence already owned by other system-test work:

```text
local deterministic fixtures
deployed Render test topology
production static readiness / production-sized capacity
```

`moda_architect` decomposes the remaining validation into environment-specific
Luna-sized tasks:

```text
SYSTEM-TEST-002  local deterministic observability/integration          Ready
SYSTEM-TEST-006  deployed Render test topology                          Ready
SYSTEM-TEST-007  production Blueprint/readiness                         Ready
SYSTEM-TEST-008  production-sized Shopify ingress capacity gate         Pending
SYSTEM-TEST-001  final accepted-evidence aggregation                    Pending
```

The new dependency graph is:

```text
SYSTEM-TEST-002 Ready -----+
                           |
SYSTEM-TEST-006 Ready -----+--> SYSTEM-TEST-008 Pending --> SYSTEM-TEST-001 Pending
                           |
SYSTEM-TEST-007 Complete --+
```

`SYSTEM-TEST-008` depends on all three preceding validation boundaries so a
production-sized capacity run is interpreted using accepted topology and
observability evidence. Its outcome is exactly `PROVEN` or `UNMET`; an unavailable
or unsuccessful capacity environment is recorded as `UNMET` rather than being
silently treated as success.

`SYSTEM-TEST-001` no longer owns local Redis/WhatsApp/PostgreSQL fixtures or live
capacity generation. It aggregates architect-accepted results and preserves any
`UNMET` production-capacity gate for final architecture review.

This refactor does not change application/gateway runtime architecture and does
not modify the approximately 22,000 Shopify webhook requests/minute reference
target.



### 2026-09-04 — Add bounded Admin Redis queue monitor for Render checkout investigation

The current developer investigation is focused on the deployed Shopify event path:

```text
Shopify checkout webhook
  -> moda-interact
  -> BullMQ / Redis
  -> moda-interact-background
  -> checkout processing
```

To improve immediate operational visibility without changing another runtime
boundary, the architecture creates `ARCH-002-ADMIN-011` as an Admin-only,
read-only queue-monitor task. It consumes the existing shared Shopify queue
contracts and polls server-side Redis through a protected Admin route.

The monitor covers the existing `checkout-events` and `order-events` queues,
current waiting/active/delayed/failed/worker state, and a bounded latest BullMQ
event-stream activity marker. It does not alter queue producers, consumers,
retention, payloads or the database.

Refresh frequency is browser-local UI state (Paused/2/5/10/30/60 seconds), so
no schema/migration is required. `REDIS_URL` remains server-only. Because the
current Blueprint does not inject Redis configuration into Admin, missing
`REDIS_URL` must degrade only the monitor; this task does not modify Gateway
Blueprints.

Successful Shopify jobs currently use `removeOnComplete: true`. The monitor must
therefore not represent completed-job counts as durable processing history.
Recent BullMQ event-stream activity is operational evidence only.


### 2026-09-04 — ADMIN-011 attempt 2 accepted

`ARCH-002-ADMIN-011` is architect-accepted Complete. The Admin-only queue monitor
now satisfies the bounded Render diagnostic requirement, including the corrected
5-second first-use polling default and browser-local refresh persistence.

The implementation remains read-only and consumes the existing Shopify queue
contracts without changing Redis/BullMQ producer, consumer, retention or payload
semantics. Manual Render `REDIS_URL` configuration remains developer-owned
deployment setup rather than an application-code dependency change.
