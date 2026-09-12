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
status: review
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

Ready for architect review.

### Files Changed

- `package.json`
- `package-lock.json`
- `app/services/billing/billing.service.ts`
- `app/routes/app/billing/route.tsx`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`

### Work Completed

- Removed Shopify-owned lifetime grant initialization and the legacy platform-policy allowance path from Free activation.
- Switched merchant billing state to `EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS` and durable shop-counter arithmetic: `max(grantedQuantity - committedQuantity - reservedQuantity, 0)`.
- Made lifetime capacity plan-independent in the billing service and merchant billing route, including mapped Paid subscriptions.
- Removed legacy adjustment aggregation and updated the shared package dependency to `@modainteract/moda-interact-shared@0.11.0`.
- Added focused Free/Paid billing-service arithmetic coverage and Paid-plan billing UI coverage.
- Repository-wide source/test search contains none of the required removed baseline symbols.

### Validation Results

- Billing UI suite: 10/10 passed.
- Billing-service suite with the pre-existing generated client: 58/59 passed; one unchanged scheduling test produced `Date(NaN)` because the old installed shared contract lacks the current billing-period drain constant.
- After clean dependency installation, the billing-service suite could not load because `database/prisma/schema.prisma` is absent and Prisma client generation is unavailable.
- `npm run prisma:validate`: blocked because `database/prisma/schema.prisma` is missing.
- `npm run build`: blocked at `prisma:generate` for the same missing schema.
- `npm run typecheck`: blocked by the stale/missing generated Prisma contract, including the absent `LIFETIME_FREE_RECOVERY_CREDITS` enum member and existing missing `nextReconcileAt` fields.
- `npm run lint`: unchanged repository baseline reports 10 errors in unrelated files, including billing options/select routes and existing dashboard/support/test files.
- `git diff --check`: passed.
- Removed-symbol search across `app` and `tests`: passed with no matches.

### Deviations

Full repository validation could not complete because the task worktree does not contain the DATABASE-013 Prisma schema/generated client. No schema or unrelated lint/typecheck failures were changed.

### Assumptions

The architect-provided DATABASE-013 and SHARED-008 contracts are authoritative; the local checkout's generated Prisma artifacts are expected to be refreshed when the database dependency is materialized.

### Unresolved Issues

Architect review should verify the implementation against the materialized DATABASE-013 schema and regenerate Prisma before merge.

### Architectural Concerns

The current checkout reports stale generated Prisma types, including the old entitlement enum; this is not resolved by a compatibility alias because the task explicitly requires the canonical first-production contract.

### Start-of-attempt Synchronization

- Parent worktree: dedicated `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-023`, clean at claim, based on `origin/main`.
- Implementation worktree: dedicated `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-023`, clean at claim, based on `origin/main`.
- Parent branch: `task/ARCH-010-SHOPIFY-023`, synchronized with `origin/main` before claim publication.
- Implementation branch: `task/ARCH-010-SHOPIFY-023`, synchronized with `origin/main` before implementation.

Implementation commit: `01f0605`.
Parent report commits: `4bce6ba` claim and `e5bee8f` completion report.

## Architect Review

### Review Status

Pending

### Review Notes

Implementation published at `01f0605`; parent report is complete and awaiting architect decision.

### Reviewed Files

`app/services/billing/billing.service.ts`, `app/routes/app/billing/route.tsx`, `tests/unit/services/billing.service.test.ts`, `tests/unit/billing-ui.test.ts`, `package.json`, `package-lock.json`

### Validation Reviewed

Focused billing UI: 10/10 passed. Billing service: 58/59 with one unchanged stale-contract failure; clean-install service run blocked by missing Prisma schema. Prisma validate/build/typecheck blocked by missing generated database contract. Lint has 10 unrelated baseline errors. Removed-symbol search and diff check passed.

### Architecture Conformance

The runtime now targets the canonical shop-lifetime counter and shared 0.11.0 contract without compatibility aliases, dual reads, plan-owned allowance, or local cancellation state.

### Follow-up

Architect review of `01f0605`; regenerate Prisma from DATABASE-013 before merge.
