---
id: ARCH-010-DATABASE-014
architecture_id: ARCH-010
title: Materialise canonical recovery-credit purchase lifecycle and immutable purchase provenance
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: copilot
claimed_at: '2026-09-13T10:34:07Z'
attempt: 1
depends_on:
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SHOPIFY-014
- ARCH-010-BACKGROUND-021
- ARCH-010-BACKGROUND-022
- ARCH-010-SHOPIFY-025
- ARCH-010-ADMIN-002
- ARCH-010-ADMIN-003
- ARCH-010-SYSTEM-TEST-001
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-010-DATABASE-014: Materialise canonical recovery-credit purchase lifecycle and immutable purchase provenance

## Why this is a forward correction

`ARCH-010-DATABASE-007` and `ARCH-010-DATABASE-013` are accepted, immutable task history. Do not edit either task file.

The product definition has since been simplified before first production:

- refunds are **not arbitrary partial quantities** chosen by a merchant/Admin;
- a merchant withdraws one whole `RecoveryCreditPurchase` from future allocation and requests a refund of **all credits that ultimately remain unused** on that purchase;
- each purchase is an independent lifecycle object;
- a shop may simultaneously own many purchases in different states;
- the merchant may reactivate a withdrawn purchase until provider refund action begins;
- the purchase must retain immutable commercial provenance and purchase-time monetary value.

ARCH-010 remains pre-production. This task therefore updates the one unreleased first-production Prisma schema and clean baseline migration. Do **not** create compatibility schema merely to preserve development-only DATABASE-007 field shapes.

## Canonical `RecoveryCreditPurchase` lifecycle

The first-production purchase lifecycle has **exactly these business states**:

```text
REQUESTED
ACTIVE
COMPLETED
WITHDRAWN
REFUNDED
```

Semantics:

```text
REQUESTED
  merchant requested a recovery-credit pack;
  provider billing/valuation has not yet been durably confirmed;
  purchase is non-spendable and non-refundable.

ACTIVE
  provider purchase is confirmed and monetarily valued;
  purchase may fund new recovery reservations;
  merchant may request refund only when availableAmount > 0.

COMPLETED
  every credit from the purchase was successfully consumed;
  currentAmount = 0 and reservedAmount = 0;
  terminal and non-refundable.

WITHDRAWN
  merchant requested refund of this purchase's remaining credits;
  no new reservation may use the purchase;
  reservations created before withdrawal may still settle;
  merchant may reactivate only while the linked refund remains pre-provider-action.

REFUNDED
  provider refund/credit was confirmed for every credit that remained unused;
  currentAmount = 0 and reservedAmount = 0;
  terminal and non-spendable.
```

Operational provider uncertainty must not add extra purchase lifecycle values. Keep provider/reporting ambiguity in existing `UsageEvent.shopifyReportState`, refund workflow status/evidence, logs and operator workflows. A purchase that has not been provider-confirmed remains `REQUESTED` and non-spendable.

## Canonical per-purchase credit state

Replace the DATABASE-007 development-only partial-refund accounting shape with fields equivalent to:

```text
creditsGranted   immutable original pack quantity
currentAmount    credits from this purchase not yet successfully consumed/refunded
reservedAmount   subset of currentAmount currently reserved by in-flight conversations
version          optimistic-concurrency/CAS version
```

Retain existing immutable/history fields that still have meaning, such as purchase ID, shop, plan, event identity and activation time.

Do **not** keep first-production per-purchase:

```text
refundingQuantity
refundedQuantity
```

They are redundant under the whole-remaining-purchase refund model and create additional drift-prone sources of truth.

`committedQuantity` may be removed from the purchase lot if no accepted runtime requires it after BACKGROUND-022; successful consumption is represented by `currentAmount` decrement plus durable `UsageReservation`/`UsageEvent` history. If inspection proves a still-pending first-production consumer genuinely requires a per-lot committed aggregate, STOP and return that exact consumer to `moda_architect` rather than silently retaining two competing balance models.

### Amount invariants

Persist/check equivalent invariants:

```text
creditsGranted > 0
currentAmount >= 0
reservedAmount >= 0
reservedAmount <= currentAmount
version >= 0
```

Lifecycle invariants:

```text
REQUESTED  -> currentAmount = 0, reservedAmount = 0
ACTIVE     -> currentAmount > 0, reservedAmount <= currentAmount
WITHDRAWN  -> currentAmount > 0, reservedAmount <= currentAmount
COMPLETED  -> currentAmount = 0, reservedAmount = 0
REFUNDED   -> currentAmount = 0, reservedAmount = 0
```

Do not persist `availableAmount`.

For an ACTIVE purchase only:

```text
availableAmount = currentAmount - reservedAmount
```

A WITHDRAWN purchase may have the same arithmetic remainder, but it has **zero spendable capacity** because its lifecycle state blocks new reservations.

## Aggregate purchased-credit counter

