---
id: ARCH-025-BACKGROUND-003
architecture_id: ARCH-025
title: Extract initial activation reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-025-BACKGROUND-002
enables:
  - ARCH-025-BACKGROUND-004
created: 2026-10-02
updated: 2026-10-03
---

# Extract initial activation reconciliation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract initial Free/Paid activation, alternate-current-plan convergence and their shared timing/lock/discount side effects into bounded collaborators while preserving the public `activateInitialPaid` compatibility path.

## Context

Initial activation is a coherent lifecycle of roughly several hundred lines and is also invoked directly by `billing-reconciliation.service.ts`. Giving it a first-class owner removes a major workflow from the queue coordinator and creates reusable exact lock/timing/discount primitives for reinstall without migrating callers.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reconciliation-timing.ts
src/services/billing-subscription-reconciliation/locking.ts
src/services/billing-subscription-reconciliation/discount-sync-publisher.service.ts
src/services/billing-subscription-reconciliation/types.ts
tests/unit/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation/reconciliation-timing.test.ts
tests/unit/services/billing-subscription-reconciliation/locking.test.ts
tests/unit/services/billing-subscription-reconciliation/discount-sync-publisher.service.test.ts
```

BACKGROUND-001/002 modules are consumable dependencies.

## Out of Scope

- reinstall lifecycle implementation.
- billing-cycle/rollover or established plan-change implementation.
- caller migration from `activateInitialPaid`.
- changes to Shared billing contracts, provider APIs or worker entrypoint.
- edits to the frozen regression file.

## Requirements

### Common ARCH-025 Background invariants

- This is a **move-only structural refactor**. Do not change billing semantics, provider protocol, queue contract, queue/job identity, retry intervals, error codes, authorization, durable lifecycle state or external worker behaviour.
- Preserve the exact public compatibility surface from `src/services/billing-subscription-reconciliation.service.ts`: `BillingSubscriptionReconciliationService`, `billingSubscriptionReconciliationService`, `activateInitialPaid`, `enqueue`, `reconstruct`, `reconcileJob`, `InitialActivationPlan`, `FREE_CYCLE_DISCOVERY_RETRY_MS`, `ROLLOVER_RETRY_MS`, `nextSubscriptionReconcileAt`, `createSubscriptionReconcilePayload` and the `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` compatibility re-export.
- Preserve the positional constructor `(database, partner, queue, logger, now, runtimeConfig, discountQueue)`. Do not modify `src/entrypoints/billing.ts` or `src/services/billing-reconciliation.service.ts` to accommodate extraction.
- Extracted modules MUST NOT import `billing-subscription-reconciliation.service.ts`; dependency direction is coordinator -> collaborator. Symbols moved out of the coordinator file that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during construction.
- Preserve parse-before-runtime-config ordering: only after `parseBillingSubscriptionReconcileJob(...)` succeeds, call `runtimeConfig.current()` exactly once and pass that immutable snapshot downstream. Malformed input must still fail during parsing before runtime-config, database or provider work.
- Normal accepted queued reconciliation performs at most the current single `getSubscriptionReconciliationSnapshot(...)` provider call and reuses `activeSubscription` plus `latestLifecycleEvent`. Do not multiply provider calls while splitting handlers.
- Reinstall reconciliation remains on its distinct `partner.getActiveSubscription(...)` path; do not replace it with the normal reconciliation snapshot helper.
- Preserve all provider/network versus Prisma transaction boundaries, `SELECT ... FOR UPDATE` targets/order, `updateMany` CAS predicates, durable rereads and post-commit side-effect ordering exactly. Preserve existing clock-read points/order too: do not coalesce, hoist or reorder repeated `now()` reads where doing so could move drain-window, period-boundary, retry or queue-delay decisions. Do not impose one global lock order across lifecycles where the current code uses different transaction shapes.
- Continue delegating canonical work to `SamePlanBillingPeriodRolloverService`, `ShopifyPlanChangeTransitionService`, `ShopifySubscriptionLifecycleReconciliationService`, `ensureCurrentBillingPeriodProjection`, `shopifyUsageEventPublisherService`, `shopifyDiscountCatalogueService` and `recoveryCapacityResumeService`; do not duplicate those implementations.
- Preserve existing `billing.subscription_reconciliation.*` structured log event names, levels, bounded field sets and emission boundaries/order relative to the I/O they describe; use the canonical Shared logger and do not log whole provider/customer payloads.
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts` is frozen: do not edit it. SHA-256 must remain `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`, and all 146 tests must pass after every task.
- Add separate focused tests for the extracted owner. Do not move assertions out of the frozen regression file, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- `tests/unit/runtime/entrypoint-isolation.test.ts` must continue passing so the billing-worker construction/startup contract remains unchanged.
- Full `npm test` must pass. If execution reveals a pre-existing baseline condition, stop and report it to `moda_architect` unless it is already durably documented in `docs/development-baseline.md`; do not silently redefine the baseline inside this task.

