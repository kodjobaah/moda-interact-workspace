---
id: ARCH-027-SHARED-001
architecture_id: ARCH-027
title: Extract deterministic merchant usage-price evaluator
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-027-SHARED-003
created: 2026-10-03
updated: 2026-10-03
---

# Extract deterministic merchant usage-price evaluator

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Extract the existing deterministic `FIXED` / `GRADUATED` / `VOLUME` merchant usage-price arithmetic into the canonical Shared billing entrypoint so Admin portfolio economics and the future Woo billing adapter can consume exactly the same price calculation without duplicating formulas.

This task produces one unpublished Shared capability only:

```text
validated usage-pricing definition + requested quantity
                    |
                    v
       evaluateMerchantUsagePrice(...)
                    |
        +-----------+-----------+
        |                       |
        v                       v
 deterministic quote      stable failure
 amount/currency          classification
```

The evaluator owns only deterministic price validation and arithmetic. It does **not** own plan membership, credit grants, per-period quantity limits, provider compatibility, Woo USD eligibility, Marketplace revenue share, provider surcharge/discount policy, portfolio upgrade economics, or purchase authorization.

## Context

ARCH-027 keeps one Moda commercial catalogue for Shopify and WooCommerce Marketplace billing.

The current Admin implementation already contains deterministic merchant usage pricing arithmetic in:

```text
moda-interact-admin/src/lib/admin/merchant/pricing-economics.ts
```

At the synchronized ARCH-027 baseline, that file contains a private `calculateCost(...)` implementation used by portfolio economics with these semantics:

```text
FIXED
    unitAmountMinor * quantity

VOLUME
    select the tier containing the requested total quantity
    flatAmountMinor + amountPerUnitMinor * quantity

GRADUATED
    walk tiers cumulatively
    for every occupied tier:
        flatAmountMinor + amountPerUnitMinor * unitsInTier
    sum occupied tiers
```

The future Woo `/charges` adapter must calculate the concrete one-time charge from the same `MerchantPricingUsageEvent` / `MerchantPricingUsageTier` configuration. Reimplementing these formulas in `moda-interact-api` would create pricing drift.

`moda-interact-shared` already publishes the public runtime entrypoint:

```text
@modainteract/moda-interact-shared/billing
```

through:

```text
src/billing.ts
src/billing.test.ts
scripts/validate-billing-entrypoint.mjs
```

Therefore ARCH-027 does not require a new Shared package subpath. Extend the existing billing entrypoint.

### Price-parity invariant

ARCH-027 has deliberately rejected provider-specific retail-price adjustment in the billing adapter.

Equivalent catalogue pricing is the customer-facing price source for both Shopify and Woo Marketplace. This Shared evaluator therefore MUST NOT contain:

```text
Woo marketplace fee adjustment
Shopify price adjustment
provider-specific multiplier
provider-specific surcharge
provider-specific discount
revenue-share arithmetic
```

Provider commercial economics may affect Moda margin analysis, but they do not alter this canonical catalogue price calculation.

### Transitional duplication

During this task, the existing Admin-local implementation remains unchanged because `moda_shared` does not own `moda-interact-admin`.

The intended sequence is:

```text
ARCH-027-SHARED-001
    implement and architect-accept canonical evaluator
        |
        +--> ARCH-027-SHARED-002
             may proceed independently
        |
        v
ARCH-027-SHARED-003
    publish accepted ARCH-027 Shared capabilities
        |
        +--> ARCH-027-ADMIN-001
             replace Admin-local arithmetic with Shared evaluator
        |
        `--> ARCH-027-API-* consumer task
             use the same Shared evaluator for Woo charges
