---
id: ARCH-025-BACKGROUND-002
architecture_id: ARCH-025
title: Extract subscription reconciliation queue and reconstruction
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 20
executor: copilot
claimed_at: 2026-10-02T19:02:35Z
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-001
enables:
  - ARCH-025-BACKGROUND-003
created: 2026-10-02
updated: 2026-10-02
---

# Extract subscription reconciliation queue and reconstruction

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract deterministic subscription-reconcile queue publication, durable next-schedule publication and startup reconstruction into one bounded collaborator while retaining the existing service façade and queue contract.

## Context

Every later lifecycle handler needs a stable way to publish an already-committed `nextReconcileAt`. Extracting queue mechanics before lifecycle code prevents handlers from depending back on the coordinator and keeps retry decisions separate from queue transport.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reconciliation-queue.service.ts
tests/unit/services/billing-subscription-reconciliation/reconciliation-queue.service.test.ts
```

The BACKGROUND-001 pure classification module may be imported but not behaviourally changed.

## Out of Scope

- lifecycle state classification changes.
- retry-policy centralisation.
- worker entrypoint/caller edits.
- Shared queue contract changes.
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

### R1 — deterministic queue publisher

Create `reconciliation-queue.service.ts` owning the existing subscription-reconcile queue mechanics. It must receive the exact `database`, subscription queue, structured logger and `now` function supplied to the façade; do not silently fall back to module-level defaults or create a second clock/logger. Move the implementation of `enqueue(...)`, `publishNext(...)` and `publishCommittedLifecycleSchedule(...)` without changing:

```text
queue name/job name
deterministic job id helper
delay = max(0, requested delay)
removeOnComplete = 100
removeOnFail = true
no-op when queue dependency is absent
```

`BillingSubscriptionReconciliationService.enqueue(...)` remains a public compatibility delegate.

### R2 — startup reconstruction query is moved, not redesigned

Move `reconstruct()` with its current Prisma `shop.findMany` predicate intact. Preserve eligibility for:

- ACTIVE pending-plan rows with a durable schedule;
- FROZEN rows with a durable schedule;
- onboarding-complete pack-enabled Free cycle discovery;
- onboarding-complete Paid or pack-enabled Free rows with BillingPeriod/rollover work;
- UNINSTALLED rows with `reinstallPendingAt` and a durable schedule.

Do not simplify duplicated-looking OR branches unless a separate behaviour task authorises it.

### R3 — reconstruction timing/logging

Preserve overdue work as zero-delay publication and future work as remaining delay. Preserve per-row enqueue-failure isolation and the exact log event meanings for:

```text
billing.subscription_reconciliation.reconstruction_started
billing.subscription_reconciliation.reconstruction_finished
billing.subscription_reconciliation.enqueue_failed
```

The returned reconstructed count preserves the source implementation exactly: increment once for each eligible row whose delegated `enqueue(...)` call resolves without throwing. Because public `enqueue(...)` currently resolves as a no-op when no queue dependency exists, reconstruction also increments in that no-queue case; this is **not** a count of BullMQ inserts.

### R4 — payload helper compatibility

Move `createSubscriptionReconcilePayload(...)` only if useful to the queue owner, but keep it compatibility-exported from `billing-subscription-reconciliation.service.ts` because `billing-reconciliation.service.ts` imports it today. No Shared contract or schema-version change is authorised.

### R5 — queue service does not decide lifecycle retries

The queue owner accepts an already-decided durable next schedule. It MUST NOT centralise initial/reinstall/cycle/plan-change/FROZEN retry policy or inspect billing lifecycle state to choose a delay.

## Work Items

- [x] Add the queue/reconstruction collaborator.
- [x] Move `enqueue`, `publishNext`, `publishCommittedLifecycleSchedule` and `reconstruct` behind it with exact current semantics.
- [x] Keep public `enqueue`/`reconstruct` façade delegates and `createSubscriptionReconcilePayload` compatibility export.
- [x] Route coordinator/later-handler publication through the collaborator without changing queue call count/options.
- [x] Add focused queue/reconstruction tests for deterministic IDs, overdue/future delay, public no-queue no-op, no-queue reconstruction count semantics, reconstruction predicate coverage and enqueue-failure isolation.
- [x] Prove the frozen 98-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal queue collaborator using the façade-supplied database/queue/logger/clock identities. Public `BillingSubscriptionReconciliationService.enqueue()` and `.reconstruct()` remain delegates. `createSubscriptionReconcilePayload` remains import-compatible from the façade file.

## Dependencies

- `ARCH-025-BACKGROUND-001`

## Enables

- `ARCH-025-BACKGROUND-003`

## Acceptance Criteria

- [ ] Queue publication/reconstruction no longer lives in the coordinator implementation.
- [ ] Existing job payload/schema, job identity and BullMQ options are unchanged.
- [ ] Reconstruction selects the same durable rows, preserves the current count semantics including the no-queue case, and performs no provider calls.
- [ ] Existing public helper/method imports continue to work without caller edits.
- [ ] Lifecycle retry choice remains outside the queue service.
- [ ] Frozen regression suite remains byte-identical and all 146 tests pass.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [x] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 98 frozen regression tests
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation/reconciliation-queue.service.test.ts` passes
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [ ] `npm test` passes with no regression
- [x] `npm run build` succeeds
- [x] `git diff --check` passes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Blocked before review. Queue extraction and focused validation are complete, but `npm test` exits nonzero with the same pre-existing full-suite failure set recorded under `ARCH025-BACKGROUND-TEST-001`; the latest run reported no additional task-specific failures. That condition is not documented in `docs/development-baseline.md`. The task explicitly requires stopping and reporting an observed pre-existing condition unless it is durably recorded there, so no full-suite pass is claimed and architect direction is required before this task can proceed to review.