### R1 — one initial-activation owner

Create `initial-activation-reconciliation.service.ts` and move the complete initial activation cluster:

```text
completeVerifiedFree
completeVerifiedPaid
recordMissingSubscription
recordProviderFailure
casPendingUpdate
recordUnsupportedPaidTrial
recordPaidActivationFailure
applyOtherCurrentPlan
```

Keep the **final provider-plan lookup and branch predicates** in the coordinator during this task. That dispatch is shared with later established-plan-change handling and the current legacy FROZEN lifecycle-`continue` fallthrough, so it must not be hidden behind an initial-only entry point. The extracted service must expose repository-internal operations sufficient for the coordinator to invoke the moved Free/Paid/failure/`applyOtherCurrentPlan` implementations without importing back from the façade.

Move `InitialActivationPlan` with the initial-activation owner or the authorised adjacent `types.ts` pure type module and compatibility re-export it from `billing-subscription-reconciliation.service.ts`. BACKGROUND-004 must import the canonical moved type rather than duplicate its shape.

### R2 — direct `activateInitialPaid` compatibility path

`BillingSubscriptionReconciliationService.activateInitialPaid(...)` remains public and retains its current signature. It delegates to the extracted initial-activation owner using the already-supplied provider evidence and plan and MUST NOT perform a provider call. Do not modify `src/services/billing-reconciliation.service.ts`.

### R3 — pure timing support, not a generic retry service

Move the current pure timing constants/helpers into `reconciliation-timing.ts`:

```text
FREE_CYCLE_DISCOVERY_RETRY_MS = 5 minutes
ROLLOVER_RETRY_MS = 60 seconds
nextSubscriptionReconcileAt(...) with the exact 24-hour tier table
```

Keep the three current façade exports compatible. The timing module contains pure constants/functions only; it does not switch on lifecycle kind or perform queue/database work.

### R4 — shared lock SQL owner

Move the exact `lockShopSettings(...)`, `lockShop(...)` and `lockSubscription(...)` `FOR UPDATE` SQL helpers into `locking.ts`. Do not change SQL text/targets. Initial activation continues to acquire `ShopSettings -> Subscription`; moving `lockShop` early merely establishes the exact shared primitive that BACKGROUND-004 will consume and MUST NOT cause initial activation to start acquiring the Shop lock.

### R5 — discount-sync publisher

Move `publishDiscountSync(...)` into a bounded `discount-sync-publisher.service.ts` because both initial activation and reinstall use it. Preserve:

- Shop domain read timing;
- `shopifyDiscountCatalogueService.requestSync(...)` call;
- deterministic discount-sync job id and queue options;
- no-op when discount queue is absent;
- best-effort failure isolation and existing `shopify.discount_sync.enqueue_failed` logging.

### R6 — initial activation semantics are exact

Preserve all existing Free/Paid/alternate-plan transaction boundaries, CAS predicates, BillingPeriod projection/creation rules, included/lifetime credit counter behaviour, pending-target clearing, onboarding completion, drain-window scheduling and error-code selection. Do not substitute a different canonical projection/rollover flow where the current initial activation branch intentionally has its own checks.

`sameDate`/expected schedule equality from BACKGROUND-001 must be reused rather than duplicated.

`applyOtherCurrentPlan(...)` and `recordMissingSubscription(...)` must remain independently invocable by the coordinator with the source values. Do not add an initial-activation-only precondition around either operation: the current coordinator can reach them after a non-initial FROZEN lifecycle reconciliation returns `continue`, and BACKGROUND-007 must be able to preserve those legacy fallthroughs without reopening this task.

