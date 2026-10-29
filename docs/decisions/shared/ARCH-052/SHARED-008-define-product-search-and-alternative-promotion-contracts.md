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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-008: Define platform-neutral product search and exact-product MCP contracts

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Portable task definition: **defined but not materialised**; developer branches/worktrees/commits are not asserted.

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
- The new fields are optional so current conversation product results still parse. MCP may populate them when known, otherwise they are absent or null as specified below.
- Re-read the exact task, parent architecture, mirrored worktree policy and prepared launcher packet before execution. No cross-repository implementation or secret-bearing logs.

## Work Items

- [ ] Modify exactly the indicated locations in `moda-interact-shared/src/commerce/schemas.ts`.
- [ ] Add deterministic product search/exact-product schema fixtures to `src/commerce/contracts.test.ts`.
- [ ] Verify `src/commerce/index.ts` already exports `schemas.ts` and make no new entrypoint if so.
- [ ] Run declared Shared validation and preserve existing conversation-tool tests.

## Interfaces / Contracts

**1. Insert this exact new schema immediately before the existing `CommerceProductSchema` in `src/commerce/schemas.ts`:**

```typescript
export const CommerceProductSaleEvidenceSchema = z.strictObject({
  regularPrice: MoneySchema.nullable(),
  salePrice: MoneySchema.nullable(),
  observedAt: DateSchema,
});
export type CommerceProductSaleEvidence =
  z.infer<typeof CommerceProductSaleEvidenceSchema>;
```

**2. Within the existing `CommerceProductSchema = z.strictObject({ ... })`, add these exact members immediately after its existing `vendor` member and before `observedAt`; leave the rest of its original declaration unchanged:**

```typescript
  categories: z.array(z.string()).optional(),
  imageUrl: z.string().nullable().optional(),
  saleEvidence: CommerceProductSaleEvidenceSchema.nullable().optional(),
```

The existing product identity, `url`, price/currency, availability, product type, vendor and timestamp fields retain their exact original types. No extension schema, new product discriminator or second output model is created.

**3. Add this exact member to the existing `CommerceToolInputs` object (do not modify its search-product input):**

```typescript
  commerce_get_product: z.strictObject({
    productId: ID,
    variantId: ID.nullable(),
  }),
```

**4. Add this exact member to the existing `CommerceToolOutputs` object (do not modify its search-product output):**

```typescript
  commerce_get_product: z.strictObject({
    product: CommerceProductSchema.nullable(),
  }),
```

The existing search input remains:

```typescript
// Existing contract; DO NOT redefine
// {query, maximumPrice?, availableOnly, limit, cursor}
CommerceToolInputs.commerce_search_products;
```

The existing search output remains:

```typescript
// Existing contract; DO NOT redefine
// {products: CommerceProductSchema[], cursor, truncated}
CommerceToolOutputs.commerce_search_products;
```

**5. Example exact-product input:**

```json
{
  "productId": "product_123",
  "variantId": null
}
```

**6. Example optional data supplied on a normal existing `CommerceProductSchema` record (all original required product fields are still mandatory):**

```json
{
  "categories": ["Running", "Accessories"],
  "imageUrl": "https://store.example.com/media/socks.jpg",
  "saleEvidence": {
    "regularPrice": "20.00",
    "salePrice": "16.00",
    "observedAt": "2026-10-29T18:00:00.000Z"
  }
}
```

**7. Example exact-product result when the item is absent:**

```json
{ "product": null }
```

Transport/provider failure is not a successful `product: null` read: it must use the existing generic `status: "ERROR"` MCP result branch. The runtime decides when a product is genuinely not found.

**Business checks explicitly delegated outside Zod:**

| Rule | Owner |
|---|---|
| Search/lookup results belong to the authenticated merchant | MCP |
| Shopify/WooCommerce URLs and images point to appropriate storefront/provider resources | MCP product adapters |
| Provider stock/availability and price/sale information are current enough for a claim | MCP/product adapter + Background presentation |
| `regularPrice`/`salePrice` imply a meaningful reduction; no misleading savings statement | Background, using provider-backed evidence |
| Product identity/variant match, pagination limits and result ordering | MCP execution |
| AI chooses a relevant alternative using merchant instructions and checkout items | BACKGROUND-010 |

## Dependencies

None.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] Current `CommerceProductSchema`/search tool contracts remain recognisable and unchanged except for three specified optional fields.
- [ ] `commerce_get_product` input and output match the exact structures above; no new product data store, independent response envelope or AI-choice schema appears.
- [ ] Existing products without the new optional fields still parse.
- [ ] A structurally valid product with misleading `saleEvidence` does not become automatically approved by Zod; the relevant MCP/Background business layers remain accountable.
- [ ] Missing required existing product fields, unexpected keys and incorrect exact-product input types fail schema parsing.

## Validation

- [ ] `npm run typecheck`, `npm test`, `npm run build` in Shared.
- [ ] Unit fixtures: old product record; new optional fields; `product: null`; exact product ID; malformed ID; unknown keys; wrong types.
- [ ] Existing `CommerceToolInputs` and output fixture tests continue passing; `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, update Completion Report, set task to `review`, hand branch evidence to `moda_architect`, and **STOP**. Do not publish or begin another task.

## Implementation Notes

**Source edit boundaries are exact**: `moda-interact-shared/src/commerce/schemas.ts`, tests in `src/commerce/contracts.test.ts`, and no additional package subpath. If a provider cannot supply the existing required `variantId` without fabrication, report the contract gap to architect; do not invent a fallback in Shared.

## Completion Report

### Status

Not Started — portable definition; no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Confirm execution baseline in dedicated task worktree.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