```

Temporary formula duplication exists only until the consumer migration tasks install the published Shared version.

## Scope

Modify only `moda-interact-shared` plus the assigned parent task report.

Expected implementation files are bounded to:

```text
moda-interact-shared/src/billing.ts
moda-interact-shared/src/billing.test.ts
moda-interact-shared/scripts/validate-billing-entrypoint.mjs
```

A small billing-local source module may be introduced if repository-local maintainability clearly benefits, but the public contract MUST remain exported through:

```text
@modainteract/moda-interact-shared/billing
```

Do not add another package export path solely for ARCH-027 pricing.

### Required public pricing contract

The accepted Shared billing entrypoint MUST expose logically equivalent runtime/type contracts to the following names and semantics.

#### Pricing modes

```ts
export const MERCHANT_USAGE_PRICING_MODES = [
  "FIXED",
  "GRADUATED",
  "VOLUME",
] as const;
```

The corresponding public mode type is the exact union:

```ts
"FIXED" | "GRADUATED" | "VOLUME"
```

#### Tier shape

A tier has exactly these logical fields:

```ts
type MerchantUsagePricingTier = Readonly<{
  upTo: number | null;
  amountPerUnitMinor: number;
  flatAmountMinor: number;
}>;
```

Validation rules:

```text
amountPerUnitMinor
    non-negative safe integer

flatAmountMinor
    non-negative safe integer

upTo when finite
    positive safe integer

finite upTo values
    strictly increasing

null upTo
    permitted only on the final tier

final tier
    MUST have upTo = null

tier count
    1..6 inclusive
```

Do not silently sort, trim, repair, clamp or normalize malformed tier evidence.

#### Pricing shape

Expose one public runtime schema and inferred/public type representing exactly:

```ts
type MerchantUsagePricing =
  | {
      mode: "FIXED";
      currency: string;
      unitAmountMinor: number;
    }
  | {
      mode: "GRADUATED" | "VOLUME";
      currency: string;
      tiers: MerchantUsagePricingTier[];
    };
```

`currency` validation is exactly:

```text
three uppercase ASCII letters: ^[A-Z]{3}$
```

This task does not perform FX conversion and does not normalize lowercase or padded currency values.

For `FIXED`:

```text
unitAmountMinor
    non-negative safe integer
```

Zero-valued pricing is valid at this primitive level. Whether a zero-cost offer is allowed to be unbounded depends on usage-event limits and remains a caller/domain responsibility.

#### Stable evaluation result

Expose:

```ts
export const MERCHANT_USAGE_PRICE_ERROR_CODES = [
  "INVALID_PRICING",
  "INVALID_QUANTITY",
  "ARITHMETIC_OVERFLOW",
] as const;
```

and a public result logically equivalent to:

```ts
type MerchantUsagePriceEvaluation =
  | Readonly<{
      ok: true;
      currency: string;
      quantity: number;
      amountMinor: number;
    }>
  | Readonly<{
      ok: false;
      code:
        | "INVALID_PRICING"
        | "INVALID_QUANTITY"
        | "ARITHMETIC_OVERFLOW";
    }>;
```

The evaluator MUST be exported as:

```ts
evaluateMerchantUsagePrice(pricing, quantity)
```

It MUST accept runtime input safely. The implementation may type the first argument as `unknown` or another runtime-safe input type provided malformed external/runtime values cannot bypass validation.

### Deterministic validation order

Evaluation order is part of the contract:

```text
1. validate pricing shape and pricing values
2. validate quantity
3. calculate price
4. verify every arithmetic result is a safe integer
```

Therefore when both pricing and quantity are invalid, return:

```text
INVALID_PRICING
```

Quantity is valid only when it is a non-negative JavaScript safe integer.

The primitive deliberately permits:

```text
quantity = 0
```

and returns an amount of zero for valid pricing. Purchase commands will require positive quantities separately; Admin economics needs zero as a valid calculation boundary.

### Exact arithmetic semantics

#### FIXED

For valid pricing:

```text
amountMinor = unitAmountMinor * quantity
```

Examples:

```text
unitAmountMinor = 100, quantity = 0 -> 0
unitAmountMinor = 100, quantity = 2 -> 200
```

Any unsafe-integer product returns:

```text
ARITHMETIC_OVERFLOW
```

#### VOLUME

Select the **first** tier satisfying:

```text
tier.upTo === null
OR
quantity <= tier.upTo
```

Then:

```text
amountMinor = tier.flatAmountMinor
            + tier.amountPerUnitMinor * quantity
