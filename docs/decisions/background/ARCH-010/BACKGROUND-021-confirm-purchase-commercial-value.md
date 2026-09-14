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
status: complete
priority: 68
executor: null
claimed_at: null
attempt: 1
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
updated: 2026-09-14
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
Ready for Architect Review.

### Files Changed
- `src/services/recovery-credit-purchase.service.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/purchased-recovery-reservation.service.ts`
- `tests/unit/services/recovery-credit-purchase.service.test.ts`
- `tests/unit/services/recovery-credit-purchase.resume-hint.test.ts`
- `tests/unit/services/billing-reconciliation.service.test.ts`
- `tests/unit/services/purchased-recovery-reservation.service.test.ts`

### Work Completed
- Replaced legacy quantity-only activation and removed obsolete `PENDING_BILLING`/`NEEDS_ATTENTION` purchase activation paths.
- Reconciliation now requires the exact provider subscription, current billing-period/meter scope, cumulative quantity proof from the purchase's immutable before quantity, positive provider cost delta, and matching currency.
- Ambiguous attribution, missing/unchanged cost, subscription/currency/quantity mismatch, non-REPORTED evidence, and multiple unresolved purchases remain `REQUESTED` with zero capacity and no aggregate grant.
- Atomically CAS-updated the exact purchase's after snapshots, immutable purchase amount/currency/valuation timestamp, `currentAmount = creditsGranted`, `REQUESTED -> ACTIVE`, and purchased-credit aggregate grant under Serializable retry behavior.
- Preserved post-commit best-effort capacity-resume scheduling and replay idempotency.
- Updated purchased recovery reservation accounting and its test harness to use the current Prisma purchase balance fields, `currentAmount` and `reservedAmount`, while retaining aggregate counter quantity accounting.
- Added explicit focused coverage that REQUESTED purchases provide no capacity, provider plan price snapshots do not determine the stored purchase amount, and a later plan handle cannot alter an activated purchase's immutable provider amount/currency.
- Audit-strengthened the tests against mutation-style weaknesses: activation now asserts the complete after quantity/cost/currency, purchase amount/currency, valuation/activation timestamps, balance/status/version write set, Serializable transaction option, and aggregate grant; identity negatives mutate the purchase snapshot scope independently of the linked UsageEvent; reservation fixtures now pass through the production ACTIVE filter so REQUESTED/WITHDRAWN/REFUNDED lots cannot be excluded by the mock itself.

### Behavioral Test Matrix

| Required behavior | Production symbol | Test evidence |
| --- | --- | --- |
| No capacity before valuation | `selectOldestSpendableLot`, `reserveInTransaction` | `purchased-recovery-reservation.service.test.ts`: REQUESTED lot returns `credits-exhausted`, remains at zero reserved/current balance unchanged. |
| Exact quantity/cost/currency and immutable snapshots | `reconcileProviderConfirmed` | `recovery-credit-purchase.service.test.ts`: before quantity `2` plus one provider unit yields after `3`; cost `12.50 - 10.00` yields `2.5`; USD is persisted in both after and purchase fields; timestamps and version are asserted. |
| Subscription, cycle, plan, and meter identity | reconciliation `scope` and candidate checks; `BillingReconciliationService.reconcilePackPurchases` | Focused billing test asserts exact period, plan, meter, subscription, quantity, cost, and currency handoff; purchase tests mutate purchase period/plan/meter snapshots and require fail-closed `over` discrepancy. |
| Ambiguity and quantity-only fail closed | `reconcileProviderConfirmed` | Multiple unresolved candidates, missing cost, non-positive delta, currency/subscription mismatch, quantity mismatch, and non-REPORTED/mismatched UsageEvent cases assert no activation, no capacity, and no aggregate grant. |
| Atomic ACTIVE/currentAmount/aggregate grant | Serializable `$transaction`, CAS `updateMany`, counter `upsert` | Activation test asserts ACTIVE, `currentAmount = creditsGranted`, `reservedAmount = 0`, all valuation fields, version increment, aggregate grant, and Serializable transaction option. |
| Idempotent replay | ACTIVE count and REQUESTED candidate selection in `reconcileProviderConfirmed` | Replay test asserts zero second activation and aggregate grant remains exactly `5`; reservation commit replay returns `already-committed` with one usage event. |
| Plan-price independence and immutable historical value | `providerPurchaseAmount` calculation in `reconcileProviderConfirmed` | Plan snapshot price `999.00` still stores provider delta `2.5`; later plan handle/cost leaves ACTIVE purchase amount/currency unchanged. |
| Post-commit resume hint | `recoveryCapacityResumeService.schedule` after `$transaction` | Resume-hint tests assert event order transaction-complete -> schedule, no hint on zero activation, and activation result survives queue failure. |

