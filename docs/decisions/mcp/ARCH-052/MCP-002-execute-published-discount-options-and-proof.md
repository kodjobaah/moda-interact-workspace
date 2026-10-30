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
- ARCH-052-MCP-001
- ARCH-052-SHARED-010
- ARCH-052-BACKGROUND-011
enables:
- ARCH-052-BACKGROUND-010
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-30'
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

1. Shop-scoped PostgreSQL is the only discount information source at outreach time; `providerStatus` is separate from merchant-owned `isAvailable`.
2. Both tools consume the exact **published** SHARED-010 `CommerceToolInputs` / `CommerceToolOutputs` members; do not define duplicated validators or infer a new schema in MCP.
3. The keyset cursor may include a signed shop/policy/mode fingerprint and last discount ID, but must not be accepted across shops or modes. Cursor token contents are opaque to the agent and not treated as authorisation.
4. Tool output `truncated=true` only if another page exists; non-null output `cursor` accompanies continuation, otherwise null. These are **MCP business rules**, not Zod refinements.
5. A discount name or `providerStatus=ACTIVE` never proves applicability. Unknown condition fields remain explicit and are never treated as unrestricted.
6. Reuse Shared logging; log unexpected exceptions without swallowing, fail closed on tenant or tool-access mismatch.

## Work Items

- [ ] Add bounded shop/mode-scoped keyset paging to the current discount lookup and exact Shared response, including cursor tamper/cross-tenant rejection.
- [ ] Add built-in `commerce_get_discount_details` handler using existing `providerSnapshot` (Woo and enriched Shopify); map incomplete rules to explicit PARTIAL/UNKNOWN.
- [ ] Respect current FIXED/AI/NONE policy on **every call**, including detail requests and calls after merchant policy changes.
- [ ] Use the existing generic MCP envelope and published feature schema, with safe structured error logging.
- [ ] Add PostgreSQL-backed tests for two shops, 120 discounts/page 75, selected vs unselected, revoked selections, missing details, Woo restrictions, Shopify partial rules and absent condition fields.

## Interfaces / Contracts

**Normative published interface: SHARED-009 -> SHARED-010** (`@modainteract/moda-interact-shared/commerce`):

```typescript
CommerceToolInputs.commerce_get_discount_options;  // {limit: 1..50 default 20, cursor: string|null default null}
CommerceToolOutputs.commerce_get_discount_options; // {mode, offers, cursor?: string|null, truncated: boolean}; MCP ALWAYS emits cursor
CommerceToolInputs.commerce_get_discount_details; // {offerId: string}
CommerceToolOutputs.commerce_get_discount_details; // {details: {offer: CommerceOffer, facts: CommerceDiscountConditionFacts}|null}
```

Existing `CommerceToolResultSchema` wraps `data`. See SHARED-009's complete Zod source and fixtures; no type or field inventing is permitted. Concrete implementation entrypoints: extend `moda-interact-mcp/src/execution/` built-in discount tool registry/dispatcher and its Prisma data reader, reusing existing private MCP context (`shopId`, `toolContext.purpose`). `CommerceDiscountConditionFacts` values are **data**, not an eligibility verdict. No new request fields for checkoutRecoveryId, outreachAttemptId or full cart.

## Dependencies

- `ARCH-052-MCP-001` — accepted outreach purpose and shop-scoped authorisation.
- `ARCH-052-SHARED-010` — published complete discount input/output contracts.
- `ARCH-052-BACKGROUND-011` — accepted source-backed Shopify catalogue enrichment, so the MCP mapping cannot invent missing Shopify rules.

## Enables

- `ARCH-052-BACKGROUND-010`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] All pages and a valid continuation cursor work for 120 discounts without accidental omission under a static dataset; change across live catalogue sync is reported as possible partial read, not a claim of exhaustive verification.
- [ ] Only current permitted shop discounts are visible for FIXED and AI; detail reads cannot access unselected FIXED offers or other shops.
- [ ] Condition outputs distinguish COMPLETE, PARTIAL and UNKNOWN on source evidence, including unsupported/large targets.
- [ ] MCP does not call external providers or private proof APIs during discount options/details retrieval.
- [ ] Generic MCP result, structured logging, tenancy and publisher/tool permissions remain intact.

## Validation

- [ ] Run MCP unit and PostgreSQL integration tests for pages, cursor tamper, tenant isolation, current policy, Woo and Shopify providerSnapshot mapping, and generic `CommerceToolResultSchema` conformance.
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
