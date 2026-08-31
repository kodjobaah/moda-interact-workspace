---
id: ARCH-002-BACKGROUND-003
architecture_id: ARCH-002
title: Add OpenTelemetry to background workers
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-002-BACKGROUND-001
- ARCH-002-SHARED-010
enables: []
created: 2026-08-29
updated: '2026-08-31'
---
# Add OpenTelemetry to Background Workers

## Superseded — Granular Replacement (2026-08-31)

This task must not be executed.

`ARCH-002-BACKGROUND-001` has now established the actual production topology.
The broad observability scope is replaced by independently reviewable
capabilities:

- `ARCH-002-BACKGROUND-005` — adopt the shared observability runtime in the
  three production worker processes;
- `ARCH-002-BACKGROUND-006` — wire shared BullMQ telemetry on background
  Worker/Queue boundaries;
- `ARCH-002-BACKGROUND-007` — add bounded worker operational metrics;
- `ARCH-002-BACKGROUND-008` — integrate GenAI active spans in the messaging
  CommerceAgent path;
- `ARCH-002-BACKGROUND-009` — integrate bounded GenAI operational metrics.

Historical content below remains architecture evidence only and does not define
executable scope.

## Granularity Gate — Do Not Hand Off Yet (2026-08-31)

This broad task remains `pending` behind `ARCH-002-BACKGROUND-001`.

When BACKGROUND-001 is architect-accepted Complete, do **not** automatically mark
this task Ready. Return it to `moda_architect` so the observability work can be
decomposed against the actual worker entrypoints and commands established by
BACKGROUND-001.

The decomposition must separate independently reviewable worker/runtime,
BullMQ, and CommerceAgent/GenAI integration capabilities rather than asking one
agent to implement the whole background observability surface in one pass.

## Current Architect Instruction — Shared Runtime

This task's executable architecture is the shared-runtime amendment in this
file plus `docs/observability/shared-observability-runtime.md`. Any earlier
service-local NodeSDK/provider/exporter/bootstrap instructions or completion
notes are historical implementation evidence and are superseded where they
conflict with the shared-runtime amendment. Service/domain semantic telemetry
remains owned by this repository.

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Instrument each ARCH-002 background worker unit with vendor-neutral
OpenTelemetry, bounded BullMQ operational telemetry and architecture-compatible
asynchronous trace-context propagation.

## Context

Accepted discovery found no OpenTelemetry implementation.

BACKGROUND-001 establishes the canonical worker deployment/service identities:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

ARCH-002 deploys the same logical services in isolated `test` and `production`
environments.

## Scope

- initialize OTel once per worker process and before instrumented libraries where
  required;
- instrument BullMQ consumer/producer boundaries as supported;
- propagate trace context across queued work without changing business semantics;
- emit bounded job duration/failure/retry/throughput telemetry;
- emit bounded queue-lag/processing-age signals where practical and useful for
  capacity reasoning;
- use worker-specific canonical resource identity;
- preserve test/production environment isolation;
- validate telemetry failure isolation;
- validate sensitive-data and metric-cardinality safety.

## Out of Scope

- OTLP backend provisioning/credentials;
- changing queue business payload semantics without architect-approved contract
  work;
- creating a separate CommerceAgent worker;
- introducing a queue-aware autoscaling controller;
- Grafana-specific business logic;
- storing complete job/customer payloads in telemetry.

## Requirements

Canonical resource identities:

```text
service.namespace=moda-interact
service.name=moda-shopify-event-worker
deployment.environment.name=<environment>
```

```text
service.namespace=moda-interact
service.name=moda-recovery-worker
deployment.environment.name=<environment>
```

```text
service.namespace=moda-interact
service.name=moda-messaging-worker
deployment.environment.name=<environment>
```

For canonical deployed environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

Do not change `service.name` between test and production.

Support standard OTel environment configuration consumed by GATEWAY-006.

Test and production exporter endpoints/credentials must remain independently
configurable.

Local/test export must be disableable/configurable so ordinary unit tests do not
require a hosted telemetry backend.

