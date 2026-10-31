---
id: ARCH-052-MCP-002
architecture_id: ARCH-052
title: Expose current shop discount catalogue to initial-outreach agent through MCP
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-012
- ARCH-052-BACKGROUND-013
- ARCH-052-BACKGROUND-014
- ARCH-052-MCP-001
- ARCH-052-SHARED-010
- ARCH-052-BACKGROUND-011
- ARCH-052-SHARED-014
enables:
- ARCH-052-BACKGROUND-010
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-31
---

# ARCH-052-MCP-002: Expose current shop discount catalogue to initial-outreach agent through MCP

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Portable definition: not materialised.**

## Objective

Implement two **generic, built-in, read-only** discount MCP tools: the existing `commerce_get_discount_options` with paged discovery, and the new `commerce_get_discount_details` for stored provider conditions. The agent, not MCP, decides basket/product relevance. No Commerce/Woo proof endpoint, bulk eligibility scan or provider call during outreach.

## Context

`ShopifyDiscount` and its shop-scoped `providerSnapshot`, `providerStatus`, `unavailableAt`, dates and merchant-owned `isAvailable` already exist in PostgreSQL. Published SHARED-010 adds the exact options page and details schema. BACKGROUND-011 enriches Shopify's sync projection; Woo coupon sync already captures most restrictions. MCP uses its existing Prisma and generic MCP result envelope. No outreach recovery/attempt DB lookup is allowed.

## Scope

- Extend MCP's current shop-scoped discount reader and built-in dispatcher for **`commerce_get_discount_options`** and **`commerce_get_discount_details`**. Do not register either through Commerce Studio or create a new generic result envelope.
- Options: use published Shared input `{limit,cursor}` (default 20, max 50), deterministic `shopId + discountId` keyset pagination and an opaque shop/policy/mode-scoped cursor (reject altered, wrong-shop, wrong-mode, expired/malformed cursors). Return `{mode,offers,cursor,truncated}` with correct next-page semantics; `NONE` returns empty with null cursor, FIXED reads current `isAvailable=true`, AI ignores the checkbox but respects current provider status, dates and unavailability. Never truncate silently.
- Details: `commerce_get_discount_details({offerId})` first rechecks the authenticated shop and current merchant mode/selection; map the **existing** `ShopifyDiscount.providerSnapshot` into SHARED-009's `CommerceDiscountConditionFactsSchema`, joined with the existing offer projection. Do not use Shopify/Woo HTTP for this. If a record does not exist for this shop, return `{details:null}`; insufficient/unsupported provider data yields `PARTIAL`/`UNKNOWN`, `UNKNOWN` targeting and `unrepresentedConditions` — never empty `COMPLETE` facts by guessing.
- Woo source mapping: `discountType`, `amount`, `productIds`, `excludedProductIds`, `productCategories`, `excludedProductCategories`, `minimumAmount`, `maximumAmount`, `usageLimit`, `usageCount`, `usageLimitPerUser`, `individualUse`, `excludeSaleItems`, `dateExpiresGmt`, `expiryUnverified`. Convert Woo numeric IDs to strings; unobserved customer/store extension restrictions remain unknown.
- Shopify source mapping: only the actual typed fields persisted by BACKGROUND-011. Preserve partial targeting and provider API/custom-rule limitations. No provider proof, no in-MCP discount applicability engine, no unapproved promotional claims.
- Use the generic `CommerceToolResultSchema`, existing private shop identity, tool access rules and Shared structured logging. Return bounded errors; no secret/customer payload leakage.

## Out of Scope

- Provider-specific proof endpoints and eligibility engines.
- Separate alternative-product evaluation orchestration.
- New Prisma tables/migrations, discount snapshot persistence, Commerce Studio discount-tool authoring.
- Changing the published generic MCP envelope or inventing cursor fields.

## Requirements

### Multi-discount combination-fact projection — normative 30 October 2026

