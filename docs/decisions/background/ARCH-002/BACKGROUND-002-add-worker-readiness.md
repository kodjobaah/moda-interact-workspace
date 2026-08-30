---
id: ARCH-002-BACKGROUND-002
architecture_id: ARCH-002
title: Add worker dependency readiness
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-BACKGROUND-001
enables: []
created: 2026-08-29
updated: 2026-08-29
---

# Add Worker Dependency Readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide a bounded operational readiness/preflight mechanism for each
independently deployable BullMQ worker unit.

The mechanism must reflect the dependencies required before the worker begins
normal queue consumption and must be usable by deployment validation and
`moda_system_test`.

## Context

Discovery found a simple HTTP liveness server in the original monolithic worker
process but no dependency-aware readiness.

BACKGROUND-001 changes the runtime into three independently deployable worker
units.

ARCH-002 deploys these as Render **background workers**.

Render background workers do not receive inbound network traffic and therefore
must not be converted into private HTTP services merely to obtain an HTTP health
endpoint.

## Scope

- define reusable bounded dependency probes;
- determine the actual dependencies required by each worker entrypoint;
- verify Redis readiness for worker units that require Redis/BullMQ;
- verify PostgreSQL readiness only for worker units that actually require
  PostgreSQL;
- perform dependency preflight before normal queue consumption begins;
- expose a deterministic non-network validation command suitable for deployment
  diagnostics/system testing;
- make runtime dependency loss observable through existing worker
  failure/error/telemetry mechanisms without leaking credentials;
- add success/failure tests;
- document readiness semantics.

## Out of Scope

- Render Blueprint configuration;
- turning a background worker into a private/web service;
- adding an HTTP server solely for Render readiness;
- changing queue business processing;
- changing retry/business semantics;
- observability backend configuration;
- provider API readiness calls.

## Requirements

Readiness checks must be bounded and non-mutating.

Do not perform Shopify, Meta, WhatsApp or LLM provider calls for readiness.

Do not probe PostgreSQL for a worker merely because another worker in the same
repository uses PostgreSQL. Inspect the actual entrypoint/runtime dependency.

Before a production worker begins consuming normal business jobs:

1. required runtime configuration must be present;
2. required Redis connectivity must be established/probed;
3. required PostgreSQL connectivity must be established/probed where applicable.

An unrecoverable startup-readiness failure must produce a clear non-zero process
failure rather than leaving a process apparently running but unable to consume
work.

Provide a deterministic command/interface that can execute the same bounded
dependency checks without starting normal business consumers. The exact command
name is repository-owned, but it must be documented for GATEWAY-003/004 and
system testing.

The readiness mechanism must work in both test and production using
environment-provided dependency URLs/credentials.

Responses/logs/errors must not expose connection strings, passwords, tokens or
tenant/customer data.

Runtime dependency outages after startup must remain visible through worker
errors/retries/telemetry. Do not invent a business-job success path when a
required dependency is unavailable.

## Work Items

- [ ] inspect each of the three worker entrypoints and record its required
      dependencies;
- [ ] implement reusable bounded Redis/PostgreSQL probes;
- [ ] perform worker-specific dependency preflight before consumption;
- [ ] add a non-network readiness/preflight command;
- [ ] add Redis failure tests;
- [ ] add PostgreSQL failure tests where applicable;
- [ ] verify an unready worker does not begin normal queue consumption;
- [ ] verify failure output contains no secrets;
- [ ] document operational semantics for test/production deployment.

## Interfaces / Contracts

Produces worker dependency-readiness behaviour consumed by:

```text
ARCH-002-GATEWAY-003
ARCH-002-GATEWAY-004
ARCH-002-SYSTEM-TEST-001
```

This task does not create an inbound worker health URL.

Render worker deployment remains:

```text
Redis/BullMQ
    ->
background worker process
```

rather than:

```text
gateway/private HTTP
    ->
background worker
```

## Dependencies

- `ARCH-002-BACKGROUND-001`

## Enables

None.

## Acceptance Criteria

- [ ] required Redis unavailability prevents normal consumption and is reflected
      predictably;
- [ ] required PostgreSQL unavailability prevents normal consumption where
      applicable;
- [ ] each worker probes only dependencies it actually requires;
- [ ] readiness/preflight checks are bounded and non-mutating;
- [ ] a deterministic non-network readiness command exists and is documented;
- [ ] worker background-service deployment does not require inbound HTTP;
- [ ] no secrets are exposed;
- [ ] test and production use the same readiness semantics.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build;
- [ ] worker-specific dependency matrix review;
- [ ] readiness/preflight command verification;
- [ ] prove failed preflight does not start normal consumers;
- [ ] sensitive-output review.

## Implementation Notes

Do not retain an HTTP listener simply because the original combined process had
one.

If an HTTP server is genuinely required by application behaviour independently
of Render worker health, record that capability separately rather than treating
it as the worker readiness contract.

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