```

The chosen tier prices the **entire** requested quantity.

Canonical vector:

```text
tiers:
  upTo=2,    amountPerUnitMinor=100, flatAmountMinor=0
  upTo=null, amountPerUnitMinor=10,  flatAmountMinor=0

quantity=2 -> 200
quantity=3 -> 30
```

Do not reproduce Admin candidate-search behaviour in this primitive. The evaluator prices the quantity it is given; it does not choose a different quantity because a later volume tier happens to be cheaper.

#### GRADUATED

Walk tiers in configured order. For each tier actually containing one or more requested units:

```text
occupiedTierCost = tier.flatAmountMinor
                 + tier.amountPerUnitMinor * unitsInThatTier
```

Sum the occupied-tier costs.

A flat amount is charged once for each **occupied** tier, matching the synchronized Admin implementation.

Canonical vector:

```text
tiers:
  upTo=2,    amountPerUnitMinor=10, flatAmountMinor=5
  upTo=null, amountPerUnitMinor=5,  flatAmountMinor=2

quantity=0 -> 0
quantity=1 -> 15
quantity=2 -> 25
quantity=3 -> 32
```

### Non-mutation and determinism

The evaluator MUST NOT mutate:

```text
pricing object
tiers array
tier objects
```

Repeated evaluation of structurally equal inputs MUST return structurally equal results.

No current time, randomness, environment variable, database access, network access or provider state may influence the result.

## Out of Scope

- Modifying `moda-interact-admin`.
- Modifying `moda-interact-api`.
- Modifying the database schema or migrations.
- Publishing `@modainteract/moda-interact-shared`.
- Changing the Shared package version.
- Creating a new package export/subpath.
- Moving the entire Admin portfolio-economics engine into Shared.
- `MerchantPricingPlan` ordering or upgrade comparisons.
- `creditsGrantedPerUnit` validation or multiplication.
- `maximumUnitsPerBillingPeriod` validation/enforcement.
- Determining whether a usage event belongs to the current plan.
- Woo USD-only provider compatibility.
- Shopify handle/meter resolution.
- Woo contract creation.
- Woo Marketplace fee/revenue-share calculation.
- Provider-specific price adjustment, multiplier, surcharge or discount.
- Currency conversion.
- Tax calculation.
- Rejecting unbounded zero-cost usage offers; the primitive lacks the usage-event maximum required to make that decision.
- Merchant purchase authorization.
- Recovery-credit purchase persistence.
- Woo webhook schemas/lifecycle contracts; those belong to the separate ARCH-027 Shared contract task.
- Consumer dependency/version updates.

## Requirements

### R1 — One canonical deterministic evaluator

Shared exposes exactly one canonical public evaluator for the per-event FIXED/GRADUATED/VOLUME arithmetic required by ARCH-027 consumers.

Consumers must not need to know which billing provider will ultimately receive the result.

### R2 — Existing Admin arithmetic is preserved

The evaluator's arithmetic must match the synchronized Admin implementation for the same validated pricing and quantity.

At minimum, exact regression vectors must prove:

```text
FIXED:
  100 x 2 = 200

VOLUME:
  [{upTo:2, unit:100, flat:0}, {upTo:null, unit:10, flat:0}]
  quantity 2 = 200
  quantity 3 = 30

GRADUATED:
  [{upTo:2, unit:10, flat:5}, {upTo:null, unit:5, flat:2}]
  quantity 1 = 15
  quantity 2 = 25
  quantity 3 = 32
