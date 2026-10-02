---
id: ARCH-025-BACKGROUND-001
architecture_id: ARCH-025
title: Extract pure subscription reconciliation classification
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-025-BACKGROUND-002
created: 2026-10-02
updated: 2026-10-02
---

# Extract pure subscription reconciliation classification

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the durable state/job classification and expected-CAS snapshot construction from `reconcileJob()` into a pure, exhaustively testable module without changing any I/O or lifecycle behaviour.

## Context

`reconcileJob()` currently embeds a large boolean state machine before any provider call. This logic determines stale-job rejection and which lifecycle owns the job, so extracting it first creates a stable, I/O-free decision boundary for all later handler tasks.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/classification.ts
tests/unit/services/billing-subscription-reconciliation/classification.test.ts
```

A directly adjacent pure types file is permitted only if required to keep `classification.ts` coherent.

## Out of Scope

- queue publication/reconstruction extraction.
- provider snapshot acquisition.
- lifecycle handlers or retry scheduling.
- current-plan database eligibility reads.
- worker/caller changes.
- edits to the frozen regression file.

## Requirements

### Common ARCH-025 Background invariants

- This is a **move-only structural refactor**. Do not change billing semantics, provider protocol, queue contract, queue/job identity, retry intervals, error codes, authorization, durable lifecycle state or external worker behaviour.
- Preserve the exact public compatibility surface from `src/services/billing-subscription-reconciliation.service.ts`: `BillingSubscriptionReconciliationService`, `billingSubscriptionReconciliationService`, `activateInitialPaid`, `enqueue`, `reconstruct`, `reconcileJob`, `InitialActivationPlan`, `FREE_CYCLE_DISCOVERY_RETRY_MS`, `ROLLOVER_RETRY_MS`, `nextSubscriptionReconcileAt`, `createSubscriptionReconcilePayload` and the `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` compatibility re-export.
- Preserve the positional constructor `(database, partner, queue, logger, now, runtimeConfig, discountQueue)`. Do not modify `src/entrypoints/billing.ts` or `src/services/billing-reconciliation.service.ts` to accommodate extraction.
- Extracted modules MUST NOT import `billing-subscription-reconciliation.service.ts`; dependency direction is coordinator -> collaborator. Symbols moved out of the coordinator file that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during construction.
- Capture exactly one `BackgroundRuntimeConfigSnapshot` per `reconcileJob()` invocation and pass that immutable snapshot to every downstream operation that currently consumes runtime configuration.
- Normal accepted queued reconciliation performs at most the current single `getSubscriptionReconciliationSnapshot(...)` provider call and reuses `activeSubscription` plus `latestLifecycleEvent`. Do not multiply provider calls while splitting handlers.
- Reinstall reconciliation remains on its distinct `partner.getActiveSubscription(...)` path; do not replace it with the normal reconciliation snapshot helper.
- Preserve all provider/network versus Prisma transaction boundaries, `SELECT ... FOR UPDATE` targets/order, `updateMany` CAS predicates, durable rereads and post-commit side-effect ordering exactly. Do not impose one global lock order across lifecycles where the current code uses different transaction shapes.
- Continue delegating canonical work to `SamePlanBillingPeriodRolloverService`, `ShopifyPlanChangeTransitionService`, `ShopifySubscriptionLifecycleReconciliationService`, `ensureCurrentBillingPeriodProjection`, `shopifyUsageEventPublisherService`, `shopifyDiscountCatalogueService` and `recoveryCapacityResumeService`; do not duplicate those implementations.
- Preserve the meaning and boundary of existing `billing.subscription_reconciliation.*` structured log events; use the canonical Shared logger and do not log whole provider/customer payloads.
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts` is frozen: do not edit it. SHA-256 must remain `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`, and all 98 tests must pass after every task.
- Add separate focused tests for the extracted owner. Do not move assertions out of the frozen regression file, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- `tests/unit/runtime/entrypoint-isolation.test.ts` must continue passing so the billing-worker construction/startup contract remains unchanged.
- Full `npm test` must pass. If execution reveals a pre-existing baseline condition, stop and report it to `moda_architect` unless it is already durably documented in `docs/development-baseline.md`; do not silently redefine the baseline inside this task.