Keep `ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)` as the hot-path shop aggregate.

Its `refundingQuantity` remains useful as an **aggregate transient hold** for all unreserved credits belonging to WITHDRAWN purchase lots. It is not duplicated on each purchase.

Required aggregate parity conceptually:

```text
aggregate.refundingQuantity
  = SUM(currentAmount - reservedAmount)
    across WITHDRAWN purchases with a live pre/completing refund workflow
```

BACKGROUND-022 and SHOPIFY-025 own runtime maintenance of that invariant.

Do not add a shop-global purchase lifecycle state.

## Immutable purchase commercial provenance

Every provider-confirmed purchase must permanently identify the exact commercial context in which it was bought.

Add direct immutable fields/relations equivalent to:

```prisma
billingPeriodId String
billingPeriod   BillingPeriod @relation("RecoveryCreditPurchaseBillingPeriod", fields: [billingPeriodId], references: [id], onDelete: Restrict)

providerSubscriptionIdSnapshot String

providerUsageQuantityBeforeSnapshot Int
providerUsageCostBeforeSnapshot     Decimal
providerUsageCostCurrencyBeforeSnapshot String

providerUsageQuantityAfterSnapshot  Int?
providerUsageCostAfterSnapshot      Decimal?
providerUsageCostCurrencyAfterSnapshot String?

providerPurchaseAmount   Decimal?
providerPurchaseCurrency String?
providerValuationConfirmedAt DateTime?
providerPriceSnapshot Json?
```

Use repository/provider-safe precision and bounds. Do not silently coerce provider money into `Decimal(20,2)` if any first-production supported currency requires different precision. If the current provider contract cannot be represented exactly, STOP and return the evidence to `moda_architect`.

Add the reverse `BillingPeriod.recoveryCreditPurchases` relation.

### Provenance rules

At purchase creation, snapshot from one verified provider/local billing context:

```text
billingPeriodId
providerSubscriptionIdSnapshot
planId
shopifyPlanHandleSnapshot
shopifyEventHandleSnapshot
providerUsageQuantityBeforeSnapshot
providerUsageCostBeforeSnapshot
providerUsageCostCurrencyBeforeSnapshot
providerPriceSnapshot
```

At provider-confirmed activation, BACKGROUND-021 adds immutable after-state and final purchase amount/currency.

A purchase may become `ACTIVE` only when all required purchase-time valuation fields are present and consistent.

Current/later BillingPlan pricing, later provider subscription, later top-up meter price and later `BillingEconomicsSnapshot` are never refund authority.

## `RecoveryCreditRefund` first-production shape

A refund row represents a **request/workflow against one purchase**, not a merchant-selected quantity.

Retain one-to-many history from purchase -> refunds because a merchant may request, reactivate/cancel, then later request again. However, at most one refund may ever complete for a purchase because successful completion makes the purchase `REFUNDED`.

Replace arbitrary partial-refund request/approval quantity semantics with snapshots equivalent to:

```text
purchaseId
shopId
source = MERCHANT_UI | ADMIN as already supported
requestedByShopifyUserId when available

purchaseCreditsGrantedSnapshot
currentAmountAtRequestSnapshot
reservedAmountAtRequestSnapshot
availableAmountAtRequestSnapshot

billingPeriodIdSnapshot
providerSubscriptionIdSnapshot
planHandleSnapshot
eventHandleSnapshot
purchaseProviderAmountSnapshot
purchaseProviderCurrencySnapshot

finalCreditQuantity             nullable until provider-action boundary; system-derived from purchase.currentAmount
expectedProviderAmount          nullable until provider settlement boundary
expectedProviderCurrency        nullable until provider settlement boundary

status
requestKey
reason
version
provider action/evidence fields
createdAt/completedAt
```

Remove/deprecate first-production fields whose only meaning was arbitrary merchant/Admin quantity selection, including development-only `creditsRequested` / `creditsApproved` semantics. Do not preserve them as authorities merely because DATABASE-007 once introduced them.

### Request-time snapshots are not the final refund quantity

At request time:

```text
availableAmountAtRequestSnapshot = currentAmount - reservedAmount
```

This proves what was refundable at the exact winning CAS state.

It is **not** the final provider refund quantity because reservations that existed before withdrawal may later fail/release and return credits to the withdrawn purchase.

Final provider refund quantity is fixed only when:

```text
purchase.status = WITHDRAWN
purchase.reservedAmount = 0
purchase.currentAmount > 0
refund.status = REQUESTED
```

At that irreversible provider-action boundary:

```text
finalCreditQuantity = purchase.currentAmount
```

ADMIN-003 owns the transition and provider settlement.

## Refund workflow status

