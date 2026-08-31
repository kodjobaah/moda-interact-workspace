---
id: ARCH-002-BACKGROUND-002
architecture_id: ARCH-002
title: Add worker dependency readiness
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 25
executor: codex
claimed_at: 2026-08-31 16:55:46+00:00
attempt: 1
depends_on:
- ARCH-002-BACKGROUND-001
enables:
- ARCH-002-BACKGROUND-005
created: 2026-08-29
updated: '2026-08-31'
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

- [x] inspect each of the three worker entrypoints and record its required
      dependencies;
- [x] implement reusable bounded Redis/PostgreSQL probes;
- [x] perform worker-specific dependency preflight before consumption;
- [x] add a non-network readiness/preflight command;
- [x] add Redis failure tests;
- [x] add PostgreSQL failure tests where applicable;
- [x] verify an unready worker does not begin normal queue consumption;
- [x] verify failure output contains no secrets;
- [x] document operational semantics for test/production deployment.

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

- [x] required Redis unavailability prevents normal consumption and is reflected
      predictably;
- [x] required PostgreSQL unavailability prevents normal consumption where
      applicable;
- [x] each worker probes only dependencies it actually requires;
- [x] readiness/preflight checks are bounded and non-mutating;
- [x] a deterministic non-network readiness command exists and is documented;
- [x] worker background-service deployment does not require inbound HTTP;
- [x] no secrets are exposed;
- [x] test and production use the same readiness semantics.

## Validation

- [x] tests;
- [x] typecheck;
- [x] production build;
- [x] worker-specific dependency matrix review;
- [x] readiness/preflight command verification;
- [x] prove failed preflight does not start normal consumers;
- [x] sensitive-output review.

## Implementation Notes

Do not retain an HTTP listener simply because the original combined process had
one.

If an HTTP server is genuinely required by application behaviour independently
of Render worker health, record that capability separately rather than treating
it as the worker readiness contract.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/README.md`
- `moda-interact-background/src/entrypoints/messaging.ts`
- `moda-interact-background/src/entrypoints/recovery.ts`
- `moda-interact-background/src/entrypoints/shopify-event.ts`
- `moda-interact-background/src/readiness.ts`
- `moda-interact-background/src/runtime/readiness.ts`
- `moda-interact-background/tests/unit/runtime/entrypoint-isolation.test.ts`
- `moda-interact-background/tests/unit/runtime/readiness.test.ts`
- `docs/decisions/background/ARCH-002/BACKGROUND-002-add-worker-readiness.md`

### Work Completed

- Recorded an explicit dependency matrix: all three current worker units require
  Redis/BullMQ and PostgreSQL through their actual worker/service graphs.
- Added reusable five-second Redis `PING` and PostgreSQL `SELECT 1` probes using
  transient clients and environment-provided configuration.
- Gated production worker dynamic imports behind readiness, so failed preflight
  cannot construct a BullMQ consumer.
- Added deterministic non-network readiness commands for each logical worker;
  these run the same probes as startup without importing worker modules.
- Sanitized readiness failures to logical service/dependency names and contained
  raw Redis error events.
- Documented command, dependency, timeout, exit-code and deployment semantics.

### Validation Results

- `npm test -- --run tests/unit/runtime/readiness.test.ts tests/unit/runtime/entrypoint-isolation.test.ts tests/unit/runtime/worker-process.test.ts`:
  passed, 3 files and 14 tests.
- `npm test`: 12 files passed, 1 file failed, 1 skipped; 65 tests passed, 1
  failed, 2 skipped. The sole failure is the existing
  `recovery-routing.service.test.ts` Prisma mock omitting
  `customerPhone.findMany`; no readiness or lifecycle test failed.
- `./node_modules/.bin/tsc --noEmit`: passed.
- `npm run build`: passed, including Prisma Client generation and production
  TypeScript compilation.
- All three compiled readiness commands exited `1` with sanitized
  `redis unavailable` output when Redis configuration was absent; an injected
  database credential marker was not emitted.
- All three compiled production start commands exited `1` on the same failed
  preflight without emitting any consumer `started` log or credential marker.
- `node dist/readiness.js invalid-worker` exited `2` with deterministic usage.
- Source review found no readiness HTTP listener, provider call, static worker
  import or connection-string logging. VS Code diagnostics were clean.
- A live Redis/PostgreSQL command-level probe was not run because Docker was not
  available in the validation shell. Concrete configuration failures and
  injected Redis/PostgreSQL success/failure behavior are covered by unit tests.

### Deviations

None.

### Assumptions

- `PING` and `SELECT 1` are the canonical non-mutating availability checks for
  the repository's Redis and PostgreSQL clients.
- The current checkout, order, pending-recovery and WhatsApp processing graphs
  all require PostgreSQL; therefore each of the three deployment units probes
  both dependencies.

### Unresolved Issues

- The existing `recovery-routing.service.test.ts` mock lacks
  `prisma.customerPhone.findMany`, leaving the unrelated full suite one test
  short of green.

### Architectural Concerns

None. No HTTP worker endpoint, provider probe, queue contract, business retry or
consumer boundary was introduced or changed.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation satisfies the worker dependency-readiness boundary:

- all three production worker entrypoints execute readiness before dynamically
  importing their BullMQ Worker modules;
- the current dependency matrix is explicit and limited to Redis and PostgreSQL
  for each of the three accepted production worker units;
- Redis readiness uses bounded `PING` and PostgreSQL readiness uses bounded
  `SELECT 1`, both through environment-provided configuration;
- failed readiness prevents normal consumer construction and returns a
  predictable non-zero process outcome;
- readiness failures expose only logical service/dependency names rather than
  raw connection strings or underlying credential-bearing errors;
- deterministic readiness commands exist for all three logical worker services
  and execute the same dependency probes without starting normal consumers;
- invalid logical service names produce a deterministic usage/error outcome;
- no inbound HTTP readiness endpoint, external provider probe, queue semantic
  change, retry change or observability-runtime implementation was introduced.

### Reviewed Files

Reviewed:

- `src/runtime/readiness.ts`;
- `src/readiness.ts`;
- all three production worker entrypoints;
- package scripts;
- readiness and entrypoint-isolation tests;
- README operational documentation;
- Completion Report.

### Validation Reviewed

Accepted evidence:

- focused readiness/lifecycle suite: 14 tests passed;
- TypeScript typecheck passed;
- production build passed;
- all three compiled readiness commands fail deterministically and sanitise
  output when dependency configuration is absent;
- all three production start commands fail readiness before consumers start;
- invalid worker name exits with deterministic usage status;
- sensitive-output/static-import/HTTP-listener review passed.

The full repository suite still contains the same unrelated
`recovery-routing.service.test.ts` Prisma mock failure already observed during
BACKGROUND-001 (`customerPhone.findMany` missing). No readiness/lifecycle test
failed, and task-specific validation, typecheck and build are green.

A live Docker-backed Redis/PostgreSQL probe was unavailable in the execution
environment. The implementation's concrete success/failure paths are covered by
focused tests, and this limitation does not block acceptance.

### Architecture Conformance

Conforms.

The task adds dependency readiness only. It does not introduce BACKGROUND-005
shared observability runtime work or change worker/business processing
semantics.

### Follow-up

`ARCH-002-BACKGROUND-002` is Complete.

`ARCH-002-BACKGROUND-004` remains Ready and independent.

`ARCH-002-BACKGROUND-005` remains Pending until BACKGROUND-004 is also
architect-reviewed Complete. Once that occurs, BACKGROUND-005 may become Ready.