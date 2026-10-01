---
id: ARCH-025-SHOPIFY-006
architecture_id: ARCH-025
title: Extract initial subscription activation workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-005
enables:
  - ARCH-025-SHOPIFY-007
created: 2026-10-01
updated: 2026-10-01
---

# Extract initial subscription activation workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the existing initial Free/Paid activation intent and guarded Free completion/retry scheduling workflow into `SubscriptionActivationService`, while leaving initial Paid durable finalisation inside `syncSubscription()` until SHOPIFY-010.

## Context

The façade currently owns four activation-oriented public methods plus token matching and lock helpers. They share the same pending-selection lifecycle. Pulling them behind one service reduces the façade while keeping the higher-risk initial Paid final commit separate for a later bounded task.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-activation.service.ts              # new
tests/unit/services/billing/subscription-activation.service.test.ts  # new
```

Consume SHOPIFY-002 BillingPlan resolution/top-up configuration.

## Out of Scope

- The initial Paid durable commit branch currently inside `syncSubscription()` (SHOPIFY-010).
- hosted plan-change callback flow.
- normal sync projection.
- route callback changes.
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

### R1 — move exact activation methods

Move implementation ownership for:

```text
prepareFreeActivation
preparePaidActivation
scheduleInitialFreeReconciliationIfCurrent
completeFreeActivation
```

plus token matching and current `ShopSettings -> Subscription` activation lock helper.

### R2 — preserve public compatibility symbols

The following remain exported from `billing.service.ts` with the same shapes/values through re-export if moved:

```text
INITIAL_BILLING_RETRY_DELAY_MS
InitialFreeActivationToken
InitialPaidActivationToken
FreeActivationResult
CompletedFreeActivation
```

### R3 — preserve locking/CAS

Keep exact lock order:

```text
ShopSettings FOR UPDATE
Subscription FOR UPDATE
```

and the exact activation-token identity fields. A stale token remains a no-op.

### R4 — preserve plan resolution and completion schedule

Use SHOPIFY-002 resolution rather than duplicating plan validation. Preserve current Free top-up configuration handling and drain-window/retry scheduling.

### R5 — do not move Paid finalisation yet

`preparePaidActivation` still only establishes the durable pending selection. SHOPIFY-010 later owns the special `syncSubscription()` Paid finalisation branch.

## Work Items

- [ ] Create `SubscriptionActivationService` and move four public workflow implementations + token/lock helpers.
- [ ] Re-export moved compatibility types/constants from `billing.service.ts`.
- [ ] Leave façade methods as same-signature delegates.
- [ ] Add focused tests for initial/replay Free, initial Paid intent, stale-token no-op, guarded Partner-error retry, lock order and Free completion scheduling.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

Internal service consumes `BillingPlanResolutionService` and Prisma. Public activation types/constants stay available from the compatibility façade module.

## Dependencies

- `ARCH-025-SHOPIFY-005`

## Enables

- `ARCH-025-SHOPIFY-007`

## Acceptance Criteria

- [ ] Four activation public methods delegate to `SubscriptionActivationService`.
- [ ] Current activation lock order/token fencing and scheduling are unchanged.
- [ ] Initial Paid final durable commit remains in `syncSubscription()` after this task.
- [ ] Existing callback imports require no migration.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `sha256sum tests/unit/services/billing.service.test.ts` returns exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/subscription-activation.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-activation.service.ts tests/unit/services/billing/subscription-activation.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Implementation Notes

Do not rename public activation methods. Avoid designing a generic state-machine framework; this is extraction of the current pending-selection lifecycle.

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
