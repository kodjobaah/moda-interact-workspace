---
id: ARCH-014-SYSTEM-TEST-001
architecture_id: ARCH-014
title: Validate Admin-authored pricing catalogue through localized merchant onboarding
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-002
- ARCH-014-ADMIN-004
- ARCH-014-ADMIN-005
- ARCH-014-SHOPIFY-002
enables: []
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-SYSTEM-TEST-001

## Terminal/manual gate

Do **not** auto-start. The developer explicitly invokes this task only after DATABASE-002, ADMIN-004, ADMIN-005 and SHOPIFY-002 are architect-accepted/integrated and the completed earlier ARCH-014 tasks remain integrated. No implementation task depends on this task.

## Objective

Prove the integrated ARCH-014 contract from Admin MerchantPricing plan creation/edit through additive MerchantPricing persistence to localized onboarding presentation, while proving the catalogue is independent from operational `BillingPlan`/topology state and Shopify remains subscription authority.

## Authorized implementation surface

Inspect existing `moda-interact-system-test` conventions first. Add only ARCH-014-specific test/fixture/helper files inside existing `test/`, `src/` and `scripts/` structure. Do not create a second orchestration framework and do not modify production implementation to make tests pass.

## Required scenario A — complete create + schema-v2 translation/highlight import + merchant render

Build a four-plan ARCH-014 catalogue in this exact order:

```text
0 Free
1 Starter
2 Growth
3 Scale
```

Requirements:

- at least one plan has 3 usage events;
- full portfolio includes at least one FIXED, one GRADUATED and one VOLUME event;
- at least one zero-cost usage event has an explicit finite maximum;
- every persisted plan has exact completed 20-locale descriptions;
- every plan has at least 3 ordered highlights; at least one plan has 4;
- every highlight has exact 20-locale title+description translations;
- at least one plan is marked featured.

Prove:

1. generated Admin template is schemaVersion 2, contains exact meta + 20 locales, and contains the exact highlight contentKey set; English description/highlights are populated and the other 19 locale values are initially empty for new content;
2. completed paste/import validates 20/20;
3. final create transaction persists only one MerchantPricing plan + exact 20 plan translations + usage events/tiers + ordered highlights + exactly 20 translations per highlight, plus ARCH-014 position shifts where required;
4. no `BillingPlan`, `BillingEconomicsSnapshot` or `BillingUpgradeEconomicsEdge` row is required/created/updated by the ARCH-014 create;
5. merchant onboarding in at least `en`, `fr`, `ja`, `pt-BR`, `pt-PT`, `zh-Hans`, `zh-Hant` displays exact corresponding DB plan description and ordered DB highlight title/descriptions;
6. plan name, recurring price, allowance, featured state and usage pricing are DB-driven;
7. merchant plan order follows `cataloguePosition`, not price/name/allowance;
8. primary merchant pricing cards render structured allowance + localized highlight blocks and do not render raw FIXED/VOLUME/GRADUATED tier mechanics.

## Scenario B — translation failure is fail-closed

Try at least:

```text
missing locale
blank locale description
unexpected pt_BR alias
English source mismatch
missing highlight translation
blank highlight title
unknown highlight contentKey
English highlight source mismatch
```

Prove no partial `MerchantPricingPlan` exists after failure and merchant app never falls back to English plan description for a supported resolved locale.

## Scenario C — portfolio-wide economics catches non-adjacent defect

Create a proposed MerchantPricing plan/edit where adjacent pairs PASS but at least one transitive lower->higher pair FAILs.

Prove:

```text
full matrix contains the transitive pair
Admin blocks final write
no MerchantPricing plan/translation/event mutation commits
```

## Scenario D — multi-meter cheapest combination

Create a lower catalogue plan where the cheapest capacity path uses a combination of at least two different usage events. Prove Admin preview selects the expected deterministic combination and applies configured `minimumUpgradePremiumBps` against the chosen higher plan.

Also cover GRADUATED and VOLUME pricing cost semantics.

## Scenario E — catalogue insertion without operational topology

Start with positions:

```text
0 Free
1 Starter
2 Scale
```

Create Growth with `AFTER:<Starter MerchantPricingPlan.id>`.

Prove exactly:

```text
Starter remains position 1
Scale shifts from 2 -> 3
Growth is created at 2
final global positions are 0,1,2,3
merchant display uses 0,1,2,3
```

Prove no `BillingUpgradeEconomicsEdge` query/write and no BillingPlan id is used to determine insertion.

## Scenario F — active visibility and activation economics

With complete persisted catalogue rows:

1. set one plan inactive through ARCH-014 Admin action;
2. prove merchant reader omits it but remaining rows preserve relative `cataloguePosition` order;
3. alter another active plan so activating the inactive plan would create a FAIL or UNVERIFIED pair;
4. prove activation is blocked and `isActive` remains false;
5. restore valid economics and prove activation succeeds.

No operational BillingPlan active flag participates.

