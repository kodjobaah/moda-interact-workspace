---
id: ARCH-052-SHARED-009
architecture_id: ARCH-052
title: Define paged discount discovery, condition details and product identity contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 15
executor: codex
claimed_at: 2026-10-30T11:40:05Z
attempt: 1
depends_on: []
enables:
- ARCH-052-SHARED-010
created: '2026-10-30'
updated: 2026-10-30
---

# ARCH-052-SHARED-009: Define discount discovery, condition facts and product identity contracts

## Architecture

ARCH-052: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Owned by `moda_shared`. This task was materialised and claimed by the prepared launcher for Attempt 1. Existing SHARED-002/006/008 and published 2.6.0 are accepted and were not reopened or rewritten.

## Objective

Make **one versioned update** to the existing generic Commerce contract in `src/commerce/schemas.ts` so the LangGraph outreach agent can page through discount options, request the conditions of promising discounts, and match provider product/category identities without a new proof engine or an alternative result envelope.

## Context

Current published 2.6.0 declares `CommerceToolInputs.commerce_get_discount_options` as `{}`; the output is `{mode, offers(max 50), truncated}`; `CommerceOfferSchema` contains no eligibility conditions. `CommerceProductSchema` includes category *labels* but no provider category/collection IDs and requires a non-null `variantId`. Woo simple products may have no variant. These gaps were verified against the attached 09:15 workspace. Shopify's existing discount synchroniser also captures only summary/status/date/code fields, so the new wire structure alone does not fill missing facts; BACKGROUND-011 owns synchronisation changes.

## Scope

- Modify only `moda-interact-shared/src/commerce/schemas.ts` and its commerce contract tests. Existing `src/commerce/index.ts` re-exports `schemas.ts`; use the **existing `@modainteract/moda-interact-shared/commerce` entrypoint**.
- Add the exact schemas and tool-dictionary members below. Keep `CommerceToolResultSchema`, `CommerceOfferSchema` and the rest of the commerce dictionaries unchanged except the named members.
- Change `CommerceProductSchema.variantId` from required string to nullable provider variant ID, and add optional provider category/collection IDs. Keep existing `categories` as display labels; do not invent taxonomy equivalence.
- Keep Zod validation structural only; **no `superRefine` or `.refine` for discount applicability, merchant authorisation, expiry, customer savings, coupon stacking, status, target coverage, pagination truth or inferred sales claims**. These belong to MCP/Background/provider adapters.
- This is intentionally one consolidated Shared implementation task, followed by a **separate release-only SHARED-010** (do not publish in this task).

## Out of Scope

No database migration, provider HTTP/GraphQL, coupon validation engine, bulk eligibility scan, AI ranking, Meta binding, cart restoration, new MCP response envelope, Commerce Studio discount publication, or changes to completed SHARED task histories.

## Requirements

- **Existing generic envelope**: `commerceToolResultSchema(CommerceToolOutputs.commerce_get_discount_details)` and the options schema work unchanged; no outreach-only envelope.
- A condition field is a provider-observed **fact**, not a guaranteed offer. A provider target list larger than the schema bound (128 IDs per dimension) must be projected as incomplete: `completeness:"PARTIAL"` with an explicit `unrepresentedConditions` code; never cut a list silently and claim `COMPLETE`. `null`, `UNKNOWN` and `PARTIAL` describe incomplete knowledge; an empty list in `COMPLETE` describes a known empty set, not permission to guess.
- The new options contract supports `limit`/`cursor`; `truncated` remains and the added `cursor` is the continuation token. Existing `{}` callers parse using schema defaults, but the **MCP outreach implementation must always return** `cursor` (including `null` on the last page). The Shared output member allows `cursor` to be omitted for the existing conversation-only Commerce preview producer, so that unrelated producer does not require a behavioural migration. Missing `cursor` is a typed/incomplete failure when Background consumes MCP-002 responses. All new consumer code must use the published version before activation.
- Product category IDs and collection IDs are opaque **provider-native strings**; Woo numeric IDs are converted to decimal strings by MCP. Shopify collection IDs are Shopify IDs. The model must not compare a category name to an ID or assert that Shopify productType equals a collection ID.
- Products with no provider variant have `variantId: null`. A genuine variation retains its actual provider ID; never fill productId into variantId to satisfy a type.
- Publish the contract as one coherent update. No historical data backfill or legacy read adapter (platform remains pre-production).