```

### R3 — Invalid configuration fails closed

Malformed pricing returns `INVALID_PRICING`; it must not be normalized into a valid price.

Required negative cases include:

```text
lowercase currency
padded currency
negative amount
fractional amount
unsafe integer amount
zero/negative finite upTo
fractional upTo
non-increasing finite tiers
null tier before the final tier
final tier not open-ended
zero tiers
more than six tiers
wrong fields for the selected pricing mode
```

### R4 — Invalid quantity fails closed

For otherwise valid pricing, each of the following returns `INVALID_QUANTITY`:

```text
negative quantity
fractional quantity
NaN
Infinity
quantity > Number.MAX_SAFE_INTEGER
```

### R5 — Overflow is explicit

Arithmetic overflow must never silently round or return an unsafe number.

Any multiplication/addition that leaves JavaScript safe-integer bounds returns:

```text
ARITHMETIC_OVERFLOW
```

### R6 — Zero is a valid primitive calculation boundary

For valid pricing:

```text
quantity = 0
```

returns:

```text
{
  ok: true,
  currency: <validated currency>,
  quantity: 0,
  amountMinor: 0
}
```

No tier flat amount is charged for zero quantity.

### R7 — No provider pricing drift

The evaluator contains no branch on Shopify/Woo/provider/platform identity and no marketplace-adjustment arithmetic.

Equivalent pricing input + quantity always produces the same retail amount irrespective of eventual provider.

### R8 — Existing billing entrypoint remains backward compatible

All existing exports from:

```text
@modainteract/moda-interact-shared/billing
```

remain available and existing Shared billing tests continue to pass.

The existing billing entrypoint validator must be extended to prove the new runtime exports and generated declaration/type exports are present in the package artifact.

## Work Items

- [ ] Re-read the synchronized Admin `pricing-economics.ts` arithmetic before implementation and record any source divergence from this task as an architectural concern rather than silently changing the contract.
- [ ] Add the public pricing-mode constant/type to the existing Shared billing entrypoint.
- [ ] Add the public tier runtime schema/type with the exact bounds/order/open-ended-final-tier rules.
- [ ] Add the public FIXED/GRADUATED/VOLUME pricing runtime schema/type.
- [ ] Add the stable pricing-evaluation error-code constant/type.
- [ ] Add the public `MerchantUsagePriceEvaluation` result type.
- [ ] Implement `evaluateMerchantUsagePrice(...)` with the exact validation order defined by this task.
- [ ] Implement FIXED arithmetic with safe-integer overflow protection.
- [ ] Implement VOLUME arithmetic with whole-quantity selected-tier semantics.
- [ ] Implement GRADUATED cumulative arithmetic with one flat amount per occupied tier.
- [ ] Preserve zero-quantity semantics without charging tier flat amounts.
- [ ] Prove evaluation does not mutate pricing/tier input.
- [ ] Add focused unit tests for all canonical positive vectors and required invalid/overflow cases.
- [ ] Extend `scripts/validate-billing-entrypoint.mjs` to prove the new runtime and type/declaration exports exist after build and in the packed artifact.
- [ ] Run the existing Shared billing regression tests.
- [ ] Run the repository's required typecheck/build/package-entrypoint validation.
- [ ] Do not modify Admin/API consumers and do not publish the package.

## Interfaces / Contracts

### Contract owner

```text
ARCH-027-SHARED-001
moda-interact-shared
```

### Package

```text
@modainteract/moda-interact-shared/billing
```

### Required public exports

The exact public names owned by this task are:

```text
MERCHANT_USAGE_PRICING_MODES
MerchantUsagePricingMode
MerchantUsagePricingTierSchema
MerchantUsagePricingTier
MerchantUsagePricingSchema
MerchantUsagePricing
MERCHANT_USAGE_PRICE_ERROR_CODES
MerchantUsagePriceErrorCode
evaluateMerchantUsagePrice
MerchantUsagePriceEvaluation
```

If repository-local declaration generation requires a mechanically different ordering of exports, that is allowed. Renaming these public contracts is not.

### Consumer ownership

After publication, intended consumers are:

```text
moda-interact-admin
    portfolio economics

moda-interact-api
    authoritative Woo one-time-charge quote calculation
