---
id: ARCH-052-SHARED-013
architecture_id: ARCH-052
title: Add source-observed subtotal threshold currency to discount condition facts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 23
executor: copilot
claimed_at: 2026-10-31T03:26:57Z
attempt: 1
depends_on:
- ARCH-052-SHARED-012
enables:
- ARCH-052-SHARED-014
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-SHARED-013 — Add subtotal threshold currency to condition facts

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Portable task definition; defined but not materialised.** This package does not create a developer branch, checkout, commit or push.

## Objective

Extend the accepted `@modainteract/moda-interact-shared@2.8.1` **structural discount-details wire contract** by adding precisely one **required-but-nullable** `subtotalRequirementCurrency` property to `CommerceDiscountConditionFactsSchema`, without changing provider eligibility logic, combination policy, the existing `commerce.v1` envelope, or the accepted published artifact.

## Context

- SHARED-011/012 added and published `CommerceDiscountCombinationFactsSchema`, `CommerceDiscountConditionFactsSchema.combination`, `CommerceDiscountDetailsSchema.providerDiscountId` and group offer support in package `2.8.1`. Preserve all of those fields and exports unchanged.
- The existing threshold money fields (`minimumSubtotal` / `maximumSubtotal`) are exact decimal **strings** but contain no currency denomination. `discountCurrency` describes a discount amount, not the condition threshold; percentage discounts may have `discountCurrency:null` while still imposing a GBP minimum.
- `ARCH-052-BACKGROUND-013` captures the Shopify MoneyV2 amount and currency, `ARCH-052-MCP-002` projects the provider-authenticated threshold currency into this contract, and `ARCH-052-BACKGROUND-010` compares it to a trusted checkout currency. This task owns **only Zod and inferred wire types**.
- Inspection of the attached 31 October source shows the focused discount fixture and tests actually live in **`src/commerce/tool-contracts.test.ts`**, not `src/commerce/contracts.test.ts`. Use the correct file.

## Scope

**Only these implementation files may change:**

1. `moda-interact-shared/src/commerce/schemas.ts` — insert one required-nullable property in the existing `CommerceDiscountConditionFactsSchema` between `maximumSubtotal` and `minimumQuantity`. Preserve the complete declarations reproduced below.
2. `moda-interact-shared/src/commerce/tool-contracts.test.ts` — update its one `discountFacts` fixture (`satisfies CommerceDiscountConditionFacts`) and its nested details/OK wrapper fixtures, and add the exact positive/negative tests shown below.

No new source file, schema name, package entrypoint, alias, DTO, API tool, queue contract, database column or new Zod helper is required. `src/commerce/index.ts` already exports `./schemas`; **do not edit it**. The existing `CurrencySchema`, `MoneySchema`, `ID` import alias and `z` import are already in `schemas.ts`; **do not add duplicates**.

## Out of Scope

- Provider queries/Prisma, currency conversion, checkout eligibility or stacking decisions, arithmetic, UI, database migrations, new Woo restore versions, registration templates, telemetry or new HTTP/MCP tools.
- No `.refine()`/`.superRefine()` business validations, transforms/defaults, or inferred currency fallback.
- No edits to accepted SHARED-011/012, package version `2.8.1`, package publication or downstream consumer pins. `ARCH-052-SHARED-014` separately owns publication after acceptance.
- No edits to `docs/decisions/**/_index.md`.

## Requirements

