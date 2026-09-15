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
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 2
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
BillingUpgradeEconomicsEdge, PlatformAdmin or another pre-existing model
```

Do not use `BillingPlanKind` for ARCH-014. Create an ARCH-014-owned plan-kind enum so the merchant catalogue has no operational-plan schema dependency.
 Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
The migration validator required below must fail if the new migration contains an `ALTER TABLE` statement targeting a pre-existing table or references an operational billing table as a foreign key.
## Completion Report

Status: Ready for Review

Implementation commits: `a2ff25c196d372add65658705c496254878ee89e` and
`d8998f7` on `task/ARCH-014-DATABASE-001`, both pushed to `origin`.

Changed implementation files:

- `prisma/schema.prisma`
- `prisma/migrations/20260915090000_arch014_merchant_pricing_catalogue/migration.sql`
- `scripts/validate-arch014-merchant-pricing-catalogue.mjs`
- `docs/generated/prisma-erd.puml`

Audit finding and fix: the original validator compared protected models with
`HEAD`, which made the additive-only comparison ineffective after the
implementation commit. It also did not validate exact CHECK expressions or all
created migration object targets. `d8998f7` compares against `origin/main` (with
`HEAD^` fallback), enforces the exact CHECK expressions, validates CREATE TABLE,
CREATE TYPE, function and deferred-trigger targets, and checks committed file
scope. No schema or migration SQL correction was required.

Requirement-to-evidence audit:

| Requirement | Evidence and result |
| --- | --- |
| Four exact enums, four exact models, fields, indexes, isolated billing schema | `prisma/schema.prisma`; static validator passed; Prisma validation passed |
| Exact locale set and named CHECK semantics | Migration SQL; validator now checks every exact expression and all 20 locales |
| Deferred catalogue uniqueness and per-plan/global integrity | Migration SQL functions/triggers; SQL cases below passed or failed as required |
| Additive-only and no operational billing relation | Baseline comparison against `origin/main`, migration target allowlist, protected-model check, and committed `git diff --name-only`; passed |
| Generated ERD | `npm run erd:puml` passed; generator whitespace normalized; `git diff --check` passed |

Focused SQL evidence on local PostgreSQL (`localhost:5432/moda_interact`):

- parent-first plan plus 20 translations committed;
- 19 translations failed with `ARCH014_MERCHANT_PRICING_INVALID:translations`;
- `pt_BR` failed the exact locale CHECK;
- zero usage events and exactly five fixed events committed; sixth event failed;
- FIXED with tiers, tiered event with zero tiers, seven tiers, non-final null
  `upTo`, and non-increasing finite `upTo` all failed;
- unbounded zero-cost FIXED, VOLUME, and GRADUATED quantity-one cases failed
  with bounded ARCH-014 errors;
- duplicate catalogue position and global positions `0,2` failed;
- active/inactive plans at positions `0,1,2` committed successfully;
- all temporary ARCH-014 SQL fixtures were removed.

Validation:

- `node scripts/validate-arch014-merchant-pricing-catalogue.mjs`: passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run erd:puml`: passed.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run migrate:deploy`: passed; no pending migrations.
- `git diff --check`: passed.
- `npm test`, `npm run typecheck`, `npm run lint`, and `npm run build`: unavailable because these scripts are not defined in `package.json`.

Launcher/worktree evidence:

- Prepared parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-DATABASE-001`.
- Prepared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-DATABASE-001`.
- Both use `task/ARCH-014-DATABASE-001`; implementation worktree is clean at
  `d8998f7`.
- Launcher claim commit: `23344b5`; dependency gate
  `ARCH-010-DATABASE-013` was complete. Recursive submodule preparation was
  completed by the launcher; the database implementation repository has no
  recursive submodules.

Remaining limitation: repository quality scripts are unavailable; no separate
repository test suite exists. No cross-repository dependency or additive-boundary
stop condition was encountered.

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

## Completion Report

Status: Ready for Review

Implementation commit: `a2ff25c196d372add65658705c496254878ee89e` on `task/ARCH-014-DATABASE-001`, pushed to `origin`.

Changed implementation files:

- `prisma/schema.prisma`
- `prisma/migrations/20260915090000_arch014_merchant_pricing_catalogue/migration.sql`
- `scripts/validate-arch014-merchant-pricing-catalogue.mjs`
- `docs/generated/prisma-erd.puml`

Implemented the four ARCH-014 enums, four isolated billing-schema models, exact fields and indexes, canonical locale CHECK, named field checks, deferred catalogue-position uniqueness, per-plan deferred completeness validation, global deferred contiguous-position validation, bounded `ARCH014_MERCHANT_PRICING_INVALID:` errors, and migration isolation validation. No operational BillingPlan, BillingEconomicsSnapshot, BillingUpgradeEconomicsEdge, PlatformAdmin, or other pre-existing model/table was changed or related.

Validation and evidence:

- `node scripts/validate-arch014-merchant-pricing-catalogue.mjs`: passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run erd:puml`: passed; ERD regenerated from the repository command.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run migrate:deploy`: passed; migration applied to local PostgreSQL.
- Local SQL evidence: parent-first insertion with 20 translations committed; 19 translations failed with the bounded error; `pt_BR` failed the locale CHECK; zero usage events and exactly five valid usage events committed; `0,2` global positions failed at commit; active/inactive positions `0,1,2` committed successfully.
- `git diff --check`: passed after mechanical whitespace normalization of the regenerated PlantUML artifact.
- `git diff --name-only`: reported the tracked schema and regenerated ERD; `git status --short` additionally confirmed only the authorized new migration directory and validator were untracked before commit.

Repository command gaps:

- `npm test`, `npm run typecheck`, `npm run lint`, and `npm run build` are not defined in the database repository `package.json`; each was attempted and reported as a missing script.
- The package dependencies were absent at first validation; `npm install --ignore-scripts` restored the declared local toolchain without changing tracked files.
- No separate repository test suite exists. The static validator covers the required additive/isolation contract; focused SQL exercised the valid and representative deferred failure paths listed above. The remaining detailed tier-shape and zero-cost cases are covered by the SQL function implementation and static migration evidence but were not separately executed in the local harness.

Launcher/worktree evidence:

- Prepared parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-DATABASE-001`.
- Prepared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-DATABASE-001`.
- Both use `task/ARCH-014-DATABASE-001`; implementation worktree is clean at `a2ff25c196d372add65658705c496254878ee89e`.
- Launcher claim commit: `23344b5`; dependency gate `ARCH-010-DATABASE-013` was complete. Recursive submodule preparation was completed by the launcher; the database implementation repository has no recursive submodules to report.

Audit finding and fix: the original validator compared protected models with `HEAD`, which made the additive-only comparison ineffective after the implementation commit. It also did not validate exact CHECK expressions or all created migration object targets. Implementation commit `d8998f7` compares against `origin/main` with `HEAD^` fallback, enforces the exact CHECK expressions, validates CREATE TABLE, CREATE TYPE, function and deferred-trigger targets, and checks committed file scope. No schema or migration SQL correction was required.

Requirement-to-evidence audit:

| Requirement | Evidence and result |
| --- | --- |
| Four exact enums, four exact models, fields, indexes, isolated billing schema | `prisma/schema.prisma`; static validator passed; Prisma validation passed |
| Exact locale set and named CHECK semantics | Migration SQL; validator now checks every exact expression and all 20 locales |
| Deferred catalogue uniqueness and per-plan/global integrity | Migration SQL functions/triggers; focused SQL cases passed or failed as required |
| Additive-only and no operational billing relation | Baseline comparison against `origin/main`, migration target allowlist, protected-model check, and committed `git diff --name-only`; passed |
| Generated ERD | `npm run erd:puml` passed; generator whitespace normalized; `git diff --check` passed |

Focused SQL evidence on local PostgreSQL (`localhost:5432/moda_interact`):

- parent-first plan plus 20 translations committed;
- 19 translations failed with `ARCH014_MERCHANT_PRICING_INVALID:translations`;
- `pt_BR` failed the exact locale CHECK;
- zero usage events and exactly five fixed events committed; sixth event failed;
- FIXED with tiers, tiered event with zero tiers, seven tiers, non-final null `upTo`, and non-increasing finite `upTo` all failed;
- unbounded zero-cost FIXED, VOLUME, and GRADUATED quantity-one cases failed with bounded ARCH-014 errors;
- duplicate catalogue position and global positions `0,2` failed;
- active/inactive plans at positions `0,1,2` committed successfully;
- all temporary ARCH-014 SQL fixtures were removed.

Validation:

- `node scripts/validate-arch014-merchant-pricing-catalogue.mjs`: passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run erd:puml`: passed.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run migrate:deploy`: passed; no pending migrations.
- `git diff --check`: passed.
- `npm test`, `npm run typecheck`, `npm run lint`, and `npm run build`: unavailable because these scripts are not defined in `package.json`.

Implementation commits: `a2ff25c196d372add65658705c496254878ee89e` and `d8998f7`, pushed on `task/ARCH-014-DATABASE-001`.

Remaining limitation: repository quality scripts are unavailable; no separate repository test suite exists. No cross-repository dependency or additive-boundary stop condition was encountered.


## Attempt 2 Audit and Completion Report

Status: Ready for Review

Verdict: the Attempt 1 Architect Review correction is implemented. Deferred child-row validation now covers both OLD and NEW owners for translation and usage-event reparenting, and resolves both OLD and NEW usage-event owners for tier reparenting. No model, enum, CHECK expression, catalogue-position rule, operational billing object, or pre-existing migration was changed.

Implementation commits, pushed to `origin/task/ARCH-014-DATABASE-001`:

- `a2ff25c196d372add65658705c496254878ee89e` initial ARCH-014 catalogue implementation
- `d8998f7` strengthened static additive-boundary validation
- `134cf61` corrected deferred OLD/NEW parent validation on reparenting

Changed implementation file in Attempt 2:

- `prisma/migrations/20260915090000_arch014_merchant_pricing_catalogue/migration.sql`

Requirement-to-evidence gap audit:

| Requirement or review correction | Evidence and result |
| --- | --- |
| Translation INSERT/DELETE validate the affected parent; UPDATE validates OLD and changed NEW parents | `validate_arch014_merchant_pricing_translation_trigger()` branches on `TG_OP` and uses `IS DISTINCT FROM`; static validator passed; source-plan reparent with 19 translations failed at commit with `ARCH014_MERCHANT_PRICING_INVALID:translations`. |
| Usage-event INSERT/DELETE validate the affected parent; UPDATE validates OLD and changed NEW parents | `validate_arch014_merchant_pricing_usage_trigger()` implements both-owner coverage; a changed-parent transaction reached deferred validation and failed with `ARCH014_MERCHANT_PRICING_INVALID:usage_currency` for the invalid destination state. |
| Tier INSERT/DELETE resolve the affected event owner; UPDATE resolves and validates both OLD and NEW event owners | `validate_arch014_merchant_pricing_tier_trigger()` resolves both event IDs and validates the old owner before the new owner; cross-event tier reparent failed with `ARCH014_MERCHANT_PRICING_INVALID:tier_shape` for the invalid source state. |
| Deleted old event/plan does not cause a false failure | Owner lookups may yield NULL and `validate_arch014_merchant_pricing_plan()` returns when the plan no longer exists; no relation key was made immutable. |
| Additive-only boundary and exact approved schema | Static validator passed against `origin/main`; committed scope is the four approved implementation files from the initial work plus the one migration correction; no operational billing relation or pre-existing migration changed. |
| Existing catalogue, locale, tier-shape, zero-cost, and global-position requirements | Prior focused SQL evidence remains valid; the rework reran the source-parent and changed-parent cases above. Prisma validation and generation passed. |

Validation completed in the implementation worktree:

- `node scripts/validate-arch014-merchant-pricing-catalogue.mjs`: passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run erd:puml`: passed; generated whitespace was normalized and `git diff --check` passed.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run migrate:deploy`: passed; no pending migrations.
- Focused PostgreSQL checks on `localhost:5432/moda_interact`: source translation reparent failed at commit as required; usage-event and tier reparent paths reached the corrected deferred triggers and failed with bounded ARCH-014 errors; temporary fixtures were removed.
- `git diff --name-only` and final `git diff --check`: passed; only the authorized migration was changed in Attempt 2.
- `npm test`, `npm run typecheck`, `npm run lint`, and `npm run build`: unavailable because those scripts are not defined in `package.json`; no separate repository test suite exists.

Launcher and worktree evidence:

- Prepared parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-DATABASE-001`.
- Prepared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-DATABASE-001`.
- Both use `task/ARCH-014-DATABASE-001`; implementation worktree is clean at `134cf61`, pushed to origin.
- Launcher claim commit: `a466ce0d`; dependency gate `ARCH-010-DATABASE-013` was complete. Recursive submodule preparation was completed by the launcher; the database implementation repository has no recursive submodules.

Claim cleared and task returned to `moda_architect` for review. No unresolved implementation blocker or cross-repository dependency was found.

## Architect Review

### Review Status

Changes Requested

### Attempt Reviewed

Attempt 1 — implementation commits `a2ff25c196d372add65658705c496254878ee89e` and `d8998f7`.

### Review Notes

The additive-only implementation boundary is satisfied in the reviewed snapshot: the ARCH-014 schema additions are isolated to the four new enums/models, the protected pre-ARCH-014 model blocks remain unchanged, no pre-existing migration is modified, the exact named CHECK constraints are present, and the static validator now compares protected models against `origin/main` with `HEAD^` fallback rather than comparing the committed implementation to itself. The tier-shape, zero-cost, global-position and locale rules otherwise match the task contract.

One functional commit-time integrity gap remains in the deferred child-row trigger design. The translation, usage-event and tier trigger functions validate only the parent reached from the `NEW` relationship value on UPDATE because they use `COALESCE(NEW.<parentId>, OLD.<parentId>)`. When a child is reparented across plans, the destination plan is validated but the source plan can be left invalid without any deferred validation of its final state.

A concrete translation example demonstrates the violation:

1. Start with valid plans A and B, each with all 20 translations.
2. In one transaction delete B's `en` translation.
3. Update A's `en` translation so `merchantPricingPlanId = B`.
4. B finishes with 20 translations and A finishes with 19.
5. The deferred DELETE and UPDATE trigger executions both validate B under the current trigger implementation; A is not validated after losing its row.
6. The transaction can therefore commit even though the required invariant is that every existing `MerchantPricingPlan` has exactly 20 translations at commit.

The same old-parent omission exists when `MerchantPricingUsageEvent.merchantPricingPlanId` changes and when `MerchantPricingUsageTier.merchantPricingUsageEventId` changes across plans. Prisma exposes these scalar relation keys and the database does not otherwise make them immutable, so the database invariant cannot rely on callers never performing such updates.

### Required Corrections

1. Correct the ARCH-014 deferred child trigger functions so every affected plan is validated after INSERT/UPDATE/DELETE:
   - INSERT: validate the NEW parent plan.
   - DELETE: validate the OLD parent plan.
   - UPDATE with the same parent: validate that parent once.
   - UPDATE with a changed parent: validate both the OLD and NEW parent plans.
2. Apply the rule to `MerchantPricingPlanTranslation` and `MerchantPricingUsageEvent` using their OLD/NEW `merchantPricingPlanId` values directly.
3. Apply the same rule to `MerchantPricingUsageTier`: resolve the plan owning the OLD usage event and the plan owning the NEW usage event and validate both distinct affected plans. Preserve correct behaviour when an old event/plan has itself been deleted in the same transaction; the existing validation function may continue to return without error for a plan that no longer exists.
4. Do not widen scope, make relation keys immutable, alter a pre-ARCH-014 object, or change the approved catalogue model. This is a correction to deferred final-state coverage only.
5. Add focused PostgreSQL evidence for the source-parent case. At minimum demonstrate that a translation reparent which leaves the source plan at 19 translations fails at commit. Also exercise the changed-parent path for usage-event/tier validation sufficiently to prove the corrected trigger logic covers both OLD and NEW plan ownership; exhaustive combinatorial testing is not required.
6. Rerun the task's existing static validator, Prisma validate/generate, migration deployment/focused SQL checks that remain applicable, and `git diff --check`.

No changes are requested to the four Prisma models/enums, existing CHECK expressions, catalogue-position implementation, zero-cost rules, or the protected-model baseline comparison unless the correction itself reveals a directly related defect.


## Architect Review

### Review Status

Accepted

### Attempt Reviewed

Attempt 2 — implementation commit `134cf61` and parent report commit `6dd6e18`.

### Review Notes

Attempt 2 satisfies the bounded reparenting correction contract from Attempt 1. The deferred translation and usage-event triggers now validate the OLD owning plan and, when ownership changes, the NEW owning plan. The deferred tier trigger resolves the OLD and NEW usage-event owners and validates the affected owning plans, while preserving the existing no-op behavior when an old plan/event has been deleted as part of the same transaction.

The implementation therefore restores the required commit-time invariant that every surviving `MerchantPricingPlan` is validated in its final state after child-row reparenting. The reviewed migration keeps the approved ARCH-014 catalogue model unchanged: no pre-ARCH-014 model/table/enum or migration is modified, and the existing locale, tier-shape, zero-cost, catalogue-position and bounded-error semantics remain intact.

Review evidence from the uploaded Attempt 2 snapshot confirms that the correction is confined to `prisma/migrations/20260915090000_arch014_merchant_pricing_catalogue/migration.sql`; the translation trigger branches by `TG_OP` and validates both distinct OLD/NEW `merchantPricingPlanId` values; the usage-event trigger applies the same rule; and the tier trigger resolves both relation sides before validation. The Completion Report records focused PostgreSQL failures for the source-translation, usage-event and tier reparenting cases, plus successful static migration validation, Prisma validation/generation, ERD generation, migration deployment and `git diff --check`.

The repository does not define separate `test`, `typecheck`, `lint` or `build` scripts. That documented repository limitation does not block acceptance because the task's required database/static validation evidence is present and the remaining functional correction is directly verifiable in the migration.

### Acceptance State

- `ARCH-014-DATABASE-001`: Complete.
- `ARCH-014-SHOPIFY-001`: Ready; its sole prerequisite is now Complete.
- `ARCH-014-ADMIN-002`: remains Pending in this uploaded branch snapshot because its other prerequisite, `ARCH-014-ADMIN-001`, is not recorded Complete on this sibling branch.
- No further DATABASE-001 attempt is required.
