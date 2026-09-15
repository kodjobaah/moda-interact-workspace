---
id: ARCH-014-ADMIN-001
architecture_id: ARCH-014
title: Implement deterministic multi-meter full-portfolio economics engine
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-ADMIN-009
enables:
- ARCH-014-ADMIN-002
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-ADMIN-001

## Objective

Add a **new pure ARCH-014 economics module** that evaluates 0..5 Shopify pricing usage events and every lower->higher plan pair in a supplied ARCH-014 catalogue order. Do not replace or reinterpret the existing operational `validateSinglePackShopifyEconomics` path in this task.

This task is deliberately pure/domain-oriented so ADMIN-002 can consume it from the plan builder without creating a second calculator.

## Authorized implementation surface

```text
src/lib/admin/merchant-pricing-economics.ts               # new primary module
src/lib/admin/upgrade-economics-guardrail.ts               # only reuse/export existing generic cost/premium helpers if needed; no operational semantic change
src/i18n/locales/en.json                                   # only messages used by economics presentation if required
src/i18n/required-keys.ts                                  # only if corresponding i18n keys added
tests/unit/merchant-pricing-economics.test.ts              # new
# existing upgrade-economics unit test only if a helper export must be adjusted
```

Do not change plan actions, Prisma writes, plan builder UI or existing BillingEconomicsSnapshot persistence here.

## Exact pure types

Define equivalents of these bounded types in `merchant-pricing-economics.ts`:

```ts
type MerchantUsagePricing =
  | { mode: "FIXED"; currency: string; unitAmountMinor: number }
  | {
      mode: "GRADUATED" | "VOLUME";
      currency: string;
      tiers: Array<{
        upTo: number | null;
        amountPerUnitMinor: number;
        flatAmountMinor: number;
      }>;
    };

type MerchantPricingUsageOffer = {
  eventHandle: string;
  creditsGrantedPerUnit: number;
  maximumUnitsPerBillingPeriod: number | null;
  pricing: MerchantUsagePricing;
};

type MerchantPricingEconomicsPlan = {
  id: string;                 // stable MerchantPricingPlan/candidate identity supplied by caller
  shopifyPlanHandle: string;
  name: string;
  includedRecoveryCredits: number;
  recurringAmountMinor: number;
  currency: string;
  usageEvents: MerchantPricingUsageOffer[];
};
```

Do not put React/Prisma objects into the pure evaluator.

## Input validation

Reject/UNVERIFIED (never silently normalize invalid commercial values) unless:

```text
0..5 usage events
unique non-empty trimmed eventHandle
creditsGrantedPerUnit positive safe integer
maximumUnitsPerBillingPeriod null or positive safe integer
pricing currency normalized uppercase 3-letter and equals plan currency
FIXED unitAmountMinor non-negative safe integer
GRADUATED/VOLUME 1..6 tiers
finite upTo positive + strictly increasing
final tier upTo=null
all price fields non-negative safe integers
recurringAmountMinor non-negative safe integer
includedRecoveryCredits non-negative safe integer
```

If a usage event has an unbounded zero-cost positive-quantity path, return UNVERIFIED `UNBOUNDED_ZERO_COST_USAGE_EVENT`. Do not discard it and do not assume a quantity cap.

## Required bounded result codes

Define ARCH-014 result codes at minimum:

```text
PORTFOLIO_ECONOMICS_OK
NO_TOPUPS_AVAILABLE
TOPUPS_CHEAPER_THAN_UPGRADE
UPGRADE_ADVANTAGE_TOO_SMALL
MISSING_PLAN_PRICE
CURRENCY_MISMATCH
INVALID_PORTFOLIO_ORDER
NON_INCREASING_ALLOWANCE
INVALID_USAGE_EVENT
INVALID_USAGE_PRICING
UNBOUNDED_ZERO_COST_USAGE_EVENT
ECONOMICS_SEARCH_LIMIT_EXCEEDED
```

Statuses remain `PASS | FAIL | UNVERIFIED`. ADMIN-002 must treat anything other than PASS as blocking.

## Pricing cost semantics

Use the current existing semantics already implemented by `calculateUsagePricingCostMinor` unless a focused test proves they differ from this contract:

```text
FIXED:
  total = unitAmountMinor * quantity

VOLUME:
  choose the one tier containing total quantity
  total = tier.flatAmountMinor + tier.amountPerUnitMinor * quantity

GRADUATED:
  quantity is allocated cumulatively through tiers
  for each entered tier add flatAmountMinor once + amountPerUnitMinor * unitsInTier
```

Quantity 0 costs 0.

## Exact candidate quantity generation per usage event