Preserve the short-circuit stale-guard evaluation in `applyOtherCurrentPlan(...)`: the `NO_CONTRACT`/`planId === null` checks must reject a genuine FROZEN row before code attempts to dereference pending fields such as `expected.pendingEffectiveAt`. BACKGROUND-001 deliberately preserves a FROZEN expected object with those pending properties absent. Do not precompute `pendingEffectiveAt.toISOString()` or otherwise reorder this guard in a way that can throw on the legacy FROZEN path.

### R7 — post-commit side effects remain post-commit

Discount sync and next-reconcile enqueue happen only after the same current commits and remain failure-isolated exactly as today.

## Work Items

- [x] Add the initial activation reconciliation service.
- [x] Add pure reconciliation timing support and compatibility re-exports.
- [x] Add exact shared lock helpers and wire initial activation to `ShopSettings -> Subscription` only.
- [x] Add the shared discount-sync publisher with existing best-effort semantics.
- [x] Move the complete initial activation helper cluster while retaining the shared final provider-plan lookup/branch dispatch in the coordinator.
- [x] Keep public `activateInitialPaid(...)` as a no-provider-call compatibility delegate.
- [x] Add focused initial-activation tests for tiered retry expiry, stale CAS, Free activation, Paid activation, alternate current plan, fail-closed errors, projection/counter replay, post-commit queue failure isolation, and FROZEN-shaped calls to `recordMissingSubscription`/`applyOtherCurrentPlan` that remain non-throwing/no-op against non-NO_CONTRACT durable state.
- [x] Add direct focused tests for `reconciliation-timing.ts`, exact lock SQL/order primitives and the discount-sync publisher rather than relying only on façade regression coverage for those newly extracted owners.
- [x] Prove the frozen 146-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal initial-activation service receives the database, queue publisher, discount publisher, logger/clock and already-obtained provider evidence. It exposes only repository-internal operations needed by the coordinator dispatch, including the exact `applyOtherCurrentPlan` fallthrough operation. Public `InitialActivationPlan`, retry constants/helper and `activateInitialPaid` remain compatible through the façade file.

## Dependencies

- `ARCH-025-BACKGROUND-002`

## Enables

- `ARCH-025-BACKGROUND-004`

## Acceptance Criteria

- [x] Initial activation transaction/retry logic no longer lives in the coordinator.
- [x] Direct and queued initial-Paid paths preserve current signatures and perform no extra provider/plan reads.
- [x] Existing Free/Paid/other-current-plan error codes, period/counter semantics and post-commit scheduling are unchanged.
- [x] Shared lock SQL and pure timing helpers have one owner without becoming generic orchestration frameworks.
- [x] Discount sync remains post-commit/best-effort and uses the existing queue contract.
- [x] Frozen regression suite remains byte-identical and all 146 tests pass.

## Validation

