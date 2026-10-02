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
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
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
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts` is frozen: do not edit it. SHA-256 must remain `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`, and all 98 tests must pass after every task.
- Add separate focused tests for the extracted owner. Do not move assertions out of the frozen regression file, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- `tests/unit/runtime/entrypoint-isolation.test.ts` must continue passing so the billing-worker construction/startup contract remains unchanged.
- Full `npm test` must pass. If execution reveals a pre-existing baseline condition, stop and report it to `moda_architect` unless it is already durably documented in `docs/development-baseline.md`; do not silently redefine the baseline inside this task.

### R1 — deterministic queue publisher

Create `reconciliation-queue.service.ts` owning the existing subscription-reconcile queue mechanics. Move the implementation of `enqueue(...)`, `publishNext(...)` and `publishCommittedLifecycleSchedule(...)` without changing:

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

- [ ] Add the queue/reconstruction collaborator.
- [ ] Move `enqueue`, `publishNext`, `publishCommittedLifecycleSchedule` and `reconstruct` behind it with exact current semantics.
- [ ] Keep public `enqueue`/`reconstruct` façade delegates and `createSubscriptionReconcilePayload` compatibility export.
- [ ] Route coordinator/later-handler publication through the collaborator without changing queue call count/options.
- [ ] Add focused queue/reconstruction tests for deterministic IDs, overdue/future delay, public no-queue no-op, no-queue reconstruction count semantics, reconstruction predicate coverage and enqueue-failure isolation.
- [ ] Prove the frozen 98-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal queue collaborator. Public `BillingSubscriptionReconciliationService.enqueue()` and `.reconstruct()` remain delegates. `createSubscriptionReconcilePayload` remains import-compatible from the façade file.

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
- [ ] Frozen regression suite remains byte-identical and all 98 tests pass.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [ ] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 98 frozen regression tests
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation/reconciliation-queue.service.test.ts` passes
- [ ] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [ ] `npm test` passes with no regression
- [ ] `npm run build` succeeds
- [ ] `git diff --check` passes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
