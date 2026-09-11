---
id: ARCH-010-DATABASE-004
architecture_id: ARCH-010
title: Strengthen recurring App Pricing BillingPeriod ownership and close/open lifecycle integrity
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-002
enables:
  - ARCH-010-BACKGROUND-001
  - ARCH-010-BACKGROUND-003
  - ARCH-010-BACKGROUND-007
  - ARCH-010-BACKGROUND-010
  - ARCH-010-BACKGROUND-012
  - ARCH-010-SHOPIFY-002
  - ARCH-010-SHOPIFY-003
  - ARCH-010-SHOPIFY-007
  - ARCH-010-SHOPIFY-009
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-DATABASE-004: Strengthen BillingPeriod ownership and close/open lifecycle integrity

## Objective

Make BillingPeriod a durable child of the shop's one Subscription for every exact Shopify App Pricing monthly billing cycle that Moda must reconcile, preserve historical periods after renewal, snapshot the mapped plan governing every newly-created Free or Paid period, snapshot included recovery allowance only where one actually exists, and enforce that a Subscription cannot have two OPEN periods.

This task provides database integrity only. It does not execute rollover or call Shopify.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-lifecycle-schema.mjs
scripts/validate-recovery-credit-pack-schema.mjs
scripts/generate-erd.mjs
package.json
docs/generated/prisma-erd.puml
```

Read:

```text
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
ARCH-010-DATABASE-002 implementation/task result
```

Use the integrated DATABASE-002 model as authoritative if exact relation names differ from the portable definition.

## Current schema facts to correct

The inspected baseline has:

```prisma
model Subscription {
  shopId          String @unique
  billingPeriodId String?
  billingPeriod   BillingPeriod?
}

model BillingPeriod {
  id            String @id
  shopId        String
  periodStart   DateTime
  periodEnd     DateTime
  status        BillingPeriodStatus
  subscriptions Subscription[]
  usageEvents   UsageEvent[]

  @@unique([shopId, periodStart, periodEnd])
}
```

Current reconciliation can create a newly-observed OPEN period without closing the previous OPEN period. The migration must normalize this before adding the new one-OPEN-period invariant.

## Required enum

Add an enum equivalent to:

```prisma
enum BillingPeriodCloseReason {
  RENEWED_SAME_PLAN
  PLAN_CHANGED
  CONTRACT_ENDED
  MIGRATION_RECONCILED

  @@schema("billing")
}
```

`PLAN_CHANGED` and `CONTRACT_ENDED` are schema vocabulary for later ARCH-010 transitions. This task must not implement those transitions.

Add a release reason enum or equivalent durable field that supports at minimum:

```prisma
enum UsageReservationReleaseReason {
  PERIOD_CLOSED

  @@schema("billing")
}
```

The field on `UsageReservation` must be nullable so existing Free/purchased reservation semantics remain compatible. Do not retroactively invent release reasons for existing rows.

## Subscription -> BillingPeriod ownership

Keep `Subscription.billingPeriodId` as the current-period pointer for backwards compatibility during ARCH-010.

Add a second, explicit ownership relation so one Subscription owns many BillingPeriods.

Conceptual target:

```prisma
model Subscription {
  billingPeriodId String?
  billingPeriod   BillingPeriod? @relation("CurrentSubscriptionBillingPeriod", ...)

  billingPeriods BillingPeriod[] @relation("SubscriptionBillingPeriods")
}