- [x] `npm run prisma:generate` (also run by `npm run build`) succeeds.
- [x] Frozen regression test SHA-256 is `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`.
- [x] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty.
- [x] Frozen regression suite passes all 146 tests.
- [x] Extracted activation-owner suite passes (11 tests).
- [x] Billing entrypoint-isolation suite passes.
- [x] Focused timing, locking and discount publisher suites pass (11 tests combined).
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.
- [x] Full `npm test` was run; it remains nonzero only for documented baseline identities and isolated transient observability-startup timeouts, as detailed below. No task-local suite failed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/discount-sync-publisher.service.ts`
- `src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/locking.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-timing.ts`
- `src/services/billing-subscription-reconciliation/types.ts`
- `tests/unit/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/reconciliation-timing.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/locking.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/discount-sync-publisher.service.test.ts`

### Work Completed

- Routed provider failure, missing subscription, Free activation, Paid activation, paid activation failure, and alternate-current-plan dispatch directly from the coordinator to `InitialActivationReconciliationService`.
- Removed duplicate coordinator activation implementations and the obsolete activation forwarding methods/CAS helper. The shared provider-plan lookup and branch predicates remain in `reconcileJob`; reinstall, cycle-discovery, rollover, and lock wrappers remain in place.
- Preserved the public `activateInitialPaid(...)` delegate and compatibility exports for the plan type, retry constants/helper, and billing drain window.
- Added focused extracted-owner tests plus direct timing, lock-SQL/order, and discount-sync publisher tests. The frozen regression test file was not modified.

### Validation Results

- `npm run build`: passed, including Prisma client generation and TypeScript compilation.
- Focused final command covering the frozen regression, initial activation owner, billing entrypoint isolation, timing, locks, and discount publisher: 6 files passed, 178 tests passed.
- Frozen regression suite: 146 tests passed. SHA-256 matched `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`; its Git diff is empty.
- Extracted activation-owner suite: 11 tests passed. Timing, lock, and discount publisher suites: 11 tests passed combined.
- Isolated `tests/unit/runtime/observability-startup.test.ts`: 10 tests passed after four of its cases timed out during full-suite execution.
- `git diff --check`: passed.
- Full `npm test`: 12 failed, 1,438 passed, 38 skipped, with one suite-loading failure. The eight non-timeout failing test identities and ARCH-020 fixture-loading failure match `ARCH025-BACKGROUND-TEST-001` in `docs/development-baseline.md`; the four translation-enum failures reported that PostgreSQL at `localhost:5432` was unavailable. The four additional observability-startup timeout cases passed on isolated rerun (10/10); prior ARCH-025 evidence records the same transient timeout pattern. No task-local test failed; no full-suite pass is claimed.

### Deviations

- The full suite did not pass because of documented baseline conditions and transient isolated observability process-spawn timeouts; all required focused task suites and build passed.

### Assumptions

- The documented `ARCH025-BACKGROUND-TEST-001` baseline applies because the full-run failures match its listed identities and fixture failure; the four timeout cases passed on isolated rerun and were not added to the baseline.

### Unresolved Issues

- Full-suite environment/baseline failures remain as recorded above; no implementation blocker remains for architect review.

### Architectural Concerns

- None.

## Attempt 2 Completion Report

### Status

Ready for Review

### Changes Completed

- A1-R1: Restored `lastSyncedAt: now` in the existing `reconcileFreeCycle(...)` `BILLING_PERIOD_PLAN_CONFLICT` update. No other Free-cycle behavior changed.
- A1-R2: Recorded the launcher-resolved physical worktrees, synchronization results, recursive submodule commit, and Attempt 2 implementation/claim commits below.
- Implementation correction commit: `ae20dd6236a83d7a0f9950dbec0e2e535a43cd55`, pushed to `task/ARCH-025-BACKGROUND-003`. It follows Attempt 1 implementation commit `e8f76fcc580bacd85af2413dcb1b7fff2c328ec2`.
- Parent Attempt 2 claim commit: `681cfe7e6261a343b1f9e10fc00d69c53fc41c4a`, pushed before implementation. This report update is the next parent task-branch commit.

### Physical Worktree and Synchronization Evidence

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-003
parent branch: task/ARCH-025-BACKGROUND-003
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-003
implementation branch: task/ARCH-025-BACKGROUND-003
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no

parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: yes
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current

git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recursive submodule database: cfeeb12456b4e05067a96857a8c47837d7e33bbd (initialized)
```

### Validation Results

- `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts`: 146/146 passed.
- Focused six-file command for frozen reconciliation, activation owner, entrypoint isolation, timing, locking and discount publisher: 6 files and 178/178 tests passed.
- Separate `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- `npm run build`: passed, including Prisma client generation and TypeScript compilation.
- Frozen regression SHA-256 remains `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`; its Git diff is empty.
- `git diff --check`: passed.
- Full `npm test`: 8 failed, 1,442 passed, 38 skipped, plus one suite-loading failure. All eight failing test identities and the missing ARCH-020 fixture suite match durable baseline `ARCH025-BACKGROUND-TEST-001`; the four PostgreSQL integration failures could not connect to `localhost:5432`. No new failure identity appeared, and the four observability-startup timeouts from the prior run did not recur.

### Deviations and Unresolved Issues

- The full suite remains nonzero only for the documented baseline identities and missing fixture condition. The Architect Review determined these known baseline failures are not a blocker when no regression is introduced.
- No task-local validation failed. No further implementation issue is known.

## Architect Review

### Review Status

Accepted — Attempt 2

### Review Notes

Attempt 2 is accepted. Correction commit `ae20dd6236a83d7a0f9950dbec0e2e535a43cd55` restores exactly the pre-task `lastSyncedAt: now` write in the existing `reconcileFreeCycle(...)` `BILLING_PERIOD_PLAN_CONFLICT` path; GitHub comparison against Attempt 1 implementation `e8f76fcc580bacd85af2413dcb1b7fff2c328ec2` shows that this is the only implementation change. The initial-activation extraction therefore returns to move-only equivalence outside its authorised surface.

A1-R2 is also closed: the Attempt 2 report records the launcher-resolved parent/implementation worktrees, synchronization result, recursive `database` submodule at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`, implementation correction commit, claim commit, validation evidence, and clean task-remote alignment. Parent report tip `dae2ed58cd5582d512c0477283d3efe3de475860` is pushed.

