---
id: ARCH-025-SHOPIFY-001
architecture_id: ARCH-025
title: Extract current billing-period projection invariants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-10-01T19:42:01Z
attempt: 1
depends_on: []
enables:
  - ARCH-025-SHOPIFY-002
created: 2026-10-01
updated: 2026-10-01
---

# Extract current billing-period projection invariants

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the current BillingPeriod cycle/projection logic from `billing.service.ts` into one repository-internal billing-period module while preserving the façade export and every current projection/CAS behaviour.

## Context

`billing.service.ts` currently owns `hasDurableBillingPeriod`, `hasMatchingBillingCycle`, `ensureMappedCurrentBillingPeriodProjection` and `deriveBillingPeriodPhase`. These functions form one coherent responsibility: validate/represent the current durable provider billing cycle and safely create/repair the mapped BillingPeriod projection. ARCH-017 already established the exact conflict-preserving semantics; this task moves that accepted logic without redesign.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/billing-period-projection.ts              # new
tests/unit/services/billing/billing-period-projection.test.ts  # new
```

No other production or test file is authorised.

## Out of Scope

- BillingPlan resolution/materialisation.
- activation, hosted callback, merchant read, purchase or sync workflow extraction beyond replacing existing helper calls with imports.
- schema/migration changes.
- edits to the frozen `billing.service.test.ts`.

## Requirements

### Common ARCH-025 invariants

- Preserve `BillingService` constructor compatibility: `new BillingService(provider, database, dispatchTranslation)`.
- Preserve every existing public `BillingService` method signature and the `billingService` singleton export.
- Preserve all current public exports from `app/services/billing/billing.service.ts`; moved symbols must be compatibility re-exported from that file.
- Do not change routes/callers as part of extraction.
- Extracted modules MUST NOT import `billing.service.ts`; dependency direction is façade/coordinator -> collaborator.
- Do not change billing rules, error codes/strings, transaction boundaries, lock order, provider call order, retry semantics, idempotency, CAS/fencing, entitlement arithmetic or durable lifecycle state.
- Do not add provider/API calls or database round trips to the equivalent path solely because code moved.
- Extracted collaborator constructors must be side-effect-free: store/wire dependencies only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during `new BillingService(...)`; the frozen suite constructs the façade with many partial test doubles.
- This is move-only refactoring: do not remove, coalesce, reorder or otherwise optimise away an existing provider/database read, write, lock or transaction as an incidental cleanup. Any intentional I/O change is outside this task.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4` and all 127 tests must pass.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — exact symbol ownership

Move the current logic equivalent to:

```text
DurableBillingCycle
CurrentBillingPeriodPlan
CurrentBillingPeriodProjectionConflictReason
CurrentBillingPeriodProjectionResult
hasDurableBillingPeriod
hasMatchingBillingCycle
ensureMappedCurrentBillingPeriodProjection
deriveBillingPeriodPhase
isSafeNonNegativeInteger   # repository-internal helper required by projection and SHOPIFY-005
```

into `billing-period-projection.ts`.

### R2 — preserve projection algorithm exactly

The extracted `ensureMappedCurrentBillingPeriodProjection(transaction, input)` must retain the current signature/return semantics and remain transaction-caller-owned. It MUST NOT open its own transaction.

Preserve exactly:

```text
invalid PAID allowance -> CONFLICT / INVALID_INCLUDED_ALLOWANCE
missing exact period -> create complete OPEN mapped period
PAID create -> create INCLUDED_RECOVERY_CREDITS counter
closed/mismatched existing durable facts -> CONFLICT, no overwrite
compatible null mapping -> repair exact existing row in place
compatible existing-period path retains the current BillingPeriod update call; do not optimise it away (the row has `updatedAt @updatedAt`)
FREE + included counter -> conflict
PAID counter arithmetic/grant mismatch -> conflict
missing PAID included counter -> create once
READY returns exact billingPeriodId + repaired flag
```

### R3 — preserve public and repository-internal exports

`deriveBillingPeriodPhase` must remain importable from `app/services/billing/billing.service.ts` through a compatibility re-export. Existing callers/tests must not migrate.

The new projection module must also export `hasDurableBillingPeriod`, `hasMatchingBillingCycle` and `isSafeNonNegativeInteger` as repository-internal helpers for later ARCH-025 tasks. They are **not** new public route contracts and need not be re-exported from the façade unless already public.

### R4 — no I/O expansion

The extracted helper performs exactly the existing Prisma operations for the same branches. No provider call, logger or additional durable read/write is introduced.

## Work Items

- [ ] Create `billing-period-projection.ts` and move the bounded projection/cycle logic, including `isSafeNonNegativeInteger`.
- [ ] Replace in-file implementations with imports/re-export wiring from `billing.service.ts`.
- [ ] Add focused unit tests for READY create, compatible repair, FREE/PAID counter rules, conflict/no-overwrite and phase/cycle helpers.
- [ ] Prove the frozen façade suite is byte-identical and green.

## Interfaces / Contracts

Internal module contract only. `DurableBillingCycle` moves with the cycle helpers. `ensureMappedCurrentBillingPeriodProjection` continues accepting an existing `Prisma.TransactionClient`; transaction ownership stays with the caller. `hasDurableBillingPeriod`, `hasMatchingBillingCycle` and `isSafeNonNegativeInteger` are stable repository-internal exports for later ARCH-025 collaborators.

Public compatibility contract: `deriveBillingPeriodPhase` continues to be exported by `billing.service.ts`.

## Dependencies

None

## Enables

- `ARCH-025-SHOPIFY-002`

## Acceptance Criteria

- [ ] BillingPeriod projection/cycle logic has one owner in `billing-period-projection.ts`.
- [ ] No equivalent implementation remains duplicated in `billing.service.ts`.
- [ ] Existing conflict reasons, reads/writes (including the compatible-row update), counter semantics and returned results are unchanged.
- [ ] `deriveBillingPeriodPhase` remains publicly available from `billing.service.ts`.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/billing-period-projection.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/billing-period-projection.ts tests/unit/services/billing/billing-period-projection.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Prefer direct function exports from the internal module rather than a class; this capability has no owned mutable state. Do not create a generic billing utility module. The extracted names may remain unchanged where practical so the diff is mechanically reviewable.


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

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