For requested `creditsNeeded > 0` and event credits `c`:

```text
soloUnits = ceil(creditsNeeded / c)
```

Candidate quantities always include `0`.

For FIXED and GRADUATED include every integer `1..min(soloUnits, maximumUnits if set)`.

For VOLUME include:

1. every integer `1..min(soloUnits, maximumUnits if set)`;
2. the first quantity of every later pricing tier (`previous finite upTo + 1`) that is greater than `soloUnits` and <= finite maximum if one exists;
3. if a finite maximum exists, include that maximum.

Reason: VOLUME pricing may become cheaper at a later tier boundary, so the solver must not assume quantities above `soloUnits` are irrelevant.

Define:

```text
MAX_PORTFOLIO_ECONOMICS_CREDITS = 100_000
MAX_METER_CANDIDATE_QUANTITY = 100_000
```

If `creditsNeeded`, any required candidate quantity, or a finite maximum needed for exact evaluation exceeds these limits, return UNVERIFIED `ECONOMICS_SEARCH_LIMIT_EXCEEDED`. Do not truncate/approximate.

## Exact multi-meter dynamic programming

Export a pure function equivalent to:

```text
findCheapestMerchantUsageCombination(usageEvents, creditsNeeded)
```

Process usage events in `eventHandle` lexicographic order so result does not depend on caller array order.

For each event, enumerate its candidate quantities and calculate that event's **total** cost at that quantity using the pricing function; do not treat tiered pricing as additive independent unit offers.

Combine events one at a time. DP state key:

```text
min(creditsNeeded, totalCreditsGranted)
```

For a candidate path retain the better result by this exact ordering:

1. lower `totalCostMinor`;
2. then lower total number of usage-event units;
3. then lower overshoot (`actualCreditsGranted - creditsNeeded`);
4. then lexicographic comparison of canonical summary strings `eventHandle:quantity` for non-zero quantities.

The returned summary contains one row per non-zero event in eventHandle order:

```text
eventHandle
quantity
creditsGranted
costMinor
```

Return actual uncapped `creditsGranted`, not only the capped DP key.

If no exact bounded path can meet the target, return an UNVERIFIED result rather than fabricating a price.

## Exact pair evaluator

For lower/higher plan:

1. identities must differ;
2. currencies must be valid and equal;
3. `higher.includedRecoveryCredits` must be strictly greater than lower;
4. `additionalCreditsNeeded = higher - lower`;
5. if lower has zero usage events: PASS `NO_TOPUPS_AVAILABLE`;
6. otherwise calculate cheapest lower-plan combination;
7. call/reuse existing premium comparison semantics using:
   - current/lower recurring amount;
   - higher recurring amount;
   - cheapest top-up cost;
   - current `minimumUpgradePremiumBps`;
8. zero-cost offers are valid economics and may correctly cause FAIL;
9. invalid/missing evidence produces UNVERIFIED and therefore blocks caller save.

Do not special-case FREE allowance to 0 in ARCH-014: this informational catalogue explicitly stores the recovery credits displayed to merchants, and the comparison uses the catalogue's `includedRecoveryCredits` value supplied by the caller.

## Exact full-portfolio evaluator

Export a pure function equivalent to:

```text
evaluateMerchantPricingPortfolio({
  orderedPlanIds,
  plansById,
  minimumUpgradePremiumBps
})
```

Validation:

- `orderedPlanIds` contains every plan exactly once;
- all ids resolve;
- no duplicate ids;
- ordering is accepted from caller and NEVER inferred by this module. The caller must derive it from MerchantPricingPlan.cataloguePosition.

Generate pair evaluations in exact nested-loop order:

```text
for i = 0..n-2
  for j = i+1..n-1
    evaluate orderedPlanIds[i] -> orderedPlanIds[j]
```

A 4-plan chain therefore returns exactly 6 results in this order:

```text
P0->P1
P0->P2
P0->P3
P1->P2
P1->P3
P2->P3
```

Export `assertMerchantPricingPortfolioPass(results)` that throws one bounded error if **any** result is FAIL or UNVERIFIED. Include failing pair handles/codes, but not raw translation/provider payloads.

## Required focused tests

Implement all of these exact cases:

1. 0 meters => PASS `NO_TOPUPS_AVAILABLE`;
2. one FIXED meter reproduces simple unit arithmetic;
3. two FIXED meters choose a cheaper mixed combination;
4. three meters where optimum uses more than one event;
5. GRADUATED cost uses cumulative tiers;
6. VOLUME later-tier entry above `soloUnits` is considered;
7. finite `maximumUnitsPerBillingPeriod` is respected;
8. zero-cost finite meter participates and can cause economic FAIL;
9. zero-cost unbounded meter => UNVERIFIED exact code;
10. duplicate event handles => invalid;
11. 6 usage events => invalid;
12. 7 tiers => invalid;
13. currency mismatch => UNVERIFIED;
14. search limit => exact UNVERIFIED code;
15. result/tie-break unchanged when input event order is reversed;
16. four plans return exactly six pair evaluations in specified order;
17. a non-adjacent pair can fail while adjacent pairs pass and assertion blocks;
18. non-increasing higher allowance => blocking result;
19. invalid ordered ids => `INVALID_PORTFOLIO_ORDER`;
20. existing `validateSinglePackShopifyEconomics` tests/behaviour remain unchanged.

## Validation

Inspect `package.json` and run:

```text
node --experimental-strip-types --test tests/unit/merchant-pricing-economics.test.ts
npm run test:unit
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run format:check
git diff --check
```

Do not require Prisma/build if this pure task did not touch Prisma/Next integration; if normal repository CI requires them, record/run them without widening implementation scope.

## Stop conditions

STOP if the implementation would require:

- changing actual App Events/top-up runtime;
- changing existing database schema;
- changing the semantics of the existing single-pack operational guardrail to make ARCH-014 work;
- inferring catalogue order inside the economics module.
- reading BillingPlan, BillingEconomicsSnapshot or BillingUpgradeEconomicsEdge data inside the economics module.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

### Status

Ready for Architect Review

### Review Findings Addressed

- Detects unbounded zero-cost VOLUME paths when only the final open-ended tier is free.
- Rejects padded event handles instead of silently trimming commercial identifiers.
- Uses one locale-independent lexicographic comparator for event ordering and tie-breaking.
- Returns `ECONOMICS_SEARCH_LIMIT_EXCEEDED` for required unbounded VOLUME tier entries above the candidate limit.

### Validation Results

- Focused ARCH-014 tests: 24/24 pass, including four regression cases for the review findings.
- Existing admin economics unit suite: 42/42 pass.
- `git diff --check`: pass.
- Implementation commit: `af1b933` (`fix(admin): close portfolio economics validation gaps`).
- Full repository tests and toolchain checks remain subject to the previously recorded missing dependency/tool binaries (`bullmq`, `typescript`, `eslint`, `prettier`).

### Handoff

- Implementation branch: `task/ARCH-014-ADMIN-001`, published and clean.
- Existing single-pack operational economics semantics remain unchanged.
- Return to `moda_architect`; do not begin ARCH-014-ADMIN-002.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `moda-interact-admin/src/lib/admin/merchant-pricing-economics.ts` — pure bounded multi-meter pricing, dynamic-programming combination, pair, portfolio, validation and blocking assertion APIs.
- `moda-interact-admin/tests/unit/merchant-pricing-economics.test.ts` — 20 focused ARCH-014 cases covering pricing modes, limits, validation, deterministic tie-breaking, portfolio ordering, failures and legacy behavior.

### Work Completed

- Added deterministic FIXED, VOLUME and GRADUATED usage pricing semantics with the required candidate quantity bounds.
- Added validation for usage events, tiers, currencies, plan prices, allowances and unbounded zero-cost paths.
- Added lexicographically ordered multi-meter dynamic programming with the specified cost, unit, overshoot and summary tie-break rules.
- Added full ordered lower-to-higher portfolio evaluation and an assertion that blocks FAIL and UNVERIFIED results.
- Left the existing `validateSinglePackShopifyEconomics` implementation and behavior unchanged.

### Validation Results

- Focused ARCH-014 tests: 20/20 pass.
- Existing admin economics unit suite: 42/42 pass.
- `git diff --check`: pass.
- `npm test`: baseline blocked by missing `bullmq` dependency in existing queue-monitor/security tests; no ARCH-014 test failure was reported before those unrelated imports failed.
- `npx tsc --noEmit --pretty false`: unavailable because `typescript` is not installed in the worktree.
- `npm run lint`: unavailable because `eslint` is not installed in the worktree.
- `npm run format:check`: unavailable because `prettier` is not installed in the worktree.
- Direct Node test runs emit the repository's existing module-type warning; tests pass despite it.

### Implementation Evidence

- Implementation commit: `a6cfc60` (`feat(admin): add portfolio pricing economics evaluator`).
- Published branch: `task/ARCH-014-ADMIN-001`.
- Parent claim commit: `da79985`.

### Deviations

- No Prisma, Next integration, operational App Events, top-up runtime, or existing single-pack guardrail changes were required.
- Architect Review remains untouched. Return to `moda_architect` for review.
