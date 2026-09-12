---
id: ARCH-010-SHOPIFY-023
architecture_id: ARCH-010
title: Conform Shopify billing runtime to the clean first-production baseline
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 9
executor: copilot
claimed_at: '2026-09-12T22:27:01Z'
attempt: 1
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-SHOPIFY-002
enables:
- ARCH-010-SHOPIFY-003
- ARCH-010-SHOPIFY-009
- ARCH-010-SHOPIFY-018
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-023: Conform Shopify billing runtime to the clean first-production baseline

## Architecture

Read first:

```text
docs/architecture/ARCH-010-first-production-baseline.md
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
docs/architecture/ARCH-010-promotional-campaigns.md
```

`ARCH-010-SHOPIFY-002` remains the immutable accepted/in-review implementation history for its attempt. This task exists because the first-production baseline deliberately removes compatibility schema that the current Shopify billing service still consumes.

## Objective

Make the merchant-facing Shopify billing runtime use only the clean ARCH-010 first-production schema/Shared contract before downstream paid-plan, capacity and provider-lifecycle tasks build on it.

## Context

Current inspected billing code contains development-era behaviour including:

```text
EntitlementCounter.FREE_RECOVERY_LIFETIME
raw SQL literal 'FREE_RECOVERY_LIFETIME'
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment aggregation
```

Those symbols are intentionally removed by DATABASE-013. The runtime must not replace them with compatibility fallbacks.

## Scope