- Consume the **newly published** `CommerceDiscountCombinationFactsSchema` from ARCH-052-SHARED-012; never project `COMPLETE` combination policy from Shared 2.7.0, which lacks it. Upgrade MCP package manifest/lockfile to the exact published version.
- For Shopify Basic source: map provider `discountClasses`, **own** `tags`, source-observed `shopifyPlus`, source `providerDiscountId`, and the separately observed `combinesWith` booleans/allowed same-line tags from BACKGROUND-013's snapshot into `facts.combination`, preserving `null` for unknown and marking `PARTIAL` for unsupported, truncated or missing observations.
- For Woo: return the already observed `individualUse` truthfully; unknown is `null`, and do not invent Shopify-style combination booleans or Plus entitlements for Woo.
- Keep the two existing MCP tools, generic `CommerceToolResultSchema`, purpose/shop guards, pagination and catalog snapshot reader. MCP reports facts only, never a new multi-discount evaluation/proof RPC or a guaranteed savings amount. Test cross-shop/revoked offers and malformed policies.


1. Shop-scoped PostgreSQL is the only discount information source at outreach time; `providerStatus` is separate from merchant-owned `isAvailable`.
2. Both tools consume the exact **published** SHARED-010 `CommerceToolInputs` / `CommerceToolOutputs` members; do not define duplicated validators or infer a new schema in MCP.
3. The keyset cursor may include a signed shop/policy/mode fingerprint and last discount ID, but must not be accepted across shops or modes. Cursor token contents are opaque to the agent and not treated as authorisation.
4. Tool output `truncated=true` only if another page exists; non-null output `cursor` accompanies continuation, otherwise null. These are **MCP business rules**, not Zod refinements.
5. A discount name or `providerStatus=ACTIVE` never proves applicability. Unknown condition fields remain explicit and are never treated as unrestricted.
6. Reuse Shared logging; log unexpected exceptions without swallowing, fail closed on tenant or tool-access mismatch.

### Exact eligibility fact mapping (no evaluation in MCP) — normative 31 October 2026

MCP-002 **does not receive a basket** and must NOT return a boolean coupon-applicability verdict. For every `commerce_get_discount_details` call, project the following independently checked, same-shop observations; **missing fields must retain `PARTIAL/UNKNOWN` plus reason codes** rather than default to unrestricted:

| Required projected facts | Source and missing-data rule |
|---|---|
| Identity/method/code/status/dates | Existing same-shop `ShopifyDiscount` record + provider snapshot; `providerDiscountId` is the persisted Shopify node ID or Woo coupon ID (`woo:coupon:<id>`); never a model-provided ID. No eligible CODE offer with absent/ambiguous/non-deliverable code. |
| Targeting + exclusions | Shopify Basic `customerGets.items` provider product/variant/collection IDs and connection `pageInfo`; Woo provider `productIds`, `excludedProductIds`, `productCategories`, `excludedProductCategories`; retain original provider ID domain and exact string ID. `hasNextPage`, malformed IDs, unavailable exclusion arrays or unsupported target type => explicit `TARGETING_INCOMPLETE` or `TARGET_EXCLUSIONS_UNKNOWN`, never `kind:ALL`. |
| Money/quantities | Consume `CommerceDiscountConditionFactsSchema.subtotalRequirementCurrency` from the **new package version published by SHARED-014**, not 2.8.1. Keep exact decimal `minimumSubtotal`/`maximumSubtotal` strings. For Shopify Basic map only `minimumRequirement` `MoneyV2.currencyCode` captured by BACKGROUND-013 alongside the corresponding amount. For Woo core use the authenticated store currency **only when its source and native Woo semantics prove it is the denomination of effective `minimumAmount`/`maximumAmount`**. Never infer from `discountCurrency`, locale or title. If effective threshold exists and currency missing, conflicting or unprovable, set `subtotalRequirementCurrency:null` with `THRESHOLD_CURRENCY_UNKNOWN` and retain the effective threshold as observed; Background MUST return UNVERIFIABLE. Preserve min/max, usage and quantity restrictions; represent `limit_usage_to_x_items` as `UNREPRESENTED_MAXIMUM_ITEMS` until modelled, never silently discard limits. |
Woo numeric source semantics are **not** synonymous with unknowns: a present `minimumAmount:"0"` / `maximumAmount:"0"` means no effective threshold; observed `usageLimit:0` / `usageLimitPerUser:0` means no quota. Preserve true source values and this interpretation in details mapping; a missing/unobserved field remains `null`/an explicit uncertainty reason. For a coupon with neither effective monetary threshold, set `subtotalRequirementCurrency:null` without `THRESHOLD_CURRENCY_UNKNOWN`, even if store currency lookup is unavailable. Never substitute `0` for absent fields.

