---
id: ARCH-014-DATABASE-001
architecture_id: ARCH-014
title: Add isolated merchant pricing catalogue persistence and integrity
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
depends_on:
- ARCH-010-DATABASE-013
enables:
- ARCH-014-ADMIN-002
- ARCH-014-SHOPIFY-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-DATABASE-001

## Objective

Create the complete ARCH-014 merchant-pricing catalogue as **new database objects only**. The resulting schema must be sufficient to create, order, activate/deactivate and render MerchantPricing plans without reading or correlating to an operational `BillingPlan` row.

## Non-negotiable additive-only boundary

This task MUST NOT:

```text
ALTER an existing pre-ARCH-014 table
add/remove/rename a field in an existing Prisma model block
add/remove/change an existing enum literal
add an index/constraint/trigger to an existing table
backfill/update/delete rows in an existing table
edit any migration that predates this task
create a reverse Prisma relation field on BillingPlan, BillingEconomicsSnapshot,
BillingUpgradeEconomicsEdge, PlatformAdmin or another pre-existing model
```

Do not use `BillingPlanKind` for ARCH-014. Create an ARCH-014-owned plan-kind enum so the merchant catalogue has no operational-plan schema dependency.

The migration validator required below must fail if the new migration contains an `ALTER TABLE` statement targeting a pre-existing table or references an operational billing table as a foreign key.

## Authorized implementation surface

Edit/create only:

```text
prisma/schema.prisma
prisma/migrations/20260915090000_arch014_merchant_pricing_catalogue/migration.sql
scripts/validate-arch014-merchant-pricing-catalogue.mjs   # new
docs/generated/prisma-erd.puml                            # regenerated only
```

Do not modify ARCH-010/011 migrations.

## Exact new enums

Add these enum blocks; do not alter existing enums:

```text
MerchantPricingPlanKind
  FREE
  PAID_METERED

MerchantPricingAllowancePeriod
  LIFETIME
  EVERY_30_DAYS

MerchantPricingBillingPeriod
  EVERY_30_DAYS

MerchantPricingUsagePricingMode
  FIXED
  GRADUATED
  VOLUME
```

All use `@@schema("billing")`.

## Exact new Prisma models

### MerchantPricingPlan

```text
id String @id @default(cuid())
shopifyPlanHandle String @unique

displayName String
planKind MerchantPricingPlanKind
isActive Boolean @default(true)
cataloguePosition Int
featured Boolean @default(false)
includedRecoveryCredits Int
allowancePeriod MerchantPricingAllowancePeriod
billingPeriod MerchantPricingBillingPeriod
recurringAmountMinor Int
currency String @db.Char(3)

translations MerchantPricingPlanTranslation[]
usageEvents MerchantPricingUsageEvent[]

createdAt DateTime @default(now())
updatedAt DateTime @updatedAt

@@index([isActive, cataloguePosition])
@@index([planKind, isActive])
@@schema("billing")
```

Do **not** add a Prisma relation to `BillingPlan` or another pre-existing operational billing model. `shopifyPlanHandle` is the Shopify App Pricing identity stored directly on the ARCH-014 row.

Do not declare Prisma `@unique`/`@@unique` for `cataloguePosition`; create the exact SQL uniqueness constraint below so it can be DEFERRABLE.

### MerchantPricingPlanTranslation

```text
id String @id @default(cuid())
merchantPricingPlanId String
merchantPricingPlan MerchantPricingPlan @relation(fields:[merchantPricingPlanId], references:[id], onDelete:Cascade)
locale String @db.VarChar(16)
merchantDescription String @db.Text
createdAt DateTime @default(now())
updatedAt DateTime @updatedAt
@@unique([merchantPricingPlanId, locale])
@@schema("billing")
```

### MerchantPricingUsageEvent

```text
id String @id @default(cuid())
merchantPricingPlanId String
merchantPricingPlan MerchantPricingPlan @relation(fields:[merchantPricingPlanId], references:[id], onDelete:Cascade)
eventHandle String
adminLabel String
creditsGrantedPerUnit Int
position Int
pricingMode MerchantPricingUsagePricingMode
currency String @db.Char(3)
fixedUnitAmountMinor Int?
maximumUnitsPerBillingPeriod Int?
tiers MerchantPricingUsageTier[]
createdAt DateTime @default(now())
updatedAt DateTime @updatedAt
@@unique([merchantPricingPlanId, eventHandle])
@@unique([merchantPricingPlanId, position])
@@schema("billing")
```

