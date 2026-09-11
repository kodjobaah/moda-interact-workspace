---
id: ARCH-010-DATABASE-009
architecture_id: ARCH-010
title: Add durable promotional recovery-credit grants and aggregate entitlement counter
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 81
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-DATABASE-002
enables:
  - ARCH-010-ADMIN-004
  - ARCH-010-BACKGROUND-019
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-020
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-DATABASE-009: Add durable promotional recovery-credit grants and aggregate entitlement counter

## Objective

Introduce a durable **promotional recovery-credit** bucket that is independent from:

- paid monthly included entitlement;
- purchased lifetime top-ups;
- the one-time shop-lifetime Free grant.

Promotional credits are Moda-funded, shop-specific, non-refundable, lifetime-until-used for ARCH-010, and create no Shopify billing/App Event.

They support use cases including targeted merchant campaigns, beta/test merchants, goodwill and support grants.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
prisma/seed.mjs
scripts/validate-billing-policy-schema.mjs
scripts/validate-recovery-credit-pack-schema.mjs
package.json
```

Also inspect the accepted models/enums for:

```text
EntitlementCounter
ShopEntitlementCounter
UsageReservation
BillingAllowanceAdjustment
BillingAuditAction
PlatformAdmin
Shop
```

Do not redesign those models unless explicitly required below.

## 1. Add a dedicated entitlement counter

Extend `billing.EntitlementCounter` with:

```text
PROMOTIONAL_RECOVERY_CREDITS
```

Canonical aggregate balance:

```text
ShopEntitlementCounter(counter = PROMOTIONAL_RECOVERY_CREDITS)

grant total      = grantedQuantity
used total       = committedQuantity
in-flight total  = reservedQuantity
remaining        = max(grantedQuantity - committedQuantity - reservedQuantity, 0)
```

`refundingQuantity` is a generic field on `ShopEntitlementCounter` but MUST remain zero for promotional credits. Promotional credits are not refundable.

A missing promotional counter means zero promotional capacity. Do **not** create a zero row for every existing shop during migration.

## 2. Promotional grant provenance ledger

Add an enum equivalent to:

```text
PromotionalCreditGrantType
  CAMPAIGN
  BETA_TESTER
  GOODWILL
  SUPPORT
  INTERNAL_TEST
  OTHER
```

Add a model equivalent to:

```text
PromotionalCreditGrant
  id
  shopId
  quantity
  grantType
  reason
  campaignReference?          // internal attribution/grouping only
  requestKey                  // globally unique idempotency key
  platformAdminId
  createdAt
