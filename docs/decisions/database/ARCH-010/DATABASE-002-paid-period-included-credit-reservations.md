---
id: ARCH-010-DATABASE-002
architecture_id: ARCH-010
title: Add period-scoped paid included-credit reservation state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 41
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-010-DATABASE-001
  - ARCH-007-DATABASE-005
enables:
  - ARCH-010-BACKGROUND-002
  - ARCH-010-BACKGROUND-003
  - ARCH-010-DATABASE-004
  - ARCH-010-SHOPIFY-003
  - ARCH-010-SHOPIFY-004
created: 2026-09-11
updated: 2026-09-11T23:14:12Z
---

# ARCH-010-DATABASE-002: Add period-scoped paid included-credit reservation state

## Objective

Add the smallest durable schema required for concurrency-safe paid included-credit consumption in one exact Shopify BillingPeriod, while preserving the existing Free lifetime counter and purchased-credit counter unchanged.

This task does **not** implement the broader future ARCH-010 subscription-history, partial-refund-lot or billing-period rollover schema. Those are later lifecycle tasks.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-recovery-credit-pack-schema.mjs
scripts/validate-billing-lifecycle-schema.mjs
package.json
docs/generated/prisma-erd.puml
```

Also inspect the canonical ARCH-010 architecture before editing:

```text
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
```

## Existing state that must be preserved

The current schema has:

```text
EntitlementCounter.FREE_RECOVERY_LIFETIME
EntitlementCounter.PURCHASED_RECOVERY_CREDITS
ShopEntitlementCounter
UsageReservation.counterId -> ShopEntitlementCounter
BillingPeriod(id, shopId, periodStart, periodEnd, status)
Subscription.billingPeriodId -> current BillingPeriod
```

Do **not** rename `FREE_RECOVERY_LIFETIME` to promotional credits. The shop-lifetime introductory grant and `PROMOTIONAL_RECOVERY_CREDITS` are separate concepts; promotional schema is owned by `ARCH-010-DATABASE-009`.

Do not change `RecoveryCreditPurchase`, refund cardinality or purchased-credit lot accounting in this task.

## Required schema

### 1. Add period counter enum

Add:

```prisma
enum BillingPeriodEntitlementCounterKind {
  INCLUDED_RECOVERY_CREDITS

  @@schema("billing")
}
```

### 2. Add BillingPeriodEntitlementCounter

Add a model equivalent to:

```prisma
model BillingPeriodEntitlementCounter {
  id String @id @default(cuid())

  shopId String
  shop   Shop @relation(fields: [shopId], references: [id], onDelete: Cascade)

  billingPeriodId String
  billingPeriod   BillingPeriod @relation(fields: [billingPeriodId], references: [id], onDelete: Cascade)

  counter           BillingPeriodEntitlementCounterKind
  grantedQuantity   Int @default(0)
  committedQuantity Int @default(0)
  reservedQuantity  Int @default(0)
  forfeitedQuantity Int @default(0)
  version            Int @default(0)

  reservations UsageReservation[] @relation("BillingPeriodUsageReservations")

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([billingPeriodId, counter])
  @@index([shopId, billingPeriodId])
  @@schema("billing")
}
```

Add reverse relations on `Shop` and `BillingPeriod` using architecture-consistent names.

### 3. Extend UsageReservation without breaking existing reservations

Preserve the existing shop-level counter relation for Free/purchased reservations. Add a second optional relation for period-scoped included reservations.

The intended end state for this task is conceptually:

```prisma
counterId String?
counter   ShopEntitlementCounter? @relation("ShopEntitlementUsageReservations", ...)