1. **Exact new property:** `subtotalRequirementCurrency: CurrencySchema.nullable(),` is **required in the strict object**, with value `string | null`. `.optional()`, `.nullish()`, `.default()`, `z.coerce`, fallbacks and naming variants are forbidden.
2. **Type and format:** Reuse the **existing** `CurrencySchema` from `src/commerce/primitives.ts`. It accepts only already normalised supported uppercase ISO-4217 codes (e.g. `GBP`); it rejects lowercase strings, unknown codes and nonstrings. It does **not** convert or infer currencies. Reuse the existing `MoneySchema` for nullable decimal strings; **no new money representation**.
3. **Meaning:** Field identifies the source-established denomination of the effective `minimumSubtotal` and/or `maximumSubtotal`. When no effective subtotal threshold exists, use `null`. When an effective threshold exists but currency is unobserved or contradictory, use `null` and have **MCP-002** emit `THRESHOLD_CURRENCY_UNKNOWN` in `unrepresentedConditions`. When two effective thresholds have different established denominations, a single scalar cannot represent both: producer emits `null` and the uncertainty reason. **This is producer policy, not a Zod refinement**.
4. **Known currency independent of discount value:** `discountCurrency:null` is valid with `subtotalRequirementCurrency:"GBP"` for percent offers. A discount with fixed-amount currency must not have that currency copied into the threshold field unless the threshold's own denomination is source-proven.
5. **Existing facts unchanged:** Retain exact existing keys/limits/nullability for `provider`, `completeness`, timestamps, `discountKind`, `targeting`, quantity, limits, `customerScope`, `excludesSaleItems`, `individualUse`, `combination`, and `unrepresentedConditions`. Do not introduce a separate `CommerceDiscountThresholdFactsSchema`.
6. **Wire nesting unchanged:** `CommerceDiscountDetailsSchema = z.strictObject({ offer: CommerceOfferSchema, facts: CommerceDiscountConditionFactsSchema, providerDiscountId: z.string().min(1).max(191).nullable() })` remains intact. Keep `CommerceToolOutputs.commerce_get_discount_details` as `{ details: CommerceDiscountDetailsSchema.nullable() }`; the generic `commerceToolResultSchema` `commerce.v1` OK/ERROR wrapper remains intact.
7. **Structural validation only:** Zod deliberately permits a threshold with unknown currency and empty `unrepresentedConditions`, or a known currency with null thresholds. Producer/consumer code is responsible for enforcing truthful completeness and evidence. Do not put source-completeness or currency-match rules into Zod.
8. **Change classification:** This is a breaking field addition only for *pre-production* consumers of the discount-details `commerce.v1` wire shape. Preserve `contractVersion: "commerce.v1"`; do not invent `commerce.v2`, duplicate locally in MCP, or overwrite the published `2.8.1` package. Consumers upgrade their pins only after SHARED-014 publishes a new immutable version.

## Work Items

- [ ] In `src/commerce/schemas.ts` add the single specified property using the **full existing declaration** in the Interfaces / Contracts section as the normative target, without altering any other schema key.
- [ ] In `src/commerce/tool-contracts.test.ts` add `subtotalRequirementCurrency: null` to the shared `discountFacts` fixture; all fixtures spreading it must therefore remain type-correct. Do not bypass `satisfies CommerceDiscountConditionFacts` with casts.
- [ ] Add the explicit test shown below; retain all existing combination, providerDiscountId and tool result tests.
- [ ] Run the repository-declared focused tests, full tests, typecheck, build, Commerce exports smoke check and whitespace validation. Record results and observed existing baseline failures, if any; do not claim unpublished artifacts are already available.
- [ ] Update the task Completion Report and status to `review`, provide implementation SHA and dedicated worktree evidence, then STOP. Publication is SHARED-014.

## Interfaces / Contracts

### 1. Exact existing imports (reuse; no new import)

These symbols are already imported in `src/commerce/schemas.ts`:

```typescript
import { z } from "zod";
import {
  IdSchema as ID,
  MoneySchema,
  CurrencySchema,
} from "./primitives";
```

The import block above names the **relevant existing members**, not an instruction to replace the full import block or remove other imports.

### 2. Complete resulting Zod declarations — normative

Copy/retain the following complete declaration block in `src/commerce/schemas.ts`. There is exactly **one new property** relative to `2.8.1`; the combination and provider identity declarations are reproduced in full **only to freeze their existing structure**, not to change them. The required field is not optional simply because its value permits `null`.

