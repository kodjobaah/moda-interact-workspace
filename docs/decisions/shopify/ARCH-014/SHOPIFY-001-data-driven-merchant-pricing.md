---
id: ARCH-014-SHOPIFY-001
architecture_id: ARCH-014
title: Consume active merchant pricing catalogue and remove hard-coded onboarding pricing
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-09-15T11:41:12Z
attempt: 2
depends_on:
- ARCH-014-DATABASE-001
enables:
- ARCH-014-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-SHOPIFY-001

## Objective

In one bounded `moda-interact` task:

1. implement the server-side reader for active ARCH-014 `MerchantPricingPlan` catalogue rows;
2. order only by `MerchantPricingPlan.cataloguePosition`;
3. pass the localized catalogue into onboarding;
4. replace hard-coded `plans`/`topUps`/plan-description presentation with database data;
5. remove the stale second plan catalogue if unreferenced;
6. preserve Shopify-hosted subscription selection/management unchanged.

Do not split reader and rendering into separate tasks/implementations.

## Binding isolation rule

The merchant pricing reader MUST NOT query/join/filter/order through:

```text
BillingPlan
BillingEconomicsSnapshot
BillingUpgradeEconomicsEdge
```

Do not use operational plan `active` state. Merchant visibility comes only from `MerchantPricingPlan.isActive`.

Do not reconstruct order from price/name/allowance/Shopify handle. The only order source is `MerchantPricingPlan.cataloguePosition`.

## Authorized implementation surface

```text
app/routes/app/home/route.jsx
app/components/onboarding/Onboarding.jsx
app/components/onboarding/Onboarding.css
app/components/onboarding/PlanSelector.jsx                    # delete only after required usage search
app/services/merchant-pricing/merchant-pricing.server.js      # new server reader; adapt directory naming only to current repo convention
app/utils/merchant-i18n.js                                    # only locale-resolution reuse/integration
app/i18n/catalogues.js                                        # focused assertion only if needed; preserve existing 20 registry
app/i18n/locales/*.json                                       # remove plan-specific keys/add generic labels in all 20
tests/unit/merchant-pricing*.test.*                           # new exact reader/renderer tests
# directly affected onboarding/i18n tests
```

Do not modify `/app/billing/select` or Shopify subscription actions.

## Existing locale registry is authoritative in this repository

The snapshot already exposes the merchant application's exact 20 locale catalogues from `app/i18n/catalogues.js`. Do not add a Shared dependency and do not introduce a second merchant-app locale list.

Add a focused assertion that the set of existing exported supported locale ids is exactly:

```text
cs, da, de, en, es, fi, fr, it, ja, ko,
nb, nl, pl, pt-BR, pt-PT, sv, th, tr, zh-Hans, zh-Hant
```

Order in `catalogues.js` need not change solely to match template order; compare exact sets where appropriate.

Locale resolution uses existing merchant-i18n rules to resolve Shopify/settings locale to one supported catalogue (for example `en-GB -> en`). After resolution, the pricing reader requires that exact DB translation. **Do not fall back from a supported resolved locale to English pricing content.**

## Exact server reader

Create one server-only function equivalent to:

```text
readActiveMerchantPricingCatalogue({ locale })
```

### Query rules

Issue one bounded Prisma query (or equivalent bounded query set if repository Prisma limitations require) against ARCH-014 tables only:

1. query `MerchantPricingPlan` rows where `isActive = true`;
2. order `cataloguePosition ASC`;
3. include the exact translation row for resolved locale;
4. include usage events ordered `position ASC`;
5. include tiers ordered `position ASC`;
6. return no operational billing-plan/topology data.

Zero active catalogue plans is valid and returns `[]`.

Before returning, assert catalogue positions are strictly increasing in the query result. Gaps are acceptable in the active subset because inactive rows retain their global positions. Do not renumber in the reader.

If corrupt data violates expected order/shape, throw bounded prefix:

```text
MERCHANT_PRICING_CATALOGUE_INVALID:
```

## Exact fail-closed catalogue validation

Before returning merchant DTO, validate each active row:

```text
shopifyPlanHandle trim non-empty
displayName trim non-empty
cataloguePosition non-negative safe integer
translation exists for exact resolved supported locale
translation description trim non-empty <=2000
plan currency uppercase 3 letters
recurringAmountMinor non-negative safe integer
includedRecoveryCredits non-negative safe integer
usage events 0..5 and contiguous positions
usage event currency == plan currency
creditsGrantedPerUnit positive
maximumUnits null or positive
FIXED: non-negative fixed amount + zero tiers
GRADUATED/VOLUME: 1..6 ordered valid tiers + final open-ended
```

The database is final integrity, but app reader must fail safely if stale/corrupt data is observed.

Do not return `adminLabel` in merchant DTO.

## Exact merchant DTO

Return objects equivalent to:

```text
{
  shopifyPlanHandle,
  displayName,
  planKind,
  cataloguePosition,
  featured,
  localizedDescription,
  includedRecoveryCredits,
  allowancePeriod,
  billingPeriod,
  recurringAmountMinor,
  currency,
  usageEvents: [
    {
      eventHandle,
      creditsGrantedPerUnit,
      maximumUnitsPerBillingPeriod,
      pricingMode,
      currency,
      fixedUnitAmountMinor,
      tiers: [{position, upTo, amountPerUnitMinor, flatAmountMinor}]
    }
  ]
}
```

No operational limits, secrets, provider evidence, `adminLabel`, Shopify access token or Admin-only fields.

## Loader integration

In `app/routes/app/home/route.jsx` preserve authentication/shop/settings logic.

Before the current early onboarding return:

1. resolve `merchantUi` as today;
2. resolve its supported locale through current merchant i18n capability;
3. read `pricingCatalogue` through `readActiveMerchantPricingCatalogue`;
4. when onboarding is incomplete return:

```text
{ settings, merchantUi, subscription: null, pricingCatalogue }
```

Pass `pricingCatalogue` to `<Onboarding>`.

Do not call Shopify Partner/Admin billing APIs to reconstruct the informational pricing catalogue.

## Hard-coded commercial data removal

Delete from `Onboarding.jsx` all source-owned merchant commercial values:

```text
const plans = [...]
const topUps = [...]
plan-specific names/prices/allowances/featured flags
hard-coded numeric Free allowance/proof quantity
plan-specific descriptionKey/topupKey wiring
```

Run before deleting stale component:

```text
rg -n "PlanSelector" app tests
```

If `PlanSelector.jsx` has no real imports/usages, delete it. If it has a real current consumer, STOP and return that evidence to `moda_architect`; do not preserve a second commercial catalogue silently.

## Static i18n cleanup

After runtime references are removed, remove these plan-specific dynamic-commercial keys from every locale JSON:

```text
onboarding.pricing.free.description
onboarding.pricing.starter.description
onboarding.pricing.growth.description
onboarding.pricing.scale.description
onboarding.pricing.free.topup
onboarding.pricing.starter.topup
onboarding.pricing.growth.topup
onboarding.pricing.scale.topup
```

Retain generic translated application copy. Add generic keys only when necessary for the dynamic renderer, for example:

```text
onboarding.pricing.monthlyAllowance
onboarding.pricing.lifetimeAllowance
onboarding.pricing.perMonth
onboarding.pricing.mostPopular
onboarding.pricing.topupLabel / topups
onboarding.pricing.fixedPricing
onboarding.pricing.graduatedPricing
onboarding.pricing.volumePricing
onboarding.pricing.creditsPerUnit
onboarding.pricing.maximumUnits
onboarding.pricing.tierRange
onboarding.pricing.pricingUnavailable
```

Any new generic key must exist with natural translations in all current 20 catalogues; do not copy English as placeholder content.

## Exact plan-card rendering

For each DTO plan:

```text
name                 = displayName from DB
description          = exact localizedDescription from DB
recurring price      = format amountMinor/currency; never stored formatted string
allowance number     = includedRecoveryCredits
allowance label      = generic i18n based on allowancePeriod
featured badge       = featured from DB
```

For FREE, recurring amount may be zero; display as localized/format-aware zero price without hard-coded `£0`.

If the hero retains a Free recovery-credit proof number, select the first active catalogue plan in `cataloguePosition` order whose `planKind=FREE` and use its `includedRecoveryCredits`. If no active Free plan exists, omit that numeric proof rather than using a constant.

## Exact usage-event rendering

Do not recreate the old cross-plan `£5/£10/£20` matrix and do not assume every plan has the same number or matching meter prices.

Render each plan's 0..5 usage offers from its own rows.

Use generic translated labels; usage-event `adminLabel` is unavailable by contract.

### FIXED

Show:

```text
formatted unit price
creditsGrantedPerUnit
optional maximum units when present using generic translated label
```

### GRADUATED / VOLUME

Show pricing-mode label and an accessible compact tier list/table:

```text
range/upTo
amountPerUnit
flatAmount
creditsGrantedPerUnit at meter level
optional maximum units
```

Do not collapse a multi-tier offer into a fabricated single `£X -> Y` price.

`eventHandle` is technical identity; do not use it as primary merchant-facing label. A generic localized “Top-up option 1/2/3” label is acceptable because commercial meaning is conveyed by credits/pricing.

## Empty/error behaviour

`pricingCatalogue=[]` renders generic localized pricing-unavailable state; it does not fabricate old plans.

A `MERCHANT_PRICING_CATALOGUE_INVALID:` reader error uses the route's existing safe error-boundary/logging conventions. Do not expose raw DB rows or silently fall back to constants.

## Subscription CTA boundary