`adminLabel` is internal Admin content and is not a merchant translation.

### MerchantPricingUsageTier

```text
id String @id @default(cuid())
merchantPricingUsageEventId String
merchantPricingUsageEvent MerchantPricingUsageEvent @relation(fields:[merchantPricingUsageEventId], references:[id], onDelete:Cascade)
position Int
upTo Int?
amountPerUnitMinor Int
flatAmountMinor Int
@@unique([merchantPricingUsageEventId, position])
@@schema("billing")
```

## Exact canonical locale set

The database locale CHECK for `MerchantPricingPlanTranslation.locale` must allow **only**:

```text
cs, da, de, en, es, fi, fr, it, ja, ko,
nb, nl, pl, pt-BR, pt-PT, sv, th, tr, zh-Hans, zh-Hant
```

No case folding or aliases (`pt_BR`, `zh_CN`, etc.).

## Required SQL constraints on new tables only

Create named CHECK constraints with these exact semantics:

```text
ck_merchant_pricing_plan_handle_nonblank
  btrim(shopifyPlanHandle) <> ''

ck_merchant_pricing_plan_display_name_nonblank
  btrim(displayName) <> ''

ck_merchant_pricing_plan_catalogue_position
  cataloguePosition >= 0

ck_merchant_pricing_plan_included_credits_nonnegative
  includedRecoveryCredits >= 0

ck_merchant_pricing_plan_recurring_amount_nonnegative
  recurringAmountMinor >= 0

ck_merchant_pricing_plan_currency
  currency ~ '^[A-Z]{3}$'

ck_merchant_pricing_translation_locale
  locale IN (exact 20 locales)

ck_merchant_pricing_translation_description
  btrim(merchantDescription) <> '' AND char_length(merchantDescription) <= 2000

ck_merchant_pricing_usage_handle_nonblank
  btrim(eventHandle) <> ''

ck_merchant_pricing_usage_admin_label
  btrim(adminLabel) <> '' AND char_length(adminLabel) <= 255

ck_merchant_pricing_usage_credits_positive
  creditsGrantedPerUnit > 0

ck_merchant_pricing_usage_position
  position BETWEEN 0 AND 4

ck_merchant_pricing_usage_currency
  currency ~ '^[A-Z]{3}$'

ck_merchant_pricing_usage_fixed_amount
  fixedUnitAmountMinor IS NULL OR fixedUnitAmountMinor >= 0

ck_merchant_pricing_usage_maximum_units
  maximumUnitsPerBillingPeriod IS NULL OR maximumUnitsPerBillingPeriod > 0

ck_merchant_pricing_tier_position
  position BETWEEN 0 AND 5

ck_merchant_pricing_tier_up_to
  upTo IS NULL OR upTo > 0

ck_merchant_pricing_tier_amounts
  amountPerUnitMinor >= 0 AND flatAmountMinor >= 0
```

Use quoted actual Prisma column names in SQL.

Create this exact logical uniqueness constraint on the new plan table:

```text
uq_merchant_pricing_plan_catalogue_position
  UNIQUE (cataloguePosition)
  DEFERRABLE INITIALLY DEFERRED
```

No pre-existing table may be referenced by this constraint.

## Deferred complete-catalogue integrity

ARCH-014 persists **no incomplete plan drafts**. The Admin validates the translation package before opening the final transaction, but the database must still guarantee final state.

Create one SQL validation function owned by ARCH-014, for example:

```text
billing.validate_arch014_merchant_pricing_plan(plan_id text)
```

Create DEFERRABLE INITIALLY DEFERRED constraint triggers on **new ARCH-014 tables only** so a parent may be inserted before its child rows within the same transaction, but the commit fails unless final state is complete.

When the parent no longer exists because it is being deleted/cascaded, per-plan validation returns without error.

For every existing `MerchantPricingPlan`, enforce:

1. exactly 20 translation rows;
2. because locale CHECK + uniqueness already restrict values, count 20 means the exact canonical set;
3. usage-event count is 0..5;
4. usage-event positions are contiguous `0..count-1`;
5. each usage-event currency equals plan currency;
6. FIXED event: `fixedUnitAmountMinor IS NOT NULL` and tier count = 0;
7. GRADUATED/VOLUME event: `fixedUnitAmountMinor IS NULL`, tier count 1..6;
8. tier positions are contiguous `0..count-1`;
9. all non-final tier `upTo` values are non-null and strictly increasing;
10. final tier `upTo IS NULL`;
11. a pricing event that can yield zero total cost for at least one positive quantity in its usable range must have non-null `maximumUnitsPerBillingPeriod`.

