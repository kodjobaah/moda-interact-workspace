---
id: ARCH-025-SHOPIFY-011
architecture_id: ARCH-025
title: Extract subscription synchronization coordinator
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 110
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-010
enables: []
created: 2026-10-01
updated: 2026-10-01
---

# Extract subscription synchronization coordinator

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the remaining `syncSubscription()` provider-to-local reconciliation workflow into `SubscriptionSyncService`, leaving `BillingService.syncSubscription()` as a thin compatibility delegate and completing the façade refactor.

## Context

This task is intentionally last. By now BillingPeriod projection, plan resolution, activation, notification and reads/commands all have stable owners. The remaining sync method can therefore become a coordinator instead of moving a 500+ line monolith intact.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-sync.service.ts              # new
tests/unit/services/billing/subscription-sync.service.test.ts  # new
```

Use collaborators from prior ARCH-025 tasks. Modify those prior collaborator files only if an unavoidable compile-level interface correction is required; if semantic changes are required, stop and return to `moda_architect` rather than broadening this task.

## Out of Scope

- redesigning subscription state machine.
- changing provider calls/contracts.
- changing plan/activation/notification semantics owned by prior tasks.
- changing routes.
- changing database schema.
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
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4` and all 127 tests must pass.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — thin façade

After this task:

```ts
BillingService.syncSubscription(...)
```

must delegate to `SubscriptionSyncService`; the façade method must not contain a full provider/transaction workflow.

### R2 — coordinator responsibilities

The extracted sync owner keeps the current high-level sequence and delegates established sub-capabilities:

```text
load Shop
read provider active subscription
no provider contract -> durable NO_CONTRACT projection -> post-commit ended-notification
active provider contract -> resolve/materialise operational plan
classify mapped/unmapped/sync-error status
initial Paid match -> delegate SHOPIFY-010 finalisation
normal current cycle -> use SHOPIFY-001 projection helper
persist Subscription projection/pending state/reconcile schedule
```

### R3 — preserve provider call count/order

Do not add duplicate provider reads. `getActiveSubscription` remains in the same high-level position and outside Prisma transactions.

### R4 — preserve all projection semantics

Preserve exactly:

```text
NO_CONTRACT clearing/preservation rules
initial activation intent preservation
unknown/inactive/invalid plan status/error mapping
current/pending plan mapping
FREE top-up reconcile scheduling
trial/cycle-null handling
BILLING_PERIOD_PLAN_CONFLICT handling
lastSyncedAt / lastSyncErrorCode / lastSyncErrorAt semantics
pending plan/effectiveAt semantics
```

### R5 — final façade shape

`billing.service.ts` should primarily contain dependency wiring, compatibility exports and thin method delegates. It must not duplicate logic now owned by collaborators.

### R6 — no opportunistic caller migration

Do not change existing routes/services to import collaborators directly. `BillingService` remains the supported application façade for this architecture.

## Work Items

- [ ] Create `SubscriptionSyncService` with provider, Prisma and prior collaborator dependencies.
- [ ] Move remaining sync orchestration and leave thin façade delegate.
- [ ] Add focused sync coordinator tests for no-contract, mapped/unmapped/error, pending-plan preservation, cycle-null, BillingPeriod conflict, Free scheduling and collaborator delegation.
- [ ] Remove now-dead duplicated private sync helpers/imports from the façade only when ownership has already moved.
- [ ] Verify final `billing.service.ts` contains no full provider/transaction workflow and all 15 public methods remain compatible.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

`SubscriptionSyncService` is repository-internal. It composes the existing `BillingProvider`, Prisma and prior ARCH-025 collaborators. No new Shared or queue contract.

## Dependencies

- `ARCH-025-SHOPIFY-010`

## Enables

None

## Acceptance Criteria

- [ ] `BillingService.syncSubscription()` is a thin delegate.
- [ ] Remaining sync orchestration has one owner and composes prior collaborators instead of duplicating them.
- [ ] Provider call ordering/count, transaction boundaries, statuses, errors, pending-state preservation and schedules are unchanged.
- [ ] All existing Shopify application callers continue importing the façade without modification.
- [ ] Frozen 127-test façade suite passes unchanged.
- [ ] Full repository test suite introduces no new failure.
- [ ] `billing.service.ts` is now a compatibility façade/coordinator rather than the owner of multiple full business workflows.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `sha256sum tests/unit/services/billing.service.test.ts` returns exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/subscription-sync.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-sync.service.ts tests/unit/services/billing/subscription-sync.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Implementation Notes

Do not pursue a line-count target mechanically. Completion is defined by responsibility ownership and delegation, not a specific final number of lines. Do not migrate callers to collaborators; that would be a separate architecture decision.

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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
