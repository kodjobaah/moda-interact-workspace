---
id: ARCH-052-SHARED-008
architecture_id: ARCH-052
title: Define platform-neutral product search and exact-product MCP contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-SHARED-008: Define platform-neutral product search and exact-product MCP contracts

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Task materialised and claimed through the prepared launcher on 2026-10-30. The launcher created dedicated mirrored task worktrees, synchronized both task branches, initialized the implementation submodules, and pushed the Attempt 1 claim before implementation began.

## Objective

Make the **existing** Commerce product-search result capable of carrying product categories, images and optional observed sale-price facts, and add one exact-product lookup input/output schema for generic MCP use. Do not define an AI-choice contract or a new product model.

## Context

The snapshot already has `CommerceProductSchema`, `CommerceToolInputs.commerce_search_products`, and `CommerceToolOutputs.commerce_search_products` in `moda-interact-shared/src/commerce/schemas.ts`. The present product schema has required `productId`, `variantId`, title, URL, availability, price/currency, product type/vendor and `observedAt`. Product search remains a direct Shopify GraphQL/WooCommerce REST MCP operation, not a PostgreSQL product catalogue or a call to Moda's hosted API.

## Scope

- Preserve all current `CommerceProductSchema` fields and existing search input/output shapes. Add only the exact optional data fields shown below to that same schema.
- Add the exact `commerce_get_product` input/output members to existing `CommerceToolInputs`/`CommerceToolOutputs`. Do not introduce a second product record type.
- Reuse the existing `CommerceToolResultSchema` success/error envelope. Do not add an outreach-specific product result envelope.
- `saleEvidence` is **observed product price data**, not an eligibility proof, verified coupon, or permission to claim any saving. Discount proof remains SHARED-005/MCP/provider owned.
- Product-reader implementation, credential use, marketplace-specific category normalisation, availability and storefront link safety remain MCP-003 responsibilities. AI decisions remain BACKGROUND-010.

## Out of Scope

- No direct provider reads, MCP tool registration, Commerce Studio publication code, database product storage, product recommendations, discount selection or business-rule Zod refinements in Shared.
- No change to the existing conversational CommerceAgent runner or unrelated product schema members.

## Requirements

- **New Zod definitions must be structural only.** Do not add `.refine`, `.superRefine`, `.transform` or `.check` for sale amount ordering, storefront host ownership, product availability, category relevance or customer eligibility.
- Preserve the original `CommerceProductSchema.url` validation definition and all other existing fields **unchanged** in this task; do not opportunistically refactor existing consumers. The new `imageUrl` field is plain nullable/optional data; runtime ownership/safety rules belong in MCP.
- `variantId` in the existing product representation remains required. A caller may use `null` in an exact-product lookup request to indicate the product-level read; MCP must return a normalised product result with the provider's actual variant ID or an error/null result as appropriate. Never fabricate a variant identity to satisfy the contract.
- The new fields are optional so current conversation product results still parse. MCP may populate them when known, otherwise they are absent or null as specified below. `categories` may be an empty array; do not insert placeholder categories or product identities to fill optional fields.
- The search response is **`{products: CommerceProduct[], cursor: string | null, truncated: boolean}`**. Every `products[]` element has the complete required product shape in Interfaces / Contracts; do not invent an `items` property or a second product representation.
- The exported TypeScript `CommerceProduct` alias MUST be inferred from the existing canonical `CommerceProductSchema`, not declared as an independently maintained interface. The aliases add no new runtime model.
- Re-read the exact task, parent architecture, mirrored worktree policy and prepared launcher packet before execution. No cross-repository implementation or secret-bearing logs.

## Work Items

- [x] Modify exactly the indicated locations in `moda-interact-shared/src/commerce/schemas.ts`.
- [x] Add deterministic product search/exact-product schema fixtures to `src/commerce/contracts.test.ts`.
- [x] Verify `src/commerce/index.ts` already exports `schemas.ts` and make no new entrypoint if so.
- [x] Run declared Shared validation and preserve existing conversation-tool tests.