Telemetry backend failure must never fail a BullMQ business job solely because
telemetry export failed.

Telemetry buffering/retries must remain bounded.

Do not use job ID, checkout token, phone number, customer ID, message ID or
similar high-cardinality identifiers as metric label dimensions.

Trace/span attributes may include safe deterministic correlation identifiers
only where justified and data-safe; do not emit credentials, authorization
headers or complete sensitive job payloads.

If correct async propagation requires a cross-repository/shared payload-contract
change, stop and return the required contract change to `moda_architect` rather
than silently changing a shared business payload.

## Work Items

- [ ] initialize OTel once/early in each worker entrypoint;
- [ ] configure canonical resource attributes;
- [ ] instrument BullMQ execution;
- [ ] implement architecture-compatible async trace propagation;
- [ ] add bounded duration/failure/retry/throughput metrics;
- [ ] add bounded queue lag/processing-age metrics where practical;
- [ ] preserve test/production environment isolation;
- [ ] add telemetry-backend outage tests;
- [ ] add cardinality validation;
- [ ] validate sensitive-data handling;
- [ ] document required OTel environment variables for GATEWAY-006.

## Interfaces / Contracts

Emits OTel/OTLP-compatible telemetry consumed by:

```text
ARCH-002-GATEWAY-006
```

GATEWAY-006 owns exporter endpoint/backend/credential infrastructure wiring.

This task owns worker instrumentation only.

## Dependencies

- `ARCH-002-BACKGROUND-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] all three worker `service.name` values are correct;
- [ ] test and production differ via `deployment.environment.name`, not
      `service.name`;
- [ ] queue/job telemetry is emitted with bounded cardinality;
- [ ] job duration/failure/retry/throughput is observable;
- [ ] queue lag/processing age is observable where implemented;
- [ ] trace context propagates where architecture-compatible;
- [ ] any required shared-contract change is returned to the architect rather
      than silently introduced;
- [ ] telemetry outage does not create business-job failures;
- [ ] exporter buffering/retries are bounded;
- [ ] secrets/customer payloads are not leaked;
- [ ] local/test hosted export can be disabled.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build;
- [ ] telemetry failure test;
- [ ] test/production resource-identity test;
- [ ] metric-cardinality review;
- [ ] sensitive-data review.

## Implementation Notes

Prefer low-cardinality queue/job labels.

Use trace IDs/request correlation for diagnosis rather than introducing
high-cardinality business identifiers into metrics.

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

## Architect Amendment — Shared Observability Runtime (2026-08-31)

**This amendment supersedes any conflicting service-local NodeSDK/provider/
exporter/bootstrap instructions earlier in this task.** Background still owns
worker/recovery/messaging/CommerceAgent semantic telemetry; generic runtime
plumbing is shared.

Do not resume implementation until:

```text
BACKGROUND-001 is Complete (actual worker entrypoints known)
ARCH-002-SHARED-010 is architect-accepted Complete
```

Then:

1. consume the exact published shared version from SHARED-010;
2. read `docs/observability/shared-observability-runtime.md`;
3. create one small preload/profile per actual production worker process:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

4. prefix each **real command produced by BACKGROUND-001** with its matching
   preload; do not invent a new worker entrypoint in this task;
5. final generic instrumentation is:

```text
BullMQ producer/consumer=true
Prisma=true where used
HTTP/fetch/Undici=true where external calls occur
```

6. construct BullMQ telemetry only through
   `@modainteract/moda-interact-shared/observability/bullmq` and pass it through
   Queue/Worker `telemetry` options;
7. use `.../observability/genai` for messaging/CommerceAgent agent/tool/turn
   helpers;
8. one inbound WhatsApp turn is one trace; never one trace for a whole customer
   conversation;
9. service-owned metrics must use bounded dimensions; arbitrary tool/agent/job/
   conversation/customer identifiers are prohibited metric attributes;
10. remove obsolete local provider/exporter/bootstrap logic only after parity is
    proven.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact-background/`.
