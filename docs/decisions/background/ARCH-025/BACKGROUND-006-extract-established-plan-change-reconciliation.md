---
id: ARCH-025-BACKGROUND-006
architecture_id: ARCH-025
title: Extract established plan-change reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-BACKGROUND-005
enables:
  - ARCH-025-BACKGROUND-007
created: 2026-10-02
updated: 2026-10-02
---

# Extract established plan-change reconciliation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract established active/trialing/retryable-SYNC_ERROR plan-change convergence into one handler while preserving its exact CAS predicates, validation/failure policy and canonical `ShopifyPlanChangeTransitionService` delegation.

## Context

After cycle/reinstall/activation extraction, established plan changes are the last substantial lifecycle engine still owned by the coordinator. Isolating them leaves `reconcileJob()` ready to become a bounded parse/context/provider/delegate coordinator.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.ts
tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts
```

Earlier ARCH-025 Background collaborators are consumable dependencies.

## Out of Scope

- modifying `ShopifyPlanChangeTransitionService`.
- changing provider snapshot acquisition.
- cycle/reinstall/activation behaviour.
- retry interval/error-code changes.
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

### R1 — move the complete established plan-change cluster

Create `established-plan-change-reconciliation.service.ts` and move:

```text
reconcileEstablishedPlanChange
establishedPlanChangeWhere
nextPlanReconcileAt
recordEstablishedPlanChangeFailure
recordEstablishedPlanChangeRetry
schedulePlanChangeCapacityResume
```

Keep the existing BillingPlan lookup for `provider.planHandle` in the coordinator/final provider-plan dispatch through BACKGROUND-007 and pass its result into this handler as `targetPlan`. Do not duplicate, remove or conditionally skip that lookup on branches where the source currently performs it. The handler retains the separate provider-`pendingPlanHandle` lookup inside the `providerIsCurrent` branch exactly as today.

### R2 — reuse shared retryable-status definition

Consume BACKGROUND-001's single retryable established-plan-change SYNC_ERROR set in both classification and `establishedPlanChangeWhere(...)`. Do not maintain a second local copy.

### R3 — provider/current/pending decision semantics

Preserve all current branches:

- provider remains on current plan -> refresh/clear pending provider projection and schedule pending effective/pre-close as today;
- provider is pending target on same cycle -> fail closed with `UNEXPECTED_IMMEDIATE_PLAN_CHANGE`;
- target appears before effective time -> reschedule exact pending effective time;
- target at/after effective time -> validate cycle/allowance/meters and delegate to `ShopifyPlanChangeTransitionService`;
- unmapped provider handle -> current UNMAPPED terminal behaviour;
- other unexpected provider plan -> current SYNC_ERROR retry behaviour.

### R4 — failure/retry policy remains lifecycle-owned

Preserve 60-second `ROLLOVER_RETRY_MS` behaviour for retryable failures, fail-closed status transitions, observed-handle updates and `PROVIDER_STATE_UNRESOLVED` / `PARTNER_API_ERROR` distinctions. The queue collaborator only publishes the chosen next time.

### R5 — canonical transition/capacity side effect

Durable plan transition remains owned by `ShopifyPlanChangeTransitionService`. On a successful transition, preserve exact next-job publication and best-effort `recoveryCapacityResumeService.schedule({ trigger: "plan-change" })`; enqueue failure remains warning-only after the committed transition.

### R6 — no provider fetch inside handler

The handler consumes the one provider snapshot already acquired by the coordinator and performs no Partner API call.

## Work Items

- [ ] Add the established plan-change reconciliation service and move the full method cluster.
- [ ] Consume the coordinator-provided provider-handle plan lookup result and preserve the separate pending-handle lookup on the provider-current branch without adding/removing reads.
- [ ] Reuse the BACKGROUND-001 retryable error set and BACKGROUND-003 timing/BACKGROUND-002 queue collaborators.
- [ ] Continue delegating durable transitions to `ShopifyPlanChangeTransitionService`.
- [ ] Add focused tests for provider-current refresh/withdrawal, exact drain/effective scheduling, same-cycle immediate change, missing cycle/meter/allowance, provider null/error retry, unmapped/unexpected plan and capacity-resume failure isolation.
- [ ] Prove handler performs zero provider API calls.
- [ ] Prove the frozen 98-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal handler receives expected durable plan-change snapshot, current plan, provider evidence, queue/timing/logger/clock dependencies and database. It does not fetch Shopify provider state.

## Dependencies

- `ARCH-025-BACKGROUND-005`

## Enables

- `ARCH-025-BACKGROUND-007`

## Acceptance Criteria

- [ ] Established plan-change implementation has one dedicated owner and no duplicate retryable-error set.
- [ ] Provider-current, early target, valid transition, unmapped and fail-closed/retry branches are behaviourally unchanged.
- [ ] `ShopifyPlanChangeTransitionService` remains the durable transition owner.
- [ ] Capacity resume remains post-transition/best-effort.
- [ ] The exact source BillingPlan lookup sequence is preserved: current-plan-by-id upstream, one provider-handle lookup in the final coordinator dispatch, and the existing pending-handle lookup only when `providerIsCurrent` requires it.
- [ ] Frozen regression suite remains byte-identical and all 98 tests pass.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [ ] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 98 frozen regression tests
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts` passes
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
