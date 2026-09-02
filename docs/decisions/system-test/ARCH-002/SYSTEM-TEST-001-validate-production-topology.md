---
id: ARCH-002-SYSTEM-TEST-001
architecture_id: ARCH-002
title: Validate integrated test and production-ready topology
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-004
  - ARCH-002-ADMIN-004
enables: []
created: 2026-08-29
updated: 2026-08-31
---

# Validate Integrated Test and Production-Ready Topology

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Validate the integrated ARCH-002 architecture after required implementation,
infrastructure and observability work is architect-accepted.

The primary functional system-test environment is the isolated Render **test**
environment.

The task also validates production-readiness invariants and requires measured
capacity evidence before ARCH-002 may claim that the production topology
supports the approximately 22,000-Shopify-webhooks-per-minute target.

This task proves the architecture. It does not own fixes in application,
gateway, database or worker repositories.

## Context

ARCH-002 uses two canonical Blueprints:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

The test environment intentionally uses the cheapest practical compute.

It is therefore **not** evidence that the production hardware configuration can
sustain the production capacity target.

Functional correctness and production capacity are separate assertions.

## Scope

### Phase A — test environment functional validation

Against the deployed test environment validate, where applicable:

- public gateway reachability;
- Shopify routing;
- Meta/WhatsApp routing;
- private-service isolation;
- Admin host-based routing through `admin.modainteract.com` in production
  configuration;
- platform-admin authentication/authorisation;
- secure internal Grafana observability presentation;
- provider webhook verification compatibility;
- app/messaging health and readiness;
- Redis/BullMQ connectivity;
- the three worker service boundaries;
- background readiness/preflight behaviour;
- PostgreSQL state transitions;
- retry/duplicate behaviour relevant to exercised flows;
- correlation/request identifiers;
- asynchronous trace context where implemented;
- recovery flow;
- messaging/CommerceAgent flow;
- dependency failure behaviour;
- telemetry arrival/resource identity;
- telemetry failure isolation;
- secret/sensitive-data absence from logs/telemetry.

### Phase B — production configuration/readiness validation

Validate that the production Blueprint/configuration:

- is isolated from test resources/secrets;
- preserves public/private boundaries;
- uses independently scalable worker services;
- uses production telemetry environment identity;
- does not present assumed hardware as measured capacity;
- has a documented deployment/rollback path.

### Phase C — production capacity evidence

Before ARCH-002 is described as production-capacity validated, execute or review
a controlled load test against a production-sized pre-cutover environment or
the production environment before live traffic.

The target is approximately:

```text
22,000 Shopify webhook requests/minute
≈ 367 requests/second
```

The load scenario must distinguish raw webhook ingress from recoveries, WhatsApp
messages and CommerceAgent/LLM work.

Do **not** infer production capacity from the cheap test environment.

If a production-sized capacity environment is not available, record the
capacity gate as unmet rather than marking the 22,000/minute requirement proven.

## Out of Scope

- modifying another repository to make a test pass;
- weakening service exposure for test convenience;
- destructive production-data tests;
- using production customer data as test fixtures;
- silently changing capacity requirements;
- implementing an autoscaling controller.

## Required Topology Assertions

Test/production logical HTTP boundary:

```text
Internet
   |
Render public load balancer
   |
moda-interact-gateway
   |
Render private network
   +--> moda-interact
   +--> moda-interact-messaging
   +--> moda-interact-admin
```

Production Admin browser routing:

```text
admin.modainteract.com
   -> moda-interact-gateway
   -> moda-interact-admin private service
```

The Admin application remains rooted at `/`; production validation must not rely
on a Next.js `/admin` base path.

Background work:

```text
moda-interact / moda-interact-messaging
   |
Redis Cloud / BullMQ
   |
   +--> moda-shopify-event-worker
   +--> moda-recovery-worker
   +--> moda-messaging-worker
```

Background workers must not be treated as HTTP upstreams.

## Webhook Integrity Assertions

Where test facilities support it:

- confirm Shopify webhook HMAC verification succeeds through the gateway;
- confirm Meta/WhatsApp verification succeeds through the gateway;
- confirm required signature headers survive proxying;
- confirm raw/body handling remains verification-compatible;
- confirm sensitive query values such as Shopify OAuth codes and Meta
  verification tokens do not appear in gateway logs.

## Health / Readiness Assertions

Verify:

```text
moda-interact
  GET /health
  GET /ready

moda-interact-messaging
  GET /health
  GET /ready
```

and worker non-network preflight/readiness commands defined by BACKGROUND-002.

Verify required dependency outages produce the expected not-ready/failure
behaviour without exposing credentials.

## Observability Assertions

Verify canonical service identity for at least:

```text
moda-interact-gateway
moda-interact
moda-interact-messaging
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
moda-interact-admin
```

where instrumentation is required by accepted tasks.

Verify:

```text
service.namespace=moda-interact
deployment.environment.name=test
```

for test and:

```text
deployment.environment.name=production
```

for production evidence.

Test and production telemetry must remain distinguishable.

Verify telemetry backend outage does not cause:

- Shopify webhook rejection solely due to telemetry;
- durable event acceptance failure solely due to telemetry;
- BullMQ job failure solely due to telemetry;
- recovery/WhatsApp/CommerceAgent failure solely due to telemetry;
- database transaction failure solely due to telemetry.

Verify credentials, authorization headers, OAuth codes, Meta verification tokens
and complete sensitive webhook/job payloads are absent from emitted operational
telemetry/log evidence.


