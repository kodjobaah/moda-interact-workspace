---
id: ARCH-058-MCP-002
architecture_id: ARCH-058
title: Ground product search, bounded catalogue browse and conversational discounts in current shop data
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-058-MCP-001
enables:
- ARCH-058-MCP-003
- ARCH-058-COMMERCE-001
- ARCH-058-BACKGROUND-001
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-058-MCP-002: Ground product search, bounded catalogue browse and conversational discounts in current shop data

## Architecture

Architecture ID: `ARCH-058`. Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Normative contracts: `docs/architecture/ARCH-058/contracts.md`. Coordinator: `moda_architect`.

**Defined but not materialised.** This portable definition does not establish a task branch, worktree, commit, deployment or successful provider call. Materialise through `/moda-task ARCH-058-MCP-002 --definition <path-to-this-file>`; use the implementation worktree and workspace root supplied by that launcher.

## Objective

Make the current merchant's actual provider products searchable by an exact typed category or by text, support an explicit bounded browse of its customer-visible catalogue, and make the existing canonical discount catalogue available to an authorized conversation. Preserve tenant boundaries, truthful pagination, exact product identity and current merchant discount policy. MCP returns product/condition facts; the existing Background host decides whether a proposed purchase supports a promotional claim.

## Context

- `src/execution/policy/shopify-core.ts` currently uses `first: $first` in `SEARCH_DOCUMENT`; `src/connections/shopify/document.ts` admits only literal bounded `first` values. The real provider always applies that guard. Tests which stub the `adminGraphql` boundary do not demonstrate that the composed search can execute.
- Product search currently requires text and has no typed category or browse argument. `src/execution/policy/shopify-core-executor.ts` also restricts argument mappings. Both the parser and executable mapping must agree with the new Shared contract.
- The current Woo reader projects stock facts without product/variation publication status or catalogue visibility. A no-query browse cannot equate an authenticated administrative listing or `stock_status: instock` with a customer-visible catalogue. The browse branch needs explicit publication checks before returning candidates.
- Shopify standard taxonomy, Shopify product type/collections, Woo native categories and Moda's broad store category are separate identities. A reference candidate from MCP-001 is not evidence that the merchant has a product.
- `src/mcp/registration.ts` in the uploaded snapshot lists/validates discount built-ins but reaches an unavailable stub. `docs/decisions/mcp/ARCH-052/MCP-002-execute-published-discount-options-and-proof.md` records an accepted complete implementation of the canonical snapshot reader. Reconcile that source discrepancy before writing a second reader.
- Current discount projection and policy reads are outreach-only, and current manifest grants describe published tools only. Shared-002 supplies the explicit built-in descriptor/grant branch. Discounts remain built-ins; product discovery remains published capabilities.

## Scope

In `moda-interact-mcp` only:

1. Extend `products.search` to the frozen nullable query, flat typed category and explicit browse input; preserve output contracts and ordinary exact-product reads.
2. Fix the literal-page-size composition failure and implement provider-correct exact membership and browse publication checks with bounded resumable product/variant scans.
3. Carry only trustworthy current price/currency/context facts and preserve actual provider identities and URLs.
4. Reuse/reconcile the accepted canonical discount reader, extend its authorized conversation path and implement built-in manifest/list/call identity matching.
5. Add tests through the actual composed provider/runtime boundaries, including structured original-error evidence.

## Out of Scope

No Admin, Gateway, Commerce, Background or Database implementation; no new provider API proxy, stored product mirror, universal Shopify-to-Woo mapping, descendant expansion, native category-listing MCP tool, discount proof endpoint, eligibility engine, legacy `commerce_evaluate_discount` revival, coupon application, checkout creation or customer send. Do not reopen accepted ARCH-052 task records. No persistent publication or live store mutation is authorized by this task.

Basic shipping reads belong to `ARCH-058-MCP-003` and its separate `commerce_get_shipping_information` / `shipping.getInformation` operation. Add no shipping fields to existing product output and change no get-product definition here. Browse adds no weather service, bestseller calculation or inferred product relevance.