## Scenario G — additive DB isolation

Against integrated migration/schema evidence prove:

- ARCH-014 migration created only `MerchantPricing*` objects and ARCH-014 functions/triggers/types;
- no pre-existing table gained an ARCH-014 column/index/constraint/trigger;
- no existing enum was modified;
- `MerchantPricingPlan` has no FK/relation to `BillingPlan`, `BillingEconomicsSnapshot` or `BillingUpgradeEconomicsEdge`;
- existing operational billing table definitions are unchanged by ARCH-014 migration.

## Scenario H — hard-coded catalogue absence

Static assertions over integrated `moda-interact` prove:

```text
no onboarding const plans commercial array
no onboarding const topUps matrix
no stale £19/£49/£99 PlanSelector catalogue
no old £35/£75/£149 hard-coded onboarding pricing
no plan-specific free/starter/growth/scale description/topup i18n keys
```

Generic i18n remains complete across all 20 catalogues.

## Scenario I — Shopify authority unchanged

During Admin catalogue create/edit/activation and merchant onboarding reads, assert no Shopify subscription-create/change/cancel mutation is invoked.

Merchant CTA still routes to existing Shopify-managed selection boundary. ARCH-014 system acceptance does not require creating a live Shopify subscription.

## Scenario J — operational billing independence

Seed or retain operational billing rows with deliberately different names/order/active states from ARCH-014 catalogue rows where safe in the test environment.

Prove ARCH-014 behaviour is unchanged:

```text
Admin catalogue order/visibility comes from MerchantPricingPlan only
portfolio economics inputs come from MerchantPricingPlan only
merchant reader order/visibility comes from MerchantPricingPlan only
```

This scenario must not mutate production operational billing semantics; use existing system-test fixture mechanisms.


## Scenario K — Admin step gating, placement concurrency and translation retention

Prove all of the following through integrated Admin behavior/state evidence:

```text
Create/Save control does not exist on steps 1..6
human placement labels are Before <name>/After <name>, never raw ids
create uses a captured ordered-id snapshot
fresh catalogue order change before submit -> exact stale-list rejection and zero writes
portfolio FAIL/UNVERIFIED cannot advance to step 7
schema-v2 create requires completed 20/20 plan + highlight translations
edit with unchanged English description/highlight source retains existing 20/20 translations without re-import
highlight reorder only retains translations
adding/removing/changing a highlight requires a new completed schema-v2 package
```

## Scenario L — completed NO_CONTRACT and empty-catalogue merchant behavior

For `onboardingCompleted=true` and merchant experience state `NO_CONTRACT`:

1. with a non-empty active catalogue, prove the loader returns the catalogue and the reusable MerchantPricing catalogue renders in the completed merchant UI;
2. prove the visible plan card contains DB-driven price, structured allowance and at least 3 ordered localized highlight cards;
3. prove the action routes to `/app/billing/select` and the `/app/billing/options` manage-capacity CTA is absent in NO_CONTRACT;
4. with zero active MerchantPricing plans, prove pricing-unavailable is rendered and there is no `/app/billing/select` or `/app/billing/options` pricing CTA;
5. prove ACTIVE/FROZEN existing merchant plan-management behavior is not replaced by this NO_CONTRACT catalogue.

## Scenario M — highlight database isolation and localization integrity

Prove DATABASE-002 specifically:

```text
creates only MerchantPricingPlanHighlight and MerchantPricingPlanHighlightTranslation persistence + ARCH-014 highlight validation objects
contains no ALTER TABLE on MerchantPricingPlan or any other pre-existing table
allows a virtual Prisma inverse relation without physical parent-table mutation
requires exact 20 translations per highlight at commit
requires exact locale set
requires title 1..120 and description 1..500
requires contiguous 0..N-1 highlight positions
plan delete cascades highlight children
```

Also prove merchant reader has no English fallback for highlight content.

## Required evidence table

Return one table in Completion Report:

| Scenario | PASS/FAIL | DB evidence | Admin/economics evidence | Merchant UI evidence | Operational-isolation / Shopify-authority evidence |
|---|---|---|---|---|---|

Record exact integrated repository commits/githashes exercised.

## Validation

Use repository-declared scripts that exist:

```text
npm test
npm run typecheck
npm run lint
git diff --check
```

If live browser evidence is useful, it may supplement but not replace deterministic state/source assertions. No provider secrets in test evidence.

## Stop conditions

STOP and report to `moda_architect` if:

- prerequisite implementations are not architect-accepted/integrated;
- integrated schema differs from ARCH-014 task contract;
- testing would require exposing provider credentials;
- ARCH-014 implementation depends on operational BillingPlan/topology rows contrary to the contract;
- a failure belongs to production implementation rather than test harness.

Do not weaken the test to match a defect.

## Completion protocol

Update Completion Report with evidence, set `status: review`, clear claim, return to `moda_architect`, STOP. Final acceptance remains manual.
