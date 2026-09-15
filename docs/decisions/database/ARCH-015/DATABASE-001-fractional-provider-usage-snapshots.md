---
id: ARCH-015-DATABASE-001
architecture_id: ARCH-015
title: Allow fractional Shopify provider-usage purchase snapshots
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-15T13:05:21Z
attempt: 1
depends_on:
- ARCH-014-DATABASE-001
enables:
- ARCH-015-SHOPIFY-002
- ARCH-015-BACKGROUND-001
- ARCH-015-BACKGROUND-003
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-DATABASE-001

## Objective

Make the existing `RecoveryCreditPurchase` provider quantity-before/after evidence capable of storing exact fractional Shopify meter quantities after negative/fractional App Event corrections.

This is a bounded evidence-type migration only.

## Required schema change

Change exactly:

```prisma
providerUsageQuantityBeforeSnapshot Int
providerUsageQuantityAfterSnapshot  Int?
```

to:

```prisma
providerUsageQuantityBeforeSnapshot Decimal
providerUsageQuantityAfterSnapshot  Decimal?
```

Use the repository's normal Prisma Decimal defaults. Do not reduce precision below the existing `UsageEvent.quantity` Decimal representation.

## Migration

Create one new ARCH-015 migration after the accepted current baseline.

Use safe PostgreSQL casts for existing integer rows to Decimal/Numeric. Existing integer values must preserve exact numeric value.

Do NOT edit or rewrite historical migration SQL.

Do NOT change:

```text
UsageEvent.quantity                     # already Decimal
creditsGranted/currentAmount/reservedAmount
ShopEntitlementCounter integer quantities
RecoveryCreditRefund credit quantities
any MerchantPricing* table
any enum
```

## Integrity/validation

Preserve all existing purchase valuation/state constraints.

Any constraint that only tests `IS NULL`/`IS NOT NULL` remains semantically unchanged.

Update current-schema validators and generated ERD to reflect Decimal provider quantities.

If a validator is specifically intended to prove the immutable historical first-production baseline, do not falsify that historical assertion. Add/update a current-schema ARCH-015 validation instead.

## Required tests/checks

- Prisma validates/generates.
- migration applies to an ARCH-010/014-compatible database;
- integer `0`, `1`, `10` become exact Decimals;
- schema permits `3.75` before snapshot;
- schema permits nullable fractional after snapshot;
- entitlement integer fields remain Int;
- historical migration files unchanged;
- ERD regenerated.

## Validation

Use repository scripts where available:

```text
npx prisma validate
npx prisma generate
npx prisma migrate deploy
# current schema validation scripts
# ERD generation
git diff --check
```

## Stop conditions

STOP if:

- migration requires changing entitlement counters to Decimal;
- additional model/enum/lock/refund fields appear necessary;
- current production data contains values that cannot be converted losslessly;
- changing these two fields breaks an existing database invariant not addressable by type-safe consumer updates.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