## Requirements

### Accepted source and contract gates

- Start by comparing the actual launcher checkout with the accepted ARCH-052 MCP-002 implementation/review and the accepted ARCH-052 MCP-003/MCP-006 provider/error work. Record the commit/source evidence and remaining integration delta. Reuse accepted code brought forward through the normal task base. If the accepted reader or diagnostic implementation cannot be located/reconciled, stop with that discrepancy for the architect rather than implementing a competing catalogue or rewriting historical completion state.
- Consume the exact Shared package published by ARCH-058-SHARED-002, targeting `4.0.0` only while the recorded accepted baseline remains `3.1.0`. Use the architect-reconciled exact version if that baseline changed. No sibling-source import, copied wire validator or assumed local package version.
- `commerce_search_products` definition version is `2.0.0`, executing `products.search` operation version `1.0.0`. `commerce_get_product` remains definition/operation `1.0.0` with unchanged definition content. The resolver remains MCP-001-owned. Do not repurpose `shopify.searchProducts` or widen its unrelated published definitions accidentally.

### Typed inputs and exact provider search

- Use the frozen Shared input: optional/nullable query with parsed default null; optional flat `category` containing `system`, `id` and nullable `taxonomyVersion`; and `browse?: boolean` with parsed default false. Preserve maximum price, available-only, limit and cursor defaults/bounds. Update `src/execution/policy/shopify-core-executor.ts` argument allowlist/mapping and the service types to match.
- With `browse: false`, require a non-null query or category. With `browse: true`, require normalized `query: null` and an absent category; retain the declared price/availability/limit/cursor filters. Reject mixed browse-plus-query/category requests, incompatible provider/system, invalid native IDs, wrong Shopify taxonomy versions and non-null Woo taxonomy versions. Do not implement business checks as Zod refinements or introduce `oneOf` into the published input subset. An invalid filter is never silently ignored.
- For Shopify, validate the canonical taxonomy GID against the active pinned reference version, then derive the approved short token. Use the pinned Admin `products(query: ...)` `category_id` filter and verify each returned `Product.category.id` for exact equality. Build/escape query syntax in trusted code; the model does not provide raw GraphQL or provider filter grammar. Do not assume `productVariants` supports the product-category filter.
- Correct the existing text-search document to a literal accepted `first` bound and keep every new product/variant connection at a literal bound accepted by the existing guard. Do not weaken or bypass `inspectShopifyReadQuery`, increase its connection budget, or remove the provider preflight to make a query pass. `availableForSale` is a valid field in the pinned Admin schema; its presence alone is not a defect.
- Keep product and variant IDs as observed. The category branch must resume within products with more variants than one page, preserve its current product/variant position, and avoid duplicate/skipped results. Do not return only the first variant of every category product and pretend the search is complete.
- For Woo, extend the existing native `products.list` port and direct reader's allowlisted query builder with a validated native category parameter. The provider may include descendant-category products; exact membership requires checking each product's actual `categories[].id` before projecting it. Do not send an undocumented `include_children` parameter. Preserve existing variation reads, credential/installation checks, transport hardening and all request/response/page budgets.
- This increment adds no native Woo category-discovery endpoint. A caller may use a native ID observed in current-shop product data. The global resolver continues returning reference meaning; when no native Woo mapping is verified, the conversation uses an explicit text search. Never turn a Shopify GID, label or store category into a Woo ID by guessing.
- Products without taxonomy assignments remain discoverable by supported text fields. Query plus category is the explicit conjunction; category-only and text-only are supported. Exact membership is the only category semantics; no descendant flag, multi-category OR or hidden broadening.

### Explicit bounded catalogue browse