## Work Items

- [x] Add the exact discount-details and page schemas below and extend only the named dictionary members.
- [x] Update existing `CommerceProductSchema.variantId` and add provider category/collection IDs.
- [x] Add structural valid/invalid JSON fixtures, compile-time inferred type tests, existing conversation-tool compatibility tests and bounded generic envelope tests.
- [x] Run declared Shared tests, typecheck and build; verify the pre-existing package entrypoint exports the new schema/type names.
- [x] Complete task report with exact changed files, validation, isolated-worktree evidence and no package publication; return to architect for acceptance.

## Interfaces / Contracts

**Normative TypeScript/Zod code for `moda-interact-shared/src/commerce/schemas.ts` (insert BOTH declarations **after the existing `CommerceOfferSchema`**, not before it, because `CommerceDiscountDetailsSchema` references that runtime constant).** `z` and aliases `ID`, `DateSchema`, `MoneySchema`, `CurrencySchema` already exist at the top of this file. Keep their current imports; do not invent a separate primitive module or change `CommerceOfferSchema`.

```typescript
/** Observed provider conditions for ONE discount, not an eligibility verdict. */
export const CommerceDiscountConditionFactsSchema = z.strictObject({
  provider: z.enum(["SHOPIFY", "WOOCOMMERCE"]),
  completeness: z.enum(["COMPLETE", "PARTIAL", "UNKNOWN"]),
  observedAt: DateSchema,
  providerStatus: z.string().max(64),
  unavailableAt: DateSchema.nullable(),
  discountKind: z.enum([
    "PERCENTAGE", "FIXED_AMOUNT", "FREE_SHIPPING", "BUY_X_GET_Y", "OTHER", "UNKNOWN",
  ]),
  discountValue: MoneySchema.nullable(),
  discountCurrency: CurrencySchema.nullable(),
  targeting: z.strictObject({
    kind: z.enum([
      "ALL", "PRODUCTS", "VARIANTS", "CATEGORIES", "COLLECTIONS", "MIXED", "UNKNOWN",
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
  minimumQuantity: z.number().int().nonnegative().nullable(),
  usageLimit: z.number().int().nonnegative().nullable(),
  usageCount: z.number().int().nonnegative().nullable(),
  perCustomerLimit: z.number().int().nonnegative().nullable(),
  customerScope: z.enum(["ALL", "RESTRICTED", "UNKNOWN"]),
  excludesSaleItems: z.boolean().nullable(),
  individualUse: z.boolean().nullable(),
  unrepresentedConditions: z.array(z.string().min(1).max(128)).max(24),
});
export type CommerceDiscountConditionFacts =
  z.infer<typeof CommerceDiscountConditionFactsSchema>;

export const CommerceDiscountDetailsSchema = z.strictObject({
  offer: CommerceOfferSchema,
  facts: CommerceDiscountConditionFactsSchema,
});
export type CommerceDiscountDetails = z.infer<typeof CommerceDiscountDetailsSchema>;
```

**Exact changes to existing declarations (do not recreate the dictionaries):**

```typescript
// In CommerceProductSchema: REPLACE the existing `variantId: ID` member.
variantId: ID.nullable(),
// ADD beside its existing optional `categories` property:
categoryIds: z.array(ID).max(128).optional(),
collectionIds: z.array(ID).max(128).optional(),

// In CommerceToolInputs: REPLACE only commerce_get_discount_options.
commerce_get_discount_options: z.strictObject({
  limit: z.number().int().min(1).max(50).default(20),
  cursor: z.string().max(2048).nullable().default(null),
}),
// ADD the new tool input (no checkoutId, attemptId, shopId or proof fields):
commerce_get_discount_details: z.strictObject({ offerId: ID }),

// In CommerceToolOutputs: REPLACE only commerce_get_discount_options.
commerce_get_discount_options: z.strictObject({
  mode: z.enum(["NONE", "FIXED", "AI_BEST_APPLICABLE"]),
  offers: z.array(CommerceOfferSchema).max(50),
  cursor: z.string().max(2048).nullable().optional(),
  truncated: z.boolean(),
}),
// ADD the new tool output, retaining the standard CommerceToolResult wrapper:
commerce_get_discount_details: z.strictObject({
  details: CommerceDiscountDetailsSchema.nullable(),
}),
```

