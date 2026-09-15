---
id: ARCH-014
title: Admin-managed merchant pricing catalogue and portfolio economics
status: agreed
coordinator: moda_architect
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014: Admin-managed merchant pricing catalogue and portfolio economics

## Status

**Agreed for implementation.**

ARCH-014 replaces hard-coded merchant-facing pricing data with a self-contained Admin-authored database catalogue and replaces the Admin calculator's single-usage-meter assumption with deterministic portfolio economics across all active catalogue plans.

## Authority boundary

```text
Shopify App Pricing
  authoritative for actual subscription creation, subscription lifecycle,
  provider billing and provider usage quantities/costs

Moda Admin
  authors Moda's informational merchant pricing catalogue, validates economics,
  supplies complete merchant-facing description translations and controls whether
  a catalogue plan is active/visible

Moda merchant application
  reads active ARCH-014 catalogue rows for presentation only;
  actual subscription selection/management remains Shopify-hosted
```

ARCH-014 MUST NOT create, approve, cancel, downgrade, upgrade or invoice a Shopify subscription.

## Binding isolation rule

ARCH-014 owns its merchant pricing catalogue end-to-end.

The ARCH-014 database migration is **additive only**. It MUST NOT ALTER, rename, delete, backfill, add a column to, add an index to, add a constraint to, or otherwise change any table or enum that existed before ARCH-014.

ARCH-014 creates only new `MerchantPricing*` types/tables/indexes/constraints/functions/triggers.

ARCH-014 Admin and Shopify application code MUST NOT read from or write to `BillingPlan`, `BillingEconomicsSnapshot`, `BillingUpgradeEconomicsEdge`, or another pre-ARCH-014 operational billing table in order to create, validate, order, activate, deactivate or render the merchant pricing catalogue.

The only permitted pre-existing billing-table read in ARCH-014 Admin is the existing platform-wide `PlatformBillingPolicy.minimumUpgradePremiumBps` value used by the economics guardrail. That policy read does not establish catalogue identity/order and must not be used to reconstruct plan commercial data.

Existing generic platform-admin authentication/audit infrastructure may continue to be used without schema changes. No ARCH-014 catalogue field is persisted into an existing table.

If implementation appears to require an operational `BillingPlan` row, operational billing topology, an old economics snapshot, or an existing-table schema change, STOP and return the requirement to `moda_architect`.

## Current problems

The supplied 2026-09-15 snapshot has four related defects:

1. `moda-interact-admin` economics evidence/guardrail assumes one recovery-credit-pack Shopify usage meter (`validateSinglePackShopifyEconomics`).
2. the economics check does not validate how a proposed merchant catalogue plan interacts with every other active catalogue plan.
3. `moda-interact/app/components/onboarding/Onboarding.jsx` hard-codes plan names, prices, allowances and top-up quantities; `PlanSelector.jsx` contains a second stale hard-coded catalogue.
4. merchant-facing plan descriptions are source-code i18n keys rather than Admin-authored translated commercial content.

## Goals

ARCH-014 must:

- create a new self-contained `MerchantPricingPlan` catalogue independent of operational billing-plan rows;
- allow one informational Shopify pricing plan to contain **0..5** Shopify App Pricing usage events;
- support FIXED, GRADUATED and VOLUME usage pricing with **1..6** tiers for tiered modes;
- record recovery credits granted per usage-event unit;
- permit an optional finite `maximumUnitsPerBillingPeriod` used by the economics solver, and require it for an otherwise unbounded zero-cost usage event;
- maintain explicit catalogue ordering through `MerchantPricingPlan.cataloguePosition`;
- never infer catalogue order from name, recurring price, allowance, creation time or Shopify handle;
- evaluate a proposed create/edit against the **entire projected active catalogue portfolio**;
- evaluate every lower->higher pair in catalogue order, not only adjacent plans;
- require every comparison to PASS before an economics-affecting create/edit/activation is committed;
- require exactly the canonical 20 merchant locales for every persisted plan description;
- generate a JSON translation template from the English source description so an administrator does not need to know the schema or locale codes;
- accept pasted JSON or uploaded `.json` through the same parser/validator;
- never persist an incomplete translation set;
- remove merchant-facing plan prices, allowances, top-up quantities and plan-specific descriptions from source code;
- preserve generic UI copy in the existing static i18n catalogues;
- preserve existing operational billing/runtime behaviour untouched.

