---
id: ARCH-023-BACKGROUND-007
architecture_id: ARCH-023
title: Add Merchant Knowledge runtime lease cadences
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 31
executor: copilot
claimed_at: 2026-10-01T09:02:39Z
attempt: 1
depends_on:
  - ARCH-023-DATABASE-005
enables:
  - ARCH-023-BACKGROUND-004
created: 2026-10-01
updated: 2026-10-01
---

# Add Merchant Knowledge runtime lease cadences

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the existing shared Background runtime lease service so the two database-owned Merchant Knowledge lease identities enforce the exact global cadence windows already required by BACKGROUND-004, without implementing the Merchant Knowledge entrypoint itself.

## Context

`ARCH-023-BACKGROUND-004` Attempt 1 is blocked because its two `startDynamicLeasedScheduler` calls require lease names absent from the pinned database enum and absent from the lease service's PostgreSQL cadence `CASE`.

`ARCH-023-DATABASE-005` owns the enum/migration. After that task is accepted, this task adopts its database revision and adds only the Background runtime cadence semantics needed before BACKGROUND-004 can resume.

The local scheduler intervals and global lease cadences must agree:

```text
MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION = 60 seconds
MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP         = 3600 seconds
```

## Scope

```text
database                                      # gitlink/pin only to accepted DATABASE-005 revision
src/runtime/background-runtime-lease.ts
tests/unit/runtime/background-runtime-lease.test.ts
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
```

Modify another existing runtime-lease-focused test only if required by the repository's actual test decomposition.

## Out of Scope

- `src/entrypoints/merchant-knowledge.ts`.
- Merchant Knowledge processing/acquisition/cleanup business logic.
- Database schema/migration edits inside this repository task.
- New `BackgroundRuntimeConfig` fields.
- Redis/advisory locks or another scheduler implementation.
- BACKGROUND-004 validation/completion.
- BACKGROUND-005 entitlement reconciliation.

## Requirements

### R1 — adopt the accepted database contract

Pin the nested database dependency to the exact architect-accepted `ARCH-023-DATABASE-005` commit before implementation/validation.

Do not edit the nested schema/migration in this task.

### R2 — exact global cadence mapping

Extend only the existing PostgreSQL `CASE` in `BackgroundRuntimeLeaseService.tryAcquire()` with:

```text
MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION -> 60
MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP         -> 3600
```

The values are seconds and must continue to gate reacquisition using persisted `lastFinishedAt` and PostgreSQL time.

Preserve all existing lease-name branches exactly.

### R3 — no new runtime configuration

Do not add cadence fields to `BackgroundRuntimeConfig`, environment variables, config files or Admin controls. These two V1 schedules are fixed by ARCH-023/BACKGROUND-004.

### R4 — unit regression

Extend the lease-service unit coverage to prove the generated acquisition SQL contains both exact enum labels and exact cadence values while preserving the existing checkout-expiry/billing/runtime mappings.

Do not weaken types with `as any` in production code.

### R5 — disposable PostgreSQL lease proof

Extend/reuse the existing task-owned disposable integration path to prove for both new lease names:

1. first owner acquires the lease;
2. release persists `lastFinishedAt`;
3. immediate reacquisition is skipped inside the fixed cadence;
4. after backdating `lastFinishedAt` beyond that lease's cadence, exactly one competing owner reacquires with the next generation;
5. stale heartbeat/release fencing remains intact;
6. test rows and owned infrastructure are removed.

Use the accepted database migrations. Do not use an unverified developer `DATABASE_URL`.

## Work Items

- [ ] Pin accepted DATABASE-005 revision.
- [ ] Add the two exact lease cadence branches.
- [ ] Add focused unit coverage.
- [ ] Add/reuse disposable PostgreSQL cadence proof for both new names.

## Interfaces / Contracts

Consumes:

```text
ARCH-023-DATABASE-005
public.BackgroundRuntimeLeaseName
```

Produces the runtime lease capability required by `ARCH-023-BACKGROUND-004` R14.

## Dependencies

- `ARCH-023-DATABASE-005`

## Enables

- `ARCH-023-BACKGROUND-004`

## Acceptance Criteria

- [ ] Both Merchant Knowledge lease identities compile without casts/workarounds.
- [ ] Global cadence is exactly 60 seconds for PENDING reconciliation.
- [ ] Global cadence is exactly 3600 seconds for upload cleanup.
- [ ] Existing lease mappings and fencing semantics are unchanged.
- [ ] No new runtime-config field or scheduler is introduced.
- [ ] Disposable PostgreSQL cadence proof passes for both names.

## Validation

- [ ] focused runtime-lease unit tests
- [ ] disposable PostgreSQL runtime-lease cadence integration
- [ ] Prisma generate against accepted database pin
- [ ] TypeScript/typecheck or repository equivalent
- [ ] production build
- [ ] changed-file lint/diagnostics
- [ ] `git diff --check`

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not resume BACKGROUND-004.

## Implementation Notes

The local `startDynamicLeasedScheduler` timer remains owned by BACKGROUND-004's entrypoint. This task only gives the distributed lease layer matching global cadence semantics.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
None.

### Deviations
None.

### Assumptions
None.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status
Pending

### Review Notes
Pending.

### Reviewed Files
Pending.

### Validation Reviewed
Pending.

### Architecture Conformance
Pending.

### Follow-up
Pending.