- Execute browse only when the validated argument is true. Do not generate a search term, wildcard, category or weather-related query to manufacture a match. A later browse after an unsuccessful search is a separate explicit invocation; never drop a requested query/category inside the search call. Browse returns a bounded sample of observed products, with no bestseller or suitability ranking claim.
- For Shopify, use the pinned provider's bounded variant/product read path without a customer text/category term. Add only trusted fixed publication filter syntax appropriate to that query (`product_status:active` for `productVariants`, or `status:active` for `products`). Project parent `Product.status` and `onlineStoreUrl`, and return a candidate only when status is exactly `ACTIVE` and its observed storefront URL is non-null and passes the existing current-shop/verified-primary-domain URL checks. A URL constructed from a handle does not satisfy this check. Do not assume a variant's stock flag proves parent publication.
- For Woo, narrowly extend the private `WooCommerceProductReadRequest` list branches in `src/connections/ports.ts` so trusted composition can mark a catalogue browse. Validate that bounded flag in `src/connections/woocommerce/provider.ts` and `direct-product-reader.ts`; do not accept caller-supplied raw paths, status expressions or arbitrary query parameters. For browse product/variation lists, the allowlisted builder sets `status=publish` and omits `search`. Add `status` and `catalog_visibility` to the internal product projection, and `status` to the internal variation projection. Check returned product status is `publish` and visibility is exactly `visible` or `catalog` before reading/returning its variants. A returned variation must also have status `publish` and belong to that verified parent through the parent-scoped endpoint and identity checks below. Exclude draft/private/pending, hidden/search-only and unknown-publication candidates; a published variation cannot override an ineligible parent.
- Keep a fixed provider ordering for browse and include its identity with the publication-filter semantics in the signed continuation. Apply the frozen `availableOnly` default true and existing price/context rules after publication checks. `availableOnly: false` may return a visible out-of-stock product with its actual availability value; it does not relax publication checks. Preserve Woo simple products' null variant IDs and all variant continuation state.
- These narrow query/projection checks belong to `products.search` browse. Do not loosen global Shopify document guards, Woo transport/grant checks or unrelated authored operation permissions. Existing text/category semantics and exact product output remain intact. The host may describe returned entries as examples from the catalogue; neither provider ordering nor a broad user question establishes popularity, weather suitability or personal relevance.

### Pagination, price and product grounding

- Version and sign the opaque cursor for the correct provider branch, current shop/connection, normalized query/category/version, `browse`, the applicable publication-filter/fixed-order semantics, price/availability semantics, market/currency context where actually established, expiry and product/variant progress. Reject tampering, expired state, cross-shop reuse and changes in any bound filter. A search cursor cannot be replayed in browse or vice versa, and a cursor issued under different publication semantics is invalid. A cursor is continuation state, not authorization.
- Preserve current bounded provider-call and page budgets, including `MAX_SEARCH_VARIANTS`, `MAX_SEARCH_PAGES` and the Woo per-invocation provider-call ceiling. Do not enlarge them to fill a browse page. If scanning reaches a bound before exhaustion, return a truthful continuation even when the current page contains zero matches. Do not report all products were searched or no product exists because one bounded page was empty. Continue from the exact pending product/variant boundary, including after publication, stock, category or price filtering. An actually exhausted result has no continuation; a bounded unfinished scan retains its cursor and truthful `truncated` value.
- For Woo variation list and exact retrieval, establish parent identity from the verified parent product and the authenticated parent-scoped `/wp-json/wc/v3/products/{productId}/variations` endpoint (with the requested variation ID for exact retrieval). Validate returned native variation IDs and exact-ID equality where requested. Native variation payloads need not contain `parent_id`: do not reject a valid endpoint-bound variation merely because it is absent. If `parent_id` is present, validate it and require exact equality with the verified parent; a malformed or mismatched value must never become product evidence. Correct the snapshot adapter's unconditional `parent_id` requirement where still present, while preserving tenant, installation, credential, private request-key and transport guards. An unchecked input parent ID or arbitrary URL is not parent authority.
- Search/exact-read output shapes remain unchanged. Use current provider prices, native sale evidence, availability and shop-validated URLs. Preserve null Woo variant IDs for simple products; do not fabricate variant IDs or infer that a category guarantees availability.
- Shopify's live `shop.currencyCode` supports a base-currency product price, not a customer-market price. Populate Woo currency only when the existing trusted current store context establishes the price denomination; otherwise retain null. Do not infer currency/market from recovery totals, locale, product text or model arguments. Market-pricing expansion is outside this increment.
- An unknown or mismatched currency cannot establish that a user's monetary budget is met, and cannot support discount arithmetic. Do not claim a verified maximum-price match in that case. Keep unknown facts explicit and let the host use its grounded no-promotion branch or ask for needed context.