```

Required relations:

- `shopId -> Shop` with `onDelete: Restrict`;
- `platformAdminId -> PlatformAdmin` with `onDelete: Restrict`.

Required invariants/indexes:

- `quantity > 0` enforced by database CHECK constraint;
- `requestKey` unique;
- index `(shopId, createdAt)`;
- index `(campaignReference, createdAt)` when campaignReference is not null or the closest Prisma/PostgreSQL-supported equivalent;
- index `(platformAdminId, createdAt)`.

`reason` is mandatory audit context and should use the existing bounded reason size convention (currently `VarChar(1000)`).

`campaignReference` is internal metadata. It is not a Shopify identifier and does not make credits expire.

## 3. Audit vocabulary

Extend `BillingAuditAction` with:

```text
PROMOTIONAL_CREDITS_GRANTED
```

Do not reuse `FREE_ALLOWANCE_ADJUSTED` for promotional grants.

## 4. No migration grant / no semantic reinterpretation

The migration MUST NOT:

- grant promotional credits to any existing shop;
- reinterpret historical `BillingAllowanceAdjustment` rows as promotions;
- alter `FREE_RECOVERY_LIFETIME` balances;
- alter purchased-credit balances/lots;
- alter BillingPeriods;
- alter subscription state.

Existing signed Free allowance adjustments are historically ambiguous and remain attached to the lifetime-Free counter unless a later explicitly authorised migration says otherwise.

## 5. No expiry in ARCH-010

Do not add `expiresAt` to the grant or counter in this task.

ARCH-010 promotional credits are lifetime-until-used. Expiring campaigns require a separate future lifecycle because expiry would need reservation-safe revocation/scheduling semantics.

## 6. Shop and PlatformAdmin relations

Add the minimum reverse relations required by Prisma to `Shop` and `PlatformAdmin`.

Do not expose these internal audit rows to merchants at schema level.

## Required validation

Add deterministic schema/migration validation proving at minimum:

1. `PROMOTIONAL_RECOVERY_CREDITS` exists in `EntitlementCounter`;
2. existing entitlement enum values remain;
3. `PromotionalCreditGrant` contains required shop/admin relations;
4. quantity must be positive;
5. requestKey is unique;
6. campaignReference is optional;
7. grant provenance indexes exist;
8. `PROMOTIONAL_CREDITS_GRANTED` audit action exists;
9. migration creates no promotional grants/counters for existing shops;
10. migration does not rewrite `BillingAllowanceAdjustment`;
11. migration does not change lifetime Free or purchased counters;
12. schema still validates/generated Prisma client builds under repository-declared commands.

Run only repository-declared schema/Prisma validation commands and `git diff --check`.

## Non-goals

Do not:

- implement Admin grant UI/actions;
- implement recovery consumption;
- add campaign expiry;
- add Shopify App Events;
- make promotional credits refundable;
- add a Shopify plan field for promotional allowance;
- alias promotional grants to the five lifetime Free credits;
- add bulk campaign execution logic.

## Stop conditions

Stop and return to `moda_architect` if:

- `ShopEntitlementCounter` no longer supports a new shop-level counter safely;
- existing migrations already use a conflicting promotional concept;
- adding grant provenance would require destructive rewrites of historical allowance adjustments;
- implementation requires another repository.

## Completion Report

### Status
Implemented; awaiting Architect Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260911150000_add_promotional_credit_grants/migration.sql`
- `scripts/validate-billing-policy-schema.mjs`

### Work Completed
- Added the non-refundable `PROMOTIONAL_RECOVERY_CREDITS` entitlement counter without creating counters for existing shops.
- Added `PromotionalCreditGrant` provenance with bounded reason, optional campaign reference, globally unique request key, restrictive Shop and PlatformAdmin relations, positive quantity CHECK, and required indexes.
- Added the `PROMOTIONAL_CREDITS_GRANTED` billing audit action.
- Kept the migration additive and row-free: it does not rewrite allowance adjustments, lifetime-Free or purchased balances, BillingPeriods, subscriptions, or seed promotional grants/counters.
- Added deterministic validator coverage for the enum/model/index/constraint contract and migration no-rewrite/no-grant safeguards.

### Validation Results
- `npm run format` passed.
- `npm run prisma:generate` passed with Prisma 6.19.3.
- `npm run prisma:validate` passed.
- `npm run test:billing-policy` passed.
- `git diff --check` passed.
- No migration was applied to the configured database.

### Git / VCS
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-009`.
- Parent branch: `task/ARCH-010-DATABASE-009`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-009`.
- Implementation branch: `task/ARCH-010-DATABASE-009`.
- Implementation commit: `597b991` (`feat(database): add promotional recovery credit grants`).
- Parent claim commit: `c321557`.
- Both mirrored task branches were pushed to their respective origins.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.
- No main branch was pushed and no submodule gitlink was staged.

### Start-of-attempt Synchronization
- Parent remote task branch fast-forwarded: not-needed; branch was newly created from current `origin/main`.
- Parent `origin/main` incorporated: already-current at claim.
- Implementation remote task branch fast-forwarded: not-needed; branch was newly created from current `origin/main`.
- Implementation `origin/main` incorporated: already-current.

### Architect Review
Pending.
