---
id: ARCH-010-DATABASE-006
architecture_id: ARCH-010
title: Move the one-time lifetime Free recovery grant to platform policy and snapshot it per shop
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-007-DATABASE-002
  - ARCH-007-DATABASE-003
enables:
  - ARCH-010-ADMIN-001
  - ARCH-010-BACKGROUND-001
  - ARCH-010-BACKGROUND-003
  - ARCH-010-BACKGROUND-011
  - ARCH-010-SHOPIFY-002
  - ARCH-010-SHOPIFY-003
  - ARCH-010-SHOPIFY-009
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-DATABASE-006: Move the one-time lifetime Free recovery grant to platform policy and snapshot it per shop

## Objective

Make the existing five lifetime Free recoveries a **shop-lifetime introductory entitlement** that is granted once when a merchant first obtains any verified Moda subscription, whether Free or Paid.

The grant MUST NOT be owned by the current `BillingPlan` and MUST NOT reset on upgrade, downgrade, renewal, uninstall or reinstall.

## Inspect before editing

```text
prisma/schema.prisma
prisma/seed.mjs
prisma/migrations/**
scripts/validate-billing-policy-schema.mjs
scripts/validate-recovery-credit-pack-schema.mjs
package.json
```

Also inspect the accepted ARCH-007 migrations that introduced:

```text
BillingPlan.freeLifetimeConversationAllowance
PlatformBillingPolicy
ShopEntitlementCounter
BillingAllowanceAdjustment
```

Do not remove a legacy column without an explicit migration/compatibility reason.

## Required schema change

Add to `billing.PlatformBillingPolicy`:

```prisma
lifetimeFreeRecoveryAllowance Int @default(5)
```

Required invariant:

```text
lifetimeFreeRecoveryAllowance >= 0
```

Add a database CHECK constraint for the non-negative invariant.

The platform-policy value is a **template for a shop's first grant**. It is not a live balance and MUST NOT retroactively change existing shops when an administrator changes the default later.

## Existing BillingPlan field

`BillingPlan.freeLifetimeConversationAllowance` currently exists and is used by ARCH-007 code.

For this task:

- keep the column for backward compatibility;
- do not drop/rename it;
- document it as legacy/non-authoritative for ARCH-010 runtime entitlement;
- dependent ARCH-010 application/background tasks MUST stop reading it as the lifetime-grant authority.

A later cleanup architecture may remove it after all consumers are migrated.

## Shop-level snapshot semantics

The durable per-shop base grant is:

```text
ShopEntitlementCounter
  counter = FREE_RECOVERY_LIFETIME
  grantedQuantity = grant captured once at first verified activation
```

After creation:

- `grantedQuantity` is never reset because the Shopify plan changes;
- `grantedQuantity` is never replaced merely because `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` later changes;
- `committedQuantity` and `reservedQuantity` are lifetime usage state;
- signed `BillingAllowanceAdjustment` rows remain additive administrative adjustments and are separate from the base grant;
- `refundingQuantity` is not used to make lifetime Free credits refundable.

## Existing-shop migration/backfill

Existing merchants may already have completed onboarding while their `FREE_RECOVERY_LIFETIME` counter has `grantedQuantity = 0`, because the old runtime derived the allowance from `BillingPlan.freeLifetimeConversationAllowance`.

The migration MUST backfill only shops with:

```text
ShopSettings.onboardingCompleted = true
```

For each such shop:

1. if no `FREE_RECOVERY_LIFETIME` counter exists, insert one with:

```text
grantedQuantity   = 5
committedQuantity = 0
reservedQuantity  = 0
refundingQuantity = 0
version            = 0
```

2. if the counter exists and `grantedQuantity = 0`, set `grantedQuantity = 5` and increment `version` exactly once;
3. if `grantedQuantity > 0`, preserve it exactly;
4. preserve every existing `committedQuantity`, `reservedQuantity` and `refundingQuantity` exactly;
5. do not create a grant for a fresh shop whose onboarding is incomplete;
6. do not inspect current plan kind when deciding whether an already-onboarded shop receives the backfill.

The value `5` is the current agreed product grant for the migration cohort. Future first activations read the current platform-policy value instead.

The SQL migration must be deterministic and idempotent under normal migration replay protections. If inserting IDs directly in SQL, use a deterministic text identifier derived from shop id/counter rather than relying on unavailable Prisma `cuid()` generation.

## Seed/default state

Update seed/default platform policy so:

```text
lifetimeFreeRecoveryAllowance = 5
```

Do not use the Free `BillingPlan` seed row as the source for this platform-policy value.

## Required validation

Add/update deterministic schema tests proving:

1. `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` exists;
2. it defaults to 5;
3. negative values are rejected by database integrity;
4. the legacy `BillingPlan.freeLifetimeConversationAllowance` column still exists for compatibility;
5. migration backfill targets onboarded Free merchants;
6. migration backfill targets onboarded Paid merchants;
7. incomplete onboarding is not granted;
8. missing counter receives one grant;
9. existing zero-grant counter receives one grant and preserves usage;
10. existing positive grant is not overwritten;
11. committed/reserved/refunding quantities are preserved;
12. migration does not create a period entitlement counter.

Run the repository-declared Prisma/schema validations from `package.json`; do not invent unavailable scripts.

## Non-goals

Do not:

- change runtime recovery routing;
- change merchant UI;
- change Shopify plan configuration;
- remove the legacy BillingPlan field;
- add promotional-credit semantics;
- make lifetime Free credits refundable;
- reset an existing merchant's lifetime usage.

## Stop conditions

Stop and return to `moda_architect` if:

- the current schema no longer contains the expected counter/platform-policy models;
- a safe existing-shop backfill cannot distinguish completed onboarding;
- existing data contains a conflicting representation that would require destructive entitlement rewriting;
- implementation would require changing another repository.

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