For rule 11 use exact deterministic checks:

```text
FIXED:
  fixedUnitAmountMinor = 0 -> maximumUnitsPerBillingPeriod required

VOLUME:
  if any tier has flatAmountMinor=0 AND amountPerUnitMinor=0 -> maximumUnitsPerBillingPeriod required

GRADUATED:
  if the cost calculated for quantity=1 is zero -> maximumUnitsPerBillingPeriod required
```

Also create a second ARCH-014-owned deferred validation function/trigger for global catalogue positions. At commit, if there are `N` `MerchantPricingPlan` rows, the ordered positions must be exactly:

```text
0, 1, 2, ... N-1
```

No gaps and no negative/duplicate positions are allowed. `isActive` does not affect global position integrity; inactive plans retain their place in the catalogue ordering.

Raise bounded SQL errors prefixed exactly:

```text
ARCH014_MERCHANT_PRICING_INVALID:
```

with a short stable reason suffix. Do not include translated descriptions in errors.

## Migration isolation validator

Create `scripts/validate-arch014-merchant-pricing-catalogue.mjs` that reads `prisma/schema.prisma` and the exact migration and fails non-zero unless:

- all four exact new enums exist with exact literals;
- all four exact new models/fields/indexes exist;
- `MerchantPricingPlan.planKind` uses `MerchantPricingPlanKind`, not `BillingPlanKind`;
- exact 20 locale literals appear in migration validation;
- the new named checks, deferrable catalogue-position uniqueness, per-plan validation function and global-position deferred validation exist;
- migration targets only ARCH-014 `MerchantPricing*` tables/functions/types plus schema bookkeeping;
- no `ALTER TABLE` target is a pre-existing non-ARCH-014 table;
- no foreign key/relation points to `BillingPlan`, `BillingEconomicsSnapshot`, `BillingUpgradeEconomicsEdge` or another pre-existing billing plan/economics table;
- no text matching these pre-existing model declarations has gained ARCH-014 fields: `model BillingPlan`, `model BillingEconomicsSnapshot`, `model BillingUpgradeEconomicsEdge`, `model PlatformAdmin`;
- no pre-existing migration changed (validator may inspect git diff when available only as supplemental evidence; Completion Report must include `git diff --name-only`).

## Required focused evidence

The static validator is mandatory. If the repository's existing ephemeral PostgreSQL harness is readily available, add/run focused migration assertions; otherwise do not invent a new test framework solely for this task.

At minimum verify through SQL/static evidence:

1. a transaction may insert parent first, then 20 translations/children, and commit successfully;
2. final plan with 19 translations fails;
3. `pt_BR` translation fails locale CHECK;
4. valid plan with 0 usage events succeeds;
5. valid plan with exactly 5 usage events succeeds;
6. a sixth usage event fails;
7. FIXED with tiers fails;
8. tiered event with zero tiers fails;
9. seven tiers fail;
10. non-final null `upTo` fails;
11. non-increasing finite `upTo` fails;
12. zero-cost unbounded FIXED/VOLUME/GRADUATED case fails as specified;
13. duplicate cataloguePosition fails;
14. positions `0,2` at commit fail global contiguity;
15. positions `0,1,2` across active/inactive rows succeed;
16. migration contains no schema change to an existing table/enum;
17. no ARCH-014 model has a Prisma/SQL relation to `BillingPlan` or operational topology/economics tables.

## Validation

Inspect `package.json`, then run the repository-declared commands that exist, including:

```text
node scripts/validate-arch014-merchant-pricing-catalogue.mjs
npm run prisma:validate
npm run prisma:generate
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
git diff --name-only
```

Regenerate the ERD using the repository's existing command only; do not hand-edit generated structure.

## Stop conditions

STOP and return evidence if:

- implementing any acceptance criterion requires changing a pre-existing table/model/enum;
- Prisma requires a reverse relation on a pre-existing model for this design;
- a proposed implementation needs an FK/correlation to `BillingPlan` or `BillingUpgradeEconomicsEdge`;
- implementation would require changing existing operational billing rows/migrations;
- the integrated database baseline differs materially from ARCH-010-DATABASE-013 in a way that affects these new objects.

Do not widen scope to solve the condition.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
