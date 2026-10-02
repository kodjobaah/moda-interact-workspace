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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-10-02T23:48:05Z
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-002
enables:
  - ARCH-025-BACKGROUND-004
created: 2026-10-02
updated: 2026-10-02
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

- [ ] Add the initial activation reconciliation service.
- [ ] Add pure reconciliation timing support and compatibility re-exports.
- [ ] Add exact shared lock helpers and wire initial activation to `ShopSettings -> Subscription` only.
- [ ] Add the shared discount-sync publisher with existing best-effort semantics.
- [ ] Move the complete initial activation helper cluster while retaining the shared final provider-plan lookup/branch dispatch in the coordinator.
- [ ] Keep public `activateInitialPaid(...)` as a no-provider-call compatibility delegate.
- [ ] Add focused initial-activation tests for tiered retry expiry, stale CAS, Free activation, Paid activation, alternate current plan, all fail-closed errors, projection/counter replay, post-commit queue/discount failures, and FROZEN-shaped calls to `recordMissingSubscription`/`applyOtherCurrentPlan` that remain non-throwing/no-op against non-NO_CONTRACT durable state.
- [ ] Add direct focused tests for `reconciliation-timing.ts`, exact lock SQL/order primitives and the discount-sync publisher rather than relying only on façade regression coverage for those newly extracted owners.
- [ ] Prove the frozen 146-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal initial-activation service receives the database, queue publisher, discount publisher, logger/clock and already-obtained provider evidence. It exposes only repository-internal operations needed by the coordinator dispatch, including the exact `applyOtherCurrentPlan` fallthrough operation. Public `InitialActivationPlan`, retry constants/helper and `activateInitialPaid` remain compatible through the façade file.

## Dependencies

- `ARCH-025-BACKGROUND-002`

## Enables

- `ARCH-025-BACKGROUND-004`

## Acceptance Criteria

- [ ] Initial activation transaction/retry logic no longer lives in the coordinator.
- [ ] Direct and queued initial-Paid paths preserve current signatures and perform no extra provider/plan reads.
- [ ] Existing Free/Paid/other-current-plan error codes, period/counter semantics and post-commit scheduling are unchanged.
- [ ] Shared lock SQL and pure timing helpers have one owner without becoming generic orchestration frameworks.
- [ ] Discount sync remains post-commit/best-effort and uses the existing queue contract.
- [ ] Frozen regression suite remains byte-identical and all 146 tests pass.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [ ] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 146 frozen regression tests
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.test.ts` passes
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