The full suite remains nonzero only for the eight identities and ARCH-020 fixture-loading condition already governed by `ARCH025-BACKGROUND-TEST-001`; no submitted-only failure identity appears. The four observability-startup timeouts seen in Attempt 1 did not recur.

#### Attempt 1 review history

The initial-activation extraction is structurally sound, but one out-of-scope durable-state change must be corrected before acceptance.

**A1-R1 — restore `lastSyncedAt` in the existing Free-cycle conflict path.**

The pre-task coordinator at `2c9cca54d3f03692633ab3930a80803c49bf3207` writes `lastSyncedAt: now` when `reconcileFreeCycle(...)` receives `BILLING_PERIOD_PLAN_CONFLICT`. Submitted implementation `e8f76fcc580bacd85af2413dcb1b7fff2c328ec2` drops that field from the same `transaction.subscription.update(...)`. `reconcileFreeCycle(...)` is billing-cycle behavior owned by later BACKGROUND-005 and is explicitly outside BACKGROUND-003's move-only initial-activation scope. Restore the exact pre-task field without otherwise changing the cycle path.

**A1-R2 — complete durable execution evidence.**

The Completion Report does not record the launcher-resolved physical parent/implementation worktrees, start-of-attempt synchronization evidence, recursive submodule state, or the pushed implementation/report commit identities. Record those facts in Attempt 2. The reviewed pushed identities are implementation `e8f76fcc580bacd85af2413dcb1b7fff2c328ec2` and Attempt 1 report `99f35a9bbb516e816b647d4397f449e5ab5e5086`; after the source correction, record the new implementation/report heads and final clean/remote-aligned state.

No other production correction is requested. The extracted activation owner, timing helpers, lock helpers, discount-sync publisher, façade compatibility, provider-plan lookup ownership, FROZEN short-circuit behavior, and post-commit side-effect ordering otherwise conform to the task.

The nonzero full-suite result is not itself a blocker for this review: the durable eight-failure plus fixture baseline matches `ARCH025-BACKGROUND-TEST-001`, and the four additional observability-startup timeout identities passed on isolated rerun. Those transient timeout identities are not added to the baseline.

### Reviewed Files

- `moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/reconciliation-timing.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/locking.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/discount-sync-publisher.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/types.ts`
- the four new focused test files authorised by this task
- this task report

### Validation Reviewed

- implementation correction commit `ae20dd6236a83d7a0f9950dbec0e2e535a43cd55` is pushed and changes only `src/services/billing-subscription-reconciliation.service.ts`; compared with Attempt 1 `e8f76fcc580bacd85af2413dcb1b7fff2c328ec2`, the sole delta restores `lastSyncedAt: now` in the Free-cycle conflict update;
- parent report tip `dae2ed58cd5582d512c0477283d3efe3de475860` is pushed;
- frozen reconciliation regression: 146/146 passed; required SHA-256 `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239` matched and frozen diff remained empty;
- focused six-file command: 178/178 passed;
- entrypoint isolation: 10/10 passed;
- `npm run build`: passed, including Prisma generation;
- `git diff --check`: passed;
- full `npm test`: 8 failed / 1,442 passed / 38 skipped plus one fixture-loading failure; all eight identities and the missing ARCH-020 fixture condition match `ARCH025-BACKGROUND-TEST-001`, with no new failure identity.

### Architecture Conformance

Accepted. A1-R1 and A1-R2 are closed. The task is again a move-only structural extraction: the coordinator retains the shared provider-plan lookup/dispatch, the extracted owner preserves initial Free/Paid/alternate-current-plan semantics and FROZEN fallthrough safety, the shared timing/lock/discount collaborators retain their exact contracts, and no provider/transaction/queue ordering regression was introduced.

### Follow-up

`ARCH-025-BACKGROUND-004` may proceed. Preserve `ARCH025-BACKGROUND-TEST-001` as a no-regression reference and keep the accepted BACKGROUND-003 collaborators behaviourally unchanged.