## Non-goals

ARCH-014 does not:

- replace Shopify subscription authority;
- create or update `BillingPlan` rows;
- read `BillingPlan` rows to decide catalogue visibility or order;
- read `BillingEconomicsSnapshot` or `BillingUpgradeEconomicsEdge` to calculate ARCH-014 portfolio economics;
- change App Events submission, purchase activation, Background billing workers or recovery-credit entitlement runtime;
- modify any pre-existing database table or enum literal;
- auto-translate content or assess linguistic quality;
- localize plan names in v1;
- require merchant-facing usage-event names/descriptions in v1; the merchant UI may use translated generic labels plus price/credit data;
- create Gateway/infrastructure work.

## Canonical locale contract

ARCH-014 deliberately creates **no Shared package task**. The 20-locale set is a small static product invariant repeated explicitly at the Database/Admin boundaries and verified against the merchant application's existing locale registry by tests.

Exact set and template order:

```text
cs
da
de
en
es
fi
fr
it
ja
ko
nb
nl
pl
pt-BR
pt-PT
sv
th
tr
zh-Hans
zh-Hant
```

No supported locale may fall back to English plan-description content.

## New additive persistence model

All objects below are new and live in the existing `billing` schema. Exact implementation is owned by `ARCH-014-DATABASE-001`.

### `MerchantPricingPlan`

```text
id                              String/cuid
shopifyPlanHandle               unique immutable Shopify App Pricing plan identity
displayName                     Admin-authored merchant-facing plan name
planKind                        FREE | PAID_METERED
isActive                        Boolean; merchant visibility switch
cataloguePosition               unique non-negative integer ordering key
featured                        Boolean
includedRecoveryCredits         Int >= 0
allowancePeriod                 LIFETIME | EVERY_30_DAYS
billingPeriod                   EVERY_30_DAYS
recurringAmountMinor            Int >= 0
currency                        uppercase 3-letter code
createdAt
updatedAt
```

`shopifyPlanHandle` identifies the Shopify App Pricing plan represented by this informational row. It is **not** a foreign key/correlation requirement to `BillingPlan`.

All persisted catalogue plans are complete records. ARCH-014 does not persist incomplete draft plans; translation/template validation occurs before the final database transaction.

### `MerchantPricingPlanTranslation`

```text
id
merchantPricingPlanId
locale
merchantDescription
createdAt
updatedAt
```

Unique `(merchantPricingPlanId, locale)`.

### `MerchantPricingUsageEvent`

```text
id
merchantPricingPlanId
eventHandle                     Shopify App Pricing usage-event handle
adminLabel                      internal Admin label only
creditsGrantedPerUnit           positive Int
position                        0..4, contiguous within plan
pricingMode                     FIXED | GRADUATED | VOLUME
currency                        exact plan currency
fixedUnitAmountMinor            FIXED only
maximumUnitsPerBillingPeriod    optional positive Int
createdAt
updatedAt
```

If the event can produce zero total price for a positive quantity and the solver would otherwise have no finite bound, `maximumUnitsPerBillingPeriod` is required. This is an economics-search bound, not Shopify subscription authority.

### `MerchantPricingUsageTier`

```text
id
merchantPricingUsageEventId
position                        0..5, contiguous
upTo                            positive Int or null
amountPerUnitMinor              non-negative Int
flatAmountMinor                 non-negative Int
```

Tiered modes require 1..6 rows, strictly increasing finite `upTo` values and final `upTo=null`.

## Persisted catalogue completeness invariant

Every persisted `MerchantPricingPlan` must be complete at transaction commit. There is no persisted incomplete-draft exception.

Final transaction state must satisfy:

```text
exactly 20 translation rows
exact locale set above
all descriptions trim-non-empty and <= 2000 characters
cataloguePosition >= 0 and unique across all MerchantPricingPlan rows
all catalogue positions globally form exactly 0..N-1
0..5 usage events
usage-event positions exactly 0..n-1
unique non-empty usage-event handles within plan
usage currency == plan currency
FIXED has fixedUnitAmountMinor and zero tiers
GRADUATED/VOLUME have no fixedUnitAmountMinor and exactly 1..6 valid tiers
tier positions exactly 0..n-1
final tier open-ended
all money/credit quantities non-negative or positive as specified
zero-cost positive-quantity paths are bounded by maximumUnitsPerBillingPeriod
```

Deferred constraints/triggers must validate only the new ARCH-014 tables so an atomic transaction can insert the parent and children before final commit.

## Translation package v1

The Admin generates this exact format from current builder data:

```json
{
  "_meta": {
    "schemaVersion": 1,
    "planHandle": "starter",
    "planName": "Starter",
    "sourceLocale": "en"
  },
  "translations": {
    "cs": { "description": "" },
    "da": { "description": "" },
    "de": { "description": "" },
    "en": { "description": "English source description" },
    "es": { "description": "" },
    "fi": { "description": "" },
    "fr": { "description": "" },
    "it": { "description": "" },
    "ja": { "description": "" },
    "ko": { "description": "" },
    "nb": { "description": "" },
    "nl": { "description": "" },
    "pl": { "description": "" },
    "pt-BR": { "description": "" },
    "pt-PT": { "description": "" },
    "sv": { "description": "" },
    "th": { "description": "" },
    "tr": { "description": "" },
    "zh-Hans": { "description": "" },
    "zh-Hant": { "description": "" }
  }
}
```

Template generation pre-populates English and leaves the other 19 values empty. A template is not itself a valid completed import.

Completed-import rules:

- strict root and `_meta` shape;
- `schemaVersion === 1`;
- `sourceLocale === "en"`;
- imported handle/name match the builder's normalized current values;
- exact locale set; no missing/unknown keys;
- every description is trim-non-empty and <=2000 characters;
- imported English description exactly matches current English source after normalization;
- paste and file upload run the same parser;
- no fallback/auto-translation is generated.

## Catalogue ordering

`MerchantPricingPlan.cataloguePosition` is the only ARCH-014 plan-order authority.

For all persisted catalogue rows, positions are globally unique and contiguous `0..N-1`.

Create placement is explicit:

```text
ONLY                            valid only when catalogue is empty
BEFORE:<currentFirstPlanId>     insert as new first plan
AFTER:<existingPlanId>          insert immediately after the named catalogue plan
```

The Admin must not infer placement from plan economics. When inserting at position `k`, existing catalogue rows at `k..N-1` are shifted upward by one in descending position order before the new row is inserted at `k`.

Existing-plan reordering is outside ARCH-014 v1. Edit preserves the row's current `cataloguePosition`.

Merchant presentation uses active rows sorted by `cataloguePosition ASC`; inactive rows remain in the catalogue/order but are omitted from the merchant DTO.

## Portfolio economics

ARCH-014 portfolio economics uses only `MerchantPricingPlan` commercial data plus the current platform-wide minimum-upgrade-premium policy.

For create/edit, construct an in-memory projected ordered portfolio from:

```text
all currently active MerchantPricingPlan rows
+ the proposed plan version inserted/replaced at its catalogue position
```

The proposed plan is included in validation even when the administrator intends to save it inactive, so it cannot be persisted with obviously invalid economics and later activated without having first passed the creation/edit guardrail. Activation must re-run economics against the then-current active portfolio.

Given ordered plans `P0..Pn`, evaluate every pair `(Pi,Pj)` where `i < j`.

For each pair:

```text
additionalCreditsNeeded = higher.includedRecoveryCredits - lower.includedRecoveryCredits
```

The lower plan's 0..5 usage events are the available top-up offers. Calculate the cheapest valid combination whose granted credits meet/exceed `additionalCreditsNeeded`, using the exact pricing mode of each meter and respecting finite maximum units.

Then apply the existing minimum-upgrade-premium policy concept:

```text
stayAndTopUp = lower recurring price + cheapest top-up combination
higherCost   = higher recurring price
```