### Files Changed

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-queue.service.ts`
- `tests/unit/services/billing-subscription-reconciliation/reconciliation-queue.service.test.ts`
- This task report only; no unrelated parent-workspace files changed.

### Work Completed

- Extracted queue publication and startup reconstruction into `ReconciliationQueueService`, wired with the façade's database, queue, logger, and clock instances.
- Kept public `enqueue()` and `reconstruct()` as façade delegates and compatibility-re-exported `createSubscriptionReconcilePayload()`.
- Preserved the reconstruction Prisma predicate, delay calculation, no-queue behavior/count semantics, enqueue failure isolation, logging, deterministic job identity, and BullMQ options.
- Added focused queue/reconstruction tests covering the requested behaviors.
- The implementation task worktree was created at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-002` on `task/ARCH-025-BACKGROUND-002`; parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-002` on the same branch. The canonical workspace checkout and shared implementation checkout were not switched or mutated, and no other task worktree was reused.
- Start synchronization: parent remote task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `already-current`; implementation remote task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` is initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Durable launcher claim: Attempt 1, executor `copilot`, claim commit `504001040d2f5a2580e4b262a10ac7fc64795d49`.
- Implementation commit `8bfb6dc` (`refactor(background): extract reconciliation queue`) was pushed to `origin/task/ARCH-025-BACKGROUND-002`; it contains only the three authorized implementation/test files. No main merge or main push was performed.

### Validation Results

- `npm run prisma:generate`: passed.
- Frozen regression file SHA-256: `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`; `git diff` for that file is empty.
- `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts`: passed, 146 tests (the task text's stated count is 98).
- `npm test -- tests/unit/services/billing-subscription-reconciliation/reconciliation-queue.service.test.ts`: passed, 6 tests.
- `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: passed, 10 tests.
- `npm run build`: passed; includes Prisma generation and TypeScript compilation.
- `git diff --check`: passed.
- `npm test`: failed (exit code 1); the latest run retained the previously reported full-suite failures under `ARCH025-BACKGROUND-TEST-001`, with no new task-specific failure reported. The same condition is not present in `docs/development-baseline.md`; per task instructions, the gate remains unmet and the issue is escalated rather than reclassified as an accepted baseline.

### Deviations

- Task status is `blocked`, not `review`, because the mandatory full-suite gate did not pass and the observed pre-existing failure condition has not been recorded in the development baseline.

### Assumptions

- The queue/reconstruction implementation is complete within the authorized three-file surface; no lifecycle retry policy or queue contract changes were introduced.

### Unresolved Issues

- `npm test` remains nonzero for the pre-existing failure set; `moda_architect` must determine the authorized next step under the task's stop condition.

### Architectural Concerns

- None identified in the queue extraction. No development-baseline entry was created or changed by this task.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
