---
id: ARCH-025-SHOPIFY-010
architecture_id: ARCH-025
title: Extract initial Paid activation finalisation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 100
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-SHOPIFY-009
enables:
  - ARCH-025-SHOPIFY-011
created: 2026-10-01
updated: 2026-10-02
---

# Extract initial Paid activation finalisation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Move only the special initial Paid durable finalisation branch out of `syncSubscription()` into the existing `SubscriptionActivationService`, preserving its strict Shop lock, exact pending-token/cycle/configuration validation and atomic entitlement creation.

## Context

After SHOPIFY-006, activation intent/retry/Free completion already has one owner, but `syncSubscription()` still contains the higher-risk initial Paid final commit. Extracting that branch separately before the general sync coordinator keeps the final task bounded and places all initial activation semantics together.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-activation.service.ts
app/services/billing/subscription-locks.ts
tests/unit/services/billing/subscription-activation.service.test.ts
```

No new service file is required unless implementation demonstrates a concrete cycle dependency; default is to extend the existing activation service.

## Out of Scope

- normal provider-to-local sync branches.
- changing Paid activation rules or configuration requirements.
- modifying provider API calls.
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

### R1 — exact branch boundary inside the caller-owned sync transaction

Move only the body of the branch currently selected when an `expectedInitialSelection` for `PAID_METERED` matches the provider result and the durable pending initial intent. The remaining `syncSubscription()` must still open the existing outer transaction, acquire the shared `ShopSettings -> Subscription` lock, reread `existingSubscription`, reject a stale expected token, and determine whether the initial-Paid branch applies.

The activation finalisation method MUST accept the existing `Prisma.TransactionClient` and execute inside that **same already-open transaction**. It MUST NOT call `database.$transaction(...)`, create a nested/second transaction, move branch detection outside the lock, or commit independently.

### R2 — preserve full lock order and durable reread

Move `lockShopForInitialPaidActivation` into the shared `subscription-locks.ts` owner created by SHOPIFY-006, retaining its exact SQL. For this branch the effective lock order must remain:

```text
ShopSettings FOR UPDATE
Subscription FOR UPDATE
Shop FOR UPDATE
```

The first two locks are already held by the caller before finalisation is invoked. The finaliser acquires the Shop lock and retains all current durable rereads/identity checks. Do not duplicate lock SQL in the activation service.

### R3 — preserve fail-closed validations

Keep current behaviour for:

```text
missing/mismatched pending plan identity
missing provider cycle
Paid trial
missing/invalid included allowance
missing required provider usage meter
inactive/mismatched plan
existing conflicting/closed BillingPeriod
included counter conflicts
invalid lifetime-Free policy
```

The same current `SYNC_ERROR`/`lastSyncErrorCode` results and no-write/conflict semantics must remain. Preserve the current error-selection order exactly: missing/unexposed usage meter -> `MISSING_USAGE_METER`; supported meter plus unsupported Paid trial -> `UNSUPPORTED_PAID_TRIAL`; other invalid configuration/conflict -> `INVALID_PAID_PLAN_CONFIGURATION`. Do not strengthen existing counter/lifetime validation beyond what this branch currently checks.

### R4 — preserve atomic success commit

Successful finalisation must still atomically create/reuse the exact BillingPeriod, included counter and lifetime-Free counter as currently required, clear the pending selection, set ACTIVE projection fields and set the exact drain-window `nextReconcileAt`.

### R5 — no provider work and no generic-projection substitution

The service receives already obtained provider subscription evidence; it must not perform a new Shopify call. Do not replace the initial-Paid branch with SHOPIFY-001 `ensureMappedCurrentBillingPeriodProjection`: the current initial-Paid branch has intentionally different validation/conflict semantics and must remain exact.

### R6 — preserve stale-token and replay boundary

A stale `expectedInitialSelection` remains a no-op before the finaliser runs. Existing BillingPeriod/counter/lifetime rows are reused or rejected using the current branch-specific predicates; do not add arithmetic checks to the existing included counter or new validation of an existing lifetime counter as incidental cleanup.

## Work Items

- [x] Extend `SubscriptionActivationService` with one bounded initial-Paid finalisation method that accepts the caller-owned `Prisma.TransactionClient`.
- [x] Move `lockShopForInitialPaidActivation` into `subscription-locks.ts` and preserve full `ShopSettings -> Subscription -> Shop` lock order.
- [x] Move only the identified branch body from `syncSubscription()`; keep outer transaction, stale-token fencing, existing-subscription reread and branch detection in sync.
- [x] Extend focused activation tests for exact successful period/counters, Shop lock, all fail-closed cases, replay preservation and drain-window schedule.
- [x] Prove no additional provider/database work was introduced around the branch.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Internal activation method accepts the caller-owned `Prisma.TransactionClient`, already obtained provider Subscription evidence, expected activation token, existing locked Subscription facts and `now`/other exact inputs needed by the current branch. It does not own or open a transaction and is not exposed to routes.

## Dependencies

- `ARCH-025-SHOPIFY-009`

## Enables

- `ARCH-025-SHOPIFY-011`

## Acceptance Criteria

- [x] Initial Paid branch body no longer lives in `syncSubscription()`, but the existing sync transaction remains the owner and no nested/second transaction is introduced.
- [x] Full `ShopSettings -> Subscription -> Shop` lock order and all strict initial Paid validation/entitlement semantics are unchanged.
- [x] Activation service performs no provider call.
- [x] `syncSubscription()` still exposes exactly the same public behaviour.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [x] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [x] `npm test -- tests/unit/services/billing/subscription-activation.service.test.ts` passes the new focused capability tests
- [x] `npm test` introduces no new failures
- [x] `npm run typecheck`
- [x] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-activation.service.ts app/services/billing/subscription-locks.ts tests/unit/services/billing/subscription-activation.service.test.ts`
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not use SHOPIFY-001 generic BillingPeriod projection to replace this branch. The finaliser is a transaction-participant, not a transaction owner. Preserve exact validation ordering and existing branch-specific permissiveness as well as strictness; “cleaning up” the predicates is a behaviour change.