## Interfaces / Contracts

The following is the **complete, prescriptive wire contract**, not a list of suggestions. The 30 October snapshot's `src/commerce/schemas.ts` is the baseline. Existing required fields and constraints are reproduced verbatim below; the only added product properties are `categories`, `imageUrl` and `saleEvidence`. The sale-evidence schema and inferred type aliases describe the **same** product model. Do not create a separate "search item" DTO or a second product model.

**1. Exact full `CommerceProductSchema` source.** In `moda-interact-shared/src/commerce/schemas.ts`, replace the existing product schema declaration with the following complete block, immediately before `CommerceOfferSchema`. Its existing `z` import and aliases `ID`, `MoneySchema`, `CurrencySchema`, `DateSchema` remain unchanged:

```typescript
export const CommerceProductSaleEvidenceSchema = z.strictObject({
  regularPrice: MoneySchema.nullable(),
  salePrice: MoneySchema.nullable(),
  observedAt: DateSchema,
});
export type CommerceProductSaleEvidence =
  z.infer<typeof CommerceProductSaleEvidenceSchema>;

export const CommerceProductSchema = z.strictObject({
  productId: ID,
  variantId: ID,
  title: z.string().min(1).max(512),
  url: z
    .url({ protocol: /^https$/ })
    .refine((v) => {
      const u = new URL(v);
      return !u.username && !u.password && !u.port;
    })
    .nullable(),
  available: z.boolean().nullable(),
  unitPrice: MoneySchema.nullable(),
  currency: CurrencySchema.nullable(),
  productType: z.string().max(512).nullable(),
  vendor: z.string().max(512).nullable(),
  categories: z.array(z.string()).optional(),
  imageUrl: z.string().nullable().optional(),
  saleEvidence: CommerceProductSaleEvidenceSchema.nullable().optional(),
  observedAt: DateSchema,
});
export type CommerceProduct = z.infer<typeof CommerceProductSchema>;
```

**2. Exact TypeScript shape of each returned product (informative projection of the Zod inference; not a new manually maintained interface).**

```typescript
// Equivalent to z.infer<typeof CommerceProductSchema>.
// Do not duplicate this interface in source; use the exported inferred type.
type CommerceProductWireShape = {
  productId: string;             // required ID, provider-normalised
  variantId: string;             // required ID, never fabricated
  title: string;                 // required, 1..512 characters
  url: string | null;            // required, existing HTTPS/no-auth/no-port check
  available: boolean | null;     // required; null = unknown
  unitPrice: string | null;      // required; decimal MoneySchema string or null
  currency: string | null;       // required; canonical CurrencySchema or null
  productType: string | null;    // required
  vendor: string | null;         // required
  categories?: string[];         // new: optional names, may be []
  imageUrl?: string | null;       // new: optional string, null or absent
  saleEvidence?: {               // new: optional, nullable
    regularPrice: string | null; // required if saleEvidence is an object
    salePrice: string | null;    // required if saleEvidence is an object
    observedAt: string;          // required ISO UTC timestamp (DateSchema)
  } | null;
  observedAt: string;            // required ISO UTC timestamp (DateSchema)
};
```

`MoneySchema` is a decimal **string**, never a JSON number; `DateSchema` uses UTC ISO datetime strings here; null and absence have distinct meanings. `categories` is an array of category **name strings**, not a taxonomy ID array. Do not invent categories, product URLs, sale facts or variant IDs when a provider lacks them. No business authorisation is implied by a structurally valid product.

**3. Existing product search input and output remain unchanged.** Preserve these exact object members in their existing `CommerceToolInputs` and `CommerceToolOutputs` (shown for clarity, **do not re-add** them):

