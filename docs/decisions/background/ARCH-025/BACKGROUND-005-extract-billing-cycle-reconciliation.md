---
id: ARCH-025-BACKGROUND-005
architecture_id: ARCH-025
title: Extract billing-cycle reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-BACKGROUND-004
enables:
  - ARCH-025-BACKGROUND-006
created: 2026-10-02
updated: 2026-10-02
---

# Extract billing-cycle reconciliation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract Free cycle discovery, current-cycle pending/cancellation projection, pre-close usage flushing and same-plan rollover into one lifecycle handler while reusing the existing canonical projection and rollover services.

## Context

The cycle paths share period-boundary timing and source-projection CAS semantics and currently occupy both private methods and a substantial inline `reconcileJob()` branch. Moving them together removes a full lifecycle engine without inventing a generic retry service.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/billing-cycle-reconciliation.service.ts
tests/unit/services/billing-subscription-reconciliation/billing-cycle-reconciliation.service.test.ts
```

Earlier ARCH-025 Background collaborators are consumable dependencies.

## Out of Scope

- modifying canonical rollover/projection/usage publisher services.
- established plan-change logic.
- provider snapshot acquisition/lifecycle replay.
- retry interval changes.
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

### R1 — one billing-cycle owner

Create `billing-cycle-reconciliation.service.ts` and move the complete cycle/pre-close cluster:

```text
recordMissingCycle
recordCycleDiscoveryFailure
reconcileRollover
recordRolloverRetry
reconcilePreClose
reconcileFreeCycle
```

Also move the substantial inline `reconcileJob()` branch that refreshes provider `pendingPlanHandle` / scheduled cancellation truth for an unchanged current cycle and performs the in-drain-window usage flush/CAS scheduling.

### R2 — preserve handler ordering

For rollover jobs preserve the current order after lifecycle replay:

1. if provider reports same current cycle with pending plan/cancellation/reversal, project that provider truth and, when inside the drain window, attempt usage flush;
2. otherwise, if durable period end is still in the future, run pre-close reconciliation;
3. only after that current pre-close opportunity, apply provider-null rollover retry when applicable;
4. at/after boundary, delegate same-plan transition to `SamePlanBillingPeriodRolloverService`.

Do not reorder provider-null handling ahead of pre-close work.

### R3 — runtime snapshot reuse

`shopifyUsageEventPublisherService.publishDue(...)` must receive the exact immutable `BackgroundRuntimeConfigSnapshot` captured once by the coordinator. The cycle handler must not call `backgroundRuntimeConfigService.current()` itself.

### R4 — canonical owners remain canonical

Same-plan period mutation remains in `SamePlanBillingPeriodRolloverService`; current-period creation/repair remains in `ensureCurrentBillingPeriodProjection`. Do not copy their transactions into the new handler.

### R5 — exact timing/CAS/error behaviour

Preserve:

- Free cycle discovery retry = `FREE_CYCLE_DISCOVERY_RETRY_MS`;
- rollover/provider-cycle retry = `ROLLOVER_RETRY_MS`;
- exact drain boundary `periodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS`;
- final-minute retry capped at exact period end;
- exact source projection CAS fields for pre-close/current-cycle updates;
- clearing only `PRE_CLOSE_USAGE_FLUSH_FAILED` after successful exact-cycle drain retry;
- preserving unrelated sync errors;
- current `PROVIDER_CYCLE_LAG`, `MISSING_BILLING_CYCLE`, `BILLING_PERIOD_PLAN_CONFLICT` and usage-publish failure semantics.

### R6 — recovery-capacity resume remains best effort

Paid same-plan transition continues to schedule `recoveryCapacityResumeService` with trigger `billing-period-rollover` through the current callback/best-effort logging boundary. Its failure must not roll back the committed rollover.

## Work Items

- [ ] Add the billing-cycle reconciliation service.
- [ ] Move cycle discovery, current-cycle pending/cancel projection, pre-close flush, same-plan rollover and their failure/retry helpers.
- [ ] Pass the one captured runtime-config snapshot into every usage-publish call.
- [ ] Reuse queue/timing collaborators and existing canonical projection/rollover services.
- [ ] Add focused tests for cycle discovery, pack-enabled Free exact projection, pending/cancellation projection, before/inside drain window, pre-close failure/retry/error clearing, provider null/lag, same-plan rollover and capacity-resume isolation.
- [ ] Prove no provider call is made by the handler itself; it consumes the coordinator's snapshot result.
- [ ] Prove the frozen 98-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal cycle handler receives already-loaded current plan/provider evidence, exact expected snapshot, captured runtime config, persisted cancellation state and repository dependencies. It performs no Shopify provider fetch.

## Dependencies

- `ARCH-025-BACKGROUND-004`

## Enables

- `ARCH-025-BACKGROUND-006`

## Acceptance Criteria

- [ ] Cycle/pre-close/rollover implementation no longer lives in `reconcileJob()` or coordinator private methods.
- [ ] Current provider-truth projection and pre-close ordering are identical to the source baseline.
- [ ] Exactly one coordinator-captured runtime config is reused for usage publishing.
- [ ] Existing canonical rollover/projection services own durable period transitions.
- [ ] Exact timing, CAS, error clearing and best-effort capacity-resume semantics remain unchanged.
- [ ] Frozen regression suite remains byte-identical and all 98 tests pass.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [ ] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 98 frozen regression tests
- [ ] `npm test -- tests/unit/services/billing-subscription-reconciliation/billing-cycle-reconciliation.service.test.ts` passes
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