### Canonical discount discovery and current policy

- Reuse the accepted PostgreSQL `ShopifyDiscount` catalogue/snapshot reader and condition mapping for both providers. Preserve the existing `commerce_get_discount_options` / `commerce_get_discount_details` inputs and normal success objects exactly. Options keep bounded signed keyset pagination; details preserve canonical identity, `providerDiscountId`, observed conditions and `PARTIAL`/`UNKNOWN` completeness.
- Extend `src/capabilities/prisma-reader.ts`, `src/execution/discount-tools.ts`, `src/runtime/service-ports.ts` and `src/mcp/registration.ts` for the frozen trusted conversational context as well as existing outreach. The generic MCP parser keeps context opaque; only the registered adapter interprets its approved purpose. Never let model tool arguments set shop, purpose, policy or grant state.
- Consume Shared's strict `CommerceConversationToolContextSchema`: `purpose: CONVERSATION`, `conversationId`, positive `inboundVersion`, and nullable `grantId`. Background supplies it under the existing opaque `toolContext` after validating its turn assertion: null grant during initial resolution, actual retained grant ID afterward. The domain reader verifies conversation ownership/current inbound version and applicable processing lease. With a grant ID, read the existing `commerceConversationGrant` and verify shop/conversation, expiry, runner and release relations before obtaining retained built-in identities from its stored JSON. Never accept hashes or a grant set supplied in context. Missing context remains an ordinary generic shop caller and receives neither conversational discount projection nor optional conversational degradation. Keep the outreach schema unchanged.
- Re-read the current authenticated shop and merchant policy on every list/call. `NONE` exposes no discount permission. `FIXED` uses the current permitted selection and active override, respecting revocation and expiry. `AI_BEST_APPLICABLE` reads the permitted current catalogue independently of the selection checkbox while preserving status, dates, unavailability and condition uncertainty.
- Details must use same-shop persisted snapshots, not Shopify/Woo per-offer HTTP, recovery/attempt reads or a model-provided coupon body. A foreign/revoked/unavailable offer is never returned as a permitted fact. Missing details remain null where the canonical contract allows; malformed/incomplete observations are not guessed into unrestricted conditions.
- Preserve source-native target IDs, effective Woo zero-threshold/quota semantics, known threshold currency and all accepted ARCH-052 targeting/exclusion/customer/sale/usage/combination uncertainty rules. MCP does not receive a basket or return an applicability verdict. Background's existing finalization adapter owns exact proposed-purchase evaluation.
- Only classified transient failures of an optional conversational lookup may return `status: OK` with the frozen `{outcome: UNAVAILABLE, reasonCode: TEMPORARY_UNAVAILABLE}` data. The normal success object is unchanged. Initial outreach retains its existing hard-failure behavior. Authorization changes, cancellation/stale invocation, malformed arguments/facts and unexpected exceptions remain outer errors; no empty-offers fallback, synthetic mode or legacy-success adapter.

### Built-in identities, manifests and retained grants