`CommerceToolResultSchema` remains unchanged; tool success data is parsed with `commerceToolResultSchema(CommerceToolOutputs.commerce_get_discount_details)` using the **existing** generic API. Missing offers return `details: null` only for genuine not-found within the current shop; provider read failures use existing generic tool error results.

**Fixtures (normative shapes, not provider assertions):**

```json
{
  "mode": "FIXED",
  "offers": [{
    "offerId": "offer-20", "title": "Socks 20", "method": "CODE",
    "code": "SOCKS20", "startsAt": null, "endsAt": null,
    "support": "SUPPORTED", "reasonCodes": []
  }],
  "cursor": "opaque-continuation-token", "truncated": true
}
```

```json
{
  "details": {
    "offer": {
      "offerId": "offer-20", "title": "Socks 20", "method": "CODE",
      "code": "SOCKS20", "startsAt": null, "endsAt": null,
      "support": "SUPPORTED", "reasonCodes": []
    },
    "facts": {
      "provider": "WOOCOMMERCE", "completeness": "COMPLETE",
      "observedAt": "2026-10-30T09:00:00.000Z", "providerStatus": "ACTIVE",
      "unavailableAt": null, "discountKind": "PERCENTAGE",
      "discountValue": "20", "discountCurrency": null,
      "targeting": {
        "kind": "PRODUCTS", "includedProductIds": ["401"],
        "includedVariantIds": [], "includedCategoryIds": [], "includedCollectionIds": [],
        "excludedProductIds": [], "excludedVariantIds": [],
        "excludedCategoryIds": [], "excludedCollectionIds": []
      },
      "minimumSubtotal": null, "maximumSubtotal": null,
      "minimumQuantity": null, "usageLimit": null, "usageCount": null,
      "perCustomerLimit": null, "customerScope": "ALL",
      "excludesSaleItems": false, "individualUse": false,
      "unrepresentedConditions": []
    }
  }
}
```

**Test fixtures:** `{}` parses as discount-options input with defaults `{limit:20,cursor:null}`. Reject `limit:0`, `limit:51`, numeric `cursor`, unknown keys, numeric `discountValue`, numeric provider IDs, and unknown outcome enums. Accept missing optional `categoryIds`/`collectionIds`, `variantId:null`, and provider-populated values. Reject a missing required discount-details `facts` object and an unknown options property. Accept omitted `cursor` structurally for the existing conversational Commerce preview path; assert that MCP-002 always supplies `cursor` in MCP integration tests. Do not assert `usageCount <= usageLimit`, `truncated === (cursor !== null)`, currency/value compatibility, that selected offers are active, positive savings, or that a product satisfies targeting **in Zod**; put these service checks in MCP and Background.

**Independent ownership:** Shared validates data shape only; Background Shopify sync maps Shopify to `providerSnapshot` in BACKGROUND-011; Woo snapshot already contains many fields; MCP-002 maps database records into these fields and implements cursor pagination, auth and current policy. MCP-003/005 supply product category IDs and nullable variants. BACKGROUND-010 uses facts and makes the suitability decision; BACKGROUND-008 owns final send and approved presentation.

## Dependencies

None. Existing SHARED-002/006/008 have already been accepted and are the baseline, not tasks to reopen.

## Enables

- ARCH-052-SHARED-010

## Acceptance Criteria

- [x] Complete code above exists in the existing Commerce schema module and exported package entrypoint.
- [x] Both new discount-tool shapes parse with the generic Commerce result envelope; existing product-search and get-product outputs still parse for genuine Shopify variants.
- [x] Woo simple product `variantId:null` parses without invented variant IDs; product category/collection IDs remain opaque provider strings.
- [x] Structural tests cover exact fixtures, defaults, unknown keys and bad primitive types; no new business-rule refinements.
- [x] No Shopify/Woo provider calls or discount ranking logic appears in Shared.

## Validation

