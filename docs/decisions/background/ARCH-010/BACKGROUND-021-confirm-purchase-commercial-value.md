---
id: ARCH-010-BACKGROUND-021
architecture_id: ARCH-010
title: Confirm purchase commercial value and activate REQUESTED recovery-credit purchases
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 68
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-015
- ARCH-010-SHOPIFY-014
enables:
- ARCH-010-BACKGROUND-022
- ARCH-010-SHOPIFY-025
- ARCH-010-ADMIN-003
- ARCH-010-SYSTEM-TEST-001
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-010-BACKGROUND-021: Confirm purchase commercial value and activate REQUESTED recovery-credit purchases

## Forward-correction boundary

`ARCH-010-BACKGROUND-014` is accepted immutable history. Its existing provider-unit-count activation path predates the final purchase-time monetary provenance rule.

This task replaces only that activation rule. Preserve accepted FIFO reservation, aggregate-counter and concurrency behaviour unless BACKGROUND-022 explicitly changes it for the final purchase lifecycle.

## Objective

A merchant top-up becomes spendable only after Background can prove the exact provider-confirmed commercial value of the exact `RecoveryCreditPurchase`.

Required lifecycle:

```text
SHOPIFY-014 creates RecoveryCreditPurchase(REQUESTED)
  + exact purchase-time before snapshot
  + one durable RECOVERY_CREDIT_PACK_PURCHASE UsageEvent

Background publishes/reconciles provider App Event

BACKGROUND-021 obtains exact provider after snapshot
  -> proves exact provider subscription / cycle / meter
  -> proves provider quantity movement for this exact event
  -> proves monetary cost delta and currency
  -> freezes immutable purchase value
  -> atomically grants currentAmount = creditsGranted
  -> REQUESTED -> ACTIVE exactly once
```

Quantity confirmation without monetary confirmation is insufficient.

## Inspect first

```text
src/services/recovery-credit-purchase.service.ts
src/services/shopify-usage-event-publisher.service.ts
src/providers/shopify-partner-billing.provider.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/recovery-billing.service.ts
prisma/schema.prisma / database schema package
relevant recovery-credit-purchase tests
```

Read accepted `BACKGROUND-015`, pending/implemented `BACKGROUND-009`, `SHOPIFY-014`, and `DATABASE-014` before editing.

## Exact provider evidence

Use the accepted provider lifecycle/read model. Do not invent a second Shopify query shape if `BACKGROUND-015` already exposes:

```text
providerSubscriptionId
currentPeriodStart/currentPeriodEnd
usage item handle
usage quantity
usage cost amount
usage cost currency
price/tier evidence where available
```

For a REQUESTED purchase, require exact match to its immutable snapshots:

```text
shopId
billingPeriodId
providerSubscriptionIdSnapshot
shopifyPlanHandleSnapshot
shopifyEventHandleSnapshot
linked UsageEvent identity
```

The provider cycle observed at confirmation must correspond to the purchase's snapshotted BillingPeriod. Do not value a purchase against a later billing cycle.

## Before/after valuation

Let purchase initiation snapshots be:

```text
Q0 = providerUsageQuantityBeforeSnapshot
C0 = providerUsageCostBeforeSnapshot
K0 = providerUsageCostCurrencyBeforeSnapshot
```

and confirmed provider state be:

```text
Q1
C1
K1
```

For the canonical one-pack App Event, require provider evidence proving the expected quantity movement for the exact durable event and no ambiguous second unresolved purchase for the same shop/meter/cycle.

The monetary basis is the authoritative provider incremental cost:

```text
providerPurchaseAmount = C1 - C0
providerPurchaseCurrency = K1 = K0
```

Do not calculate purchase value from:

```text
current BillingPlan price
current plan tier
locally configured pack price
provider tier table arithmetic when an exact cost delta is available
later BillingEconomicsSnapshot
client input
```

If before/after evidence is missing, currency differs, cost delta is non-positive, provider cycle/subscription changed ambiguously, or the provider quantity cannot be mapped uniquely to this purchase, do not activate.

## Atomic activation

Activation is one Serializable transaction with repository-standard bounded retry/CAS.

Re-read the exact purchase and require:

```text
status = REQUESTED
currentAmount = 0
reservedAmount = 0
version = expected
valuation fields still unset
UsageEvent/provider confirmation is durable
```

Then atomically:

```text
purchase.providerUsageQuantityAfterSnapshot = Q1
purchase.providerUsageCostAfterSnapshot = C1
purchase.providerUsageCostCurrencyAfterSnapshot = K1
purchase.providerPurchaseAmount = C1 - C0
purchase.providerPurchaseCurrency = K1
purchase.providerValuationConfirmedAt = now
purchase.currentAmount = creditsGranted
purchase.status = ACTIVE
purchase.activatedAt = now
purchase.version += 1

ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS).grantedQuantity += creditsGranted
counter.version += 1
```

Exactly-once replay must not grant twice or overwrite historical money/provenance.

## Ambiguity/failure behaviour

The canonical purchase lifecycle intentionally has no `NEEDS_ATTENTION` purchase status.

If provider reconciliation is ambiguous:

```text
purchase remains REQUESTED
currentAmount remains 0
no aggregate grant occurs
linked UsageEvent/reporting/provider evidence carries retry/NEEDS_ATTENTION state
```

Never convert ambiguity into ACTIVE capacity.

A definitive provider/reporting failure remains operationally visible through the linked event/evidence and requires reconciliation; do not invent a sixth purchase lifecycle state in this task.

## Existing capacity-resume integration

Preserve any accepted/pending BACKGROUND-009 post-commit resume-hint integration around purchase activation.

The hint may be emitted only **after** the activation transaction commits. Queue failure must not roll back purchase activation.

## Required tests

At minimum prove:

1. REQUESTED purchase cannot provide capacity before valuation;
2. exact matching before/after provider quantity/cost/currency activates once;
3. activation sets `currentAmount = creditsGranted`, `reservedAmount = 0`, `status = ACTIVE`;
4. aggregate purchased grant increases exactly once;
5. replay is idempotent;
6. current/later BillingPlan price is never used;
7. plan change after purchase does not alter stored purchase amount;
8. provider subscription mismatch fails closed;
9. provider BillingPeriod/cycle mismatch fails closed;
10. meter-handle mismatch fails closed;
11. missing/ambiguous cost fails closed;
12. currency mismatch fails closed;
13. quantity-only confirmation does not activate;
14. a second ambiguous pending purchase cannot steal the first purchase's cost delta;
15. valuation fields become immutable after activation;
16. any capacity-resume hint is post-commit/best-effort;
17. focused tests, full repository tests/build/Prisma validation and `git diff --check` pass or unrelated baselines are documented.

## Non-goals

Do not implement merchant refund actions/UI, Admin settlement, or the final reservation allocator lifecycle correction owned by BACKGROUND-022.

## Stop conditions

STOP if exact purchase valuation cannot be proven from provider evidence without guessing, if a completed task must be rewritten, or if SHOPIFY-014 does not provide the required immutable before snapshot.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