billingPeriodEntitlementCounterId String?
billingPeriodEntitlementCounter   BillingPeriodEntitlementCounter? @relation("BillingPeriodUsageReservations", ...)
```

Name the existing `ShopEntitlementCounter.reservations` relation explicitly as `ShopEntitlementUsageReservations` if Prisma requires disambiguation.

Migration requirements:

- existing rows with `counterId` remain valid and preserve their exact foreign key;
- `counterId` becomes nullable only because new paid-period reservations use the new relation;
- new `billingPeriodEntitlementCounterId` is nullable;
- add an index on `billingPeriodEntitlementCounterId`;
- database must reject a reservation that points to **both** counter families or **neither** counter family. Prisma cannot express this XOR invariant; add a PostgreSQL CHECK constraint in the migration:

```text
(counterId IS NOT NULL) <> (billingPeriodEntitlementCounterId IS NOT NULL)
```

Use actual quoted schema/table/column names from the generated migration rather than copying pseudo-SQL blindly.

Do not add a new reservation source enum in this task unless it is genuinely required by Prisma/runtime correctness. Counter relation identity is sufficient for this bounded paid-period reservation task.

### 4. Quantity integrity

Add database CHECK constraints, if equivalent constraints do not already exist, guaranteeing for `BillingPeriodEntitlementCounter`:

```text
grantedQuantity >= 0
committedQuantity >= 0
reservedQuantity >= 0
forfeitedQuantity >= 0
committedQuantity + reservedQuantity + forfeitedQuantity <= grantedQuantity
```

Do not add a constraint that prevents later period-close logic from atomically moving remaining capacity into `forfeitedQuantity`.

## Migration safety

This task intentionally avoids reshaping `BillingPeriod` ownership/history, so no historical plan snapshot needs to be fabricated.

Existing `UsageReservation` rows must migrate losslessly. Do not delete/recreate reservations or counters.

If the integrated database already contains a newer ARCH-010 period-counter model, STOP and return the schema delta to `moda_architect` rather than creating a competing model.

## Generated client / mirror expectations

Canonical schema/migration ownership is `moda-interact-database`. Do not edit `moda-interact` or `moda-interact-background` from this task.

Downstream tasks will consume the generated Prisma shape after the developer performs the normal integration/submodule/database propagation workflow.

## Required validation

Run exactly the repository-declared relevant commands:

```bash
npm run format
npm run validate
npm run prisma:generate
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run erd:puml
git diff --check
```

If an existing validator must be updated because it asserts the old non-null `UsageReservation.counterId`, update it narrowly and add assertions for:

1. `BillingPeriodEntitlementCounterKind` exists;
2. `BillingPeriodEntitlementCounter` exists;
3. unique `(billingPeriodId, counter)` exists;
4. `UsageReservation.counterId` is nullable;
5. `billingPeriodEntitlementCounterId` exists and is indexed;
6. migration preserves old counter FK and adds the new FK;
7. XOR CHECK constraint exists;
8. non-negative/capacity CHECK constraints exist;
9. `FREE_RECOVERY_LIFETIME` still exists;
10. `PURCHASED_RECOVERY_CREDITS` still exists.

## Non-goals

Do not implement:

- application callback logic;
- Background reservation services;
- plan changes;
- billing-period close/open rollover;
- SubscriptionEvent history;
- promotional-credit grants;
- partial refund lots/allocation;
- UI;
- BullMQ;
- Admin changes.

## Stop conditions

STOP and return to `moda_architect` if:

- preserving existing UsageReservation rows requires destructive migration;
- a newer integrated schema already provides an incompatible period reservation model;
- adding the XOR constraint exposes existing invalid rows;
- the task would require fabricating historical BillingPeriod plan identity.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260911160000_add_billing_period_entitlement_reservations/migration.sql`
- `scripts/validate-billing-lifecycle-schema.mjs`
- `docs/generated/prisma-erd.puml`

### Work Completed
- Added `BillingPeriodEntitlementCounterKind.INCLUDED_RECOVERY_CREDITS` and `BillingPeriodEntitlementCounter` with the billing-period uniqueness rule, shop/period access index, reverse relations, and quantity fields.
- Extended `UsageReservation` with nullable `counterId` and optional `billingPeriodEntitlementCounterId`, preserving the existing named shop-counter relation and adding the indexed period-counter relation.
- Added an additive migration that preserves the existing `UsageReservation_counterId_fkey`, makes only its column nullable, adds the new period-counter FK/index, and rejects both/neither counter families through an XOR CHECK.
- Added non-negative checks for all period-counter quantities and a capacity check allowing close logic to move remaining capacity into `forfeitedQuantity` without exceeding the grant.
- Kept `FREE_RECOVERY_LIFETIME`, `PURCHASED_RECOVERY_CREDITS`, purchased-credit purchase/refund models, and lot accounting unchanged. No application or worker repositories were modified.
- Updated the billing lifecycle validator with all ten required period-reservation and legacy-counter assertions; regenerated the PlantUML ERD.

### Validation Results
- `npm ci` passed in the isolated implementation worktree to restore declared dependencies; npm reported three existing high-severity audit findings.
- `npm run format` passed.
- `npm run validate` passed.
- `npm run prisma:generate` passed with Prisma Client `6.19.3`.
- `npm run test:recovery-credit-packs` passed.
- `npm run test:billing-lifecycle` passed, including all ten required assertions.
- `npm run erd:puml` passed and emitted the new period counter/relation edges.
- `git diff --check` passed after removing two generator-produced trailing spaces from the updated ERD.
- No migration was applied to a database; the migration is additive and preserves existing rows/FKs without backfill or destructive table/row operations.