Inspect the current implementation before editing, especially:

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/**
app/components/dashboard/**billing**
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
```

Search the entire Shopify repository source/tests for every removed baseline symbol listed below and update only code required for clean-baseline conformance.

## Out of Scope

Do not:

- implement SHOPIFY-003/004/006/007/009/018 or other downstream tasks;
- change database schema;
- create compatibility aliases or backfill reads;
- implement Admin behaviour;
- implement background reservation/admission logic;
- add a local subscription-cancellation workflow;
- reopen or rewrite SHOPIFY-002 history.

## Requirements

### 1. Canonical lifetime-Free state

All current lifetime-Free reads/writes use:

```text
EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS
ShopEntitlementCounter.grantedQuantity
ShopEntitlementCounter.committedQuantity
ShopEntitlementCounter.reservedQuantity
```

Remove every runtime/test/raw-SQL reference to:

```text
FREE_RECOVERY_LIFETIME
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_ALLOWANCE_ADJUSTED
```

There is no legacy adjustment query and no fallback to a plan-owned allowance.

### 2. Merchant billing state is plan-independent for lifetime-Free capacity

Where the existing billing service returns lifetime-Free capacity, calculate it only from the durable shop lifetime counter:

```text
available = max(grantedQuantity - committedQuantity - reservedQuantity, 0)
```

That counter is a shop-lifetime entitlement and remains visible/usable under both mapped Free and mapped Paid subscriptions according to downstream admission order.

Do not make the lifetime counter conditional on the current plan being Free.

Do not create/increment the grant in read-model code; first verified activation ownership remains with the background activation workflow.

### 3. Preserve first verified activation semantics

Any SHOPIFY-002 activation/onboarding path touched by this task must continue to establish only the canonical activation/reconciliation intent defined by accepted architecture. Do not reintroduce plan-owned lifetime allowance inputs.

If SHOPIFY-002 currently writes/initialises a removed field directly, replace only that use with the final baseline contract required by the existing accepted behaviour; do not broaden scope into downstream background work.

### 4. Remove old local cancellation contract usage if present

Search source/tests for:

```text
appSubscriptionCancel
SubscriptionCancellationRequest
SubscriptionCancellationMode
SubscriptionCancellationStatus
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
```

The earlier inspection found no current `appSubscriptionCancel` runtime in the Shopify repository. Preserve that architecture. If stale types/tests remain, remove them; do not create a substitute local cancellation mutation.

### 5. Remove refund/promotion compatibility only where current runtime references it

If current Shopify source/tests still depend on:

```text
RecoveryCreditPurchaseStatus.REFUNDED
CURRENT_CYCLE_APP_EVENT_CORRECTION
PROMOTIONAL_RECOVERY_CREDITS
campaign-less direct PromotionalCreditGrant
```

remove those compatibility assumptions and target DATABASE-013's final model.

Do **not** implement the downstream top-up/refund/promotion UI tasks in this correction task.


### 6. Remove Free-only exhaustion message compatibility

The supplied Shopify runtime still contains `BILLING_FREE_ALLOWANCE_EXHAUSTED` UI action/test handling. SHARED-007 removes that development-only code. Delete the obsolete handler/test branch and use only the generic `BILLING_RECOVERY_CAPACITY_EXHAUSTED` contract for first-production full-capacity exhaustion.

### 7. Shared contract

Consume the package published by SHARED-008. Do not maintain a local copy of a removed cancellation or billing compatibility schema.

### 8. No compatibility substitute

Do not introduce:

- optional legacy plan allowance properties;
- local duplicate entitlement enums;
- dual-read code;
- migration-version detection;
- signed legacy adjustment arithmetic;
- raw SQL using removed enum literals.

If an accepted merchant behaviour cannot be represented by DATABASE-013/SHARED-008, STOP and report the exact architecture gap.

## Work Items

- [ ] Verify DATABASE-013 and SHARED-008 are Complete and available to the task worktree.
- [ ] Verify SHOPIFY-002 is architect-accepted Complete before claiming this task.
- [ ] Search source/tests for all removed baseline symbols.
- [ ] Replace lifetime-Free enum/raw SQL with `LIFETIME_FREE_RECOVERY_CREDITS`.
- [ ] Delete plan allowance and signed adjustment reads from merchant billing state.
- [ ] Make lifetime-Free read model independent of current Free/Paid plan type.
- [ ] Remove any remaining local cancellation compatibility if present.
- [ ] Remove only directly encountered obsolete refund/promotion compatibility.
- [ ] Remove `BILLING_FREE_ALLOWANCE_EXHAUSTED` handler/test compatibility and retain the generic exhaustion code.
- [ ] Add/update focused regression tests.
- [ ] Run repository-declared validation.

## Interfaces / Contracts

Consumes:

```text
DATABASE-013 final Prisma baseline
@modainteract/moda-interact-shared release published by SHARED-008
```

Canonical lifetime entitlement:

```text
EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS
```

No new cross-service contract is introduced.

## Dependencies

- `ARCH-010-DATABASE-013`
- `ARCH-010-SHARED-008`
- `ARCH-010-SHOPIFY-002`

## Enables

- `ARCH-010-SHOPIFY-003`
- `ARCH-010-SHOPIFY-009`
- `ARCH-010-SHOPIFY-018`

## Acceptance Criteria

1. Shopify source/tests contain no runtime reference to `FREE_RECOVERY_LIFETIME`.
2. Shopify source/tests contain no runtime reference to `BillingPlan.freeLifetimeConversationAllowance` or `BillingAllowanceAdjustment`.
3. Lifetime-Free availability is derived solely from `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)` and is not conditional on Free-plan membership.
4. Existing accepted first-activation/onboarding behaviour remains intact without plan-owned allowance input.
5. No `appSubscriptionCancel` or local cancellation request state machine is introduced.
6. No local duplicate of a removed Shared billing/cancellation contract remains.
7. Shopify source/tests contain no `BILLING_FREE_ALLOWANCE_EXHAUSTED` compatibility handler; generic `BILLING_RECOVERY_CAPACITY_EXHAUSTED` remains supported.
8. Any directly encountered old refund/promotion compatibility has been removed without implementing downstream feature scope.
8. Focused billing-service tests cover canonical lifetime counter arithmetic under both Free and Paid mapped-plan states.
9. Repository-wide search verifies removed baseline symbols are absent from implementation/test code except intentional historical documentation outside repository implementation ownership.
10. Required repository validation passes or only documented unchanged baseline failures remain.

## Validation

Use scripts actually declared in `package.json`. At minimum:

```text
focused billing service/unit tests for touched behaviour
repository typecheck when declared
repository lint when declared
repository build when declared
git diff --check
```

Run source/test searches for:

```text
FREE_RECOVERY_LIFETIME
freeLifetimeConversationAllowance
BillingAllowanceAdjustment
appSubscriptionCancel
SubscriptionCancellationRequest
RecoveryCreditPurchaseStatus.REFUNDED
CURRENT_CYCLE_APP_EVENT_CORRECTION
PROMOTIONAL_RECOVERY_CREDITS
BILLING_FREE_ALLOWANCE_EXHAUSTED
```

Any remaining implementation reference must be explained and may not recreate compatibility state.

## Implementation Notes

This task is a baseline-conformance bridge. Keep it small and deterministic so downstream ARCH-010 tasks start from one clean contract.

## Completion Report

### Status

In Progress.

### Files Changed

Populate during implementation.

### Work Completed

Populate during implementation.

### Validation Results

Populate during implementation.

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

Pending implementation.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

Pending.

### Follow-up

None yet.