```

Neither consumer is modified by this task.

### Compatibility

This task is additive to the existing `/billing` public entrypoint.

It must not change serialized queue schemas, billing schema-version constants, Shopify provider-context helpers, billing reconcile contracts, or existing system-message contracts.

## Dependencies

None.

This task is independent of ARCH-027 database implementation because it extracts deterministic catalogue arithmetic only and performs no persistence.

## Enables

- `ARCH-027-SHARED-003`

`ARCH-027-SHARED-003` is the later publication-only gate and must also depend on the other accepted ARCH-027 Shared implementation task(s) before becoming executable.

Consumer tasks must depend on the **published** Shared package gate, not directly on unpublished SHARED-001 source.

## Acceptance Criteria

- [ ] `@modainteract/moda-interact-shared/billing` exports all exact contracts listed under Interfaces / Contracts.
- [ ] Pricing modes are exactly `FIXED`, `GRADUATED`, and `VOLUME`.
- [ ] Currency accepts exactly three uppercase ASCII letters and is not normalized.
- [ ] Tier count is constrained to 1..6 for tiered pricing.
- [ ] Finite tier boundaries are positive safe integers and strictly increase.
- [ ] Only the final tier may be open-ended and the final tier must be open-ended.
- [ ] FIXED `100 x 2` evaluates to `200` minor units.
- [ ] The canonical VOLUME vector evaluates quantity 2 to `200` and quantity 3 to `30` minor units.
- [ ] The canonical GRADUATED vector evaluates quantities 1/2/3 to `15`/`25`/`32` minor units.
- [ ] Valid quantity zero evaluates to zero without charging a tier flat amount.
- [ ] Invalid pricing is classified as `INVALID_PRICING`.
- [ ] Invalid quantity is classified as `INVALID_QUANTITY` when pricing is valid.
- [ ] When both pricing and quantity are invalid, the result is `INVALID_PRICING` because pricing validation occurs first.
- [ ] Unsafe arithmetic is classified as `ARITHMETIC_OVERFLOW`; no successful result contains an unsafe integer.
- [ ] Zero-cost valid pricing is accepted by this primitive.
- [ ] The evaluator does not inspect provider/platform identity or apply marketplace adjustments.
- [ ] Input pricing/tier objects are not mutated.
- [ ] Existing Shared billing tests remain green.
- [ ] Existing `/billing` exports remain backward compatible.
- [ ] Billing package-entrypoint validation proves runtime exports, type declarations and packed-artifact inclusion.
- [ ] No Admin/API source or dependency file changes are present.
- [ ] No package version/publication change is present.

## Validation

Before running validation, inspect `moda-interact-shared/package.json` and use the scripts actually declared by the synchronized repository.

Required checks:

```text
focused billing tests
    npx tsx --test src/billing.test.ts

Shared full unit test suite
    npm test

TypeScript
    npm run typecheck

Build
    npm run build

Public billing package entrypoint
    npm run validate:billing-entrypoint

Whitespace
    git diff --check

changed-file/repository checks required by moda_shared
```

The Completion Report must record the exact commands and results rather than replacing them with generic statements such as "tests passed".

No live provider credentials, database, network call or Woo sandbox is required for this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    ->
set status: review
    ->
return to moda_architect
    ->
STOP
```

Do not:

```text
publish Shared
start SHARED-002/SHARED-003
modify Admin
modify API
implement Woo billing commands
```

## Implementation Notes

Prefer extending the existing Shared `./billing` entrypoint instead of creating another package surface.

The source may be factored into a billing-local module if that keeps `src/billing.ts` maintainable, provided the required symbols remain exported from `@modainteract/moda-interact-shared/billing`.

Do not copy the Admin **portfolio** algorithm. This task extracts only the single usage-pricing definition evaluator required by both Admin and the Woo adapter.

The Admin-specific concepts below remain Admin-owned:

```text
findCheapestMerchantUsageCombination
evaluateMerchantPricingPair
evaluateMerchantPricingPortfolio
minimum upgrade premium
event-combination search
portfolio ordering
economics override policy
```

The future Admin consumer task must replace its local per-quantity arithmetic with this Shared primitive while proving the existing portfolio outputs remain unchanged.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- The synchronized Admin `pricing-economics.ts` remains the accepted source behaviour for FIXED/GRADUATED/VOLUME arithmetic at task start.
- `@modainteract/moda-interact-shared/billing` remains the canonical Shared billing package entrypoint.
- Provider retail-price parity remains an ARCH-027 invariant; no provider-specific pricing adjustment belongs in this evaluator.

### Unresolved Issues

None within this bounded Shared arithmetic task.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
