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
- ARCH-014-ADMIN-003
- ARCH-014-SHOPIFY-001
enables: []
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-SYSTEM-TEST-001

## Terminal/manual gate

Do **not** auto-start. The developer explicitly invokes this task after DATABASE-001, ADMIN-001/002/003 and SHOPIFY-001 are integrated and manually smoke-checked. No implementation task depends on this task.

## Objective

Prove the integrated ARCH-014 contract from Admin MerchantPricing plan creation/edit through additive MerchantPricing persistence to localized onboarding presentation, while proving the catalogue is independent from operational `BillingPlan`/topology state and Shopify remains subscription authority.

## Authorized implementation surface

Inspect existing `moda-interact-system-test` conventions first. Add only ARCH-014-specific test/fixture/helper files inside existing `test/`, `src/` and `scripts/` structure. Do not create a second orchestration framework and do not modify production implementation to make tests pass.

## Required scenario A — complete create + translation template/import + merchant render

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
- at least one plan is marked featured.

Prove:

1. generated Admin template contains exact schema/meta and 20 locales, English populated + 19 empty;
2. completed paste/import validates 20/20;
3. final create transaction persists only one MerchantPricing plan + exact 20 translations/events/tiers plus ARCH-014 position shifts where required;
4. no `BillingPlan`, `BillingEconomicsSnapshot` or `BillingUpgradeEconomicsEdge` row is required/created/updated by the ARCH-014 create;
5. merchant onboarding in at least `en`, `fr`, `ja`, `pt-BR`, `pt-PT`, `zh-Hans`, `zh-Hant` displays exact corresponding DB description;
6. plan name, recurring price, allowance, featured state and usage pricing are DB-driven;
7. merchant plan order follows `cataloguePosition`, not price/name/allowance.

## Scenario B — translation failure is fail-closed

Try at least:

```text
missing locale
blank locale description
unexpected pt_BR alias
English source mismatch
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