- Use the exact Shared canonical discount descriptors and contract-hash payload helper. Descriptor version is `1.0.0`; the hash covers canonical name/version/description/input/output schema. MCP must verify the schemas and hashes against the installed approved Shared contract, not treat a self-asserted hash as authority.
- Project the separate `builtInTools` manifest branch and matching `{kind: BUILT_IN, toolName, definitionVersion, contractHash}` grants. Keep published grants unchanged. Partition both branches deliberately in `src/capabilities/manifest.ts`, `src/mcp/ports.ts`, list/call validation and any shared runner projection.
- Reject duplicate names, collisions with published tool names, unknown built-ins, missing/unexpected descriptors, hash/version drift and combined bounds above the frozen limit. Do not fabricate capability/tool/revision database IDs or grant everything appearing in `tools/list`.
- Only a current-policy-permitted allowlisted built-in may enter a newly authorized conversation grant. For a retained grant, re-project its exact authorized descriptor identities without widening the set; current policy can remove availability/deny execution without rewriting the retained grant. A conversation originally granted under `NONE` cannot acquire tools from a later policy change. Follow the frozen trusted context and host transport contract; do not invent an unreviewed header or accept a model-supplied retained set.
- Outreach's separate current context remains valid without fabricated conversation grants. Before execution, re-read current policy, shop/connection and appropriate retained identity. Existing current release, descriptor, deadline, provider budget and tenant checks remain decisive.

### Original failure evidence

Follow `docs/observability/shared-logging.md` and use Shared structured logging at the owning boundary. Preserve actual sanitized Shopify/Woo response messages/codes, status/request IDs or original SDK errors/causes, and distinguish the Moda reason. Keep actual Prisma/contract errors for database-only discount reads without inventing a provider response. Logger failure must not change the tool's behavior. Preserve accepted redaction and bounded body/field handling; do not expose error payloads, keys, coupon values, customer data or raw provider bodies to the model/customer.

## Work Items

- [ ] Reconcile accepted ARCH-052 catalogue and provider diagnostic code with the actual implementation base; record only the remaining authorized delta.
- [ ] Update the Shared dependency and typed search/category/browse mapping and service checks without changing unrelated tools.
- [ ] Implement Shopify category-product/variant pagination, fix the literal query guard failure and preserve the real provider preflight.
- [ ] Add Woo native category filtering with exact returned-category verification and explicit text fallback behavior.
- [ ] Implement explicit browse through the existing provider composition with the frozen publication/visibility projections and checks, stock filtering and unchanged scan budgets.
- [ ] Bind browse, publication/order and all other search semantics to cursors, and preserve current-shop product/price/currency/URL evidence.
- [ ] Extend canonical discount execution and purpose-specific degradation without a second evaluator or catalogue.
- [ ] Implement built-in manifest/list/call identity projection and retained-grant/current-policy checks.
- [ ] Add focused composed-boundary tests, record validation, set status to `review` and return to the architect.

## Interfaces / Contracts

The frozen ARCH-058 contracts and the exact package accepted by SHARED-002 are normative. Public schemas remain Shared-owned; query interpretation, bounded pagination, authorization and provider mapping remain MCP-owned. Do not expand the schema subset or create an alternative product/discount envelope.

Primary touchpoints: `src/execution/policy/{shopify-core,shopify-core-executor}.ts`, `src/connections/ports.ts`, `src/connections/shopify/{document,provider}.ts`, `src/connections/woocommerce/{direct-product-reader,provider}.ts`, `src/execution/discount-tools.ts`, `src/capabilities/{records,prisma-reader,manifest}.ts`, `src/mcp/{ports,registration}.ts`, `src/runtime/{prisma,service-ports}.ts`, and the existing accepted catalogue reader once reconciled. In particular, update the policy executor's `allowedKeys`/argument mapping; Shopify document response parsers and internal product projection; Woo `products.list`/`products.variations.list` private request validation and `pathFor` field/query projection; and cursor construction/validation together. No new shipping projection belongs in this task. Keep new helpers beside their owning implementation, with semantic product/discount names.

