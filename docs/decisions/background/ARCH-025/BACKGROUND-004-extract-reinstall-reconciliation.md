---
id: ARCH-025-BACKGROUND-004
architecture_id: ARCH-025
title: Extract reinstall reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-BACKGROUND-003
enables:
  - ARCH-025-BACKGROUND-005
created: 2026-10-02
updated: 2026-10-03
---

# Extract reinstall reconciliation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the complete UNINSTALLED reinstall lifecycle into a dedicated handler while preserving its distinct provider call, authority fencing, transaction shapes, canonical rollover/projection reuse and post-commit side effects.

## Context

Reinstall is a separate lifecycle with different authority and provider semantics from ordinary ACTIVE-shop reconciliation. Keeping it as an explicit handler prevents the final coordinator from conflating reinstall with the one-snapshot normal path.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts
tests/unit/services/billing-subscription-reconciliation/reinstall-reconciliation.service.test.ts
```

BACKGROUND-001 through BACKGROUND-003 internal modules may be consumed but not behaviourally broadened.

## Out of Scope

- replacing reinstall with normal lifecycle snapshot processing.
- refactoring `SamePlanBillingPeriodRolloverService` or `ensureCurrentBillingPeriodProjection`.
- deleting dead/unreferenced helpers as cleanup.
- worker/caller changes.
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

### R1 — move the complete reinstall cluster

Create `reinstall-reconciliation.service.ts` and move:

```text
reconcileReinstall
completeReinstallWithoutContract
completeReinstallFree
completeReinstallPaid
activateReinstallPaid
activateReinstallAfterRollover
recordReinstallProviderFailure
recordReinstallBlocked
isReinstallAuthority
```

`activateReinstallAfterRollover` currently has no callsite; move it unchanged rather than deleting or repurposing it as incidental cleanup.

### R2 — preserve the distinct provider path

Reinstall continues to call `partner.getActiveSubscription(shopifyShopId)` exactly once after the coordinator has accepted the exact UNINSTALLED marker/schedule. It MUST NOT call `getSubscriptionReconciliationSnapshot(...)`, lifecycle replay, or make an additional Partner API call.

### R3 — preserve each current transaction/lock shape

Do not normalise reinstall locks. Preserve the exact existing shapes, including:

- no-contract and Free/same-cycle Paid activation: `Shop -> ShopSettings -> Subscription` before authority reread;
- later-cycle Paid transition: existing Shop lock/authority check followed by `SamePlanBillingPeriodRolloverService.transitionInTransaction(...)` in the same transaction;
- `activateReinstallAfterRollover`'s current `ShopSettings -> Subscription` shape.

Before choosing same-cycle versus later-cycle Paid handling, preserve the current **non-transactional** `database.subscription.findUnique(...)` alignment read in `completeReinstallPaid(...)`; do not move it under a lock/transaction or eliminate it as redundant during extraction.

`isReinstallAuthority` must continue rereading both Shop status/marker and Subscription schedule inside the current transaction boundary.

### R4 — preserve exact plan/provider validation

Keep current behaviour for inactive/unmapped plan, unsupported kind, missing usage meter, period alignment, exact Paid period/counter replay, Free pack-cycle projection conflicts and provider-cycle lag.

### R5 — no-contract discount catalogue state is part of the transaction

The existing no-contract reinstall transaction's discount-catalogue UNAVAILABLE/updateMany writes remain in that transaction and are not replaced by the post-commit discount-sync publisher.

### R6 — retry and post-commit semantics

Provider transport failure uses the existing tiered `nextSubscriptionReconcileAt(reinstallPendingAt, now)` policy. Blocked reinstall remains terminal (`nextReconcileAt: null`). Successful Free/Paid reinstall keeps current post-commit discount sync and durable next-job publication behaviour.

## Work Items

- [ ] Add the reinstall reconciliation service and move the full reinstall method cluster including the currently unreferenced helper.
- [ ] Delegate the UNINSTALLED accepted branch from the coordinator without changing its pre-provider stale/authority checks.
- [ ] Reuse BACKGROUND-003 timing, lock, queue and discount collaborators.
- [ ] Continue using `ensureCurrentBillingPeriodProjection` and `SamePlanBillingPeriodRolloverService` rather than reimplementing them.
- [ ] Add focused tests for no-contract, Free, exact Paid, later-cycle Paid, stale reinstall marker, provider failure, terminal blocked states, lock order and post-commit queue/discount failure.
- [ ] Prove exactly one `getActiveSubscription` call and zero normal reconciliation snapshot calls on reinstall paths.
- [ ] Prove the frozen 146-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal reinstall service consumes the database, Partner provider, queue/timing/locking/discount collaborators, logger and clock. Coordinator remains responsible for initial job parse/context/classification and invokes reinstall only after the existing UNINSTALLED job identity/schedule fence passes.

## Dependencies

- `ARCH-025-BACKGROUND-003`

## Enables

- `ARCH-025-BACKGROUND-005`

## Acceptance Criteria

- [ ] All reinstall implementation is owned by the extracted service and coordinator only delegates accepted reinstall work.
- [ ] Reinstall still uses one direct active-subscription provider call and no normal reconciliation snapshot call.
- [ ] Existing transaction shapes, authority rereads, period/counter validation and no-contract discount writes are unchanged.
- [ ] Existing retry/blocked/error/log/post-commit behaviours are unchanged.
- [ ] Existing rollover/projection services remain canonical owners.
- [ ] Frozen regression suite remains byte-identical and all 146 tests pass.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [ ] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 146 frozen regression tests
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation/reinstall-reconciliation.service.test.ts` passes
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