### Git / VCS
Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-002`
  parent branch: `task/ARCH-010-DATABASE-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-002`
  implementation branch: `task/ARCH-010-DATABASE-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation commit: `8a68686 feat(database): add paid period credit reservations`; implementation branch pushed to origin.
Parent claim commit: `d6e770b chore: claim ARCH-010-DATABASE-002`; parent report branch updated below and pushed to origin.
Neither task branch was merged to `main`; parent submodule gitlink was not staged.

### Architect Review

#### Review Status

Accepted

#### Attempt 1 — Accepted

Architect review verified:

- `BillingPeriodEntitlementCounterKind` is added in the billing schema with the
  required `INCLUDED_RECOVERY_CREDITS` value;
- `BillingPeriodEntitlementCounter` is added with:
  - durable Shop ownership;
  - exact BillingPeriod ownership;
  - unique `(billingPeriodId, counter)`;
  - `(shopId, billingPeriodId)` access index;
  - granted/committed/reserved/forfeited quantities;
  - optimistic `version`;
  - reverse UsageReservation relation;
- `Shop` and `BillingPeriod` contain the corresponding reverse relations;
- the pre-existing `ShopEntitlementCounter.reservations` relation is explicitly
  named `ShopEntitlementUsageReservations` without changing its semantics;
- `UsageReservation.counterId` is made nullable without deleting/recreating rows
  or replacing the existing `UsageReservation_counterId_fkey`;
- `UsageReservation.billingPeriodEntitlementCounterId` is added as a nullable,
  indexed second counter-family relation;
- the migration adds the new period-counter foreign key with the intended cascade
  semantics;
- the PostgreSQL `UsageReservation_counter_family_xor` CHECK enforces exactly one
  counter family per reservation, rejecting both-counter and no-counter rows;
- the period counter has explicit non-negative CHECKs for granted, committed,
  reserved and forfeited quantities;
- the capacity CHECK enforces
  `committed + reserved + forfeited <= granted` without preventing later period
  close logic from moving unused capacity into forfeited quantity;
- existing `FREE_RECOVERY_LIFETIME` and `PURCHASED_RECOVERY_CREDITS` counter
  vocabulary remains present and unchanged;
- no purchased-credit purchase/refund/lot model was redesigned by this task;
- the migration is additive and contains no destructive reservation/counter
  rewrite or historical BillingPeriod-plan fabrication;
- `validate-billing-lifecycle-schema.mjs` contains the required assertions for the
  new enum/model/uniqueness, nullable old relation, new indexed relation, preserved
  old FK/new FK, XOR constraint, quantity/capacity checks and legacy counters;
- the generated ERD contains the new period counter and relation surface;
- the declared validation contract passed:
  - `npm run format`;
  - `npm run validate`;
  - `npm run prisma:generate`;
  - `npm run test:recovery-credit-packs`;
  - `npm run test:billing-lifecycle`;
  - `npm run erd:puml`;
  - `git diff --check`;
- no migration was applied to a shared database during review;
- the Completion Report records the canonical parent and implementation worktrees,
  confirms neither shared checkout nor another task worktree was reused, and
  records all four start-of-attempt synchronization outcomes;
- implementation commit `8a68686` is the reviewed implementation head;
- the submitted handoff identifies final parent review-report commit `f113a6b`.

The final parent report hash is external handoff evidence and is not required to be
self-embedded into the commit that contains this same task file.

**Architect decision: Accepted.**

Because `completion_mode: automatic`, this task is complete. `executor` and
`claimed_at` are cleared while `attempt: 1` is preserved.

Dependency reconciliation:

- `ARCH-010-DATABASE-004` depends only on this task and is promoted to `ready`;
- `ARCH-010-BACKGROUND-002` remains pending because it still has additional
  Background/ARCH-007 prerequisites;
- `ARCH-010-BACKGROUND-003` remains pending because it still depends on
  DATABASE-004 and several Background prerequisites;
- `ARCH-010-SHOPIFY-003` remains pending because it still depends on DATABASE-004,
  BACKGROUND-002, BACKGROUND-003, SHOPIFY-002 and other prerequisites;
- `ARCH-010-SHOPIFY-004` remains pending because SHOPIFY-003 is not yet complete.