Retain the existing refund workflow values unless schema inspection proves a naming conflict:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
COMPLETED
REJECTED
CANCELLED
NEEDS_ATTENTION
```

Here `RecoveryCreditRefund.CANCELLED` means the refund request is terminal/cancelled (for example merchant reactivated the purchase or no credits remained). It is distinct from `RecoveryCreditPurchase.WITHDRAWN`, which means the purchase is withdrawn from new credit allocation pending refund.

Use bounded `reason` to distinguish terminal closure causes such as merchant reactivation, Admin rejection and no credits remaining.

## Database uniqueness

Add migration-level constraints/indexes proving at least:

1. at most one non-terminal refund per purchase in:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
```

2. at most one `COMPLETED` refund per purchase;
3. request keys remain globally unique;
4. useful indexes exist for merchant list views by `shopId,status,createdAt/activatedAt` and Admin refund queues.

Use PostgreSQL partial unique indexes where Prisma cannot express the invariant directly and add validators that prove the SQL exists.

## Purchase monetary refund basis

The final refund amount is always based on the immutable original purchase monetary value, never current pricing.

When Admin locks provider action and `reservedAmount == 0`:

```text
G = purchase.creditsGranted
R = purchase.currentAmount
M = purchase.providerPurchaseAmount
```

The expected provider refund is the exact proportional historical-purchase value for `R/G`, using a deterministic currency-safe rounding rule approved by the repository/provider representation.

There is no sequence of completed partial refunds for one purchase in first production. A successful refund makes the purchase terminal `REFUNDED`.

If provider money precision/rounding cannot be represented deterministically from current provider evidence, STOP rather than inventing a current-price or floating-point approximation.

## Clean baseline migration

ARCH-010 has not reached production. Update the existing first-production baseline migration so a clean empty database is created directly in this final shape.

Do not add:

```text
legacy compatibility columns
runtime dual-read/dual-write
second production migration solely to preserve development schema
```

Update ERD/schema docs and validation scripts.

## Required validation

At minimum prove:

1. enum contains exactly the five purchase lifecycle states;
2. REQUESTED defaults non-spendable with `currentAmount=0,reservedAmount=0`;
3. ACTIVE/WITHDRAWN require positive current amount and valid reservation bound;
4. COMPLETED/REFUNDED require zero current/reserved;
5. `availableAmount` is not persisted;
6. per-purchase `refundingQuantity/refundedQuantity` are absent from the final baseline;
7. direct BillingPeriod/provider-subscription provenance exists;
8. purchase valuation fields can prove immutable original amount/currency;
9. refund request-time current/reserved/available snapshots exist;
10. arbitrary merchant/Admin refund quantity fields are not first-production authorities;
11. one non-terminal refund per purchase is DB-enforced;
12. one completed refund per purchase is DB-enforced;
13. aggregate `ShopEntitlementCounter.refundingQuantity` remains available;
14. clean baseline migration + Prisma validation succeed;
15. ERD/schema validators reflect the final model;
16. `git diff --check` passes.

## Non-goals

Do not implement provider reconciliation, reservation runtime, merchant UI/actions, Admin settlement or system tests in this task.

## Stop conditions

STOP and return evidence to `moda_architect` if:

- an accepted first-production consumer outside the planned correction tasks requires the old arbitrary-partial-refund fields;
- exact provider monetary precision cannot be represented safely;
- a completed task file would need to be edited;
- a production database already exists and would require compatibility migration semantics.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql`
- `moda-interact-database/scripts/validate-first-production-baseline.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`

### Work Completed
- Replaced the development purchase status enum with the canonical `REQUESTED`, `ACTIVE`, `COMPLETED`, `WITHDRAWN`, and `REFUNDED` lifecycle.
- Replaced per-purchase legacy quantity counters with `currentAmount` and `reservedAmount`, retaining aggregate `ShopEntitlementCounter.refundingQuantity`.
- Added restrictive billing-period linkage and immutable provider subscription, usage, valuation, amount, currency, and price provenance fields.
- Replaced arbitrary refund quantity fields with request-time amount snapshots and provider settlement fields.
- Added lifecycle/amount checks, partial unique refund indexes, migration foreign keys, validator coverage, and regenerated the ERD.

### Validation Results
- `npm run prisma:validate` passed.
- `npm run prisma:generate` passed.
- `npm run test:first-production-baseline` passed.
- `npm run erd:puml` passed.
- `git diff --check` passed.
- The baseline migration remains clean: no `UPDATE`, `INSERT INTO`, or `DELETE FROM` statements.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-014`
- Implementation branch: `task/ARCH-010-DATABASE-014`
- Implementation commit: `cd8dc213bc0a80601094253e3d0739cc6b479f5b`
- Implementation remote verification: local `HEAD` and `origin/task/ARCH-010-DATABASE-014` both resolve to `cd8dc213bc0a80601094253e3d0739cc6b479f5b`.
- Parent claim commit remains `e1ca470`; only this task report is changed in the parent workspace and the database submodule gitlink is not staged.

### Architect Review
Ready for `moda_architect` review.