Every pair must PASS. FAIL or UNVERIFIED blocks create/edit/activation.

The algorithm and deterministic tie-break/search rules are owned by `ARCH-014-ADMIN-001`.

## Admin plan-management flow

Keep current navigation host:

```text
/billing?view=plans
/billing?view=plans&drawer=register-plan
/billing?view=plans&planId=<MerchantPricingPlan.id>
```

The `plans` view is refactored to use the ARCH-014 MerchantPricing catalogue. ARCH-014 must not call `mutateBillingPlanAction` and must not query `getBillingPlans()`/`getBillingPlanById()` for this view.

Use a wide coherent builder:

```text
1 Plan
2 Catalogue placement
3 Shopify recurring pricing
4 Shopify pricing usage events
5 English merchant description
6 Portfolio economics
7 Translation import + final review
```

The user may download the generated JSON template, populate it externally, then either paste the completed JSON or upload the `.json` file.

No database write occurs merely because the administrator reaches the translation step or validates a file.

Final create is one transaction that:

1. revalidates authorization, builder payload and completed translation package;
2. validates the explicit catalogue placement against current catalogue order;
3. constructs the projected portfolio and requires all economics PASS;
4. shifts ARCH-014 catalogue positions when required;
5. creates one `MerchantPricingPlan` plus exactly 20 translations and 0..5 usage events/tiers;
6. writes existing bounded generic Admin audit evidence if the current audit action can represent this without schema changes;
7. commits atomically.

No `BillingPlan`, `BillingEconomicsSnapshot` or `BillingUpgradeEconomicsEdge` query/write occurs in this transaction.

Edits update only ARCH-014 catalogue tables. `shopifyPlanHandle` and `cataloguePosition` are immutable in v1. If English source description changes, all 20 descriptions must be resupplied/validated in the same save. Activation re-runs full projected-portfolio economics before `isActive=true` commits.

## Merchant read model

`moda-interact` queries only new ARCH-014 catalogue tables:

```text
MerchantPricingPlan.isActive = true
ORDER BY MerchantPricingPlan.cataloguePosition ASC
```

For the resolved supported merchant locale, require the exact matching translation row. Missing data is an invalid catalogue condition; do not substitute hard-coded values or an English plan-description fallback.

The merchant DTO contains plan name, localized description, recurring pricing, allowance data, featured flag, catalogue position and ordered usage-event pricing/credit data. `adminLabel` is not merchant-facing.

No operational billing-plan join/topology query is permitted.

## Hard-coded data removal

After `ARCH-014-SHOPIFY-001`:

- `Onboarding.jsx` has no `const plans` or `const topUps` commercial catalogue;
- the hard-coded hero Free quantity is removed/derived from active catalogue data;
- unused stale `PlanSelector.jsx` is deleted after an exact usage search proves it is unreferenced;
- plan-specific static description/top-up i18n keys are removed after code references are removed;
- generic UI labels remain translated in static i18n.

## Repository ownership

```text
moda-interact-database
  new additive MerchantPricing* schema/order/completeness integrity only

moda-interact-admin
  pure multi-meter/full-portfolio economics engine
  MerchantPricing catalogue list/builder/actions
  explicit catalogue placement
  translation template/import
  activation/economics orchestration

moda-interact
  active localized catalogue query ordered by cataloguePosition
  data-driven onboarding rendering
  hard-coded commercial catalogue removal

moda-interact-system-test
  terminal integrated acceptance
```

No Shared or Gateway implementation task is required.

## Task graph

```text
ARCH-010-DATABASE-013 -> ARCH-014-DATABASE-001
ARCH-010-ADMIN-009   -> ARCH-014-ADMIN-001

ARCH-014-DATABASE-001 + ARCH-014-ADMIN-001
    -> ARCH-014-ADMIN-002

ARCH-014-DATABASE-001
    -> ARCH-014-SHOPIFY-001

ARCH-014-ADMIN-002 + ARCH-014-SHOPIFY-001
    -> ARCH-014-SYSTEM-TEST-001
```

System test is terminal/manual-gated and enables no implementation task.