```typescript
export const CommerceDiscountCombinationFactsSchema = z.strictObject({
  discountClasses: z.array(z.enum(["ORDER", "PRODUCT", "SHIPPING"])).max(3).nullable(),
  shopifyPlus: z.boolean().nullable(),
  combinesWith: z.strictObject({
    orderDiscounts: z.boolean().nullable(),
    productDiscounts: z.boolean().nullable(),
    shippingDiscounts: z.boolean().nullable(),
  }).nullable(),
  discountTags: z.array(z.string().min(1).max(128)).max(64).nullable(),
  allowedSameLineProductTags: z.array(z.string().min(1).max(128)).max(64).nullable(),
});
export type CommerceDiscountCombinationFacts = z.infer<
  typeof CommerceDiscountCombinationFactsSchema
>;
export const CommerceDiscountConditionFactsSchema = z.strictObject({
  provider: z.enum(["SHOPIFY", "WOOCOMMERCE"]),
  completeness: z.enum(["COMPLETE", "PARTIAL", "UNKNOWN"]),
  observedAt: DateSchema,
  providerStatus: z.string().max(64),
  unavailableAt: DateSchema.nullable(),
  discountKind: z.enum([
    "PERCENTAGE",
    "FIXED_AMOUNT",
    "FREE_SHIPPING",
    "BUY_X_GET_Y",
    "OTHER",
    "UNKNOWN",
  ]),
  discountValue: MoneySchema.nullable(),
  discountCurrency: CurrencySchema.nullable(),
  targeting: z.strictObject({
    kind: z.enum([
      "ALL",
      "PRODUCTS",
      "VARIANTS",
      "CATEGORIES",
      "COLLECTIONS",
      "MIXED",
      "UNKNOWN",
    ]),
    includedProductIds: z.array(ID).max(128),
    includedVariantIds: z.array(ID).max(128),
    includedCategoryIds: z.array(ID).max(128),
    includedCollectionIds: z.array(ID).max(128),
    excludedProductIds: z.array(ID).max(128),
    excludedVariantIds: z.array(ID).max(128),
    excludedCategoryIds: z.array(ID).max(128),
    excludedCollectionIds: z.array(ID).max(128),
  }),
  minimumSubtotal: MoneySchema.nullable(),
  maximumSubtotal: MoneySchema.nullable(),
  subtotalRequirementCurrency: CurrencySchema.nullable(),
  minimumQuantity: z.number().int().nonnegative().nullable(),
  usageLimit: z.number().int().nonnegative().nullable(),
  usageCount: z.number().int().nonnegative().nullable(),
  perCustomerLimit: z.number().int().nonnegative().nullable(),
  customerScope: z.enum(["ALL", "RESTRICTED", "UNKNOWN"]),
  excludesSaleItems: z.boolean().nullable(),
  individualUse: z.boolean().nullable(),
  combination: CommerceDiscountCombinationFactsSchema,
  unrepresentedConditions: z.array(z.string().min(1).max(128)).max(24),
});
export type CommerceDiscountConditionFacts = z.infer<
  typeof CommerceDiscountConditionFactsSchema
>;
export const CommerceDiscountDetailsSchema = z.strictObject({
  offer: CommerceOfferSchema,
  facts: CommerceDiscountConditionFactsSchema,
  providerDiscountId: z.string().min(1).max(191).nullable(),
});
export type CommerceDiscountDetails = z.infer<
  typeof CommerceDiscountDetailsSchema
>;
```

### 3. Exact existing dependent tool input and output (do not change)

```typescript
// Existing member of CommerceToolInputs in src/commerce/schemas.ts
commerce_get_discount_details: z.strictObject({ offerId: ID }),

// Existing member of CommerceToolOutputs in src/commerce/schemas.ts
commerce_get_discount_details: z.strictObject({
  details: CommerceDiscountDetailsSchema.nullable(),
}),
```

