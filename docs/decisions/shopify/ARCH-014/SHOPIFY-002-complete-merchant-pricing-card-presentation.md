---
id: ARCH-014-SHOPIFY-002
architecture_id: ARCH-014
title: Complete MerchantPricing catalogue visibility and render localized merchant plan cards
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-09-15T16:53:10Z
attempt: 1
depends_on:
- ARCH-014-DATABASE-002
- ARCH-014-SHOPIFY-001
enables:
- ARCH-014-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-SHOPIFY-002

## Objective

Complete the merchant-facing ARCH-014 pricing experience so:

1. the pricing catalogue is visible both during onboarding and to a merchant who completed onboarding but currently has `NO_CONTRACT`;
2. zero active catalogue plans fail closed with no contradictory pricing CTA;
3. pricing plans render as the agreed **merchant card design**, using structured plan data plus ordered localized Admin-authored highlight blocks;
4. raw Shopify meter mechanics (`FIXED`, `VOLUME`, `GRADUATED`, tier tables) are no longer the primary content of a pricing card.

This task intentionally combines the previously identified `NO_CONTRACT` visibility correction and the new card/highlight rendering requirement because both belong to the same `moda-interact` reader/presentation path and have not yet been implemented as a corrective task.

After DATABASE-002 completes, this task may run in parallel with `ARCH-014-ADMIN-004`. It MUST NOT depend on ADMIN-004 implementation code.

## Binding GPT-5.6 Luna rule

Implement the exact reader contract, component structure and state behavior below. Do not infer another route, pricing authority, fallback policy or card-content source.

Shopify remains actual subscription authority. ARCH-014 remains presentation-only.

## Prerequisite gate

Start only after accepted/integrated `ARCH-014-DATABASE-002` is available in the app database submodule/client.

Verify Prisma exposes:

```text
MerchantPricingPlanHighlight
MerchantPricingPlanHighlightTranslation
MerchantPricingPlan.highlights
```

If missing, STOP. Do not reproduce highlight content in static JSON/i18n as a workaround.

## Exact files/surfaces

Primary implementation surface:

```text
app/services/merchant-pricing/merchant-pricing.server.js
app/routes/app/home/route.jsx
app/components/onboarding/Onboarding.jsx
app/components/onboarding/Onboarding.css                 # remove/move old pricing-only styles as required
app/components/dashboard/UsageOverview.jsx
```

Create exactly one reusable pricing presentation component:

```text
app/components/merchant-pricing/MerchantPricingCatalogue.jsx
app/components/merchant-pricing/MerchantPricingCatalogue.css
```

Do not create separate onboarding and dashboard pricing-card implementations.

Update tests under existing conventions, especially:

```text
tests/unit/merchant-pricing-reader.test.js
tests/unit/home-route.test.ts
existing/new focused MerchantPricingCatalogue source/render tests
```

## Exact merchant reader contract

Extend `readActiveMerchantPricingCatalogue({ locale })`.

Continue to query only:

```text
MerchantPricingPlan.isActive = true
ORDER BY cataloguePosition ASC
```

No `BillingPlan`/operational billing join is permitted.

For each plan, include:

```text
plan translation for the exact resolved supported locale
usage events/tiers as already returned by SHOPIFY-001
highlights ordered by position ASC
for each highlight, translation for the exact same resolved locale
```

Return each DTO exactly with the existing fields plus:

```js
highlights: [
  {
    contentKey,
    position,
    title,
    description
  }
]
```

Do not expose:

```text
highlight database id
highlight translation database id
adminLabel
```

If the exact locale's plan description or any highlight title/description is missing, blank or duplicated, treat the catalogue as invalid/fail-closed. **Do not fall back to English.**

Highlights are ordered only by their database `position`.

## Reusable MerchantPricingCatalogue component

`MerchantPricingCatalogue.jsx` is the only pricing-card renderer used by Onboarding and completed-onboarding `NO_CONTRACT` presentation.

Props:

```js
merchantUi
pricingCatalogue
showChoosePlanAction   // boolean
```

The component uses the existing `createMerchantI18n(merchantUi)` for generic labels and money formatting.

### Empty catalogue

When `pricingCatalogue.length === 0`:

```text
render the existing localized pricing-unavailable message
render zero plan cards
render no /app/billing/select link/button
render no /app/billing/options link/button
```