### R1 — pure classification contract

Create `src/services/billing-subscription-reconciliation/classification.ts` as a pure module. It may depend on shared/Prisma enums and plain data types, but it MUST NOT access Prisma, queues, Shopify/provider APIs, logging, clocks or runtime config.

The classifier consumes the already-loaded durable row plus parsed queue job and returns a discriminated result representing either the exact accepted reconciliation kind/expected CAS snapshot or an exact skip result.

Accepted kind strings remain:

```text
reinstall
initial-activation
cycle-discovery
rollover
established-plan-change
frozen-reconciliation
```

### R2 — preserve decision order and skip evidence

Preserve the current evaluation order and skip reason strings so structurally identical input still emits the same `job_skipped` reason/fields. In particular preserve:

```text
missing-shop-subscription-or-shopify-id
uninstalled-reconciliation-not-due
subscription-id-mismatch
stale-next-reconcile-at
shop-not-active
next-reconcile-at-cleared
subscription-state-ineligible
```

Reinstall eligibility remains evaluated before the normal ACTIVE-shop state machine. Do not make UNINSTALLED work pass through ACTIVE-only classification.

### R3 — expected snapshot types

Move the current internal expected-state types (`InitialActivationExpected`, `FreeCycleExpected`, `RolloverExpected`, `EstablishedPlanChangeExpected`, `ReinstallExpected`) into the pure classification boundary or a directly adjacent pure type module. Preserve the exact fields used by current CAS predicates.

Move the current pure `sameDate(left, right)` equality helper with these reconciliation-state primitives and preserve its null/date semantics. Later activation and reinstall handlers must reuse this helper rather than duplicate date-equality rules.

The established-plan-change retryable SYNC_ERROR set remains exactly:

```text
UNEXPECTED_IMMEDIATE_PLAN_CHANGE
MISSING_BILLING_CYCLE
MISSING_USAGE_METER
INVALID_INCLUDED_ALLOWANCE
```

Expose that repository-internal constant from the pure module so BACKGROUND-006 reuses the same definition rather than duplicating it.

### R4 — preserve post-classification plan gates

Current-plan database eligibility checks for cycle discovery/rollover occur after state classification because they require a BillingPlan read. Do not pull those I/O checks into the pure classifier in this task.

## Work Items

- [ ] Add the pure classification module and discriminated result/expected snapshot types.
- [ ] Replace the boolean classification block in `reconcileJob()` with the pure classifier while leaving subsequent plan/provider/lifecycle work in place.
- [ ] Preserve exact accepted `kind` values and skipped reason/field logging.
- [ ] Add exhaustive focused tests for every accepted kind plus every current skip reason and stale schedule/subscription fence.
- [ ] Prove classifier tests perform no database/provider/queue work.
- [ ] Prove the frozen 98-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Repository-internal pure contract only. `BillingSubscriptionReconciliationService` remains the public façade/coordinator and translates classification results into the same current log/provider/handler flow.

## Dependencies

None

## Enables

- `ARCH-025-BACKGROUND-002`

## Acceptance Criteria

- [ ] Reconciliation kind selection is owned by a pure module with no I/O.
- [ ] Reinstall, initial activation, cycle discovery, rollover, established plan change, frozen and skip outcomes match current behaviour exactly.
- [ ] All current skip reason strings and decision precedence remain unchanged.
- [ ] Retryable established-plan-change SYNC_ERROR classification uses one shared pure constant.
- [ ] No provider/database call count or transaction boundary changes.
- [ ] Frozen regression suite remains byte-identical and all 98 tests pass.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [ ] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 98 frozen regression tests
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation/classification.test.ts` passes
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