The existing `commerceToolResultSchema(CommerceToolOutputs.commerce_get_discount_details)` and exported inferred types automatically see the new required nested field. Do not add or rename tool parameters, provider IDs, response versions or exports. `src/commerce/index.ts` already has `export * from "./schemas";`.

### 4. Complete positive response fixture (valid wire shape, not an eligibility verdict)

```json
{
  "contractVersion": "commerce.v1",
  "status": "OK",
  "data": {
    "details": {
      "offer": {
        "offerId": "offer-20",
        "title": "Socks 20",
        "method": "CODE",
        "code": "SOCKS20",
        "startsAt": null,
        "endsAt": null,
        "support": "SUPPORTED",
        "reasonCodes": []
      },
      "facts": {
        "provider": "WOOCOMMERCE",
        "completeness": "PARTIAL",
        "observedAt": "2026-10-30T09:00:00.000Z",
        "providerStatus": "ACTIVE",
        "unavailableAt": null,
        "discountKind": "PERCENTAGE",
        "discountValue": "20",
        "discountCurrency": null,
        "targeting": {
          "kind": "PRODUCTS",
          "includedProductIds": [
            "401"
          ],
          "includedVariantIds": [],
          "includedCategoryIds": [],
          "includedCollectionIds": [],
          "excludedProductIds": [],
          "excludedVariantIds": [],
          "excludedCategoryIds": [],
          "excludedCollectionIds": []
        },
        "minimumSubtotal": "100.00",
        "maximumSubtotal": null,
        "subtotalRequirementCurrency": "GBP",
        "minimumQuantity": null,
        "usageLimit": null,
        "usageCount": null,
        "perCustomerLimit": null,
        "customerScope": "ALL",
        "excludesSaleItems": false,
        "individualUse": false,
        "combination": {
          "discountClasses": null,
          "shopifyPlus": null,
          "combinesWith": null,
          "discountTags": null,
          "allowedSameLineProductTags": null
        },
        "unrepresentedConditions": [
          "UNREPRESENTED_MAXIMUM_ITEMS"
        ]
      },
      "providerDiscountId": "woo:coupon:offer-20"
    }
  },
  "renderedText": "Discount details loaded"
}
```

`completeness:"PARTIAL"` and the example reason above deliberately avoid claiming eligibility; reason codes are bounded strings in the current schema, not newly added enum cases. Runtime consumer rules determine their significance.

**Additional required semantic fixture states** (each uses the **same complete `facts` shape** above and replaces only the named fields):

- No effective threshold: `minimumSubtotal:null`, `maximumSubtotal:null`, `subtotalRequirementCurrency:null`, without `THRESHOLD_CURRENCY_UNKNOWN`.
- Percentage discount with verified GBP threshold: `minimumSubtotal:"100.00"`, `discountCurrency:null`, `subtotalRequirementCurrency:"GBP"`.
- Effective threshold with unproven currency: `minimumSubtotal:"100.00"`, `subtotalRequirementCurrency:null`, `completeness:"PARTIAL"`, `unrepresentedConditions:["THRESHOLD_CURRENCY_UNKNOWN"]`.
- Source conflict between effective min/max currencies: retain both amount strings, set `subtotalRequirementCurrency:null`, `completeness:"PARTIAL"` and the same uncertainty reason. The schema itself does not discover the conflict.
- Malformed currency values must fail: `"gbp"`, `"GB"`, `"ZZZ"`, `""`, number `123`, boolean `false`, object and array.

### 5. Required TypeScript tests — normative

In **`src/commerce/tool-contracts.test.ts`** (which already imports `CommerceDiscountConditionFacts`, `CommerceDiscountDetailsSchema`, `CommerceToolOutputs`, `commerceToolResultSchema`, `assert` and `test`), use the existing fixture and helpers. This code is the required behaviour, not a suggestion to implement separate helpers or alter Zod to make the tests pass.