## Completion Report

### Status

Ready for Architect Review; task status is `review`.

### Files Changed

- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/billing/subscription-activation.service.ts`
- `moda-interact/app/services/billing/subscription-locks.ts`
- `moda-interact/tests/unit/services/billing/subscription-activation.service.test.ts`

### Work Completed

- Moved the initial Paid durable finalisation into `SubscriptionActivationService.finalizeInitialPaidActivation`, passing the existing `Prisma.TransactionClient`, provider evidence, expected token, locked subscription facts and `now`. The method performs no nested transaction and no provider call.
- Kept outer transaction ownership, `ShopSettings -> Subscription` locks, durable Subscription reread, stale-token rejection and initial Paid branch selection in `syncSubscription()`.
- Moved the exact Shop `FOR UPDATE` helper into `subscription-locks.ts`; finalisation preserves `ShopSettings -> Subscription -> Shop` lock order and the original validation/error selection, period/counter conflict semantics, atomic entitlement writes and drain-window scheduling.
- Added focused tests for successful initial Paid activation, supplied-transaction ownership, lock ordering, validation/error precedence (including both usage-meter and Paid-trial errors), period/counter replay and conflicts, invalid lifetime policy and exact reconciliation scheduling.
- Confirmed the production diff is limited to the four authorized implementation files. No additional provider calls or database round trips were introduced by the move.
- Implementation commits `9c039a87f98ff3b8c0f51bb9fd9b4552855fda44` and `b3f0733388f5b2d83d259a61a4319eb15448af45` are pushed to `task/ARCH-025-SHOPIFY-010`; the remote task ref matches the final commit.

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-010`, branch `task/ARCH-025-SHOPIFY-010`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-010`, branch `task/ARCH-025-SHOPIFY-010`.
- Shared canonical workspace and shared implementation checkout switched or mutated for task work: no. Another task worktree reused: no.

### Start-of-Attempt Synchronization

- Parent remote task branch fast-forwarded: not needed; parent `origin/main` was already current.
- Implementation remote task branch fast-forwarded: not needed; implementation `origin/main` was already current.
- The launcher prepared and claimed Attempt 1 (`copilot`) at `2026-10-02T08:03:06Z`; parent claim commit `ec59aca98f5a2f867ee87975eb4dc79f49311d2e` is pushed.

### Recursive Implementation Submodules

- `git submodule sync --recursive`: passed.
- `git submodule update --init --recursive`: passed.
- Recorded submodule commit: `database` at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Validation Results

- `npm run prisma:generate`: passed; Prisma Client v6.19.3 generated.
- Frozen test SHA-256: `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; `git diff -- tests/unit/services/billing.service.test.ts` is empty.
- Frozen façade suite: 195 passed / 18 failed / 213 total. All 18 failing identifiers match the frozen list in `ARCH025-TEST-001`.
- Focused activation suite: 21/21 passed.
- Full `npm test`: 95 files; 1,024 passed / 24 failed / 33 skipped (1,081 total). All 24 failing identifiers match `ARCH025-TEST-001` (18 frozen façade failures and six additional documented baseline failures); no new failing identifier was observed.
- `npm run typecheck`: passed.
- Required targeted ESLint command: passed. The installed TypeScript 5.9.3 emits the existing `@typescript-eslint/typescript-estree` supported-version warning; no lint errors.
- `npm run build`: passed for client and server bundles. Existing Vite/Rollup dependency annotation, external Prisma browser-entry, empty-chunk and chunk-size warnings were non-fatal.
- `git diff --check`: passed.