| Customer/use/sale restrictions | Source Shopify `context`, `appliesOncePerCustomer`, bounded usage counters; Woo `usageLimitPerUser`, `usageLimit`, `usageCount`, `excludeSaleItems`, `emailRestrictionsPresent`, `uninspectedMetadataPresent` (from BACKGROUND-014), `expiryUnverified` and other source-backed extension/metadata restrictions. Never read or persist the raw email/metadata arrays. Where a restriction cannot be represented/proven, emit an explicit reason (e.g. `CUSTOMER_RESTRICTION_UNVERIFIED`, `EXPIRY_UNVERIFIED`, `SALE_ITEM_STATUS_UNKNOWN`) and do not map to permissive `ALL` or `false`. |
| Combination | Shopify `discountClasses`, `combinesWith` class booleans, own `tags`, allowed same-line tags, shop-plan `shopifyPlus`; Woo observed `individualUse`. Missing combination facts may allow a **standalone** discount if all unrelated eligibility conditions are complete, but cannot allow an unverified pair. |

**Required completeness behaviour:** Compute the returned completeness from source proof **after** SHARED-011 combination projection. Remove the obsolete `COMBINATION_POLICY_NOT_REPRESENTED_IN_SHARED_FACTS` reason only when all corresponding new combination fields are genuinely mapped; keep all other legacy and newly observed uncertainty reasons. Do not equate an empty `unrepresentedConditions` array with `COMPLETE` if the source was missing required observations. Conversely, do not carry the old constant-false `PARTIAL` when the only reason was absent contract projection and the source is now fully represented. `offer.support:SUPPORTED` and `facts.completeness:COMPLETE` are still **not** an eligibility decision. Use no new MCP tool, basket read, provider network call or Zod business-rule refinement.

### Actual failures from the owning MCP boundary (31 October 2026)

This discount reader performs **PostgreSQL snapshot reads only**, not Shopify
or WooCommerce HTTP calls. On an unexpected Prisma/DB/contract exception,
log the actual original `Error.name`/`Error.message` and `cause` with the
existing Shared logger, safely redacted and bounded, plus the distinct MCP
reason code, trusted shop and operation. **Do not invent** Shopify, Woo or
other provider error text when no provider was called. Preserve the existing
public `CommerceToolResultSchema`/MCP error response (never expose DB
exception details or raw provider logs as a tool result). When the handler
receives a propagated `McpRequestError`, retain its existing status/code,
log the originating cause where available and do not replace the original
exception with a synthetic provider message. Unexpected exceptions remain
visible and propagate to the existing failure boundary, not a silent
`{details:null}` success.

## Work Items

- [ ] Add bounded shop/mode-scoped keyset paging to the current discount lookup and exact Shared response, including cursor tamper/cross-tenant rejection.
- [ ] Add built-in `commerce_get_discount_details` handler using existing `providerSnapshot` (Woo and enriched Shopify); map incomplete rules to explicit PARTIAL/UNKNOWN.

- [ ] Upgrade the MCP Shared pin and lockfile to the exact SHARED-014 published version, then map required-nullable `subtotalRequirementCurrency`, exact targeting/exclusion IDs, Woo `emailRestrictionsPresent`/`uninspectedMetadataPresent`, source restrictions and all source completeness reasons as specified above; do not treat missing Woo extension/customer restrictions as unrestricted. If either flag is true or null, include an explicit uncertainty reason; only verified `false` is absence of that particular restriction.
- [ ] Respect current FIXED/AI/NONE policy on **every call**, including detail requests and calls after merchant policy changes.
- [ ] Use the existing generic MCP envelope and published feature schema, with safe structured error logging.
- [ ] Preserve actual Prisma/contract exception messages and causes in server-side Shared logs while keeping MCP client/tool error payloads minimal; never fabricate a provider error for a DB-only read.
- [ ] Add PostgreSQL-backed tests for two shops, 120 discounts/page 75, selected vs unselected, revoked selections, missing details, Woo restrictions, Shopify partial rules and absent condition fields.

## Interfaces / Contracts

**Normative published interface: SHARED-009 -> SHARED-010 -> SHARED-011/012 -> SHARED-013/014** (`@modainteract/moda-interact-shared/commerce`):