```typescript
// src/commerce/tool-contracts.test.ts, next to the existing discount-details tests
// The existing discountFacts fixture MUST first be extended with:
// subtotalRequirementCurrency: null,

test("discount threshold currency is required and remains structurally nullable", () => {
  const known = {
    ...discountFacts,
    minimumSubtotal: "100.00",
    maximumSubtotal: null,
    subtotalRequirementCurrency: "GBP",
    discountCurrency: null,
  } satisfies CommerceDiscountConditionFacts;
  ok(CommerceDiscountConditionFactsSchema, known);
  ok(CommerceDiscountDetailsSchema, { ...discountDetails, facts: known });

  const noThreshold = {
    ...discountFacts,
    minimumSubtotal: null,
    maximumSubtotal: null,
    subtotalRequirementCurrency: null,
  } satisfies CommerceDiscountConditionFacts;
  ok(CommerceDiscountConditionFactsSchema, noThreshold);

  const unknownCurrency = {
    ...discountFacts,
    minimumSubtotal: "100.00",
    maximumSubtotal: null,
    subtotalRequirementCurrency: null,
    completeness: "PARTIAL",
    unrepresentedConditions: ["THRESHOLD_CURRENCY_UNKNOWN"],
  } satisfies CommerceDiscountConditionFacts;
  ok(CommerceDiscountConditionFactsSchema, unknownCurrency);

  const conflictingCurrencies = {
    ...discountFacts,
    minimumSubtotal: "100.00",
    maximumSubtotal: "200.00",
    subtotalRequirementCurrency: null,
    completeness: "PARTIAL",
    unrepresentedConditions: ["THRESHOLD_CURRENCY_UNKNOWN"],
  } satisfies CommerceDiscountConditionFacts;
  ok(CommerceDiscountConditionFactsSchema, conflictingCurrencies);

  const { subtotalRequirementCurrency: _unused, ...omitted } = known;
  bad(CommerceDiscountConditionFactsSchema, omitted);
  bad(CommerceDiscountDetailsSchema, { ...discountDetails, facts: omitted });
  bad(CommerceToolOutputs.commerce_get_discount_details, {
    details: { ...discountDetails, facts: omitted },
  });

  for (const invalid of ["gbp", "GB", "ZZZ", "", 0, false, {}, []]) {
    bad(CommerceDiscountConditionFactsSchema, {
      ...known,
      subtotalRequirementCurrency: invalid,
    });
  }
  bad(CommerceDiscountConditionFactsSchema, {
    ...known,
    extraCurrencyProperty: "GBP",
  });

  // Zod validates the wire, not whether a threshold is currently eligible.
  ok(CommerceDiscountConditionFactsSchema, {
    ...unknownCurrency,
    unrepresentedConditions: [],
  });
  ok(CommerceDiscountConditionFactsSchema, {
    ...noThreshold,
    subtotalRequirementCurrency: "GBP",
  });

  const resultSchema = commerceToolResultSchema(
    CommerceToolOutputs.commerce_get_discount_details,
  );
  const response = {
    contractVersion: "commerce.v1",
    status: "OK" as const,
    data: { details: { ...discountDetails, facts: known } },
    renderedText: "Discount details loaded",
  };
  ok(resultSchema, response);
  assert.deepEqual(resultSchema.parse(response), response);
  bad(resultSchema, {
    ...response,
    data: { details: { ...discountDetails, facts: omitted } },
  });
});
```

**Fixture update:** within the already-defined `discountFacts` object, immediately after `maximumSubtotal: null,`, insert `subtotalRequirementCurrency: null,`. Do not change the fact's existing `combination`, `providerDiscountId`, `targeting` or `unrepresentedConditions` fields. Nested `discountDetails` and the generic tool-result fixture must continue to validate unchanged apart from the nested new required field.

### 6. Producer/consumer and version gate

