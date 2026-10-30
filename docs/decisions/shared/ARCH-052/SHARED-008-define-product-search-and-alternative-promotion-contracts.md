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
- The new fields are optional so current conversation product results still parse. MCP may populate them when known, otherwise they are absent or null as specified below.
- Re-read the exact task, parent architecture, mirrored worktree policy and prepared launcher packet before execution. No cross-repository implementation or secret-bearing logs.

## Work Items

- [x] Modify exactly the indicated locations in `moda-interact-shared/src/commerce/schemas.ts`.
- [x] Add deterministic product search/exact-product schema fixtures to `src/commerce/contracts.test.ts`.
- [x] Verify `src/commerce/index.ts` already exports `schemas.ts` and make no new entrypoint if so.
- [x] Run declared Shared validation and preserve existing conversation-tool tests.

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

**Source edit boundaries are exact**: `moda-interact-shared/src/commerce/schemas.ts`, tests in `src/commerce/contracts.test.ts`, and no additional package subpath. If a provider cannot supply the existing required `variantId` without fabrication, report the contract gap to architect; do not invent a fallback in Shared.

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