## Admin Security / Observability Assertions

Verify:

- anonymous requests cannot use privileged Admin functionality;
- an authorised platform administrator can access intended Admin functionality;
- authenticated non-admin identities cannot perform privileged Admin actions;
- privileged server actions/route handlers enforce authorisation server-side;
- `admin.modainteract.com` reaches the private Admin service only through the
  gateway;
- non-Admin hosts cannot reach the Admin upstream through `/admin/*`;
- the Admin `/observability` presentation is restricted to platform
  administrators;
- Grafana operational data is not made anonymous/public to satisfy iframe
  embedding;
- no Grafana or admin authentication credential is browser/log exposed;
- test and production observability views remain distinguishable;
- Grafana unavailability does not break unrelated Admin functionality.

## Failure-Path Assertions

Where practical validate:

- unavailable private HTTP upstream;
- Redis unavailable;
- PostgreSQL unavailable where required;
- worker startup/readiness failure;
- transient worker/job failure;
- retryable work;
- duplicate event delivery;
- invalid provider signature;
- telemetry backend outage;
- invalid/missing deployment configuration.

Do not introduce destructive production-data operations merely for validation.

## Ownership Boundary

`moda_system_test` may:

- execute/deploy architecture-approved test facilities;
- call public interfaces;
- invoke documented worker readiness commands;
- observe queues/services;
- inspect resulting state;
- query/inspect architecture-approved telemetry;
- run architecture test/load scenarios;
- record failures/evidence.

`moda_system_test` must not modify another repository's implementation just to
make the test pass.

If a defect is found:

1. record the failing scenario and evidence;
2. identify the apparent owning component;
3. return the defect to `moda_architect`;
4. allow `moda_architect` to reopen/create the owning task;
5. rerun the affected validation only after the fix is architect-accepted.

## Dependencies

- `ARCH-002-GATEWAY-004`
- `ARCH-002-ADMIN-004`

GATEWAY-004 is the final infrastructure-validation dependency and is expected to
be Complete only after GATEWAY-003 and its implementation/observability
prerequisites are Complete.

ADMIN-004 is the final Admin operational-presentation dependency and must be
architect-accepted before integrated ARCH-002 validation begins.

If GATEWAY-004 is Complete but a required implementation/observability
prerequisite is discovered not to be architect-accepted, this task must return
the coordination inconsistency to `moda_architect`.

## Enables

None.

## Acceptance Criteria

- [ ] deployed test gateway is reachable;
- [ ] Shopify traffic reaches the intended private service;
- [ ] Meta/WhatsApp traffic reaches the intended private service;
- [ ] private application services are not directly public where architecture
      requires them private;
- [ ] production `admin.modainteract.com` routes through the gateway to the
      private Admin service without a Next.js `/admin` base path;
- [ ] anonymous and authenticated non-admin users cannot perform privileged Admin
      operations;
- [ ] authorised platform administrators can access intended Admin functionality;
- [ ] the Admin `/observability` page presents the approved private/authenticated
      Grafana view without anonymous/public dashboard exposure;
- [ ] Grafana unavailability does not break unrelated Admin functionality;
- [ ] provider verification remains compatible with gateway proxying;
- [ ] app/messaging health/readiness behave correctly;
- [ ] worker readiness/preflight behaves correctly;
- [ ] Redis/BullMQ connectivity works for required producers/consumers;
- [ ] the three worker service boundaries process only their owned work;
- [ ] PostgreSQL state transitions required by exercised flows are observable;
- [ ] retry/duplicate behaviour is validated where applicable;
- [ ] request/correlation context is preserved where required;
- [ ] async trace context is preserved where required;
- [ ] recovery flow is validated where applicable;
- [ ] messaging/CommerceAgent flow is validated where applicable;
- [ ] relevant dependency failure behaviour is validated;
- [ ] test and production resource/secrets are isolated;
- [ ] OTel service/environment identity is correct;
- [ ] telemetry backend failure does not become a business correctness
      dependency;
- [ ] prohibited secrets/sensitive payloads are absent from tested logs/telemetry;
- [ ] production Blueprint does not represent assumed capacity as measured;
- [ ] measured evidence exists before claiming approximately 22,000
      webhooks/minute production capacity;
- [ ] defects are returned to the architect rather than silently repaired;
- [ ] test/capacity evidence is recorded;
- [ ] task is ready for architect acceptance.

## Validation

- [ ] test-environment functional suite;
- [ ] provider webhook integrity suite;
- [ ] health/readiness suite;
- [ ] worker boundary/readiness suite;
- [ ] failure-path suite;
- [ ] observability identity/isolation suite;
- [ ] sensitive-data review;
- [ ] test/production isolation review;
- [ ] production Blueprint review;
- [ ] controlled production-sized capacity/load test or explicit unmet-capacity
      gate;
- [ ] rollback/deployment evidence review.

## Architecture Completion Gate

Completion of this task is required before `ARCH-002` may be marked Implemented,
unless `moda_architect` explicitly records a particular validation area as not
applicable.

`ARCH-002` must not claim that production sustains the approximately
22,000-webhooks-per-minute target until measured capacity evidence has been
accepted.

## Completion Report

### Status

Not Started

### Environment / Topology Tested

None.

### Scenarios Executed

None.

### Results

Not run.

### Capacity Evidence

Not run.

### Defects Identified

None.

### Follow-up Tasks Requested

None.

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

### Reviewed Evidence

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