### Deviations

None. The GitKraken push helper rejected the implementation worktree's inherited `origin/main` upstream; the implementation commit was explicitly pushed to the same-named task branch, never to `main`.

### Assumptions

The existing branch behavior and durable baseline `ARCH025-TEST-001` are authoritative; no billing rule or repository-level baseline changes were requested.

### Unresolved Issues

The unchanged `ARCH025-TEST-001` baseline remains: 18 frozen BillingService failures and six additional full-suite failures.

### Architectural Concerns

None identified. Architect Review remains Pending; no acceptance decision has been made by this agent.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 accepted.

The extraction preserves the exact initial Paid finalisation boundary. `syncSubscription()` still owns the existing outer Prisma transaction, acquires `ShopSettings -> Subscription` through `lockInitialFreeActivationState(...)`, rereads the durable Subscription, rejects a stale `expectedInitialSelection`, and determines whether the initial-Paid branch applies before delegating.

`SubscriptionActivationService.finalizeInitialPaidActivation(...)` accepts the caller-owned `Prisma.TransactionClient`; it does not open a nested/second transaction and performs no provider/API call. The moved Shop `FOR UPDATE` SQL is now owned by `subscription-locks.ts`, preserving the effective `ShopSettings -> Subscription -> Shop` lock order.

Direct comparison with the pre-task branch confirms the finaliser retains the original plan identity/activity/kind/handle checks, usage-meter visibility, included-allowance validation, cycle/trial rules, BillingPeriod identity/snapshot checks, included-counter conflict predicate and lifetime-Free policy behavior. Error selection remains `MISSING_USAGE_METER` before `UNSUPPORTED_PAID_TRIAL`, with other invalid/configuration/conflict states resolving to `INVALID_PAID_PLAN_CONFIGURATION`; no incidental arithmetic strengthening was introduced.

The success path still reuses or creates the exact BillingPeriod, included counter and lifetime-Free counter in the caller transaction, clears the pending selection, writes the ACTIVE projection fields and computes the same drain-window `nextReconcileAt`.

Production extraction commit reviewed: `9c039a87f98ff3b8c0f51bb9fd9b4552855fda44`.
Final implementation task ref reviewed: `b3f0733388f5b2d83d259a61a4319eb15448af45`; the second commit changes only focused test coverage for missing allowance and pending-plan identity failures.
Parent Completion Report reviewed: `e346532d2eaf9f08d39ead710d2d4af902a5b137`.

### Reviewed Files

- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/billing/subscription-activation.service.ts`
- `moda-interact/app/services/billing/subscription-locks.ts`
- `moda-interact/tests/unit/services/billing/subscription-activation.service.test.ts`
- `docs/decisions/shopify/ARCH-025/SHOPIFY-010-extract-initial-paid-activation-finalisation.md`
- `docs/decisions/shopify/ARCH-025/_index.md`
- `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`
- `docs/development-baseline.md` (`ARCH025-TEST-001`)

### Validation Reviewed

- Focused activation suite: 21/21 passed.
- Frozen façade SHA-256 remains `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; frozen test diff is empty.
- Frozen façade suite: 195 passed / 18 failed; every failing identifier is contained in `ARCH025-TEST-001`.
- Full suite: 1,024 passed / 24 failed / 33 skipped; every failing identifier is contained in `ARCH025-TEST-001`, with no task-only failure.
- Prisma generation, typecheck, task-scoped ESLint, production build and `git diff --check`: passed.
- GitHub branch comparison shows the implementation task branch is two commits ahead of accepted SHOPIFY-009 main baseline `c7b14b5131fd00506da651e7bf0d10e8309c2f9b`; the first commit contains the authorised four-file extraction/test delta and the final commit modifies only the focused activation test.
- Completion Report records launcher-resolved parent/implementation worktrees, start-of-attempt synchronization, recursive database-submodule materialisation and clean pushed task refs.
- Uploaded review snapshot contains no cross-task `node_modules` symlink.

### Architecture Conformance

Conforms to ARCH-025 and SHOPIFY-010. Initial Paid finalisation now has the intended activation owner without changing transaction ownership, lock order, provider boundary, stale-token fencing, branch-specific validation/error semantics, entitlement creation/reuse, durable projection fields or public `BillingService.syncSubscription()` behavior.

### Follow-up

`ARCH-025-SHOPIFY-011` is promoted to `ready`. It is the final ARCH-025 implementation task.
