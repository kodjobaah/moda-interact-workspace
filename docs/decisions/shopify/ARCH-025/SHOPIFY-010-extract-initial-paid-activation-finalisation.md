---
id: ARCH-025-SHOPIFY-010
architecture_id: ARCH-025
title: Extract initial Paid activation finalisation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-009
enables:
  - ARCH-025-SHOPIFY-011
created: 2026-10-01
updated: 2026-10-01
---

# Extract initial Paid activation finalisation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Move only the special initial Paid durable finalisation branch out of `syncSubscription()` into the existing `SubscriptionActivationService`, preserving its strict Shop lock, exact pending-token/cycle/configuration validation and atomic entitlement creation.

## Context

After SHOPIFY-006, activation intent/retry/Free completion already has one owner, but `syncSubscription()` still contains the higher-risk initial Paid final commit. Extracting that branch separately before the general sync coordinator keeps the final task bounded and places all initial activation semantics together.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-activation.service.ts
tests/unit/services/billing/subscription-activation.service.test.ts
```

No new service file is required unless implementation demonstrates a concrete cycle dependency; default is to extend the existing activation service.

## Out of Scope

- normal provider-to-local sync branches.
- changing Paid activation rules or configuration requirements.
- modifying provider API calls.
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

### R1 — exact branch boundary

Move the branch currently selected when an `expectedInitialSelection` for `PAID_METERED` matches the provider result and the durable pending initial intent. The remaining `syncSubscription()` detects/dispatches; activation service owns the transaction.

### R2 — preserve Shop lock and durable reread

Keep the existing `shopify.Shop FOR UPDATE` lock before accepting initial Paid status and retain all current durable rereads/identity checks.

### R3 — preserve fail-closed validations

Keep current behaviour for:

```text
missing/mismatched pending plan identity
missing provider cycle
Paid trial
missing/invalid included allowance
missing required provider usage meter
inactive/mismatched plan
existing conflicting/closed BillingPeriod
included counter conflicts
invalid lifetime-Free policy
```

The same current `SYNC_ERROR`/`lastSyncErrorCode` results and no-write/conflict semantics must remain.

### R4 — preserve atomic success commit

Successful finalisation must still atomically create/reuse the exact BillingPeriod, included counter and lifetime-Free counter as currently required, clear the pending selection, set ACTIVE projection fields and set the exact drain-window `nextReconcileAt`.

### R5 — no provider work inside activation transaction

The service receives already obtained provider subscription evidence; it must not perform a new Shopify call.

## Work Items

- [ ] Extend `SubscriptionActivationService` with one bounded initial-Paid finalisation method.
- [ ] Move only the identified transaction branch from `syncSubscription()` and delegate to it.
- [ ] Extend focused activation tests for exact successful period/counters, Shop lock, all fail-closed cases, replay preservation and drain-window schedule.
- [ ] Prove no additional provider/database work was introduced around the branch.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

Internal activation method accepts the already resolved provider Subscription evidence plus the expected activation token/current plan dependencies necessary to execute the existing transaction. Do not expose it to routes.

## Dependencies

- `ARCH-025-SHOPIFY-009`

## Enables

- `ARCH-025-SHOPIFY-011`

## Acceptance Criteria

- [ ] Initial Paid finalisation no longer lives as a full transaction implementation inside `syncSubscription()`.
- [ ] All strict initial Paid validation/lock/entitlement semantics are unchanged.
- [ ] Activation service performs no provider call.
- [ ] `syncSubscription()` still exposes exactly the same public behaviour.
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

Do not use SHOPIFY-001 generic BillingPeriod projection to weaken the stricter initial-Paid acceptance rules. Reuse lower-level helpers only when they preserve the existing exact validation and lock semantics.

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