- Owner: `moda-interact-shared`; canonical npm entrypoint `@modainteract/moda-interact-shared/commerce` via current exported `./schemas`.
- Producer: `ARCH-052-MCP-002`, mapping authenticated Shopify/Woo source observations, never AI-generated currency.
- Consumers: `ARCH-052-BACKGROUND-010` and `ARCH-052-BACKGROUND-008`; those validate fresh basket currency and do deterministic eligibility/stacking and final-send gates, **not Shared Zod**.
- Published pre-change baseline: `2.8.1`. Implement SHARED-013 first; after accepted review, publish under `ARCH-052-SHARED-014` using a new npm version. Shared package/type pins are updated in owning consumer tasks.
- No changes to `InitialOutreachCheckoutOfferSetSchema`, `CommerceDiscountCombinationFactsSchema`, `CommerceOfferSchema`, `CommerceToolInputs`, `CommerceToolResultSchema`, or ARCH-053 Woo restore `v1`.

## Dependencies

- `ARCH-052-SHARED-012` — previously accepted published 2.8.1 baseline.

## Enables

- `ARCH-052-SHARED-014` — release the accepted schema update (not implementation work).

## Acceptance Criteria

- [ ] `CommerceDiscountConditionFactsSchema` has **exactly one** added required key `subtotalRequirementCurrency` of `CurrencySchema.nullable()`; all original fields and `z.strictObject` behaviour remain intact.
- [ ] `CommerceDiscountConditionFacts` inferred type requires the new `string | null` property; existing typed fixtures compile after explicit update.
- [ ] `CommerceDiscountDetails` and the `commerce_get_discount_details` OK wrapper reject missing nested currency field, reject unknown keys and invalid currency forms, and accept valid full nested wire fixtures.
- [ ] Verified GBP threshold with percent discount / `discountCurrency:null` is accepted; null with threshold, null without threshold, and conflicting-source scenarios are structurally representable (no business rule introduced in Zod).
- [ ] Existing provider identity, combinations, targeting, offer-set and Woo restore contracts retain their exact keys, names, nullability and tests; no `commerce.v2` introduced.
- [ ] Only `src/commerce/schemas.ts` and `src/commerce/tool-contracts.test.ts` are implementation-source changes. No package version bump, code publication, schema migration or other service edits.
- [ ] Validation passes or environment-only baseline exceptions are explicitly documented with evidence; no new regression or silently swallowed error.

## Validation

Run from the launcher-resolved dedicated `moda-interact-shared` implementation worktree, after inspecting the local `package.json`:

```bash
npx tsx --test src/commerce/tool-contracts.test.ts
npm test
npm run typecheck
npm run build
npm run validate:commerce-entrypoints
git diff --check
```

- [ ] Focused discount contracts and full declared Shared suite.
- [ ] Shared typecheck and build, then Commerce published-export smoke check against built output.
- [ ] `git diff --check`, changed-files summary and Completion Report evidence of physical parent/implementation worktrees, branch sync, exact commits and relevant submodule state.

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update only this task's claim/report sections, set status to `review`, return the implementation SHA and Completion Report to `moda_architect`, and **STOP**. Do not publish Shared, implement consumers, push main, merge branches or edit an `_index.md`.

## Implementation Notes

- If another named schema or future field is needed, report it to `moda_architect` rather than altering the contract independently.
- Do not add a generic logger to Shared for this structural-only change. Do not emit coupon codes, checkout URLs, customer data or provider secrets in diagnostics.
- Work within the launcher-resolved dedicated task worktree; do not infer the developer's absolute root. SHARED-014 owns publication, and MCP/BACKGROUND own product condition mapping and eligibility decisions.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Pre-production breaking contract change; existing immutable published `2.8.1` remains unchanged.

### Unresolved Issues

None at definition.

### Architectural Concerns

Return any mismatch in actual published Shared exports or producer-source semantics to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None.
