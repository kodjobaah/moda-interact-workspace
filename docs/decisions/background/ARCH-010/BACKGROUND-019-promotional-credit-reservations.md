---
id: ARCH-010-BACKGROUND-019
architecture_id: ARCH-010
title: Reserve and consume promotional recovery credits ahead of purchased and lifetime Free capacity
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
  - ARCH-010-DATABASE-009
  - ARCH-010-BACKGROUND-002
  - ARCH-010-BACKGROUND-011
  - ARCH-010-BACKGROUND-014
enables:
  - ARCH-010-BACKGROUND-008
  - ARCH-010-BACKGROUND-009
  - ARCH-010-SYSTEM-TEST-001
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-BACKGROUND-019: Reserve and consume promotional recovery credits ahead of purchased and lifetime Free capacity

## Objective

Add concurrency-safe promotional-credit reservation/commit/release and integrate the final ARCH-010 capacity order:

```text
FREE
  promotional
  -> purchased lifetime
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

PAID
  current-period included
  -> promotional
  -> purchased lifetime
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

Promotional recovery capacity is lifetime-until-used, non-refundable, plan-independent and excluded from Shopify recovery-meter billing.

## Inspect before editing

```text
src/services/recovery-billing.service.ts
src/services/effective-billing-policy.service.ts
src/services/free-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/paid-included-recovery-reservation.service.ts   # integrated name may differ
src/services/checkout-recovery.service.ts
src/services/recovery-credit-purchase.service.ts
src/domain/**
tests/unit/services/**billing**
tests/unit/services/**reservation**
tests/integration/*reservation*.test.ts
database/prisma/schema.prisma
package.json
```

Read the implemented forms of BACKGROUND-002, BACKGROUND-011 and BACKGROUND-014 before editing. Reuse their transaction/CAS/idempotency conventions; do not invent a fourth reservation architecture.

## 1. Promotional reservation primitive

Add one focused service, for example:

```text
src/services/promotional-recovery-reservation.service.ts
```

Use the existing `UsageReservation` model pointing to:

```text
ShopEntitlementCounter(counter = PROMOTIONAL_RECOVERY_CREDITS)
```

Canonical availability:

```text
remaining = max(grantedQuantity - committedQuantity - reservedQuantity, 0)
```

Do not use:

- `refundingQuantity` as promotional state;
- `BillingAllowanceAdjustment`;
- current BillingPlan allowance fields;
- Shopify usage totals;
- BillingPeriod allowance counters.

A missing promotional counter is a normal zero-capacity condition, not a data-integrity error.

## 2. Reservation lifecycle

Promotional reservation must have the same correctness properties as accepted lifetime/purchased reservations:

- deterministic source identity for the same recovery;
- replay returns/reuses the same effective reservation rather than double-reserving;
- atomic increment of `reservedQuantity` only when remaining capacity exists;
- commit moves exactly the reserved quantity from reserved to committed;
- definitive pre-provider failure releases exactly once;
- ambiguous provider outcome preserves protected capacity using the existing ambiguity convention;
- no negative counters;
- concurrent requests cannot spend the same final promotional credit twice.

Promotional source identity is shop-lifetime/period-independent. Do not include BillingPeriod identity.

## 3. Final admission order

Refactor only as much as needed so one canonical recovery admission path implements:

```text
FREE:
  promotional reserve
  -> purchased FIFO lot reserve (BACKGROUND-014)
  -> lifetime Free reserve (BACKGROUND-011)
  -> capacity exhausted

PAID:
  current BillingPeriod included reserve (BACKGROUND-002)
  -> promotional reserve
  -> purchased FIFO lot reserve (BACKGROUND-014)
  -> lifetime Free reserve (BACKGROUND-011)
  -> capacity exhausted
```

Do not leave a second caller with the old `included -> purchased -> free` or `purchased -> free` routing.

## 4. Provider billing rule

A recovery funded by promotional credits:

- records the normal internal recovery/accounting evidence required by the existing workflow;
- MUST NOT create/publish the normal paid Shopify recovery-meter App Event;
- MUST NOT create a recovery-credit-pack purchase App Event;
- MUST NOT be treated as paid overage.

The same exclusion already applies to purchased and lifetime-Free-funded recoveries. Preserve that model.

## 5. Billing-cycle drain behaviour

Promotional capacity is not period-scoped and creates no Shopify billing App Event.

During the App Pricing five-minute DRAINING phase:

```text
paid included             -> unavailable for new recovery
promotional               -> may still fund recovery
purchased                 -> may still fund recovery
lifetime Free             -> may still fund recovery
```

provided the subscription/shop execution gate is otherwise valid.

For Free, provider-cycle drain likewise does not pause promotional-funded recovery; it only pauses actions that create cycle-scoped App Events such as buying a new top-up.

BACKGROUND-008 is amended to revalidate this exact fallback order immediately before provider action.

## 6. Execution-state gates remain stronger than credit balances

Promotional credits do not bypass:

```text
Shop.status != ACTIVE
Subscription.status = NO_CONTRACT
Subscription.status = FROZEN
reinstallPendingAt != null
provider/configuration safety gates
```

The counter may remain positive while execution is disabled. Preserve the balance and return the existing execution-state block rather than consuming it.

## 7. Capacity restoration

A new promotional grant can restore capacity for recoveries previously blocked with `RECOVERY_CAPACITY_EXHAUSTED`.

Do not introduce an Admin->Background package dependency or a second cross-repository queue solely for the grant.

`BACKGROUND-009`'s PostgreSQL repair scan is the durable restoration mechanism. After this task, its admission recheck must see promotional capacity and resume still-valid blocked recoveries normally.

A future direct hint may optimise latency but is not required for correctness.

## Required tests

At minimum prove:

1. Free + promotional available reserves promotional before purchased;
2. Free promotional exhausted -> purchased;
3. Free promotional+purchased exhausted -> lifetime Free;
4. Paid included available -> included before promotional;
5. Paid included exhausted + promotional available -> promotional;
6. Paid included+promo exhausted + purchased available -> purchased;
7. Paid included+promo+purchased exhausted + lifetime Free available -> lifetime Free;
8. all buckets exhausted -> typed capacity-exhausted result;
9. concurrent attempts cannot overspend the final promotional credit;
10. duplicate source identity is idempotent;
11. commit/release counters remain balanced;
12. promotional-funded recovery creates no Shopify normal recovery-meter App Event;
13. promotional-funded recovery creates no top-up purchase App Event;
14. DRAINING may admit promotional after included is unavailable;
15. FROZEN/NO_CONTRACT/inactive shop never consumes promotional balance;
16. missing promotional counter behaves as zero capacity;
17. purchased FIFO lot behaviour remains unchanged after promotional insertion;
18. lifetime Free remains last fallback;
19. no automatic paid overage branch exists.

Run focused unit/concurrency tests, repository-declared full tests/build/typecheck as applicable, and `git diff --check`.

## Non-goals

Do not:

- grant promotional credits;
- add Admin UI;
- add expiry/revocation;
- refund promotional credits;
- modify Shopify plan configuration;
- add a new App Event/meter;
- change purchased lot ordering within the purchased bucket;
- change the one-time lifetime Free grant amount.

## Stop conditions

Stop and return to `moda_architect` if:

- BACKGROUND-014 has not produced a callable FIFO purchased reservation path;
- recovery admission has materially diverged from the inspected service boundaries;
- promotional-funded recovery cannot be excluded from Shopify meter publication without changing another repository;
- implementation would require weakening FROZEN/NO_CONTRACT/inactive execution gates.

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
