---
id: ARCH-078-DATABASE-001
architecture_id: ARCH-078
title: Persist unmapped Shopify usage-event handles on Subscription
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: [ARCH-078-BACKGROUND-001, ARCH-078-SHOPIFY-001, ARCH-078-ADMIN-001]
created: 2026-11-22
updated: 2026-11-22
---

# ARCH-078-DATABASE-001 — Persist unmapped Shopify usage-event handles on Subscription

## Architecture

[ARCH-078](../../../architecture/ARCH-078-shopify-provider-authoritative-billing-plan-and-usage-event-mapping.md) is authoritative.

## Objective

Add one durable PostgreSQL field to `billing.Subscription` so Shopify and Background can record provider-returned usage-event handles that do not yet have matching `MerchantPricingUsageEvent` catalogue records.

## Exact schema change

File:

```text
prisma/schema.prisma
```

In the existing `model Subscription` in schema `billing`, add:

```prisma
unmappedShopifyUsageEventHandles String[] @default([])
```

Place it beside the existing observed Shopify plan/provider fields. Do not change the `SubscriptionProjectionStatus` enum or any existing status/last-sync fields.

## Exact forward migration

Create only this new migration:

```text
prisma/migrations/20261122090000_arch078_unmapped_shopify_usage_event_handles/migration.sql
```

SQL:

```sql
ALTER TABLE "billing"."Subscription"
ADD COLUMN "unmappedShopifyUsageEventHandles" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[];
```

Do not edit, rename or regenerate any previously applied migration. Do not add a down migration.

## Field contract

- The field is always non-null and defaults to an empty PostgreSQL `TEXT[]`.
- It stores exact Shopify `TieredPrice` usage-event handles returned by the current active subscription that have no exact matching `MerchantPricingUsageEvent.eventHandle` under the exact `MerchantPricingPlan.shopifyPlanHandle`.
- The application owns mapping semantics. Database work must not add a trigger or check constraint for the mapping.
- Existing subscriptions receive `[]` through the migration default. Do not attempt to infer historical provider handles or backfill from `shopifyRecoveryUsageEventHandle`.
- Do not add a GIN or other index in this task. The initial Admin query is a bounded operational view; add an index only in a separately reviewed task if measured query plans justify it.
- No new table, enum, relation or status is required.

## Work items

1. Update the `Subscription` Prisma model with the exact field above.
2. Add the exact forward migration above.
3. Add a focused database validation script:

   ```text
   scripts/test-arch078-unmapped-shopify-usage-event-handles-postgres.mjs
   ```

   It must support `--mode fresh` and `--mode upgrade`, using the repository's existing disposable PostgreSQL test conventions.
4. Add these package scripts:

   ```json
   "test:arch078-unmapped-shopify-usage-event-handles:postgres:fresh": "node scripts/test-arch078-unmapped-shopify-usage-event-handles-postgres.mjs --mode fresh",
   "test:arch078-unmapped-shopify-usage-event-handles:postgres:upgrade": "node scripts/test-arch078-unmapped-shopify-usage-event-handles-postgres.mjs --mode upgrade"
   ```

5. Regenerate the scoped Prisma ERD using the existing `npm run erd` command. Commit the generated `docs/generated/prisma-erd.puml` and `docs/generated/prisma-erd.png` changes if the generator updates them.
6. Regenerate the Prisma client using the repository's existing `npm run prisma:generate` command only after schema and migration validation.

## PostgreSQL test requirements

Fresh mode:
- Apply the complete migration history plus the ARCH-078 migration to a fresh disposable PostgreSQL database.
- Verify `billing."Subscription"."unmappedShopifyUsageEventHandles"` exists as `TEXT[]`, is `NOT NULL`, and has an empty-array default.
- Insert a Subscription without specifying the field and verify it reads as `[]`.
- Update it to `ARRAY['gold-top-up','premium-top-up']` and verify exact values/order are retained.
- Update it back to `ARRAY[]::TEXT[]` and verify the array clears.
- Verify the migration does not add a new enum, table, trigger or index.

Upgrade mode:
- Apply all migrations preceding ARCH-078 to a disposable database.
- Insert at least one existing Subscription row before applying ARCH-078.
- Apply the new migration.
- Verify the existing row is preserved and receives `[]`.
- Verify the field can subsequently be populated and cleared without changing the subscription's status, `lastSyncErrorCode` or `lastSyncErrorAt`.

Use the repository's existing PostgreSQL container and cleanup helpers. Do not use a developer or production database.

## Acceptance criteria

- [ ] `Subscription.unmappedShopifyUsageEventHandles` exists exactly as `String[] @default([])`.
- [ ] One additive forward migration adds `TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[]`.
- [ ] Fresh and upgrade PostgreSQL modes pass and prove existing rows are preserved.
- [ ] Prisma validation and generation pass.
- [ ] The generated ERD reflects the new field.
- [ ] No prior migration, `_index.md`, unrelated model, enum, trigger, index or table is changed.

## Validation commands

Run from the `moda-interact-database` repository:

```bash
npm run prisma:validate
npm run test:arch078-unmapped-shopify-usage-event-handles:postgres:fresh
npm run test:arch078-unmapped-shopify-usage-event-handles:postgres:upgrade
npm run prisma:generate
npm run erd
git diff --check
```

Inspect the actual `package.json` and existing disposable-PostgreSQL helper before implementing. Report any baseline tool/environment failure separately; do not claim a test passed if its container did not start.

## Stop condition

After schema, migration, ERD and both PostgreSQL modes pass, submit the task for architect review and stop. Do not edit consumer repositories or update their submodule pins in this task.