```typescript
// Existing CommerceToolInputs member; preserve it verbatim.
commerce_search_products: z.strictObject({
  query: z.string().min(1).max(200),
  maximumPrice: MoneySchema.optional(),
  availableOnly: z.boolean().default(true),
  limit: z.number().int().min(1).max(20).default(10),
  cursor: z.string().max(2048).nullable().default(null),
}),

// Existing CommerceToolOutputs member; preserve it verbatim.
commerce_search_products: z.strictObject({
  products: z.array(CommerceProductSchema).max(20),
  cursor: z.string().max(2048).nullable(),
  truncated: z.boolean(),
}),
```

The elements of `products` are **exactly** the complete `CommerceProductSchema` above. Do not rename `products` to `items`, or turn it into a different container. `maximumPrice`, `availableOnly`, `limit` and `cursor` retain their existing input semantics and defaults. The existing `CommerceAlternativeSchema.product` also references `CommerceProductSchema`, so its nested product inherits these optional fields automatically; do not modify the alternative schema, proposal or generic envelope.

**4. Add these exact two new members (and no others) to the existing schema objects in `src/commerce/schemas.ts`:**

```typescript
// New member of existing CommerceToolInputs:
commerce_get_product: z.strictObject({
  productId: ID,
  variantId: ID.nullable(),
}),

// New member of existing CommerceToolOutputs:
commerce_get_product: z.strictObject({
  product: CommerceProductSchema.nullable(),
}),
```

`variantId: null` is allowed **only in the lookup request**, to ask for a product-level read. When `product` is non-null, its `variantId` is the **required** actual provider-normalised ID. If there is no legitimate variant ID, the MCP adapter returns `product: null` for a genuinely absent product or the existing generic error branch for a provider failure; Shared does not fabricate identities.

**5. Fully populated example of a search result item and its surrounding search response:**

```json
{
  "products": [
    {
      "productId": "product_123",
      "variantId": "variant_456",
      "title": "Performance running socks",
      "url": "https://shop.example.com/products/running-socks",
      "available": true,
      "unitPrice": "16.00",
      "currency": "GBP",
      "productType": "Accessories",
      "vendor": "Example Brand",
      "categories": ["Running", "Accessories"],
      "imageUrl": "https://shop.example.com/media/socks.jpg",
      "saleEvidence": {
        "regularPrice": "20.00",
        "salePrice": "16.00",
        "observedAt": "2026-10-29T18:00:00.000Z"
      },
      "observedAt": "2026-10-29T18:00:00.000Z"
    }
  ],
  "cursor": null,
  "truncated": false
}
```

The example is illustrative provider data, not a promise of availability or eligible savings. Every required existing field is present. Products **without** `categories`, `imageUrl` and `saleEvidence` must continue to parse. Each new field may independently be omitted; `imageUrl` and `saleEvidence` also accept `null`.

**6. Exact-product request and complete successful response:**

```json
{
  "productId": "product_123",
  "variantId": null
}
```

```json
{
  "product": {
    "productId": "product_123",
    "variantId": "variant_456",
    "title": "Performance running socks",
    "url": "https://shop.example.com/products/running-socks",
    "available": true,
    "unitPrice": "16.00",
    "currency": "GBP",
    "productType": "Accessories",
    "vendor": "Example Brand",
    "categories": ["Running", "Accessories"],
    "imageUrl": "https://shop.example.com/media/socks.jpg",
    "saleEvidence": {
      "regularPrice": "20.00",
      "salePrice": "16.00",
      "observedAt": "2026-10-29T18:00:00.000Z"
    },
    "observedAt": "2026-10-29T18:00:00.000Z"
  }
}
```

For a genuine not-found result, the successful **data** shape is exactly `{ "product": null }`. Transport, authentication, permission, timeout or provider failures must use the existing `CommerceToolResultSchema` `status: "ERROR"` envelope with its allowed `CommerceErrorCodeSchema`; they must **not** masquerade as not-found. `CommerceToolResultSchema`/`commerceToolResultSchema` remain unchanged.

