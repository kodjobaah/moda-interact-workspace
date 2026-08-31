---
id: ARCH-002-MESSAGING-002
architecture_id: ARCH-002
title: Add OpenTelemetry to Meta ingress
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-002-GATEWAY-001
- ARCH-002-SHARED-010
enables: []
created: 2026-08-29
updated: '2026-08-31'
---
# Add OpenTelemetry to Meta Ingress

## Superseded — Granular Replacement (2026-08-31)

This task must not be executed.

The broad messaging observability task is replaced by separate shared-runtime, semantic-ingress, and BullMQ-producer tasks.

Replacement tasks:

- `ARCH-002-MESSAGING-003`
- `ARCH-002-MESSAGING-004`
- `ARCH-002-MESSAGING-005`

This change applies the current architect task-granularity policy. Historical
implementation/completion material below is retained only as evidence and does
not define executable scope.

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

Instrument Meta/WhatsApp HTTP ingress and queue publication with vendor-neutral
OpenTelemetry and correlation propagation.

## Context

Accepted discovery found no OpenTelemetry implementation in the messaging
ingress.

ARCH-002 requires the same logical service identity in isolated test and
production environments.

## Scope

- initialize OpenTelemetry once/early;
- instrument inbound HTTP handling;
- instrument Redis/BullMQ publication where supported;
- emit bounded acceptance/failure/latency telemetry;
- use canonical resource identity;
- preserve test/production telemetry isolation;
- propagate trace/correlation context into queued work where the accepted
  contract permits;
- validate telemetry failure isolation;
- validate sensitive-data/cardinality handling.

## Out of Scope

- OTLP backend provisioning/credentials;
- background consumer instrumentation;
- tenant-facing analytics;
- Grafana-specific application logic;
- changing shared queue/business contracts without an architect decision.

## Requirements

Canonical identity:

```text
service.namespace=moda-interact
service.name=moda-interact-messaging
deployment.environment.name=<environment>
```

For deployed ARCH-002 environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

Do not encode the environment into `service.name`.

Test and production exporter endpoints/credentials must remain independently
configurable.

Local/unit-test hosted export must be disableable.

Telemetry failure must not fail otherwise valid Meta webhook handling or durable
queue publication solely because export failed.

Telemetry buffering/retries must be bounded.

Do not emit:

- Meta access tokens;
- WhatsApp access tokens;
- authorization headers;
- `hub.verify_token`;
- complete inbound payloads;
- customer/message content;
- high-cardinality business identifiers as metric labels.

If async propagation requires a cross-service/shared payload-contract change,
return it to `moda_architect`.

## Work Items

- [ ] initialize OTel once/early;
- [ ] instrument HTTP ingress;
- [ ] instrument queue publication where supported;
- [ ] propagate trace context where architecture-compatible;
- [ ] add canonical resource identity;
- [ ] preserve test/production resource isolation;
- [ ] add exporter-failure isolation tests;
- [ ] add sensitive-data validation;
- [ ] add metric-cardinality validation;
- [ ] document required OTel variables for GATEWAY-006.

## Interfaces / Contracts

Emits OTel/OTLP telemetry consumed by:

```text
ARCH-002-GATEWAY-006
```

The logical service remains:

```text
moda-interact-messaging
```

in both test and production.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] canonical service identity is correct;
- [ ] test and production differ through deployment environment attributes, not
      service name;
- [ ] ingress telemetry is emitted with bounded cardinality;
- [ ] backend outage does not break ingress/business acceptance;
- [ ] context propagation works where architecture-compatible;
- [ ] any required shared-contract change is returned to the architect;
- [ ] secrets/payloads are not leaked;
- [ ] buffering/retry behaviour is bounded;
- [ ] local/test hosted export can be disabled.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build;
- [ ] telemetry failure test;
- [ ] test/production resource identity test;
- [ ] sensitive-data review;
- [ ] metric-cardinality review.

## Implementation Notes

Keep application instrumentation backend-neutral.

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
exporter/bootstrap instructions earlier in this task.** Messaging owns Meta/
WhatsApp ingress semantics; generic runtime plumbing is shared.

Do not resume implementation until `ARCH-002-SHARED-010` is architect-accepted
Complete.

Then:

1. consume the exact published shared version;
2. read `docs/observability/shared-observability-runtime.md`;
3. add a process preload with:

```js
initNodeObservability({
  serviceName: "moda-interact-messaging",
  instrument: { http: true, fetch: true, prisma: false },
});
```

4. preload before the existing React Router production entrypoint;
5. use `@modainteract/moda-interact-shared/observability/bullmq` for inbound
   message Queue publication and pass the shared telemetry object through the
   Queue's supported `telemetry` option;
6. preserve messaging-specific acceptance/failure/latency semantics using the
   global provider installed by shared runtime;
7. do not create local NodeSDK/provider/exporter/sampler or BullMQOtel helpers;
8. validate HTTP -> Queue trace continuity and failure isolation.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact-messaging/`.