Correction mapping: no Architect Review corrections were present; the latest review section remained `Pending`.

### Validation Results
- Focused purchase, reconciliation, resume-hint, and reservation tests: passed, 70/70 tests after mutation-strengthening edits; the two edited files are committed as implementation `b10c5d1`.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run test:unit`: 57 files passed and 912 tests passed; 2 unchanged baseline failures in `tests/unit/runtime/observability-startup.test.ts` (worker close-resource source assertion and expected shared runtime `0.9.0` versus package `0.11.0`).
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `git diff --check`: passed.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-021`
- Implementation branch: `task/ARCH-010-BACKGROUND-021`
- Implementation commits: `229fd5f` (`Confirm recovery credit purchase commercial value`), `cbdd18e` (`fix background purchase reservation balances`), `59206a6` (`test background purchase valuation evidence`), and `b10c5d1` (`test background purchase mutation strength`), pushed to `origin/task/ARCH-010-BACKGROUND-021`.
- Database gitlink was not changed or staged.
- Parent report commits: `e308a3e` (claim), `7090504` (return for review), `5f047e5` (validation evidence), `4731de0` (`docs background 021 audit evidence`), and `00af590` (`docs background 021 git evidence`), pushed to `origin/task/ARCH-010-BACKGROUND-021`.

### Architect Review
Pending.

## Architect Review — Attempt 1

### Status

**Accepted**

This review intentionally prioritises production functionality and commercial
correctness over exhaustive test-count coverage.

`ARCH-010-BACKGROUND-021` now satisfies the first-production authority boundary for
turning a non-spendable `REQUESTED` top-up into spendable purchased recovery capacity.

### Accepted provider-confirmed valuation

A purchase activates only from one exact provider-confirmed commercial context.

The accepted authority chain is:

```text
immutable purchase before snapshot
  -> exact linked one-pack UsageEvent is REPORTED
  -> exact current provider subscription / plan / billing period / pack meter
  -> exactly one unresolved REQUESTED purchase in that scope
  -> provider quantity proves Q1 = Q0 + 1
  -> provider cost proves C1 > C0
  -> provider currency proves K1 = K0
  -> immutable purchase amount = C1 - C0
```

The implementation does not derive historical purchase value from:

```text
current BillingPlan price
later plan price
local pack configuration
provider tier arithmetic
client input
later BillingEconomicsSnapshot
```

This is the required commercial provenance rule.

### Accepted scope and fail-closed behaviour

The purchase candidate scope requires the durable purchase snapshots and linked
UsageEvent to agree on:

```text
shop
BillingPeriod
Shopify plan handle
pack meter handle
RECOVERY_CREDIT_PACK_PURCHASE metric
one provider unit
REPORTED state
```

Provider subscription identity is then checked against the purchase's immutable
`providerSubscriptionIdSnapshot`.

The reconciliation fails closed when:

```text
provider subscription is absent/mismatched
billing-period scope does not match
plan handle does not match
meter handle does not match
linked UsageEvent is not REPORTED
provider quantity is invalid or not Q0 + 1
provider cost is absent/invalid/non-positive delta
provider currency differs
more than one unresolved REQUESTED purchase is attributable to the same scope
```

No ambiguous case becomes spendable capacity.

### Accepted cumulative provider-quantity semantics

Provider pack quantity is cumulative for the provider meter, while individual local
purchase lots may later move through:

