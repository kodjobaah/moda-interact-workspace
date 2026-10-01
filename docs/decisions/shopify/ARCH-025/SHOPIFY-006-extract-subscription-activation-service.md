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
status: review
priority: 60
executor: copilot
claimed_at: 2026-10-01T23:04:43Z
attempt: 1
depends_on:
  - ARCH-025-SHOPIFY-005
enables:
  - ARCH-025-SHOPIFY-007
created: 2026-10-01
updated: 2026-10-02
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

- [x] Create `SubscriptionActivationService` and move four public workflow implementations + token matching.
- [x] Create `subscription-locks.ts` and move the existing `ShopSettings -> Subscription` lock helper without changing SQL or ordering.
- [x] Create `billing-retry-policy.ts` and move the exact `INITIAL_BILLING_RETRY_DELAY_MS = 60_000` constant; re-export it from the façade.
- [x] Re-export moved compatibility types/constants from `billing.service.ts`.
- [x] Leave façade methods as same-signature delegates.
- [x] Add focused tests for initial/replay Free, initial Paid intent, stale-token no-op, guarded Partner-error retry, lock order and Free completion scheduling.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Internal service consumes `BillingPlanResolutionService`, Prisma, `subscription-locks.ts` and `billing-retry-policy.ts`. `matchesInitialFreeActivationToken` remains a repository-internal activation export for sync. Public activation types/constants and `INITIAL_BILLING_RETRY_DELAY_MS` stay available from the compatibility façade module.

## Dependencies

- `ARCH-025-SHOPIFY-005`

## Enables

- `ARCH-025-SHOPIFY-007`

## Acceptance Criteria

- [x] Four activation public methods delegate to `SubscriptionActivationService`.
- [x] Current activation lock order/token fencing and scheduling are unchanged and the shared lock SQL exists in only one module.
- [x] `INITIAL_BILLING_RETRY_DELAY_MS` has one internal owner and remains publicly importable from `billing.service.ts` without changing the callback route.
- [x] Initial Paid final durable commit remains in `syncSubscription()` after this task.
- [x] Existing callback imports require no migration.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate` passed.
- [x] Frozen test SHA-256 is `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`.
- [x] `git diff -- tests/unit/services/billing.service.test.ts` is empty.
- [x] Frozen façade suite: 195 passed, 18 failed; every failing identifier matches `ARCH025-TEST-001`.
- [x] Focused activation suite: 6 passed.
- [x] Full suite: 983 passed, 24 failed, 33 skipped across 92 files; all 24 failing identifiers match `ARCH025-TEST-001`.
- [x] `npm run typecheck` passed.
- [x] Targeted ESLint passed (existing TypeScript parser-version warning only).
- [x] `npm run build` passed (existing bundler and chunk-size warnings only).
- [x] `git diff --check` passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not rename public activation methods. Avoid designing a generic state-machine framework; this is extraction of the current pending-selection lifecycle.


## Completion Report

### Status

Review

### Files Changed

Implementation repository (`moda-interact`):

- `app/services/billing/billing.service.ts`
- `app/services/billing/subscription-activation.service.ts` (new)
- `app/services/billing/subscription-locks.ts` (new)
- `app/services/billing/billing-retry-policy.ts` (new)
- `tests/unit/services/billing/subscription-activation.service.test.ts` (new)

Parent workspace: this task report only.

### Work Completed

- Moved Free/Paid activation preparation, guarded Free retry scheduling, Free completion, and activation-token matching into `SubscriptionActivationService`; the four façade methods retain their signatures and delegate.
- Moved the single `ShopSettings -> Subscription` lock implementation into `subscription-locks.ts`; the still-local hosted and sync paths reuse it.
- Moved the exact 60,000 ms retry constant into `billing-retry-policy.ts` and re-exported it with the activation compatibility types from `billing.service.ts`.
- Left initial Paid durable finalisation in `syncSubscription()` and made no route or frozen-test changes.
- Added six focused tests covering initial/replay Free, Paid intent only, stale-token no-op, guarded Partner-error retry, lock order, and drain-window completion scheduling.

### Validation Results

Passed: Prisma client generation, focused activation suite (6/6), typecheck, targeted ESLint, production build, frozen test SHA/diff verification, and `git diff --check`.

The frozen façade suite ran 213 tests: 195 passed and 18 failed. Its exact failing identifiers match the frozen-suite list in `ARCH025-TEST-001`. Full `npm test` ran 1,040 tests across 92 files: 983 passed, 24 failed, and 33 skipped. All 24 failures match the 18 frozen plus six unrelated full-suite identifiers recorded in `ARCH025-TEST-001`; no new failing identifier was observed.

Build emitted the existing Zod/Rollup annotation, external Prisma browser entry, and large-chunk warnings. Targeted ESLint emitted the existing TypeScript parser compatibility warning; lint passed.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None. The unchanged `ARCH025-TEST-001` baseline failures remain documented and are not task-introduced.

### Architectural Concerns

None identified. The shared retry constant and lock SQL each have a single internal owner; initial Paid durable finalisation remains in `syncSubscription()` for SHOPIFY-010.

### Launcher and VCS Evidence

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-006
parent branch: task/ARCH-025-SHOPIFY-006
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-006
implementation branch: task/ARCH-025-SHOPIFY-006
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recorded database submodule commit: cfeeb12456b4e05067a96857a8c47837d7e33bbd
launcher claim commit: 895e0b4fb4c4bb5e5403a4baf8f269d60e3e0e52
implementation commit: e0b5ec0644239d74b44b0f492270440de0dae5f0 (pushed to origin/task/ARCH-025-SHOPIFY-006)
parent report commit: 8a5795cd03b7858feed178035d085f91d51ac1e7
parent report publication: pushed to origin/task/ARCH-025-SHOPIFY-006 at 8a5795cd03b7858feed178035d085f91d51ac1e7
```

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
