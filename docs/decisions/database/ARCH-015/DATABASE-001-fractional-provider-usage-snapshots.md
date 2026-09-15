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
status: complete
priority: 10
executor: null
claimed_at: null
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

## Completion Report

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-DATABASE-001` on `task/ARCH-015-DATABASE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-DATABASE-001` on `task/ARCH-015-DATABASE-001`.
- Shared/default checkout switched or mutated: no.
- Another task worktree reused: no.

### Start-of-Attempt Synchronization

- Parent remote task branch fast-forwarded: not-needed.
- Parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed.
- Implementation `origin/main` incorporated: already-current.
- Recursive submodule synchronization and initialization: passed; no recursive submodules were present.
- Launcher claim commit: recorded by the deterministic preparation packet.

### Implementation

- Changed only `RecoveryCreditPurchase.providerUsageQuantityBeforeSnapshot` and
	`providerUsageQuantityAfterSnapshot` from `Int`/`Int?` to `Decimal`/`Decimal?`.
- Added migration `20260915140000_arch015_fractional_provider_usage_snapshots`
	using lossless `DECIMAL(65,30)` casts for existing integer rows.
- Added the current-schema ARCH-015 validator and preserved the historical
	first-production `Int` assertion against the immutable baseline migration
	rather than the mutable current schema.
- Regenerated PlantUML and PNG ERD artifacts; only the two provider quantity
	types changed in the ERD.
- Preserved entitlement counters, purchase credit amounts, refund quantities,
	MerchantPricing models, enums, and existing valuation/state constraints.

### Validation Evidence

- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- Historical first-production baseline validator: passed.
- ARCH-015 current-schema validator: passed.
- `npm run migrate:deploy`: passed; the new migration applied successfully to
	a fresh local PostgreSQL database built from the ARCH-010/014-compatible
	migration chain.
- `npm run status`: passed; database schema is up to date.
- Fresh local database metadata confirmed both columns as `numeric(65,30)`.
- Fresh local Decimal probe preserved exact `0`, `1`, and `10`, accepted `3.75`,
	and accepted a nullable after value; entitlement and refund quantity
	columns remained PostgreSQL `integer`.
- ERD PlantUML and PNG regeneration: passed.
- Historical migration diff check: no historical migration files changed.
- `git diff --check`: passed.
- Implementation commit: `a61c4d1`.

### Revalidation Findings

- No implementation gap was found after comparing the canonical task against
	the schema, migration, validators, ERD, and focused checks.
- The configured shared database reported `npm run status` as up to date, but
	the mandated local database `moda_interact` contains a stale
	`RecoveryCreditPurchase` table shape despite its migration ledger naming
	ARCH-010/014 migrations. Applying ARCH-015 there fails because the two
	target columns do not exist. This is an environment baseline mismatch,
	not a migration defect; validation was therefore repeated successfully
	against a fresh local database created from the checked-in migrations.

### Completion Report Status

- Ready for architect review.
- Claim cleared; task lifecycle is `review`.

### Architect Review

The bounded evidence-type migration is complete and contains no database,
consumer, pricing, entitlement, refund, or enum expansion. Review commit
`a61c4d1` and promote the task according to the coordinator lifecycle.

## Architect Review — Attempt 1

### Status

**Accepted**

Architect review verified implementation commit
`a61c4d11ad06eded6eaf4097c593b46245332b76` against the ARCH-015 v1.1
database contract and the workflow-owned Completion Report at
`9ac512838f7651f513f70f22397329433afaa3d8`.

The implementation satisfies the functional contract:

```text
RecoveryCreditPurchase.providerUsageQuantityBeforeSnapshot: Int -> Decimal
RecoveryCreditPurchase.providerUsageQuantityAfterSnapshot:  Int? -> Decimal?
existing integer evidence is cast losslessly to DECIMAL(65,30)
UsageEvent.quantity remains Decimal
entitlement / owned-credit / refund-credit quantities remain Int
no new model, enum, lock, refund or pricing schema is introduced
existing purchase valuation/state constraints remain in force
```

The migration is additive to the accepted migration chain and does not rewrite
historical migration SQL. The historical first-production validator continues to
assert the immutable historical `INTEGER` baseline, while the ARCH-015 validator
asserts the current Decimal schema and migration. The generated ERD reflects only
the two authorised provider-evidence type changes.

The executor's revalidation correctly distinguishes the stale local `moda_interact`
fixture from migration correctness. The mandated migration applies successfully to a
fresh database created from the checked-in ARCH-010/014-compatible migration chain,
with exact integer preservation, fractional `3.75` support, nullable after-snapshot
support, and integer entitlement/refund quantities. The stale local fixture is an
environment-baseline limitation and is not a production implementation defect.

No further implementation attempt is required.

### Dependency reconciliation

`ARCH-015-DATABASE-001` is now **Complete**.

Do not promote an enabled dependant solely from this acceptance. In the reviewed
workspace snapshot, `ARCH-015-SHOPIFY-002` still also depends on
`ARCH-015-SHOPIFY-001`; `ARCH-015-BACKGROUND-001` additionally depends on
`ARCH-015-SHOPIFY-002`; and `ARCH-015-BACKGROUND-003` additionally depends on the
later purchase/reconciliation/refund path.

The user has separately stated that `ARCH-015-SHARED-001` has been marked Complete.
That newer Shared lifecycle edit is intentionally not rewritten by this DATABASE
review patch because it is outside this task's workflow-owned files and is not present
in the uploaded DATABASE-001 snapshot. Reconcile the combined frontier after those
branches/states are brought together.