Do not fabricate Free/Starter/Growth/Scale.

### Non-empty catalogue

Render cards in received order without sorting again.

Each card structure is exactly:

```text
small plan-name pill / eyebrow
featured "Most popular" badge when featured=true
plan display name
formatted recurring price + generic per-month label
localized plan description
structured allowance block
zero or more ordered localized highlight cards
```

#### Plan-name pill

Use `plan.displayName` as text and CSS text-transform/typography for the compact pill. Do not add another database field for this label.

#### Featured badge

Use existing generic translated `Most popular` copy. The badge is controlled only by `plan.featured`.

#### Price

Render from:

```text
recurringAmountMinor
currency
billingPeriod
```

No hard-coded currency symbol or plan price.

#### Structured allowance block

The large allowance content MUST be derived, never authored as free text:

```text
includedRecoveryCredits
allowancePeriod
planKind
```

For `FREE` / `LIFETIME`, use the neutral/outlined allowance treatment.

For `PAID_METERED` / `EVERY_30_DAYS`, use the strong green allowance treatment matching the existing Moda visual language/reference card:

```text
<large number>
recovery conversations
every month
```

Generic words remain static translated UI copy. The numeric allowance always comes from the MerchantPricing plan row.

Do not synthesize an `Included capacity` highlight automatically; if the Admin authored one, it appears below as a normal highlight.

#### Highlight cards

For `plan.highlights` in position order render one outlined item:

```text
<title>
<description>
```

Both strings come from the exact-locale DB translation returned by the reader.

Do not replace them with `billingCommerce.feature.*`, onboarding plan-specific keys or other static feature copy.

### Raw usage-event mechanics

Remove the current primary plan-card rendering that exposes:

```text
FIXED / GRADUATED / VOLUME labels
tier range table
amount-per-unit table cells
flat-amount table cells
maximum-units technical labels
```

from `Onboarding.jsx` / the primary MerchantPricing card.

`usageEvents` remain in the MerchantPricing DTO because they are valid Admin-authored Shopify pricing data and may be used by future/other merchant pricing surfaces. This task does not delete them from the reader or database.

Do not invent merchant-facing top-up marketing copy from raw meter structure. The qualitative highlight copy such as `Subscriber top-up rates` is Admin-authored through DATABASE-002/ADMIN-004.

## Onboarding integration

Replace the pricing-card markup currently inside:

```text
app/components/onboarding/Onboarding.jsx
```

with the reusable `MerchantPricingCatalogue` component.

Onboarding continues to render its hero/benefits/how-it-works sections.

The existing top/hero `Choose plan` buttons to:

```text
/app/billing/select
```

are rendered **only when `pricingCatalogue.length > 0`**.

When the catalogue is empty, keep non-pricing navigation such as `How it works`, but render no Choose-plan CTA.

Onboarding passes:

```text
showChoosePlanAction = false
```

to the pricing component because its non-empty page already has the Shopify selection CTA in the surrounding onboarding UI.

## Completed-onboarding NO_CONTRACT integration

Current gap: the loader reads `pricingCatalogue`, but the normal completed-onboarding return object does not include it, and `UsageOverview` does not render it.

Fix exactly:

1. `loader` returns `pricingCatalogue` in the normal completed-onboarding return object as well as onboarding return;
2. `Index` passes `merchantExperienceState` and `pricingCatalogue` to `UsageOverview`;
3. extend `UsageOverview` props accordingly;
4. when `merchantExperienceState === "NO_CONTRACT"`:
   - render `MerchantPricingCatalogue` near the current-plan/lifecycle area;
   - pass `showChoosePlanAction = true`;
   - do **not** render the existing `/app/billing/options` `Manage plan & recovery capacity` button/current-plan action for that state;
5. when state is `ACTIVE` or `FROZEN`, preserve the existing UsageOverview plan-management presentation and do not inject the no-contract catalogue there.

The pricing component's non-empty `showChoosePlanAction=true` action routes only to:

```text
/app/billing/select
```

Shopify remains plan-selection authority.

When NO_CONTRACT catalogue is empty, the component shows pricing unavailable and no pricing CTA.

## Styling target

Match the structural design represented by the accepted pricing-card reference:

```text
wide desktop: equal-height multi-column cards
featured plan visually emphasized without changing data order
compact plan-name pill
large price
localized introductory description
large allowance block
stacked rounded highlight cards
responsive collapse for narrower widths
```

Do not hard-code plan count to four. CSS/grid must render 1..N active plans.

Do not hard-code names Free/Starter/Growth/Scale. The visual target is a layout, not a fixed catalogue.

Use existing Moda green/neutral tokens/current CSS values where already available. Do not introduce a second global styling framework.

## i18n cleanup

After rendering highlights from DB, run exact reference searches for legacy feature keys such as:

```text
billingCommerce.feature.ai
billingCommerce.feature.multilingual
billingCommerce.feature.analytics
billingCommerce.feature.noWhatsappBill
```

Delete these keys from all 20 locale files **only if they have zero remaining runtime references after this task**. If any are still used by another supported surface, preserve them there; do not break unrelated UI.

Generic labels such as per month, most popular, recovery conversations and pricing unavailable remain in static i18n.

## Required tests

### Reader

Prove:

```text
only active plans returned
cataloguePosition order preserved
exact requested locale used for plan description
exact requested locale used for every highlight
highlight position order preserved
missing exact-locale plan translation fails closed
missing exact-locale highlight translation fails closed
no English fallback
no adminLabel/highlight DB ids leaked
```

### Onboarding

Prove:

```text
non-empty catalogue -> pricing component receives plan DTOs
empty catalogue -> pricing unavailable
empty catalogue -> no /app/billing/select choose-plan CTA in onboarding
non-empty -> Shopify choose-plan CTA remains
raw UsageEvent FIXED/VOLUME/GRADUATED/tier table component is not rendered as card content
```

### NO_CONTRACT

Prove loader/result/render behavior:

```text
onboardingCompleted=true + merchantExperienceState=NO_CONTRACT + non-empty catalogue
  -> loader contains pricingCatalogue
  -> UsageOverview receives it
  -> MerchantPricingCatalogue renders
  -> /app/billing/select action available
  -> /app/billing/options manage-capacity action absent

same state + empty catalogue
  -> pricing unavailable
  -> no /app/billing/select
  -> no /app/billing/options
```

### ACTIVE/FROZEN regression

Prove accepted current behavior remains:

```text
ACTIVE -> existing current-plan/manage-capacity UI remains
FROZEN -> existing lifecycle/current-plan behavior remains
catalogue not injected into those states by this task
```

### Card content

With fixture data prove:

```text
price from DB
allowance number from DB
main description from DB locale
featured badge from DB flag
3+ highlight titles/descriptions from DB locale and correct position
changing fixture highlight text changes rendered output without source-code change
no hard-coded Free/Starter/Growth/Scale requirement
```

## Required static scans

After implementation:

```bash
rg -n 'const plans|const topUps|£35|£75|£149|\$35|\$75|\$149' app tests
rg -n 'billingCommerce\.feature\.(ai|multilingual|analytics|noWhatsappBill)' app --glob '!app/i18n/locales/*.json'
rg -n 'BillingPlan|BillingEconomicsSnapshot|BillingUpgradeEconomicsEdge' app/services/merchant-pricing app/components/merchant-pricing
```

Review each result; expected commercial hard-codes/operational dependencies in the ARCH-014 pricing path are zero.

## Required validation

Inspect declared scripts first. Run at minimum:

```bash
npm test
npm run typecheck
npm run build
npm run lint
git diff --check
```

Any changed-file failure is task-owned. Existing unchanged baselines may be referenced only with exact evidence.

## Stop conditions

STOP and return to `moda_architect` if:

- DATABASE-002 highlight models are absent after correct preparation;
- completing the task appears to require querying operational BillingPlan/topology state;
- exact-locale highlights cannot be loaded without English fallback;
- the current merchant experience-state contract materially differs from inspected `NO_CONTRACT` semantics;
- the desired card layout would require reintroducing hard-coded plan-specific commercial copy;
- Shopify subscription creation/management would need to move into Moda.

Do not weaken ARCH-014 authority/isolation to continue.

## Completion protocol

Completion Report must include reader DTO example with highlights, screenshots/source evidence for non-empty/empty/NO_CONTRACT states, focused test counts, hard-code scans and full validation results. Set `status: review`, clear claim, return to `moda_architect`, STOP.
