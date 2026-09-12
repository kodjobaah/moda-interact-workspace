---
id: ARCH-010-BACKGROUND-019
architecture_id: ARCH-010
title: Reserve selected promotional campaign credits before every other capacity source
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 82
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-011
  - ARCH-010-BACKGROUND-002
  - ARCH-010-BACKGROUND-011
  - ARCH-010-BACKGROUND-014
enables:
  - ARCH-010-BACKGROUND-008
  - ARCH-010-BACKGROUND-009
  - ARCH-010-SYSTEM-TEST-001
  - ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-BACKGROUND-019: Reserve selected promotional campaign credits before every other capacity source

## Objective

Implement exact-grant promotional reservation/commit/release for the merchant's one currently selected promotion and make that promotion the **highest-priority recovery-capacity source**.

Canonical order:

```text
PAID
  selected promotional
  -> current BillingPeriod included
  -> purchased FIFO lot
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

FREE
  selected promotional
  -> purchased FIFO lot
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

## Inspect before editing

```text
src/services/recovery-billing.service.ts
src/services/effective-billing-policy.service.ts
src/services/*reservation*.ts
src/services/checkout-recovery.service.ts
database/prisma/schema.prisma
tests/unit/services/**billing**
tests/integration/*reservation*.test.ts
```

Read the implemented forms of BACKGROUND-002, BACKGROUND-011, BACKGROUND-014 and DATABASE-011. Reuse the same Serializable/CAS/idempotency architecture.

## 1. Resolve the selected campaign transactionally

Before reserving any other recovery-capacity bucket, resolve `MerchantPromotionSelection` and its exact `PromotionalCreditGrant`/`PromotionCampaign`.

A selected promotion is usable for a new reservation only if all are true in the reservation transaction:

```text
campaign.status = ACTIVE
campaign.startsAt <= now < campaign.expiresAt
grant.shopId = current shop
grant.campaignId = campaign.id
remaining grant quantity > 0
scope eligibility still holds
normal ARCH-010 shop/subscription execution gate is open
```

Scope eligibility:

```text
GLOBAL -> eligible
SHOP   -> campaign.targetShopId == shopId
PLAN   -> campaign.targetPlanId == current effective mapped BillingPlan.id
```

If the selection is expired/closed/ineligible/exhausted, treat promotional capacity as unavailable and continue to the next canonical source. Do not delete history in Background.

## 2. Exact promotional grant reservation

Use `UsageReservation.promotionalCreditGrantId` from DATABASE-011. Do not reserve from the aggregate promotional counter alone.

Availability:

```text
remaining = quantity - committedQuantity - reservedQuantity
```

Reserve with bounded Serializable/CAS retry, deterministic recovery source identity, replay-before-allocation and exact grant versioning.

Maintain aggregate `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` only as compatible aggregate accounting if the accepted schema/runtime requires it; grant-lot counters and campaign eligibility are spendability authority.

## 3. Commit/release around expiry

- reservation created while campaign is usable remains protected;
- that existing reservation may commit after campaign expiry/close/plan change because recovery was already admitted;
- definitive pre-provider failure releases exactly once;
- release after campaign is unusable does not make that quantity spendable unless the same campaign later becomes running/eligible again;
- committed reservation updates `firstUsedAt/lastUsedAt` and `exhaustedAt` when appropriate;
- duplicate commit never increments usage twice.

## 4. Promo-first routing

Refactor the one canonical recovery admission path to call promotional reservation **before** paid included capacity.

```text
if selected promotional reserve succeeds:
    fund from promotion
else if PAID:
    try current-period included
    -> purchased FIFO
    -> lifetime Free
else FREE:
    purchased FIFO
    -> lifetime Free
```

`BACKGROUND-002` remains owner of the period-included reservation primitive; it no longer owns top-level priority.

Do not leave another caller with the obsolete `paid included -> promotional` order.

## 5. Provider/App Event rule

Promotional-funded recovery:

- creates no normal paid Shopify recovery-meter App Event;
- creates no top-up purchase App Event;
- is never paid overage;
- keeps normal internal recovery/accounting evidence.

During the five-minute provider BillingPeriod DRAINING phase, a usable selected promo may still fund a new recovery because it creates no cycle-scoped App Event. If no promo is usable, Paid included remains unavailable during drain and routing proceeds to purchased/lifetime Free per BACKGROUND-008.

## 6. Lifecycle gates remain stronger

Positive/selected promotional capacity never bypasses:

```text
Shop.status != ACTIVE
Subscription = NO_CONTRACT
Subscription = FROZEN
reinstallPendingAt != null
other existing provider/configuration execution blocks
```

Preserve grant/history while blocked.

## Required tests

At minimum prove:

1. Paid selected promo + paid included available consumes promo first;
2. promo exhausted -> Paid included;
3. Free selected promo consumes promo first;
4. no usable promo -> Free purchased -> lifetime Free;
5. no usable promo -> Paid included -> purchased -> lifetime Free;
6. PLAN promo becomes unavailable after plan change without deleting grant;
7. GLOBAL/SHOP targeting is checked correctly;
8. expired/closed campaign cannot fund new reservation;
9. reservation made before expiry may commit after expiry;
10. released-after-expiry quantity is not currently spendable;
11. reopened same campaign can later make the original unused grant spendable again when reselected;
12. concurrent workers cannot overspend final promo credit;
13. duplicate reserve/commit is idempotent;
14. promo-funded recovery creates no Shopify usage App Event;
15. DRAINING may use promo before all other buckets;
16. FROZEN/NO_CONTRACT/inactive shop never consumes promo;
17. all buckets exhausted yields typed capacity-exhausted result;
18. no automatic paid overage exists.

## Non-goals

Do not implement Admin campaign management, merchant selection UI/action, promotion marketing delivery, automatic campaign selection or an expiry scheduler.

## Stop conditions

Stop if DATABASE-011 exact grant ownership is unavailable, or if implementing promo-first routing would require duplicating the accepted reservation architecture rather than composing existing primitives.

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