Existing CTA/navigation continues to the canonical Shopify-hosted plan-selection path. Do not add local per-plan subscription creation/change mutations.

## Required tests

### Reader tests

1. existing locale registry exact 20-set assertion;
2. `en-GB` resolves to `en`, then exact DB `en` translation required;
3. `pt-BR` distinct from `pt-PT`;
4. `zh-Hans` distinct from `zh-Hant`;
5. active MerchantPricingPlan returns exact localized DTO;
6. inactive MerchantPricingPlan excluded;
7. missing exact translation fails; no English fallback;
8. 0 active plans returns `[]`;
9. cataloguePosition order wins over name/price/allowance/createdAt;
10. active subset with global positions `0,2,5` returns that relative order without renumbering/failure;
11. duplicate/decreasing/corrupt returned order fails closed when observable;
12. 0/5 usage events supported;
13. invalid usage pricing fails closed;
14. DTO excludes `adminLabel`/secrets;
15. ARCH-014 reader performs no BillingPlan/BillingEconomicsSnapshot/BillingUpgradeEconomicsEdge query/join.

### Rendering/source tests

16. plan card values come from fixture DTO and change when fixture changes;
17. exact localized DB description rendered;
18. FIXED offer rendered;
19. GRADUATED tiers rendered;
20. VOLUME tiers rendered;
21. no offer renders no fabricated top-up;
22. featured comes from DB;
23. Free hero quantity comes from active DB catalogue or is omitted;
24. empty catalogue renders generic unavailable state;
25. all removed plan-specific static keys are absent;
26. all new generic keys exist across all 20 catalogues;
27. stale `PlanSelector.jsx` deleted if unreferenced;
28. source search proves old hard-coded commercial arrays/prices are gone;
29. CTA remains Shopify selection boundary and no subscription mutation is introduced.

## Validation

Inspect `package.json`, then run:

```text
npm test
npm run typecheck
npm run lint
npm run prisma:validate
npm run prisma:generate
npm run build
rg -n "const plans =|const topUps =|£19|£35|£49|£75|£99|£149" app/components/onboarding app/routes/app/home
rg -n "onboarding\.pricing\.(free|starter|growth|scale)\.(description|topup)" app tests
rg -n "billingPlan|BillingPlan|BillingEconomicsSnapshot|BillingUpgradeEconomicsEdge" app/services/merchant-pricing app/components/onboarding app/routes/app/home || true
git diff --check
```

The first two `rg` checks may return only unrelated historical/test fixture text explicitly justified in the Completion Report; no runtime hard-coded commercial catalogue matches are allowed. The operational-billing `rg` must not show an ARCH-014 catalogue-reader dependency; unrelated subscription state outside the reader may be justified only if it predates and is not used to select/order catalogue rows.

## Stop conditions

STOP and return evidence if:

- integrated Prisma client lacks ARCH-014 new models/fields;
- `PlanSelector.jsx` is actually consumed by a current supported flow (architect must decide whether to migrate that consumer);
- implementing the reader requires changing Shopify subscription selection/creation semantics;
- implementation appears to require BillingPlan/operational topology data for catalogue visibility/order;
- current 20-locale registry differs from architecture exact set.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Blocked; returned to `moda_architect` for prerequisite correction.

### Preparation Evidence

- Dependency gate passed for `ARCH-014-DATABASE-001` according to the deterministic launcher.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-SHOPIFY-001` on `task/ARCH-014-SHOPIFY-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-SHOPIFY-001` on `task/ARCH-014-SHOPIFY-001`.
- Launcher claim commit: `418eb996a28ea14861275de4436552539a9bedfd`.
- Recursive submodule synchronization and initialization passed; database submodule is pinned at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.

### Blocking Evidence

- `database/prisma/schema.prisma` at the prepared submodule revision contains no `MerchantPricingPlan`, `MerchantPricingPlanTranslation`, `MerchantPricingUsageEvent`, or `MerchantPricingUsageTier` models.
- `database/prisma/migrations` at the prepared revision contains no ARCH-014 MerchantPricing migration.
- `node_modules` was not present in the fresh implementation worktree, but dependency installation was not started because the missing Prisma contract is an explicit task stop condition.
- The task cannot implement the required reader or exact DTO without inventing unavailable Prisma fields or expanding into the database task's owned surface. No application implementation files were changed and no implementation commit was created.

### Audit Result

- `PlanSelector.jsx` is currently unreferenced by `app` or `tests`, but its deletion and the remaining onboarding work are deferred because the required database contract is absent.
- No billing, Shopify subscription, route, shared, or database changes were attempted.
- Architect action required: materialize and synchronize the completed ARCH-014-DATABASE-001 schema/models into the task's prepared database submodule, then rerun `/moda-task ARCH-014-SHOPIFY-001` for a fresh implementation attempt.

### Architect Review

Changes blocked by prerequisite schema absence. Ready for `moda_architect` decision; stop here.