**7. Exports and source boundaries.** The existing `src/commerce/index.ts` already has `export * from "./schemas"`; that export continues to publish `CommerceProductSaleEvidenceSchema`, inferred `CommerceProductSaleEvidence`, `CommerceProductSchema`, inferred `CommerceProduct`, and both `CommerceToolInputs`/`CommerceToolOutputs` members from `@modainteract/moda-interact-shared/commerce`. Do **not** create a new package subpath, change `package.json` exports, change the generic result envelope or publish from this implementation task. `ARCH-052-SHARED-003` owns the release gate.

**Business checks delegated outside Zod:**

| Rule | Owner |
|---|---|
| Search/lookup result belongs to the authenticated shop | MCP |
| Product, image and storefront URLs are authorised and safe to present | MCP provider adapters |
| Price, sale evidence and stock are current enough to be claimed | MCP adapter and Background presentation |
| `regularPrice` > `salePrice` supports an actual discount claim | Background, using provider evidence |
| Pagination and identity resolution of product versus variant | MCP execution |
| Alternative relevance and merchant instructions | BACKGROUND-010 |

No `.refine`, `.superRefine`, `.transform` or `.check` is added for these new business rules. Do not remove or rewrite existing validation of `CommerceProductSchema.url`.

**8. Add the following deterministic test to `src/commerce/contracts.test.ts`.** Add `CommerceProductSchema` to the file's existing imports from `./index`. Reuse the existing `test`, `ok` and `bad` helpers; the block below is runnable source, not pseudocode:

```typescript
test("ARCH-052-SHARED-008 product search and exact-product shapes", () => {
  const originalProduct = {
    productId: "product_123",
    variantId: "variant_456",
    title: "Performance running socks",
    url: "https://shop.example.com/products/running-socks",
    available: true,
    unitPrice: "20.00",
    currency: "GBP",
    productType: "Accessories",
    vendor: "Example Brand",
    observedAt: "2026-10-29T18:00:00.000Z",
  };
  const enrichedProduct = {
    ...originalProduct,
    unitPrice: "16.00",
    categories: ["Running", "Accessories"],
    imageUrl: "https://shop.example.com/media/socks.jpg",
    saleEvidence: {
      regularPrice: "20.00",
      salePrice: "16.00",
      observedAt: "2026-10-29T18:00:00.000Z",
    },
  };

  ok(CommerceProductSchema, originalProduct); // backwards-compatible
  ok(CommerceProductSchema, enrichedProduct);
  ok(CommerceProductSchema, {
    ...originalProduct, categories: [], imageUrl: null, saleEvidence: null,
  });
  ok(CommerceToolInputs.commerce_search_products, { query: "running socks" });
  ok(CommerceToolOutputs.commerce_search_products, {
    products: [enrichedProduct], cursor: null, truncated: false,
  });
  ok(CommerceToolOutputs.commerce_find_similar_products, {
    alternatives: [{
      product: enrichedProduct,
      proposal: { operations: [{ kind: "ADD", variantId: "variant_456", quantity: 1 }] },
      extraSpend: "16.00",
      resultingTotal: "16.00",
      currency: "GBP",
      evidence: null,
      similarityReasons: ["Related running accessory"],
    }],
    truncated: false,
  });
  ok(CommerceToolInputs.commerce_get_product, {
    productId: "product_123", variantId: null,
  });
  ok(CommerceToolInputs.commerce_get_product, {
    productId: "product_123", variantId: "variant_456",
  });
  ok(CommerceToolOutputs.commerce_get_product, { product: enrichedProduct });
  ok(CommerceToolOutputs.commerce_get_product, { product: null });

  const missingRequired = { ...originalProduct } as Record<string, unknown>;
  delete missingRequired.variantId;
  bad(CommerceProductSchema, missingRequired);
  bad(CommerceProductSchema, { ...originalProduct, extra: true });
  bad(CommerceProductSchema, { ...originalProduct, unitPrice: 20 });
  bad(CommerceProductSchema, { ...originalProduct, categories: [123] });
  bad(CommerceProductSchema, { ...originalProduct, imageUrl: 123 });
  bad(CommerceProductSchema, {
    ...enrichedProduct, saleEvidence: { ...enrichedProduct.saleEvidence, extra: true },
  });
  bad(CommerceProductSchema, {
    ...enrichedProduct, saleEvidence: { ...enrichedProduct.saleEvidence, salePrice: 16 },
  });
  bad(CommerceToolInputs.commerce_get_product, {
    productId: "product_123",
  }); // variantId required, even if null
  bad(CommerceToolInputs.commerce_get_product, {
    productId: "", variantId: null,
  });
  bad(CommerceToolInputs.commerce_get_product, {
    productId: "product_123", variantId: null, shopId: "foreign_shop",
  });
  bad(CommerceToolOutputs.commerce_get_product, {
    product: enrichedProduct, unexpected: true,
  });
  bad(CommerceToolOutputs.commerce_search_products, {
    products: [enrichedProduct], cursor: null, truncated: false, extra: true,
  });

  // Structural proof only: this is not a valid saving, but must parse.
  ok(CommerceProductSchema, {
    ...enrichedProduct,
    saleEvidence: { ...enrichedProduct.saleEvidence, salePrice: "25.00" },
  });
});
```