model BillingPeriod {
  subscriptionId String
  subscription   Subscription @relation("SubscriptionBillingPeriods", fields: [subscriptionId], references: [id], onDelete: Restrict)

  currentForSubscriptions Subscription[] @relation("CurrentSubscriptionBillingPeriod")
}
```

Use Prisma-valid relation names. Do not create a second Subscription record per billing period.

### Backfill subscriptionId

Because `Subscription.shopId` is unique, backfill each existing BillingPeriod by joining its `shopId` to that shop's durable Subscription.

Migration requirements:

1. add `subscriptionId` nullable;
2. backfill from `billing.Subscription.shopId`;
3. verify every BillingPeriod has exactly one matching Subscription;
4. if any BillingPeriod cannot be mapped unambiguously, fail/stop migration rather than guessing;
5. make `subscriptionId` NOT NULL only after successful verification;
6. add index `(subscriptionId, periodStart, periodEnd)`.

Do not delete historical periods.

## Period plan/allowance snapshot fields

Add nullable snapshot fields for historical compatibility:

```text
planId                              String?
shopifyPlanHandleSnapshot           String?
planNameSnapshot                    String?
planKindSnapshot                    BillingPlanKind?
includedRecoveryCreditsGranted      Int?
```

Add `planId -> BillingPlan` with `onDelete: SetNull` and an inverse relation on BillingPlan.

New Paid periods created after ARCH-010 must populate all five fields and set `includedRecoveryCreditsGranted` to the configured Paid monthly allowance.

New Free periods created after ARCH-010 must populate `planId`, `shopifyPlanHandleSnapshot`, `planNameSnapshot` and `planKindSnapshot = FREE`, and MUST set `includedRecoveryCreditsGranted = null`. A Free provider BillingPeriod exists to track Shopify's monthly commercial/usage-meter cycle; it MUST NOT create or imply a monthly Free recovery allowance. This schema task must not fabricate plan identity for historical CLOSED periods where the exact plan cannot be proven.

For the one current OPEN period pointed to by `Subscription.billingPeriodId`, the migration may backfill plan snapshot fields from the current Subscription/BillingPlan only when that identity is exact and unambiguous.

Do not copy today's plan onto every historical period.

## Close metadata

Add:

```text
closedAt    DateTime?
closeReason BillingPeriodCloseReason?
```

OPEN periods keep both null.

New ARCH-010 close transitions must write both fields. Historical periods may remain null unless the migration itself normalizes an orphaned OPEN row as described below.

## Normalize multiple legacy OPEN periods

Before adding the one-OPEN-period uniqueness rule, normalize the current baseline safely.

For each Subscription:

1. read `Subscription.billingPeriodId`;
2. if it points at one OPEN period, that row remains OPEN;
3. every other OPEN period owned by that same Subscription is changed to:

```text
status      = CLOSED
closedAt    = periodEnd
closeReason = MIGRATION_RECONCILED
```

4. if multiple OPEN periods exist and `billingPeriodId` is null, invalid, or does not identify one unambiguous current row, stop the migration and report the affected shop/subscription IDs. Do not pick the latest row heuristically.

If a Subscription has zero OPEN periods, do not fabricate one.


## Free-plan provider BillingPeriod invariant

A mapped active Free plan may have a Shopify monthly billing cycle even though its Moda recovery entitlement is lifetime. This distinction is mandatory when the Free Shopify App Pricing plan carries the recovery-credit-pack usage meter.

Database semantics:

```text
Free BillingPeriod
  = Shopify commercial / App Event billing-cycle record
  != Free recovery entitlement reset