```typescript
CommerceToolInputs.commerce_get_discount_options;  // {limit: 1..50 default 20, cursor: string|null default null}
CommerceToolOutputs.commerce_get_discount_options; // {mode, offers, cursor?: string|null, truncated: boolean}; MCP ALWAYS emits cursor
CommerceToolInputs.commerce_get_discount_details; // {offerId: string}
CommerceToolOutputs.commerce_get_discount_details; // {details: {offer: CommerceOffer, facts: CommerceDiscountConditionFacts, providerDiscountId: string|null}|null}
```

Existing `CommerceToolResultSchema` wraps `data`. See SHARED-009's complete Zod source and fixtures; no type or field inventing is permitted. Concrete implementation entrypoints: extend `moda-interact-mcp/src/execution/` built-in discount tool registry/dispatcher and its Prisma data reader, reusing existing private MCP context (`shopId`, `toolContext.purpose`). `CommerceDiscountConditionFacts` values are **data**, not an eligibility verdict. No new request fields for checkoutRecoveryId, outreachAttemptId or full cart.

## Dependencies

- `ARCH-052-MCP-001` — accepted outreach purpose and shop-scoped authorisation.
- `ARCH-052-SHARED-010` — published complete discount input/output contracts.
- `ARCH-052-BACKGROUND-011` — accepted source-backed Shopify catalogue enrichment, so the MCP mapping cannot invent missing Shopify rules.
- `ARCH-052-BACKGROUND-013` — source-backed Shopify own tags/classes, plan status and subtotal threshold source amount/currency.
- `ARCH-052-BACKGROUND-014` — source-backed Woo email/metadata restriction presence without storing personal data.
- `ARCH-052-SHARED-014` — newly published currency-qualified condition-facts schema; upgrade MCP manifest/lockfile to the exact version before projecting details.

## Enables

- `ARCH-052-BACKGROUND-010`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] All pages and a valid continuation cursor work for 120 discounts without accidental omission under a static dataset; change across live catalogue sync is reported as possible partial read, not a claim of exhaustive verification.
- [ ] Only current permitted shop discounts are visible for FIXED and AI; detail reads cannot access unselected FIXED offers or other shops.
- [ ] Condition outputs distinguish COMPLETE, PARTIAL and UNKNOWN on source evidence, including unsupported/large targets.

- [ ] MCP source facts conform to **SHARED-014**, not the already published 2.8.1 schema: missing required `subtotalRequirementCurrency` property is a schema failure; a threshold without provable currency is incomplete; a verified no-threshold offer has `subtotalRequirementCurrency:null` without a false missing-currency warning. Truncated targeting and unknown exclusions never yield authoritative ALL; the obsolete unrepresentable-combination reason is removed only after complete new projection.
- [ ] MCP does not call external providers or private proof APIs during discount options/details retrieval.
- [ ] Generic MCP result, structured logging, tenancy and publisher/tool permissions remain intact.

- [ ] Inject distinctive database, schema and `McpRequestError` failures; verify original origin and message in redacted server logs, no fake Shopify/Woo response, no exception content in model-facing MCP results and no catch-to-empty-success.

## Validation

- [ ] Run MCP unit and PostgreSQL integration tests for pages, cursor tamper, tenant isolation, current policy, Woo and Shopify providerSnapshot mapping, and generic `CommerceToolResultSchema` conformance.

- [ ] Add fixtures for product ID versus variant ID, category/collection IDs, excluded IDs, `hasNextPage`/overflow, missing money currency, Woo email/metadata presence flags true/false/null, unknown sale-item/expiry/usage restriction, exact provider identity, and Shopify fully observed Basic versus combination-only partial. Assert no tool produces a basket-level SUPPORTED decision.
- [ ] Run declared MCP typecheck/build and `git diff --check`; record actual command outcomes.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, complete the report, set `status: review`, return to `moda_architect`, and **STOP**. Do not start enabled tasks or merge/push main.

## Implementation Notes

Use the existing MCP database connection, discount models and feature/tool registry. The agent—not MCP—owns ranking and deciding which offer matches the checkout. MCP must return only facts established by its source data. Do not implement a new discount evaluator, provider-proof endpoint or a separate product recommendation engine.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Implementation must confirm package versions and the current task worktree baseline.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Escalate any unexpected provider API/auth/Shared/schema/contract gap to `moda_architect` without inventing a second implementation.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only. No implementation accepted.

### Reviewed Files

Relevant October 29, 2026 code snapshot and task definition; no implementation source changes for this task reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through the canonical launcher only after all dependency task YAMLs are Complete.
