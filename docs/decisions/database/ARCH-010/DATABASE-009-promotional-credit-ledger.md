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
status: in_progress
priority: 81
executor: copilot
claimed_at: 2026-09-11T15:30:00Z
attempt: 2
depends_on:
  - ARCH-007-DATABASE-002
enables:
  - ARCH-010-ADMIN-004
  - ARCH-010-BACKGROUND-019
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-020
created: 2026-09-11
updated: 2026-09-11T15:30:00Z
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
In Progress

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

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested

The ARCH-010-DATABASE-009 target schema is directionally correct, but the migration does not actually migrate the PostgreSQL `billing.EntitlementCounter` enum to the new schema value. This creates schema/migration drift and is a blocking database correctness issue.

##### Accepted implementation findings

Architect review verified the following and does not request redesign of them:

- `EntitlementCounter` in `schema.prisma` contains `PROMOTIONAL_RECOVERY_CREDITS` alongside the existing lifetime-Free and purchased-credit counters;
- `PromotionalCreditGrantType` contains the required grant provenance vocabulary;
- `PromotionalCreditGrant` has positive quantity, mandatory bounded reason, optional campaign reference, globally unique request key, PlatformAdmin provenance and created timestamp;
- Shop and PlatformAdmin reverse relations are present;
- the Shop and PlatformAdmin relations use `onDelete: Restrict`;
- the migration creates the grant type/table, unique request-key index, shop/campaign/admin provenance indexes, restrictive foreign keys, and the positive-quantity CHECK;
- `BillingAuditAction.PROMOTIONAL_CREDITS_GRANTED` is present in the Prisma schema and the migration adds it to the PostgreSQL enum;
- the migration is row-free: it creates no promotional counter/grant for existing shops and does not reinterpret `BillingAllowanceAdjustment`, lifetime-Free balances, purchased-credit balances/lots, BillingPeriods, or subscription state;
- no promotional expiry field or Shopify billing identifier/event is introduced;
- the Completion Report contains the canonical parent/implementation worktrees and all four start-of-attempt synchronization outcomes.

##### Correction 1 — migrate the PostgreSQL entitlement enum

The Prisma schema adds:

```prisma
enum EntitlementCounter {
  FREE_RECOVERY_LIFETIME
  PURCHASED_RECOVERY_CREDITS
  PROMOTIONAL_RECOVERY_CREDITS
}
```

but `20260911150000_add_promotional_credit_grants/migration.sql` never adds the new value to the existing PostgreSQL enum.

No migration anywhere in the submitted database history contains `PROMOTIONAL_RECOVERY_CREDITS`.

Add the migration operation, using the repository's existing PostgreSQL enum convention, equivalent to:

```sql
ALTER TYPE "billing"."EntitlementCounter"
  ADD VALUE 'PROMOTIONAL_RECOVERY_CREDITS';
```

Do not create a replacement enum or rewrite existing counter rows. This must remain an additive enum extension.

##### Correction 2 — make the validator prove schema/migration alignment

The current billing-policy validator proves that the Prisma schema contains the promotional counter, but it does not prove that the migration adds that value to the database enum. That allowed this defect to pass validation.

Strengthen `scripts/validate-billing-policy-schema.mjs` so it deterministically proves at least:

1. the Prisma `EntitlementCounter` still contains the pre-existing:
   - `FREE_RECOVERY_LIFETIME`;
   - `PURCHASED_RECOVERY_CREDITS`;
   - and the new `PROMOTIONAL_RECOVERY_CREDITS`;
2. the DATABASE-009 migration contains the `ALTER TYPE "billing"."EntitlementCounter" ... ADD VALUE 'PROMOTIONAL_RECOVERY_CREDITS'` operation;
3. the DATABASE-009 migration contains the `PROMOTIONAL_CREDITS_GRANTED` BillingAuditAction enum extension;
4. the Shop and PlatformAdmin relations are present with `onDelete: Restrict` in the Prisma model and/or equivalent restrictive foreign-key evidence in the migration;
5. the existing no-row/no-reinterpretation guards remain intact.

Keep the existing positive quantity, uniqueness, optional campaign reference, index, and migration no-rewrite assertions.

##### Scope guard

Do not redesign the accepted promotional-credit schema.

Attempt 2 should be limited to:

- the missing additive PostgreSQL enum migration operation;
- focused validator strengthening;
- any normal formatting/generated artifact refresh genuinely required by those changes;
- Completion Report/VCS evidence.

Do not implement Admin actions/UI, credit consumption, campaign expiry, Shopify App Events, refunds, bulk campaigns, or runtime entitlement behaviour.

##### Attempt 2 validation

After the normal canonical-worktree synchronization and successful Attempt 2 claim, rerun the task's repository-declared validation contract:

```text
npm run format
npm run prisma:generate
npm run prisma:validate
npm run test:billing-policy
git diff --check
```

If the repository/task already uses migration-status inspection in this worktree, it may remain inspection-only. Do not apply DATABASE-009 to the shared database merely for architect review.

Return the same task to `review` with the updated Completion Report and published implementation/parent branches.

