---
id: ARCH-002-SYSTEM-TEST-002
architecture_id: ARCH-002
title: Validate shared observability and WhatsApp worker performance
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-002-SHOPIFY-007
- ARCH-002-BACKGROUND-007
- ARCH-002-BACKGROUND-009
- ARCH-002-MESSAGING-004
- ARCH-002-MESSAGING-005
- ARCH-002-ADMIN-009
- ARCH-002-GATEWAY-006
enables: []
created: 2026-08-31
updated: 2026-08-31
---

# Validate shared observability and WhatsApp worker performance

## Objective

Validate the shared observability runtime across the integrated test topology and
establish a measurable WhatsApp/CommerceAgent performance baseline before any
worker split decision.

## Infrastructure gate

This task requires an architect-accepted integrated test topology.

`ARCH-002-GATEWAY-004` is therefore a direct dependency in addition to the
signal-specific observability prerequisites. This keeps the task aligned with
the ARCH-002 rollout order:

```text
implementation prerequisites
    -> test Blueprint deployment
    -> infrastructure validation
    -> integration/system validation
```

Do not mark this task Ready solely because the telemetry-emitter and
GATEWAY-006 dependencies are Complete.

## Scope

- verify HTTP -> BullMQ -> worker trace continuity;
- verify Shopify/Admin/Messaging standard HTTP and Prisma telemetry where applicable;
- verify Background BullMQ, HTTP/tool and GenAI spans;
- verify one trace per WhatsApp conversation turn, not per whole conversation;
- measure queue wait, worker processing, agent invocation, tool and provider HTTP durations;
- verify production sampling configuration does not affect metrics collection;
- verify telemetry backend outage does not affect request/job correctness.

## Out of Scope

- deciding final production capacity before measured load tests;
- splitting the WhatsApp/CommerceAgent worker without evidence;
- exposing high-cardinality identifiers as metric labels.

## Acceptance Criteria

- [ ] cross-service trace continuity proven in test;
- [ ] turn-level WhatsApp trace model proven;
- [ ] latency breakdown is visible for queue/worker/agent/tools/provider HTTP;
- [ ] metrics remain available when trace sampling is reduced;
- [ ] backend failure isolation proven;
- [ ] evidence is sufficient for architect to decide whether CommerceAgent needs an independent worker pool.

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
