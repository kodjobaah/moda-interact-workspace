---
id: ARCH-025-SHOPIFY-006
architecture_id: ARCH-025
title: Extract initial subscription activation workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-005
enables:
  - ARCH-025-SHOPIFY-007
created: 2026-10-01
updated: 2026-10-01
---

# Extract initial subscription activation workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the existing initial Free/Paid activation intent and guarded Free completion/retry scheduling workflow into `SubscriptionActivationService`, while leaving initial Paid durable finalisation inside `syncSubscription()` until SHOPIFY-010.

## Context

The façade currently owns four activation-oriented public methods plus token matching and lock helpers. They share the same pending-selection lifecycle. Pulling them behind one service reduces the façade while keeping the higher-risk initial Paid final commit separate for a later bounded task.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-activation.service.ts              # new
app/services/billing/subscription-locks.ts                           # new shared internal lock owner
app/services/billing/billing-retry-policy.ts                         # new shared internal retry constant owner
tests/unit/services/billing/subscription-activation.service.test.ts  # new
```

Consume SHOPIFY-002 BillingPlan resolution/top-up configuration.

## Out of Scope

- The initial Paid durable commit branch currently inside `syncSubscription()` (SHOPIFY-010).
- hosted plan-change callback flow.
- normal sync projection.
- route callback changes.
- edits to frozen `billing.service.test.ts`.

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
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — move exact activation methods

Move implementation ownership for:

```text
prepareFreeActivation
preparePaidActivation
scheduleInitialFreeReconciliationIfCurrent
completeFreeActivation
```

plus token matching. Move the current `ShopSettings -> Subscription` lock helper into `subscription-locks.ts` because the same lock is also required by hosted callback and subscription sync; the activation service consumes that shared internal lock owner rather than owning it exclusively.

### R2 — preserve public compatibility symbols and shared retry ownership

Move `INITIAL_BILLING_RETRY_DELAY_MS` with its exact `60_000` value into `billing-retry-policy.ts`, and compatibility re-export it from `billing.service.ts`. The activation service, later hosted callback service, later sync service and existing callback route must all resolve the same internal constant without route migration.

The following remain exported from `billing.service.ts` with the same shapes/values through re-export if moved:

```text
INITIAL_BILLING_RETRY_DELAY_MS
InitialFreeActivationToken
InitialPaidActivationToken
FreeActivationResult
CompletedFreeActivation
```

### R3 — preserve locking/CAS through one shared lock owner

`subscription-locks.ts` owns the existing helper logic (prefer retaining the current function name `lockInitialFreeActivationState` during this structural phase). Keep exact lock order:

```text
ShopSettings FOR UPDATE
Subscription FOR UPDATE
```

and the exact activation-token identity fields. A stale token remains a no-op. Do not duplicate this SQL in activation, hosted-plan-change or sync services.

### R4 — preserve plan resolution and completion schedule

Use SHOPIFY-002 resolution rather than duplicating plan validation. Preserve current Free top-up configuration handling and drain-window/retry scheduling.

### R5 — do not move Paid finalisation yet

`preparePaidActivation` still only establishes the durable pending selection. SHOPIFY-010 later owns the special `syncSubscription()` Paid finalisation branch.

### R6 — stable repository-internal token matcher

`matchesInitialFreeActivationToken` (name may remain exact) must move with activation ownership and remain a repository-internal export usable by the still-unextracted sync path and later `SubscriptionSyncService`. Do not duplicate token comparison logic in sync.

## Work Items

- [ ] Create `SubscriptionActivationService` and move four public workflow implementations + token matching.
- [ ] Create `subscription-locks.ts` and move the existing `ShopSettings -> Subscription` lock helper without changing SQL or ordering.
- [ ] Create `billing-retry-policy.ts` and move the exact `INITIAL_BILLING_RETRY_DELAY_MS = 60_000` constant; re-export it from the façade.
- [ ] Re-export moved compatibility types/constants from `billing.service.ts`.
- [ ] Leave façade methods as same-signature delegates.
- [ ] Add focused tests for initial/replay Free, initial Paid intent, stale-token no-op, guarded Partner-error retry, lock order and Free completion scheduling.
- [ ] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Internal service consumes `BillingPlanResolutionService`, Prisma, `subscription-locks.ts` and `billing-retry-policy.ts`. `matchesInitialFreeActivationToken` remains a repository-internal activation export for sync. Public activation types/constants and `INITIAL_BILLING_RETRY_DELAY_MS` stay available from the compatibility façade module.

## Dependencies

- `ARCH-025-SHOPIFY-005`

## Enables

- `ARCH-025-SHOPIFY-007`

## Acceptance Criteria

- [ ] Four activation public methods delegate to `SubscriptionActivationService`.
- [ ] Current activation lock order/token fencing and scheduling are unchanged and the shared lock SQL exists in only one module.
- [ ] `INITIAL_BILLING_RETRY_DELAY_MS` has one internal owner and remains publicly importable from `billing.service.ts` without changing the callback route.
- [ ] Initial Paid final durable commit remains in `syncSubscription()` after this task.
- [ ] Existing callback imports require no migration.
- [ ] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [ ] `npm test -- tests/unit/services/billing/subscription-activation.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-activation.service.ts app/services/billing/subscription-locks.ts app/services/billing/billing-retry-policy.ts tests/unit/services/billing/subscription-activation.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not rename public activation methods. Avoid designing a generic state-machine framework; this is extraction of the current pending-selection lifecycle.


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