```text
ACTIVE
COMPLETED
WITHDRAWN
REFUNDED
```

Architect review confirms that this does not create a re-grant or misattribution path.

`alreadyMatchedUnits` is reconciliation/discrepancy context; it is not the authority
that activates a new purchase.

A new activation still requires the exact candidate's immutable:

```text
providerUsageQuantityBeforeSnapshot = Q0
```

and exact provider:

```text
providerUnits = Q0 + 1
```

plus unique unresolved REQUESTED ownership and the monetary/currency proof above.

Therefore an earlier purchase becoming COMPLETED/WITHDRAWN/REFUNDED cannot cause the
new purchase to inherit or fabricate that earlier purchase's provider delta.

### Accepted atomic activation

The accepted mutation occurs inside one Serializable transaction with bounded retry.

The exact purchase is CAS-rechecked as:

```text
status = REQUESTED
currentAmount = 0
reservedAmount = 0
version = expected
valuation not previously committed
```

and atomically becomes:

```text
providerUsageQuantityAfterSnapshot = Q1
providerUsageCostAfterSnapshot = C1
providerUsageCostCurrencyAfterSnapshot = K1
providerPurchaseAmount = C1 - C0
providerPurchaseCurrency = K1
providerValuationConfirmedAt = now
currentAmount = creditsGranted
status = ACTIVE
activatedAt = now
version += 1
```

In the same transaction:

```text
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS).grantedQuantity
  += creditsGranted
```

If the purchase CAS loses, no aggregate grant commits.

Replay cannot grant twice because the purchase is no longer REQUESTED after the first
successful transaction.

### Accepted reservation safety

Purchased-credit reservation reads only `ACTIVE` purchase lots.

Therefore these purchase states provide no new spendable reservation capacity:

```text
REQUESTED
WITHDRAWN
REFUNDED
COMPLETED
```

The lot arithmetic continues to use:

```text
spendable = currentAmount - reservedAmount
```

while the shop aggregate continues to respect committed, reserved and refund-held
quantity.

This preserves the existing reservation model until the explicit lifecycle/refund
concurrency correction owned by `ARCH-010-BACKGROUND-022`.

### Accepted post-commit resume behaviour

Capacity resume is emitted only after the Serializable activation transaction returns
successfully.

A queue/scheduling failure does not roll back or duplicate the provider-confirmed
purchase activation.

This preserves the accepted BACKGROUND-009 recovery-capacity-resume architecture.

### Validation accepted

```text
Focused functional suite:
  70 / 70 passed

Full unit suite:
  912 passed
  2 unchanged observability baseline failures

Build:
  passed

Prisma validate:
  passed

Prisma generate:
  passed

git diff --check:
  passed
```

The strengthened focused tests now verify actual mutation semantics, including:

```text
exact provider after quantity/cost/currency
exact provider monetary delta
valuation and activation timestamps
ACTIVE/currentAmount/reservedAmount/version write set
aggregate grant
Serializable transaction option
plan/cycle/meter/subscription mismatch rejection
ACTIVE-only purchase-lot selection
REQUESTED/WITHDRAWN/REFUNDED exclusion
```

No further test-matrix expansion is required for this task.

### Accepted implementation evidence

Developer handoff:

```text
Implementation:
b10c5d1

Parent report:
21086dd
```

The review archive contains the complete source snapshot but no nested Git metadata,
so the architect review validates the supplied implementation state and source
behaviour rather than independently reconstructing commit ancestry inside the archive.

### Dependency reconciliation

`ARCH-010-BACKGROUND-021` is Complete.

All declared prerequisites of:

```text
ARCH-010-BACKGROUND-022
```

are now Complete, so `BACKGROUND-022` is promoted to `ready`.

`ARCH-010-SHOPIFY-025` remains Pending because it still depends on
`ARCH-010-BACKGROUND-022`.

The current implementation-ready ARCH-010 frontier is:

```text
ARCH-010-SHOPIFY-012
ARCH-010-BACKGROUND-022
```

No additional BACKGROUND-021 implementation attempt is required.