Provider references for the frozen behavior: [Shopify Admin 2026-07 products](https://shopify.dev/docs/api/admin-graphql/2026-07/queries/products), [Shopify Admin product variants](https://shopify.dev/docs/api/admin-graphql/2026-07/queries/productVariants), [Shopify Admin Product fields](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Product), [Shopify Admin taxonomy category](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/TaxonomyCategory), [Woo REST products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/), [Woo REST variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/), [Woo v3 controller](https://woocommerce.github.io/code-reference/files/woocommerce-includes-rest-api-controllers-version3-class-wc-rest-products-controller.html), and [WordPress taxonomy-query defaults](https://developer.wordpress.org/reference/classes/wp_tax_query/__construct/). These establish query semantics; they do not certify a successful live merchant call. Verify against the source-pinned schema and actual accepted provider adapter during implementation.

## Dependencies

- `ARCH-058-MCP-001`: accepted reference lookup, required-feature selection and installed published Shared contracts. Its dependencies transitively provide the accepted Database and Shared artifacts.

The accepted ARCH-052 source reconciliation is a mandatory baseline check, not a request to redo those tasks. Background owns trusted conversational context production, retained grant persistence and final promotional validation; Commerce owns published product definitions.

## Enables

- `ARCH-058-MCP-003`: extend the accepted provider composition with the separate basic shipping-information operation, without changing product output.
- `ARCH-058-COMMERCE-001`: publish the four executable standard capabilities and approved response/behavior changes after its other declared prerequisites, including MCP-003, are accepted.
- `ARCH-058-BACKGROUND-001`: use authorized product and discount observations in conversation finalization.
- `ARCH-058-SYSTEM-TEST-001`: exercise the integrated provider, manifest and host flow.

## Acceptance Criteria

- [ ] A real adapter-to-provider preflight composition accepts the corrected pinned Shopify text, category and browse documents; an invalid/unbounded document remains rejected.
- [ ] Category-only, text-only and combined searches obey exact membership; invalid/mismatched categories fail explicitly. Woo child-only products cannot satisfy an exact parent filter.
- [ ] An explicit browse with query null/category absent succeeds; omitted/false browse with neither filter and browse combined with a query/category fail validation. No term/category is fabricated to execute browse.
- [ ] Shopify browse excludes non-ACTIVE parents and missing/foreign/unverified storefront URLs. Woo browse includes only publish + visible/catalog parents and publish variations of those parents, regardless of stock; draft/private/pending/hidden/search-only and unknown-publication candidates never escape.
- [ ] Default available-only browse excludes false/unknown availability; available-only false retains actual availability while preserving publication checks. Returned examples carry no invented bestseller, weather-suitability or relevance claim.
- [ ] Category/browse products with multiple variant pages and pages containing only filtered-out items return truthful, resumable progress without fabricated/exhausted results. Empty unfinished pages retain a cursor; exhaustion is reported only when proved.
- [ ] Cursor tampering, cross-mode replay, publication/order-policy changes, cross-shop/provider/filter/context changes and stale expiry fail closed; all provider work stays within existing budgets.
- [ ] Native Woo variations without `parent_id` remain usable through a verified parent-scoped list/exact read; present malformed/mismatching parent IDs and unverified parent contexts are rejected as product evidence. No tenant or private-read guard is relaxed.
- [ ] Search/get product result shapes and the get-product 1.0.0 definition remain unchanged; basic shipping remains MCP-003-owned.
- [ ] Current-shop prices/availability/URLs/IDs remain source-backed; null currency/variant values remain null, and no unknown monetary context becomes a budget or saving claim.
- [ ] Canonical discount options/details execute for authorized conversations and outreach, retain accepted condition uncertainty, and obey live NONE/FIXED/AI policy, revocation and overrides.
- [ ] Retained built-in identity is exact and never widens; list/call/hash/name-collision/policy-change fixtures pass without fake database identities.
- [ ] Optional operational unavailability is distinct from empty catalogue, missing details and hard errors; outreach and generic terminal-error behavior are preserved.
- [ ] Logs retain distinct real source failures with safe redaction and no leakage into tool outputs. No provider proof call, legacy evaluator, persistent publication or customer send was introduced.

## Validation

Run from the canonical launcher-provided MCP implementation worktree. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`.

- [ ] Extend `tests/unit/execution/policy/shopify-core.test.ts`, `tests/unit/connections/shopify/provider.test.ts`, `tests/unit/connections/woocommerce/direct-product-reader.test.ts` and `tests/unit/connections/woocommerce/provider.test.ts`; add `tests/unit/execution/policy/product-search-composition.test.ts` exercising the real document guard and provider composition. Run `npm exec -- tsx --test tests/unit/execution/policy/shopify-core.test.ts tests/unit/execution/policy/product-search-composition.test.ts tests/unit/connections/shopify/provider.test.ts tests/unit/connections/woocommerce/direct-product-reader.test.ts tests/unit/connections/woocommerce/provider.test.ts`.
- [ ] Include browse fixtures through those real boundaries: no-query/no-category success; false/default mode and mixed-argument rejection; exact internal status/visibility projection and allowlisted query parameters; active Shopify product with a verified URL versus draft/null/foreign URL; Woo publish visible/catalog parent versus draft/private/pending/hidden/search-only parent; published versus unpublished variations; true/false/unknown availability; and empty filtered pages followed by later matches. Assert the existing call/page/deadline bounds and continuation state at a mid-variant-page boundary. Reject search-to-browse/browse-to-search cursor replay, changed publication/order semantics and ordinary tenant/filter tampering. Include unsupported extra native request keys to prove the read guard was not broadened.
- [ ] Add real native-shape Woo list/exact-read fixtures with `parent_id` absent, a valid matching optional parent ID, a mismatching/malformed present parent ID, an incorrect exact variation ID and an unverified/cross-shop parent context. Prove the already authenticated parent-scoped endpoint plus observed parent is the authority and that valid variable products are not discarded because an undocumented response field is absent. Keep the unchanged public product schema and private request/transport checks in these assertions.
- [ ] Extend `tests/unit/execution/discount-tools.test.ts`, `tests/unit/capabilities/manifest.test.ts`, `tests/unit/capabilities/prisma-reader.test.ts`, `tests/unit/mcp/capability-invocation.test.ts` and `tests/unit/runtime/service-ports.test.ts`; run those exact files with `npm exec -- tsx --test`.
- [ ] Reuse/extend the accepted catalogue PostgreSQL tests. If the reconciled source has none, add `tests/integration/discount-catalogue.integration.test.ts` to the existing owned disposable fixture and run `npm run test:integration:docker`. Cover two shops, multiple pages, revoked selections, unknown restrictions, threshold currencies, active overrides and the separate conversational/outreach failure policies.
- [ ] Include real logger-sink assertions for distinct provider responses and SDK/Prisma errors, with deliberate credentials/PII sentinels proving redaction and no public-result leakage.
- [ ] Run `npm run typecheck`, `npm run lint`, `npm run build` and `git diff --check`. Record exact accepted dependency versions and validation outcomes; distinguish fixture success from live-provider certification.

## Stop Condition

Stop if accepted ARCH-052 code or frozen cross-repository contracts cannot be reconciled, or a provider-semantic gap would require a new endpoint/schema beyond this task. Ask the architect to resolve that concrete gap. Once the scoped implementation and validation are complete, set status to `review`, finish the report and return to `moda_architect`. Do not mark complete, publish tools, deploy, send a customer message or start another task.

## Implementation Notes

The first increment intentionally uses exact single-category membership. Woo has a bounded text path when native mapping is unavailable. Explicit browse supplies a bounded sample for a broad commerce question without fabricating a query or claiming a complete assortment/popularity result. A taxonomy classification is a search aid; a merchant product read is assortment evidence; a canonical discount snapshot is condition evidence. Applicability and the final customer-facing recommendation remain in the existing Background host. Basic shipping is the separate MCP-003 read operation.

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

Accepted ARCH-052 reader/error work and the exact published Shared package will be reconciled in the developer checkout before extending them.

### Unresolved Issues

The uploaded snapshot's built-in discount stub differs from the accepted ARCH-052 completion record; this task requires source reconciliation, not a duplicate implementation.

### Architectural Concerns

None beyond the explicit source/contract and provider-semantic gates above.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