For compatibility, retain and run the pre-existing `commerce_search_products` fixtures in this file alongside the new tests. Do not revise unrelated fixtures merely to make this task pass.

## Dependencies

None.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [x] Current `CommerceProductSchema`/search tool contracts remain recognisable and unchanged except for three specified optional fields.
- [x] `commerce_get_product` input and output match the exact structures above; no new product data store, independent response envelope or AI-choice schema appears.
- [x] Existing products without the new optional fields still parse.
- [x] A structurally valid product with misleading `saleEvidence` does not become automatically approved by Zod; the relevant MCP/Background business layers remain accountable.
- [x] Missing required existing product fields, unexpected keys and incorrect exact-product input types fail schema parsing.

## Validation

- [x] `npm run typecheck`, `npm test`, `npm run build` in Shared.
- [x] Unit fixtures: old product record; new optional fields; `product: null`; exact product ID; malformed ID; unknown keys; wrong types.
- [x] Existing `CommerceToolInputs` and output fixture tests continue passing; `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, update Completion Report, set task to `review`, hand branch evidence to `moda_architect`, and **STOP**. Do not publish or begin another task.

## Implementation Notes

**Source edit boundaries are exact**: `moda-interact-shared/src/commerce/schemas.ts` and tests in `src/commerce/contracts.test.ts`. No changes to `src/commerce/index.ts`, `package.json`, source consumers or another package subpath. This is an implementation task; SHARED-003 handles accepted package publication. If a provider cannot supply the existing required `variantId` without fabrication, report the contract gap to architect; do not invent a fallback in Shared.

## Completion Report

### Status

Ready for Review. Attempt 1 was claimed and pushed by the prepared launcher. Implementation commit `ed242ab` and parent report commit `c16ce4c5` are pushed on their mirrored task branches.

### Files Changed

`src/commerce/schemas.ts` and `src/commerce/contracts.test.ts` in `moda-interact-shared`.

### Work Completed

- Added the exact structural `CommerceProductSaleEvidenceSchema` and type, plus the three requested optional fields to the existing `CommerceProductSchema`; all original fields and URL validation remain unchanged.
- Added exact-product input/output schemas to the existing tool dictionaries without changing search input/output shapes or adding another product model/envelope.
- Added fixtures for legacy and extended product records, structurally misleading price evidence, `product: null`, malformed IDs/types and unknown keys.
- `src/commerce/index.ts` already exports `schemas.ts`; no new package entrypoint was needed. Product provider and promotion business checks remain outside Shared.

### Prepared Launcher and Start-of-Attempt Synchronization Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-008`, branch `task/ARCH-052-SHARED-008`, prepared start HEAD `961ec7b2aa172ce86e7c0cf014f561b8ff7ff3b1`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-008`, repository `moda-interact-shared`, branch `task/ARCH-052-SHARED-008`, prepared start HEAD `683a7e55b1d173445c585342529ee3a04f28a22d`.
- Both worktrees were created fresh; each task branch required no remote fast-forward and already included `origin/main`. Recursive implementation submodule synchronization and update passed; no recursive submodule entries were present and status was `ready`.
- Attempt 1 claim commit `21fdc5acce5c056efcc9c7adb6809250c6989eea` was committed and pushed by the launcher. No shared/default checkout or another task worktree was used for implementation.
- Implementation commit `ed242ab` and parent report commit `c16ce4c5` were pushed on their respective `task/ARCH-052-SHARED-008` branches.

### Validation Results

- `npm ci --prefer-offline` installed the locked dependencies. npm reported three audit notices (1 low, 2 high) and five pending package install scripts; these did not prevent the successful build or tests.
- `npm run typecheck` passed.
- Focused commerce contract tests passed: 13 tests, 0 failures.
- `npm test` passed: 385 tests, 384 passed, 0 failed, 1 skipped because `TEST_REDIS_URL` is not configured (BullMQ trace-context integration).
- `npm run build` passed and generated the Commerce JS and declarations.
- A clean import from `@modainteract/moda-interact-shared/commerce` verified the product and sale-evidence schemas and exact-product tool contracts are available through the existing public entrypoint.
- `git diff --check` passed.

### Deviations

The initial sandboxed dependency install and validation attempts were denied while creating `node_modules`, the `tsx` IPC socket and a temporary tsup config. Retried with the required repository/temp-file access; dependency installation and all required validation completed successfully.

### Assumptions

MCP will supply provider-owned identity, URL safety and current-price semantics; Background will decide whether observed price evidence supports customer-facing wording.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Accepted

### Review Notes

The task is correctly submitted in `review` at Attempt 1. The implementation branch `task/ARCH-052-SHARED-008` is clean at `ed242ab` and contains only the two task-scoped files. `CommerceProductSaleEvidenceSchema`, the three optional product fields, and the exact-product input/output members match the task. The original product identity, URL validation, price/currency, availability, type/vendor, timestamp, and search input/output structures remain unchanged. `saleEvidence` accepts structurally valid but misleading price ordering without approving a saving; URL safety and provider/business interpretation remain outside Shared. No second product model, package subpath, persistence, provider runtime, or AI-choice contract was introduced.

The Completion Report records dedicated mirrored worktrees, branch synchronization, recursive submodule preparation, and pushed implementation/report commits. Typecheck, focused contract tests (13 passed), full test suite (384 passed, 1 skipped, 0 failed), build, public `/commerce` import, and `git diff --check` passed. npm's audit notices and pending optional install scripts did not affect validation or change dependency manifests. No tests were rerun for this review.

### Reviewed Files

- Attempt 1 Completion Report, launcher evidence, task scope, Acceptance Criteria and Validation.
- Shared implementation branch `task/ARCH-052-SHARED-008` at `ed242ab`, clean with a two-file diff from `origin/main`.
- `src/commerce/schemas.ts` and `src/commerce/contracts.test.ts`.
- Existing `/commerce` entrypoint and ARCH-052 publication/dependency records.

### Validation Reviewed

Reviewed `npm run typecheck`, focused contract tests (13 passed), `npm test` (384 passed, 1 skipped, 0 failed), `npm run build`, public `/commerce` import/export check, and `git diff --check`. No tests were rerun for this review.

### Architecture Conformance

The change extends the existing product contract without redefining its model or changing existing search and conversation contracts. Shared owns only structural parsing; provider trust, availability, URL safety, and customer-facing interpretation remain with MCP and Background. The implementation conforms to the task and ARCH-052.

### Follow-up

Set this automatic-completion task to `complete`. All four implementation prerequisites for `ARCH-052-SHARED-003` are now architect-accepted Complete, so mark that publication task `ready`. Keep all tasks enabled by SHARED-003 Pending until the publication task is completed and accepted.