```

For a Free BillingPeriod:

- `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)` MUST NOT be created;
- `includedRecoveryCreditsGranted` MUST be null;
- `FREE_RECOVERY_LIFETIME` remains the shop-level lifetime counter and is never reset by Free period creation/rollover;
- purchased lifetime credits are unchanged;
- UsageEvents for `RECOVERY_CREDIT_PACK_PURCHASE` may reference the exact current Free BillingPeriod so App Event reporting/reconciliation is cycle-scoped exactly like Paid pack purchases.

The migration MUST NOT fabricate a missing current Free BillingPeriod from plan configuration alone. It may backfill Free period plan snapshot fields only when the existing `Subscription.billingPeriodId` and exact current period are already unambiguous. Runtime reconciliation tasks own creation of a missing provider-confirmed Free period.

## Backfill current paid-period entitlement without resetting merchants

Existing ARCH-007/008 paid merchants may already have a current `Subscription.billingPeriodId` and normal paid `RECOVERY_CONVERSATION` UsageEvents but no `BillingPeriodEntitlementCounter`, because DATABASE-002 introduces that model after those usages were recorded.

For each current OPEN period whose current Subscription maps exactly to an active `PAID_METERED` BillingPlan:

1. require a non-null non-negative safe-integer `includedRecoveryConversationAllowance`;
2. populate current-period plan snapshot fields from that exact current BillingPlan;
3. calculate the existing **net normal paid recovery usage** for that BillingPeriod using the same scope the pre-ARCH-010 effective policy used:

```text
shopId = subscription.shopId
billingPeriodId = current BillingPeriod.id
metric = RECOVERY_CONVERSATION
shopifyEventHandle = current plan.shopifyUsageEventHandle
sum(quantity)
```

4. require the resulting quantity to be a non-negative integer; do not silently clamp corrupted/ambiguous data;
5. if the unique `INCLUDED_RECOVERY_CREDITS` period counter is absent, create it with:

```text
grantedQuantity   = includedRecoveryConversationAllowance
committedQuantity = min(existingNormalPaidUsage, includedRecoveryConversationAllowance)
reservedQuantity  = 0
forfeitedQuantity = 0
version            = 0
```

6. if a counter already exists, validate it and do not reset any quantity;
7. legacy normal paid usage beyond the configured allowance, if present in pre-ARCH-010 data, is migration history only and must **not** make `committedQuantity` exceed the grant or imply that ARCH-010 permits future overage.

Purchased-credit recoveries are not counted in this backfill because the accepted ARCH-007 model does not emit the normal paid recovery meter event for purchased-credit-funded recoveries.

This backfill prevents deployment from granting a fresh current-period allowance to an already-using paid merchant.

If the current period's usage cannot be scoped unambiguously to the current plan/meter, stop migration rather than guessing.

## One OPEN period invariant

Prisma cannot express a partial unique index. Add raw PostgreSQL migration SQL equivalent to:

```sql
CREATE UNIQUE INDEX ...
ON "billing"."BillingPeriod" ("subscriptionId")
WHERE "status" = 'OPEN';
```

Use the exact generated enum/storage syntax and quote names correctly.

Preserve the existing exact period uniqueness (`shopId`, `periodStart`, `periodEnd`) unless the generated/integrated schema already has a stricter equivalent. Do not weaken it.

## Period boundary integrity

Add/retain checks where practical:

```text
periodStart < periodEnd
includedRecoveryCreditsGranted IS NULL OR includedRecoveryCreditsGranted >= 0
```

Do not add a CHECK that requires plan snapshot fields on every legacy CLOSED period.

## UsageReservation period-close support

Add nullable:

```text
releaseReason UsageReservationReleaseReason?
```

Do not change the DATABASE-002 XOR rule: exactly one of shop-level `counterId` or period-level `billingPeriodEntitlementCounterId` remains required.

No migration should change existing reservation status, quantity, counter ownership or sourceKey.

## ERD / validator requirements

Update repository-owned validators/ERD generation narrowly.

Required assertions include:

1. BillingPeriod has non-null `subscriptionId` ownership relation;
2. Subscription retains one current `billingPeriodId` pointer and has historical `billingPeriods` relation;
3. plan snapshot fields exist and are nullable for legacy history;
4. close metadata exists;
5. releaseReason exists and is nullable;
6. migration backfills subscriptionId before NOT NULL;
7. migration normalizes extra legacy OPEN rows only using the current pointer;
8. partial unique one-OPEN-period index exists;
9. exact period uniqueness remains;
10. periodStart < periodEnd integrity exists;
11. current OPEN paid periods receive snapshot/counter backfill without resetting consumed allowance;
12. backfill committed quantity equals `min(existing normal paid recovery usage, configured included allowance)`;
13. invalid/ambiguous current usage causes migration failure rather than a guessed reset;
14. DATABASE-002 period entitlement counter/XOR/quantity constraints remain unchanged.

## Validation

Run exactly:

```bash
npm run format
npm run validate
npm run prisma:generate
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run erd:puml
git diff --check
```

If the migration validator uses a shadow/test database, follow the repository's existing documented command only; do not invent a destructive production migration test.

## Non-goals

Do not implement:

- rollover worker/service;
- BullMQ;
- Shopify calls;
- merchant UI;
- upgrade/downgrade/cancellation execution;
- top-up refund lot accounting;
- promotional-credit model (owned separately by DATABASE-009);
- SubscriptionEvent history beyond BillingPeriod history;
- Admin changes.

## Stop conditions

STOP and return to `moda_architect` if:

- any existing BillingPeriod cannot be mapped to exactly one Subscription;
- current paid-period usage cannot be scoped to one exact plan/meter for entitlement backfill;
- multiple OPEN rows exist without an unambiguous current pointer;
- the integrated schema already contains a conflicting BillingPeriod ownership/history model;
- adding the partial unique index would require guessing historical current state;
- DATABASE-002 reservation/counter constraints would need destructive rewrite.

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