- [x] Inspect `package.json` and run the exact existing Shared test/typecheck/build scripts and `git diff --check`.
- [x] Record actual package exports and test results. Unperformed checks remain unchecked in Completion Report.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set status `review`, record the full Completion Report, hand to architect and STOP. Do not start SHARED-010 or any consumer tasks.

## Implementation Notes

Use the existing Shared `@modainteract/moda-interact-shared/commerce` published path. Do not reimplement cross-service parsers in MCP or Background, or change unrelated package subpaths. Extend the existing tests in `src/commerce/contracts.test.ts`; no release work in this task. Environment remains pre-production so a coordinated consumer upgrade is permitted, but not an unplanned halfway rollout. Follow `docs/agent-worktree-isolation-policy.md` and the launcher preparation packet.

## Completion Report

### Status

Implementation complete; awaiting architect review.

### Files Changed

- `moda-interact-shared/src/commerce/schemas.ts`
- `moda-interact-shared/src/commerce/contracts.test.ts`
- This task report only: `docs/decisions/shared/ARCH-052/SHARED-009-define-discount-discovery-and-product-identity-contracts.md`

### Work Completed

- Added strict discount condition facts/details schemas and inferred types, paged discount options input/output, and discount-details tool input/output using the existing Commerce dictionaries and generic result envelope.
- Made product `variantId` nullable and added optional bounded provider category and collection ID arrays while keeping category labels unchanged.
- Added exact structural fixtures, compile-time `satisfies` checks for both inferred types, invalid primitive/unknown-key coverage, conversation compatibility coverage, and generic-envelope bounds for both discount options and discount details. No business-rule refinements or provider/ranking logic were added.
- Did not change package version, publish the package, or start SHARED-010.

### Validation Results

- `npm test`: PASS — 387 tests, 386 passed, 1 skipped, 0 failed. The skipped test is part of the existing suite; no new skip was added.
- `npm run typecheck`: PASS.
- `npm run build`: PASS, including ESM and declaration builds.
- `npm run validate:commerce-entrypoints`: PASS — existing `@modainteract/moda-interact-shared/commerce` entrypoint imported cleanly. Generated `dist/commerce/index.d.ts` exports `CommerceDiscountConditionFactsSchema`, `CommerceDiscountConditionFacts`, `CommerceDiscountDetailsSchema`, and `CommerceDiscountDetails`.
- `git diff --check`: PASS.
- Review correction follow-up: `./node_modules/.bin/tsx --test src/commerce/contracts.test.ts`: PASS — 15 tests, 15 passed, 0 failed; includes generic Commerce result envelope parsing for the discount-options output. `git diff --check`: PASS.
- Package scripts and package metadata were inspected. The package remains version 2.6.0; no publication was performed.

### Deviations

Dependency tools were initially absent in the isolated worktree. Lockfile-pinned dependencies were installed with `npm ci`; the declared checks then completed successfully. Running `npm test` under the restricted sandbox initially failed because `tsx` could not create its local IPC socket; the same declared validation sequence passed with the required OS permission.

### Assumptions

The prepared launcher’s synchronized branches are the baseline for this Attempt 1.

### Unresolved Issues

None known. The one skipped test is identified in the test runner output and is not specific to this task.

### Isolated-Worktree and Start-of-Attempt Synchronization Evidence

- Prepared launcher: `scripts/start-agent-task.py ARCH-052-SHARED-009 --prepare --executor codex --json`; dependency gate passed, claim was pushed, and recursive submodule verification reported ready.
- Canonical root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-009`, branch `task/ARCH-052-SHARED-009`; synchronized start head `3350fe0be699d6f89240254ead445c1bdffa6abd`, then launcher claim commit `2250a3021f73a10e39591b11fca0f83383404ec2`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-009`, branch `task/ARCH-052-SHARED-009`; synchronized start head `be13b8675750b8cb0315adcc748f77c7e4831440`.
- The launcher verified these as separate task worktrees. The implementation diff is limited to the two scoped Shared files; the parent worktree contains only this task report update.

### Architectural Concerns

None identified. The options output keeps `cursor` optional for existing conversation-preview compatibility, as specified.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation review.

### Reviewed Files

No architecture concern identified. The task remains pending architect acceptance.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Added the missing generic Commerce result envelope assertion for discount options after architect review identified the coverage gap. Task remains in review pending architect acceptance.
