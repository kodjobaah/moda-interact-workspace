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
status: blocked
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-058-MCP-001
- ARCH-058-DATABASE-002
- ARCH-058-SHARED-006
enables:
- ARCH-058-MCP-003
- ARCH-058-COMMERCE-001
- ARCH-058-BACKGROUND-001
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: 2026-11-04
---

# ARCH-058-MCP-002: Ground product search, bounded catalogue browse and conversational discounts in current shop data

## Architecture

Architecture ID: `ARCH-058`. Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Normative contracts: `docs/architecture/ARCH-058/contracts.md`. Coordinator: `moda_architect`.

**Definition revision 10 — contract-identity correction.** Attempt 1 stopped correctly at the Shared contract-integrity gate and its WIP implementation remains preserved at `4bffa87ed4af0fb40513ad75d38df49c51746360`. This task is now architecturally **blocked** with its claim cleared; do not delete, revert, cherry-pick around or recreate that WIP. DATABASE-002 and SHARED-006 are new forward prerequisites. After both are Complete and architect-accepted, moda_architect returns this same task to Ready and `/moda-task ARCH-058-MCP-002` reclaims it as the next attempt in the canonical dedicated worktrees. Do not reuse the old claim, rerun taxonomy-source selection or recreate MCP-001 work. The [revision-10 contract correction](../../../architecture/ARCH-058/shared-hash-reconciliation.md) is binding.

## Objective

Extend the accepted MCP tool provider with exact category search, explicit catalogue browse and the existing shop-scoped discount catalogue. MCP resolves the authenticated shop, advertises executable tools and returns current source facts. Background owns conversation state, retained workflow grants, turn admission, offer applicability and customer wording.

## Context

The baseline for this amendment is `moda-interact-workspace-ARCH-058-MCP-002.zip`. Its Completion Report below is preserved byte-for-byte, including the resolved Database blocker, the Shared mismatch and unfinished validation. The earlier source-gap list below remains the implementation specification; it is not a claim that the preserved WIP has not already addressed some of those gaps. Continue from that WIP and assess remaining changes against the existing requirements. Do not repeat MCP-001 taxonomy source selection/importer work.

The snapshot establishes these implementation gaps:

- `shopify-core.ts:SEARCH_DOCUMENT` uses variable `first: $first`, rejected by `connections/shopify/document.ts`. Its `SearchInput.query` and provider composition are text-only.
- Woo request keys are independently checked in `connections/resolver.ts`, `connections/woocommerce/provider.ts` and `direct-product-reader.ts`; changing only the port type cannot enable a category/browse request.
- Woo list/exact mapping unconditionally requires `parent_id`, although native variation ownership is established by the verified parent endpoint. The search loop also advances some variation indexes only after validation, leaving filtered records able to repeat.
- Current product search and exact get omit publication qualification; Woo `available` is inferred from stock alone. Applying visibility only to fallback browse would still let ordinary text/category results and their final exact refresh expose drafts, hidden products or Shopify UNLISTED products. Sections 3–5 qualify all recommendation product reads using private provider facts, without adding public fields or changing tool versions.
- `discount-tools.ts` and `runtime/service-ports.ts` expose discount descriptors only for an outreach purpose and current non-NONE mode. The generic capability reader performs the associated settings/selection reads. These must become context-independent tool discovery; the accepted catalogue executor retains current shop configuration checks on actual calls. `mcp/snapshot.ts` also needs exact canonical descriptor/manifest equality.
- The current upload contains `src/execution/discount-catalogue.ts`, its unit/PostgreSQL coverage and the production `executeDiscountTool` wiring. Its `execute` still rejects callers without the outreach purpose; remove that gate at the existing reader as well as in discovery/registration. Preserve its fact projection and keyset cursor.
- The built-in branch in `mcp/registration.ts` currently calls `ports.executeDiscountTool` directly. Unlike `executePublishedTool`, that branch has no per-call deadline/cancellation/result-byte wrapper; the service's HTTP envelope bound is a separate limit. Section 7 specifies the narrow reuse of the existing execution mechanics needed to close that gap.
- The accepted Woo diagnostic path is present in `direct-product-reader.ts`, including `safeException`, `sourceProviderError`, provider status/request ID and original bounded error/cause logging. Preserve that implementation. The older missing-catalogue/missing-diagnostics statements in the untouched initial report below are superseded by this source inspection.

## Scope

Only `moda-interact-mcp` source, tests and its task report. Public input/output contracts come from the architect-accepted Shared **5.0.0** publication produced by SHARED-006; runner remains **1.1.0**. ARCH-058 does **not** pin or downgrade MCP's direct Zod dependency: preserve its existing direct version unless an independent task explicitly changes it. Built-in identity is `toolName + definitionVersion` only; no contract hash, generated-schema digest or replacement fingerprint is permitted. Product-search definition is **2.0.0**, operation `products.search` **1.0.0**. Exact product definition/operation remain **1.0.0**. Shipping implementation belongs to MCP-003.

### Exact implementation map

Paths in this table are relative to the MCP implementation worktree. Test fixtures must exercise these implementations, not alternative helpers that reproduce the intended answers.

| Path | Required change |
| --- | --- |
| `src/execution/policy/shopify-core.ts` | Extend `SearchInput`; replace search document/filter composition; add the category document and provider parsers; implement the three bounded search branches below; qualify publication in every search/exact-get path and Woo availability from the selected source's stock/purchasable facts; correct optional Woo `parent_id` handling. Keep basket behavior and public product schemas/versions unchanged. |
| `src/execution/policy/product-search-cursor.ts` — new | Own only the signed version-2 search cursor, normalized filter fingerprint and strict provider progress parsing described below. Move the existing product-search cursor mechanics here; no other cursor protocol changes. |
| `src/execution/reference-taxonomy/category-membership.ts` — new | Export `createPrismaProductCategoryReader` and the narrow `ProductCategoryReader` port below. Read the already accepted taxonomy tables by exact ID; no embedding/import/source download. |
| `src/execution/policy/shopify-core-executor.ts` | Add `category`/`browse` only to `products.search` mappings; inject the category reader and trusted environment into its adapter. Keep the legacy `shopify.searchProducts` mapping text-only. Preserve actual output-schema validation and rendering. |
| `src/connections/{ports,resolver,prisma-reader}.ts` | Add the exact private list fields and trusted cursor connection identity below; forward fields through the resolver and extend its strict key checks. Select Woo installation `id`/`credentialVersion` alongside the already selected fields; no extra connection query. |
| `src/connections/woocommerce/{provider,direct-product-reader}.ts` | Extend `approvedRequest`, `validRequest` and `pathFor` together; add the fixed list/exact publication and purchasable projections, published-list filters and fixed ordering; preserve accepted credential/transport/original-error work. |
| `src/capabilities/{records,prisma-reader,manifest,resolve}.ts` | Keep the exact generic shop/release/plan projections; remove discount settings/selection reads from this capability reader. Project the canonical pair independently of caller context/current mode and build the provider manifest tool union with `deduplicateTools(capabilities, builtInTools)`; read no retained grant. Preserve MCP-001 required-feature selection. |
| Existing `src/execution/{discount-tools,discount-catalogue}.ts` | Replace purpose-dependent descriptor projection and remove the reader's outreach-purpose gate. Preserve the existing factory, current mode/FIXED selection/override checks, condition mapping and keyset cursor. Apply section 7's exact NONE/details/cursor ordering and section 8's query-scoped unavailable-data classification for every caller. |
| `src/mcp/{ports,snapshot,registration,execution}.ts` | Use the canonical descriptor DTO and exact manifest/list equality. Remove the purpose/list-time mode gate; route built-in calls through the bounded wrapper in section 7. Share the existing call-policy/deadline/cancellation/result-byte mechanism within `execution.ts`, preserving published-call behavior. |
| `src/runtime/{ports,prisma,service-ports}.ts` | Add the category reader to the existing composition and remove the outreach-only listing call. Preserve the existing `createPrismaDiscountCatalogueReader` -> `ports.discounts` -> `ShopifyServiceComposition.discounts` -> `executeDiscountTool` chain; forward the added private RPC signal/deadline through its existing spread. The published execution registry retains its generic shop/environment authorization read. |
| `package.json`, `package-lock.json` | After SHARED-006 acceptance, pin Shared exactly `5.0.0`; do not change MCP's direct `zod` version for ARCH-058. Retain all other dependency versions/scripts and update the Database gitlink only to the accepted DATABASE-002 descendant supplied by normal task preparation. Verify the no-hash public exports and strict name/version built-in identity below. |
| Tests named in Validation | Add/extend focused fixtures and the existing disposable database harness. No new test framework or runtime dependency is required. |

## Out of Scope

No Shared/Database source changes or package publication; MCP owns only the explicit consumer dependency alignment above; no edits to MCP-001, accepted ARCH-052 reports, Admin taxonomy or decision indexes. No conversation context parser, conversation/retained-grant/recovery-lifecycle reader, lease/takeover check or workflow authorization module in MCP. Existing unrelated execution adapters may still consume their established opaque toolContext. No new taxonomy source, native category-discovery endpoint, Shopify-to-Woo category translation, descendant expansion, product mirror, discount proof API, basket eligibility engine, coupon application, checkout/cart mutation, shipping fields in product results, tool publication, environment setup or customer send. Runtime filenames and symbols must not contain architecture task IDs.

## Requirements

### 1. Consume the known prerequisites once

MCP-001 is Complete at accepted implementation `1dd5430b9d3108bf93bba86c1fb9233736f606d3`. Preserve its taxonomy/required-feature work and the MCP-002 WIP at `4bffa87ed4af0fb40513ad75d38df49c51746360`. DATABASE-002 must be present through the accepted Database gitlink before this task resumes; do not edit either historical ARCH-058 migration. Shared 4.0.0 remains historical evidence only.

After DATABASE-002 and SHARED-006 are Complete and this task has been returned to Ready/reclaimed, run from the canonical MCP implementation worktree:

```bash
npm install --package-lock-only --save-exact @modainteract/moda-interact-shared@5.0.0
npm ci --no-audit --no-fund
npm ls --depth=0 @modainteract/moda-interact-shared zod
```

Inspect the lock diff. The root Shared pin must be exactly `5.0.0`; MCP's existing direct Zod dependency must remain unchanged by this task. Compare the installed Shared integrity with the accepted SHARED-006 receipt. In a clean Node process import `@modainteract/moda-interact-shared/commerce` and assert: both canonical discount descriptors have definitionVersion `2.0.0`; legacy `1.0.0` fails strict Shared parsing; neither descriptor nor its projected built-in grant contains `contractHash`; `commerceBuiltInToolContractPayload` and `CommerceConversationToolContextSchema` are not exported; and the corrected discount built-in timestamp fixtures from SHARED-005 parse/reject exactly as published. Do not add another hash/fingerprint, npm override or dependency downgrade. A missing export, unexpected extra identity field, unresolved Database migration or failed schema composition is a hard prerequisite failure returned to moda_architect.

Keep the actual merchant-knowledge schema composition and taxonomy-fixture `z.toJSONSchema` paths in normal typecheck; those repository-local uses are not contract identity. Reuse the normal reclaimed-task preparation packet; do not repeat taxonomy/package source discovery.

The current upload already includes the ARCH-052 catalogue source, `tests/unit/execution/discount-catalogue.test.ts`, its production wiring and the persisted-snapshot scenario in `tests/integration/prisma.integration.test.ts`. The existing factory is `createPrismaDiscountCatalogueReader(database, {cursorSecret?, now?}): DiscountCatalogueReader`, whose method is `execute(call: DiscountSystemToolCall): Promise<CommerceToolResult>`. `runtime/ports.ts:createPersistedMcpPorts` constructs it once; `runtime/prisma.ts` passes `ports.discounts` to `createShopifyServicePorts`; `runtime/service-ports.ts` supplies the existing logger and invokes `options.discounts.execute`. Preserve this chain and its existing `COMMERCE_CURSOR_SECRET` source. The catalogue is no longer a missing-source blocker.

Historical provenance remains ARCH-052-MCP-002's correction `89e9ad3` after `7cbceee89b2ae0115bd2b948418b4169b977ea8f`, plus ARCH-052-MCP-006's accepted diagnostic correction `1d18e6c866311d0a3238a919f335643ffbefd8c1`. An abbreviated recorded commit is not a fabricated full SHA. At normal task preparation, verify the observed source/composition is still present in the accepted MCP-001 base. Only an actual missing path or changed incompatible signature is a new prerequisite failure. Do not recreate the reader/logger, repeat integration already present in this upload or check out an old task commit over MCP-001.

For query-schema validation, reuse the prepared MCP artifact `artifacts/shopify-admin-2026-07.json`. Its existing installer pins SHA256 `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`. If the MCP-local copy is absent but the accepted generated Commerce artifact is supplied, run the existing `npm run schema:install:shopify -- <absolute-accepted-commerce-artifact-path>` from the supplied MCP implementation worktree; that path ends in `lib/discovery/artifacts/admin-2026-07.json` in the accepted Commerce checkout. Do not infer a sibling path from MCP-001. Commerce's already selected generation route is `scripts/sync-shopify-admin-schema.mjs` over exact `@shopify/dev-mcp@1.15.4` file `dist/data/admin_2026-07.json.gz`; it is provenance, not permission for this task to alter another repository or select/download another schema. Generated schema files are intentionally absent from both uploaded ZIPs, as documented by MCP README. Their archive absence is not a missing source implementation. Reuse prepared artifacts without regeneration; if neither prepared copy is available, report the exact missing local artifact through normal preparation. A mismatched hash is a hard preparation failure. This local artifact copy is not persistent-environment setup.

### 2. Normalize the public search input before I/O

Replace the old interface with `export type SearchInput = z.input<typeof CommerceToolInputs.commerce_search_products>`; use `z.output` for normalized internal input after parsing that Shared schema. Trim a non-null query; a whitespace-only query is `INVALID_INPUT`. Keep null as null, with no synthetic wildcard. Defaults remain query null, browse false, availableOnly true, limit 10 and cursor null; maximumPrice remains optional. Keep the exact flat Shared category object.

| Parsed request | Service action |
| --- | --- |
| browse false, query non-null, no category | Text branch. |
| browse false, category present, query null or non-null | Exact category branch; a supplied query is an additional conjunction. |
| browse true, query null, category absent | Explicit catalogue browse branch. |
| No query/category with browse false; browse combined with query/category | `INVALID_INPUT`, zero provider calls. |
| Wrong category system for the connection; invalid native ID; missing/mismatched Shopify version; non-null Woo version | `INVALID_INPUT`, zero provider calls. |

Shopify category membership is verified by `ProductCategoryReader.read({environment, categoryId, taxonomyVersion, signal})`, returning `{generationId, categoryId, taxonomyVersion}` from this fixed parameterized read (use the existing generated Prisma tagged-SQL interface; never concatenate the values):

```sql
SELECT g."id" AS "generationId", g."taxonomyVersion", c."categoryId"
FROM "commerce"."ReferenceTaxonomyGeneration" AS g
LEFT JOIN "commerce"."ReferenceTaxonomyCategory" AS c
  ON c."generationId" = g."id" AND c."categoryId" = $2
WHERE g."environment" = $1::"commerce"."CommerceEnvironment"
  AND g."source" = 'SHOPIFY_STANDARD_PRODUCT_TAXONOMY'
  AND g."languageTag" = 'en' AND g."isActive" = true
LIMIT 2;
```

Bind `$1` to `databaseEnvironment` of the trusted server environment and `$2` to the supplied category ID. English is the already pinned MCP-001 corpus; do not select another language/source here. Zero generation rows is outer `UNAVAILABLE`; more than one is a malformed database state and hard outer `UNAVAILABLE`; one row with the wrong version or a null categoryId is `INVALID_INPUT`. Select no vectors. Preserve original database errors. Text and browse make no taxonomy database/embedding call. Inject the reader through `runtime/prisma.ts` and `service-ports.ts`; do not import a sibling source tree or query from the agent.

Require the verified category ID to have the canonical `gid://shopify/TaxonomyCategory/` prefix; use only its verified ASCII alphanumeric/hyphen suffix as the `category_id` token. Woo IDs use the existing positive decimal parser (`^[1-9][0-9]{0,14}$`, safe integer) and stay shop-scoped. No reference-to-native mapping is inferred.

### 3. Fixed Shopify query paths and exact continuation

Keep API `2026-07` and `inspectShopifyReadQuery` unchanged. Use literal connection bounds, fixed sort `ID`, `reverse: false`, and trusted GraphQL documents. `SEARCH_DOCUMENT` becomes `CommerceSearchProducts($query: String!, $after: String)` with `productVariants(first: 20, after: $after, query: $query, sortKey: ID, reverse: false)`. Remove `$first` and the `first` variable. Add parent `status` to the existing `productFields` constant and the private search/exact-get source parsers, so `GET_PRODUCT_DOCUMENT` and `GET_VARIANT_DOCUMENT` also observe it. Their operation names, arguments and first-variant selection remain unchanged. This adds a private provider fact, not a public product field or a changed exact-get definition.

For text, escape backslash and double quote in the trimmed customer text and enclose it as one quoted Shopify search term. The exact filter is `product_status:ACTIVE AND <quoted-text>`. Do not interpolate raw search grammar. For browse, use exactly `product_status:ACTIVE`. Evaluate availability, maximum price and currency locally from observed fields; remove the current guessed `variants.price`/`available_for_sale` filter construction instead of relying on undocumented filter keys. Every text/category/browse candidate and exact-get product additionally requires observed parent `status === ACTIVE` and an actual non-null storefront URL passing existing current-shop/verified-primary-domain HTTPS rules. The provider filter does not replace that local check. Do not synthesize a URL from `handle`.

The private status parser recognizes `ACTIVE`, `DRAFT`, `ARCHIVED` and `UNLISTED`. A known non-ACTIVE product is ineligible: consume/exclude it in search, or return the existing `{product:null}` result from exact get. A null or unsafe storefront URL has the same nonqualifying outcome. Missing, null, wrong-type or unknown status, or a missing/wrong-type queried URL field, is malformed provider data: outer `UNAVAILABLE`, retryable false, retaining original safe validation diagnostics. Do not convert a malformed required qualifier into an empty catalogue. `availableOnly:false` cannot bypass these publication rules. Shopify `available` continues to use its native `availableForSale` value after publication qualification.

Add `CATEGORY_SEARCH_DOCUMENT` with this exact selection (reuse the updated `productFields` constant for identical fields when assembling the trusted string); no fragments or caller-provided selections:

```graphql
query CommerceSearchProductsByCategory($query: String!, $after: String, $variantAfter: String) {
  shop { currencyCode primaryDomain { url } }
  products(first: 1, after: $after, query: $query, sortKey: ID, reverse: false) {
    edges {
      cursor
      node {
        id title handle vendor productType onlineStoreUrl status
        category { id name }
        collections(first: 20) { nodes { id } }
        featuredImage { url }
        variants(first: 20, after: $variantAfter, sortKey: ID, reverse: false) {
          edges { cursor node { id price compareAtPrice availableForSale } }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
```

Its trusted search string is `status:active AND category_id:<verified-short-token>`, followed by ` AND <quoted-text>` only when a query was supplied. Verify the returned `Product.category.id` equals the requested canonical GID and apply the same ACTIVE/URL qualification as other product reads. A different assigned category is consumed and excluded; it is not an automatic descendant match.

Freeze category progress as `{productAfter, currentProductId, variantAfter}`. Start with three nulls. While a product has unconsumed variants, keep `productAfter` at the cursor **before** that product, retain its observed ID, and advance `variantAfter` only to the last consumed edge. The repeated `products(first: 1)` query must return that same retained product ID; a missing/replaced parent is retryable outer `UNAVAILABLE` with diagnostic `MCP_PRODUCT_CURSOR_STALE`, not exhaustion. Once all its variants are consumed, advance `productAfter` to that product edge and clear the other two fields. If no more parent exists, cursor is null. This uses one provider request per step and never requires storing product/variant arrays inside a cursor.

Across both Shopify branches, retain `MAX_SEARCH_VARIANTS = 20` and `MAX_SEARCH_PAGES = 3`; at most three GraphQL reads occur in an invocation, even for a filtered/empty page. A caller limit below 20 stops **before** consuming unprocessed edges. Every scanned excluded edge advances progress. `hasNextPage: true` without a usable advancing cursor, oversized connection output or a malformed identity is outer `UNAVAILABLE`; never translate it into exhaustion. Existing per-call execution policy may impose a lower request/deadline limit and remains authoritative. The public result is `{products, cursor, truncated: cursor !== null}`.

### 4. Exact Woo requests, visibility and resumable scans

Add only these fields to the private `WooCommerceProductReadRequest` list branches:

```typescript
// Existing page/perPage/search/productId fields remain.
products.list: categoryId?: number; catalogueBrowse?: true;
products.variations.list: catalogueBrowse?: true;
```

Apply the identical allowed-key/value checks in `validWooProductRead`, `approvedRequest` and `validRequest`. `categoryId` is a positive safe native integer. `catalogueBrowse` is either absent or literal true; browse prohibits search/category on `products.list`. Unknown keys fail before transport. Exact retrieval branches do not gain these fields.

In `pathFor`, add `category=<id>` for category reads. For all product/variation list branches set fixed `orderby=id&order=asc&status=publish`; browse omits `search`. Add `status,catalog_visibility,purchasable` to ordinary product list **and exact** `_fields`, and `status,purchasable` to ordinary variation list **and exact** `_fields`; preserve the existing identity, prices, stock, category, image, permalink and variation fields. Do not add `include_children`, caller-selected status/visibility, arbitrary query parameters or raw URLs. These are private projection/qualification changes; public product shapes and exact-get definition/operation versions remain unchanged. MCP-003's later explicit SHIPPING projection remains separate and does not acquire product-recommendation visibility restrictions.

For a category request, inspect the **full returned** categories array before the bounded public projection: a product matches only when one observed native ID equals the requested ID. A child-only membership does not match. Apply this publication table before mapping a simple product or making a variation read; do not rely only on the provider list filter:

| Product-read branch | Required observed parent fields | Required selected variation field |
| --- | --- | --- |
| Text/category search and exact get | `status: publish`; `catalog_visibility: visible|catalog|search` | `status: publish` |
| Browse | `status: publish`; `catalog_visibility: visible|catalog` | `status: publish` |

Known nonpublished status (`draft`, `pending`, `private`, `future` or `trash`) or `catalog_visibility: hidden` is ineligible in every product-read branch. Search-only visibility is ineligible only for browse. Consume/exclude a known ineligible search entry; return the existing `{product:null}` shape for exact get. Required status must be one of `publish,draft,pending,private,future,trash`; parent visibility must be one of `visible,catalog,search,hidden`. A missing/null/wrong-type/unknown required qualifier is malformed provider data: outer `UNAVAILABLE`, retryable false, with original safe validation diagnostics, not successful empty data. Validate required parent qualifiers before any variation read; validate each selected variation status before accepting that variation. `availableOnly:false` never relaxes publication or visibility. Keep the current safe-permalink projection and Background's separate requirement for a non-null safe recommendation URL.

For `available`, inspect only the selected simple-product or variation payload, never a variable parent's `purchasable` value. The supplied `purchasable` field may be boolean, null or absent; any other non-null type is malformed and follows the same hard path above. After that validation, use this ordered truth table; do not infer buyability from stock alone or infer backorder availability:

| Selected source facts | Public available |
| --- | --- |
| `purchasable === false` or `stock_status === "outofstock"` | false |
| Otherwise, `purchasable === true` and `stock_status === "instock"` | true |
| Otherwise, including missing/null purchasable or unrecognized/unknown/backorder stock | null |

Apply availableOnly and price filtering after publication qualification and this mapping. A variable parent's false/null purchasable flag must not suppress its independently observed published variations.

For every `type: variable` parent, use its verified parent-scoped variation list; do not depend on the incidental `variations` ID array being populated and do not emit the parent as a simple purchasable variant. Native variation `parent_id` is optional: when absent, the authenticated `/products/{verifiedProductId}/variations` endpoint establishes parent authority; when present, validate it with the native ID parser and require equality. List/exact variation IDs must be valid, and an exact read must equal the requested variation ID. Malformed/conflicting relationship evidence is an outer error for search; exact get retains its existing `{product: null}` missing/mismatch outcome. Never coerce `"1e2"`, blank or an unsafe number into an ID.

Keep product/variation page size 20, at most three newly fetched product pages and at most twelve total Woo provider reads per invocation, subject to the existing lower execution-policy ceiling. Freeze progress as the existing product page/index and variation page/index, plus retained parent ID and hashes of the ordered IDs on partially consumed pages. When a resumed page is re-read, changed page identities are `MCP_PRODUCT_CURSOR_STALE` / retryable outer `UNAVAILABLE`; do not silently skip/repeat records after a shifted catalogue. Advance a scanned index before filtering, so a bad or unpublished entry cannot trap the cursor. When the output limit/budget is reached, retain the exact next unconsumed position. Reset variation progress only after its parent is finished. A provider claim of more data beyond the existing maximum page 1000 is outer `UNAVAILABLE` with `MCP_PRODUCT_SEARCH_PAGE_LIMIT`, not false exhaustion or an unusable page-1001 cursor. Live catalogue changes do not create a snapshot/exhaustiveness guarantee.

### 5. Cursor identity, prices and exact-product preservation

Use existing HMAC-SHA256 mechanics and `COMMERCE_CURSOR_SECRET`, minimum 32 characters; no new secret or storage. The version-2 payload is strict `{version: 2, bindingHash, expiresAt, progress}`. `bindingHash` is SHA-256 of Shared `canonicalJson` over trusted environment, shop ID, provider, connection identity, branch, normalized query/category, verified taxonomy generation/version where applicable, browse, fixed order/visibility version, maximumPrice, availableOnly, limit, established market and currency. Pin the private visibility-rule identity to `PUBLIC_PRODUCTS_V1`, covering sections 3–4's all-path publication and selected-source purchasability rules; it is not a public product field. TTL stays 60,000 ms. Validate signature before parsing bounded progress, and reject all old-version/tampered/expired/cross-shop/cross-connection/cross-mode/filter-drift cursors as `INVALID_INPUT`. Excluded publication/visibility/availability records still advance the same consumed-edge/index state; continuation never changes the branch or weakens its qualification. The final encoded cursor must fit Shared's **2048-character** bound; an oversized provider cursor is a hard result failure, never truncation or a dropped continuation.

Expose required readonly `sourceIdentity: string` only on the private resolved connection. Construct it with Shared `canonicalJson`: Shopify `{platform: "SHOPIFY", shopDomain}` using the verified canonical domain; Woo `{platform: "WOOCOMMERCE", installationId, credentialVersion, canonicalSiteUrl}` using the verified existing installation (nonempty ID, positive safe-integer version and canonical origin). Read Woo values in the existing shop projections in `connections/prisma-reader.ts` and `capabilities/prisma-reader.ts`; do not add a query or put this identity in public product data. Reinstallation/credential-version changes therefore cannot reuse a prior connection's continuation.

Preserve observed native IDs, native sale evidence and safe URLs. `availableOnly: true` accepts only `available === true`; false does not relax any publication rule or browse's stricter visibility. Numeric maximum-price comparison uses the existing decimal/BigInt logic only when price and its currency are known and compatible with any trusted price context; unknown/mismatched context cannot pass that filter. Shopify `shop.currencyCode` establishes base currency, not customer-market pricing. Woo runtime currency remains null unless its existing trusted provider/store context actually establishes denomination; do not copy recovery currency, locale or model text. A non-null unsupported market context remains unable to certify matching prices. No new currency or price-context public field is added.

Keep product get/search output schemas and the immutable `commerce_get_product` definition unchanged. Its operation stays `products.get` version `1.0.0`; only the private source projection and result qualification above change. In particular, existing Shopify exact get with variantId null returns the observed first variant when its parent qualifies; this task does not redefine that selection behavior. Background must select/confirm an observed native Shopify variant, and must not treat a null selection as authorization for the first variant. Woo simple products retain null variant IDs. Every exact refresh reapplies current publication qualification and the source availability mapping; an initially public product that became unpublished/unlisted/hidden cannot retain its old recommendation evidence. Shipping's product-only `VARIANT_REQUIRED` belongs solely to MCP-003.

### 6. Generic shop discovery, with no workflow context

Keep `parseMcpRequestContext` and the existing private-ingress trust boundary unchanged: authenticated outer shopId and server environment determine tenant scope. For product/shipping/discount discovery and these catalogue calls, an absent toolContext and any otherwise valid opaque object have identical semantics. Do not parse `CommerceConversationToolContextSchema`, discriminate a purpose, or use nested shop/turn/grant fields as authority. Keep existing opaque forwarding to unrelated registered adapters unchanged.

Remove `discountPolicy` from `ShopCapabilityRecords` and remove the `shopSettings`, `shopRecoveryPolicyOverride` and selection-only `shopifyDiscount` delegates/queries from `PrismaShopCapabilityTransaction`. Do not add conversation, retained-grant, checkout or outreach-attempt delegates. The successful generic capability read keeps exactly five top-level Prisma delegate calls in its existing RepeatableRead transaction, with the existing relation-loading behavior:

| Delegate call | Exact retained projection |
| --- | --- |
| `shop.findUnique` | `where: {id: context.shopId}`; `select: {id:true,domain:true,status:true,platform:true,wooCommerceInstallation:{select:{id:true,shopId:true,status:true,canonicalSiteUrl:true,credentialVersion:true}}}`. These Woo fields also supply the private cursor identity in section 5. |
| `commerceReleasePointer.findUnique` | `where: {environment: databaseEnvironment(context.environment)}`; `select: {releaseId:true}`. |
| `commerceRelease.findUnique` | `where: {id: pointer.releaseId}`; retain the existing `releaseInclude`, including MCP-001's accepted required-feature fields. |
| `subscription.findUnique` | `where: {shopId: context.shopId}`; `select: {status:true,plan:{select:{active:true,features:{where:{featureId:{in:featureIds}},select:{featureId:true,enabled:true}}}}}`. `featureIds` is the distinct release feature-ID set as before. |
| `shopFeaturePreference.findMany` | `where: {shopId: context.shopId,featureId:{in:featureIds}}`; `select: {featureId:true,enabled:true}`. |

The shop/pointer reads can retain their existing parallel execution; release and entitlement reads keep their existing dependency order. Missing or malformed shop/release/plan data keeps the existing typed outcome. This reader makes zero discount settings/override/catalogue queries and zero workflow-state queries. `createMcpService` already resolves a fresh snapshot for every RPC, including each tools/call; do not add a second generic capability read solely for a built-in call. Keep `runtime/execution-registry.ts`'s existing shop/environment reader context for published calls.

Use these exact private DTO/export changes:

```typescript
// src/mcp/ports.ts — type imported from installed Shared
export type McpSystemTool = CommerceBuiltInToolDescriptor;

// src/execution/discount-tools.ts — pure projection, no database/context argument
export function projectShopDiscountTools(records: ShopCapabilityRecords): McpSystemTool[];
```

`resolveShopCapabilities` first applies its existing `requireActiveShop` and published-release checks. The pure projection returns both installed `commerceDiscountBuiltInDescriptors` when subscription status is ACTIVE or TRIALING and `subscription.plan.active === true`; otherwise it returns `[]`. It uses no merchant offer mode, selection, optional preference, purpose or workflow state. The same active Free/paid plan rule applies to Shopify and Woo. The already present catalogue reader must remain wired through the existing production `executeDiscountTool` port; a missing port is a hard configuration failure, never permission to fabricate successful empty data.

### 7. Canonical provider identities and current catalogue semantics

Use Shared `commerceDiscountBuiltInDescriptors`, `isTrustedCommerceBuiltInDescriptor`, `deduplicateTools` and `isBuiltInTool`. `commerceBuiltInToolContractPayload` no longer exists. `McpSystemTool` contains only the canonical no-hash descriptor; remove its old mode/allowedDiscountIds listing fields. Tests compare the strict canonical descriptor fields and built-in grant projection by `name/toolName + definitionVersion`, not a generated-schema digest. Keep the existing `resolveDiscountAuthorizationPolicy` helper for the accepted executor's current shop configuration; it is not a conversation grant reader.

Extend `projectCommerceManifest(release, selected, positions, builtInTools = [])` with `builtInTools: readonly CommerceBuiltInToolDescriptor[]`. `resolveShopCapabilities` computes the pure shop-plan descriptor set once, supplies it to the manifest and exposes that same set as systemTools. Build `grantedTools` with Shared `deduplicateTools(capabilities, builtInTools)` and validate the actual Shared manifest. Remove `runtime/service-ports.ts`'s separate `projectInitialOutreachDiscountTools` call so list/resource projection cannot diverge. Feature snapshots, response hash, release identity, selected published capabilities and their provenance remain unchanged.

In `validateSnapshot`, require exact canonical name/version/description/input-schema correspondence between systemTools and manifest.builtInTools. Reject duplicate names, collisions with published advertised/underlying names, unknown descriptors and a combined advertised list above 32; do not silently remove a descriptor to fit. Remove the mode-based snapshot rejection. Every eligible shop sees the same pair before/after NONE/FIXED/AI changes, independently of opaque caller context. `grantedTools` in this provider manifest describes its advertised capability union; Background owns any persisted workflow grant and model availability check. MCP never reads or mutates that workflow grant.

In `src/mcp/registration.ts`, retain the existing `CommerceToolInputs` parsing before execution and remove `isInitialOutreachDiscountCallAllowed`. In `src/execution/discount-catalogue.ts:execute`, remove the `CommerceOutreachToolContextSchema` import/check and `MCP_DISCOUNT_PURPOSE_FORBIDDEN` branch. The existing reader continues to recheck the authenticated shop, current settings, active override and current FIXED selection. Neither layer interprets a caller purpose or conversation identifier.

#### 7.1 Reuse the existing bounded call mechanism

The uploaded built-in branch has no per-call wrapper. In the existing `src/mcp/execution.ts`, extract its current policy selection, combined request/SDK abort controller, timer, provider budget, promise race, final deadline check, result-schema parse and result-byte bound into one private helper. Keep this helper in that file; do not create another execution framework, generic logger, policy reader or provider registry. Use these exact private signatures:

```typescript
type BoundedToolCall = Pick<CapabilityInvocation, "deadlineAt" | "signal" | "budget">;

async function executeBoundedToolCall(
  ports: McpServicePorts,
  context: McpRequestContext,
  requestSignal: AbortSignal,
  sdkSignal: AbortSignal,
  selectedPolicy: McpExecutionPolicy | undefined,
  invoke: (call: BoundedToolCall) => Promise<CommerceToolResult>,
): Promise<CommerceToolResult>;

export async function executeDiscountTool(
  ports: McpServicePorts,
  context: McpRequestContext,
  name: DiscountSystemToolName,
  args: Record<string, unknown>,
  requestSignal: AbortSignal,
  sdkSignal: AbortSignal,
  selectedPolicy?: McpExecutionPolicy,
): Promise<CommerceToolResult>;
```

`executePublishedTool` retains its exported signature and existing invocation/diagnostic/operational-reporting behavior; its callback constructs the same `CapabilityInvocation` with the helper's deadline, signal and budget. `executeDiscountTool` invokes only the existing discount port with `{context, name, arguments: args, signal, deadlineAt}`. It creates no published capability/tool/revision identity and makes no provider request. Keep the existing policy-failure handling inside the shared mechanism: selected policy is reused without another database read; an absent/unreadable policy follows `recordPolicyFailure` and returns the same hard result without invoking the callback. Both paths use the same selected `toolDeadlineMs`/`maxResponseBytes`, clean up timers/listeners, observe a late rejection and discard a result after deadline/cancellation. Preserve `service.ts:boundedResponse` as the independent HTTP envelope bound.

Add required `signal: AbortSignal` and `deadlineAt: number` fields to the existing `McpServicePorts.executeDiscountTool` input and `DiscountSystemToolCall` interface. Preserve its existing context/name/arguments/logger fields and factory signature. The existing `runtime/service-ports.ts` spread forwards these fields and adds its logger. Replace registration's direct optional-port call with `executeDiscountTool(ports, context, systemTool.name, args, request.signal, extra.signal, policy)`. A missing port returns outer UNAVAILABLE/retryable true; it must not become successful unavailable catalogue data. Wrapper exceptions retain the actual error/cause in the existing Shared logger with the real tool name. Do not call published-capability operational reporting with invented IDs, and do not log a resolved reader ERROR twice.

Inside the reader, check the supplied abort/deadline before starting the transaction, before/after every awaited query group, before each next catalogue batch and before returning. An expired/aborted call throws the existing typed DEADLINE/409/retryable true with `MCP_TOOL_CALL_CANCELLED`; it never becomes optional data. Keep the existing production clock defaults: wrapper `ports.now ?? Date.now` and reader factory `options.now ?? Date.now`. Deterministic fixtures supply the same clock function through both existing seams; do not add a transported/model clock or another runtime clock dependency. Extend the private transaction option type with `timeout: number` and `maxWait: number`; after the initial deadline check calculate `remainingMs = Math.max(1, Math.ceil(call.deadlineAt - now()))` and call the same RepeatableRead transaction with `timeout: remainingMs` and `maxWait: Math.min(2000, remainingMs)`. Do not add a global Prisma setting, another client, retry or query. The wrapper still bounds the public response if an already-started database operation settles late; that completion cannot start another batch or expose data.

#### 7.2 Exact current-shop catalogue branches

Move the options `limit`/`cursor` shape check before its mode-specific early return, using the values already parsed by registration. For NONE, reject every non-null cursor as `MCP_DISCOUNT_CURSOR_INVALID` before returning empty options: this mode never issues a continuation token. NONE details is a hard FORBIDDEN mapped to outer DENIED. For FIXED details, reject an offerId outside `policy.allowedDiscountIds` before a detail query, with the same outer DENIED result. Use `MCP_DISCOUNT_NOT_AUTHORIZED` as that private denial reason. A permitted detail lookup uses `shopifyDiscount.findUnique({where:{id:offerId,shopId:call.context.shopId}})` and retains the existing post-read shop check and `rowIsCurrent` filter. Only a permitted absent/non-current record returns `{details:null}`. These replace the uploaded reader's NONE/details-null shortcuts; they do not introduce conversation permission.

| Current authorized shop state / request | Exact catalogue behavior for every caller |
| --- | --- |
| NONE; options with initial cursor null | `OK` data `{mode:"NONE",offers:[],cursor:null,truncated:false}`. This is an observed configured mode, not a default for a failed configuration read. No catalogue scan is needed. |
| FIXED; options | Existing bounded page over current permitted selected IDs or the active exact-ID override, with `mode:"FIXED"`. |
| AI_BEST_APPLICABLE; options | Existing bounded provider-current catalogue page independently of selection checkboxes, with the actual configured mode. |
| NONE; details, or FIXED details outside the current permitted set | Outer `ERROR`, `code:"DENIED"`, `retryable:false`. No facts escape the configured scope. |
| Authorized details ID has no qualifying same-shop record | Existing `OK` data `{details:null}`. Wrong-shop IDs never expose another shop's record. |
| Authorized record exists | Existing exact offer/condition projection; unsupported or missing source observations stay PARTIAL/UNKNOWN. |
| Invalid/expired/tampered/cross-shop/cross-mode cursor | Existing typed invalid-input rejection. A cursor from a prior mode is not accepted by the NONE branch. |
| Missing/malformed/unavailable shop configuration or failed shop/provider authorization | Existing hard outer error; never fabricate NONE, empty offers or optional absence. |

Preserve the accepted catalogue keyset algorithm, shop/mode/FIXED-policy/generation binding, expiry, actual page boundaries and generation-change error. Current provider status, dates and unavailability remain data filters; no provider HTTP, basket/applicability evaluator or new options-filter argument is added. Both structuredContent and text serialize the same validated result; isError is true exactly for outer ERROR. NONE's successful empty options result does not cause Background to call it: the host owns whether a tool should run.

### 8. Generic unavailable-data outcome and original failures

Keep the accepted shop-scoped PostgreSQL snapshot reader, exact offer identity and completeness mapping. Normal options/details outputs, native target IDs, threshold currency, Woo zero threshold/quota rules, exclusions, usage/customer/sale restrictions and combination uncertainty remain unchanged. `details:null` is distinct from an unavailable read.

After shop/configuration/scope checks succeed, a **catalogue data-read** failure from a genuine Prisma error/cause carrying `P1001`, `P1002`, `P1008`, `P1017` or `P2024` becomes `OK` data `{outcome:"UNAVAILABLE",reasonCode:"TEMPORARY_UNAVAILABLE"}`. Apply exactly the same classification to every caller. Do not inspect purpose, conversation state, prompt or workflow to select an error path. The caller decides whether this unavailable information permits its workflow to continue.

Make the query boundary explicit inside the existing reader. `currentPolicy` retains `shop.findUnique`, `shopSettings.findUnique`, `shopRecoveryPolicyOverride.findUnique` and any FIXED-selection `shopifyDiscount.findMany`; all four are authorization/configuration reads and their failures remain hard. Remove only `shopifyDiscountCatalogue.findUnique` from its existing `Promise.all` and return `{platform, policy}`. For permitted non-NONE options, read `{syncGeneration:true}` from `shopifyDiscountCatalogue` after `currentPolicy` succeeds, then retain the existing generation/fingerprint/cursor and bounded batch algorithm. NONE initial options and details do not need this generation query. The optional-data classification applies only to that options-generation read, the options page's `shopifyDiscount.findMany`, and the permitted same-shop details `shopifyDiscount.findUnique`.

At those three query boundaries only, wrap a qualifying original exception in one private `CatalogueDataReadFailure` in `discount-catalogue.ts`, retaining it as `cause`, store that marker in a call-local variable and throw it out of the transaction. Every other exception propagates unchanged. Handle the marker only when the transaction rejection is that exact marker object, after rollback and after checking the RPC abort/deadline again: log the original sanitized cause through `call.logger.error` using `mcp.discount.catalogue.unavailable`, then validate/return the canonical successful unavailable-data result. Transaction-start/commit/rollback failures are not that marker; if transaction cleanup rejects with a different error, retain that actual hard error and the saved original cause in diagnostics. Do not catch a failed statement and continue querying inside its transaction, classify the whole transaction catch, or convert the existing `MCP_DISCOUNT_DATABASE_READ_FAILED` wrapper merely because its outer code is UNAVAILABLE.

Authorization/configuration reads, P1000, missing tables/columns, invalid SQL, result parsing, cursor/generation conflicts, unexpected errors and aborted/expired RPC execution remain hard outer errors. Classify at the owning catalogue query boundary, not from error prose or merely an outer UNAVAILABLE code. No catch-to-empty-offers, fabricated mode or broad retry loop is permitted.

BACKGROUND-001 owns the initial-outreach compatibility adaptation: its existing selector treats this exact unavailable-data branch as its existing mandatory-read failure before graph projection, while conversational recommendations can omit a promotion. MCP has one result contract and one error path for both. Preserve current NONE/FIXED/AI and initial-outreach mode-mismatch/selection regressions; only their former purpose-exclusive discovery expectation changes.

Use the accepted Shared structured logger boundary. Preserve the original sanitized Prisma/SDK/provider error and cause, safe provider status/request ID and separate Moda reason. Do not invent a provider error for a DB-only catalogue read, expose raw failures in tool output or build another generic redactor/logger. Provider adapters remain responsible for their own source diagnostics.

## Work Items

- [ ] After DATABASE-002 + SHARED-006 acceptance and normal reclaim, consume exact Shared 5.0.0 and the accepted Database descendant; preserve MCP's direct Zod version and verify the no-hash built-in/public-export contract plus real schema composition.
- [ ] Verify the prepared MCP-001 source/artifacts once against the current supplied catalogue/diagnostic composition; report only an actual new mismatch.
- [ ] Implement the exact input/category reader, literal Shopify documents, three search branches and version-2 cursor.
- [ ] Update all three Woo guards/projections, all-path publication qualification, selected-source purchasable/stock mapping and optional parent-ID validation; preserve transport and public product contracts.
- [ ] Remove purpose/policy discovery coupling; retain the five generic capability reads and exact canonical descriptor DTO/projection.
- [ ] Advertise both canonical built-ins for eligible shops; remove both purpose gates, reuse the bounded call mechanism and implement the exact current-shop catalogue/error branches.
- [ ] Run agent-owned checks, prepare the exact required developer database run, complete the report and submit for review.

## Interfaces / Contracts

Shared 5.0.0 after accepted SHARED-006 and `docs/architecture/ARCH-058/contracts.md` sections 2.2–4.1 own the public interfaces. ARCH-058 imposes no MCP Zod pin. The private fields and algorithms above are now selected implementation decisions, not alternatives for the agent to redesign. Shopify's [pinned products filter](https://shopify.dev/docs/api/admin-graphql/2026-07/queries/products) uses `category_id` with a short taxonomy token; [Product variants](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Product) supports bounded after/first/sortKey traversal and identifies online-store publication through onlineStoreUrl. Shopify's [unlisted-product guidance](https://shopify.dev/docs/apps/build/product-merchandising/unlisted-products) explains why a direct URL and stock alone do not authorize product discovery. Use section 1's exact prepared schema artifact and installer, not a new schema/version download. [Woo products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/) and [variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/) define the native list/exact response shapes and distinguish publication, visibility, purchasable and stock. Native payload fields are data, not new execution permission.

## Dependencies

- `ARCH-058-MCP-001`: Complete at Attempt 3; preserve accepted resolver and required-feature eligibility.
- `ARCH-058-DATABASE-002`: accepted forward migration removing persisted built-in `contractHash` while preserving grant integrity.
- `ARCH-058-SHARED-006`: accepted immutable Shared 5.0.0 publication containing SHARED-003/004/005. These dependencies gate returning this same task to Ready; they do not authorize resetting or recreating its WIP.

The ARCH-052 catalogue and Woo diagnostic source/composition described in section 1 are present in this upload and must remain in the accepted MCP-001 base. Preserve those completed implementations; do not reopen them or repeat integration. No upstream task depends on terminal system testing.

## Enables

- `ARCH-058-MCP-003`: separate shipping operation on the accepted provider/authorization composition.
- `ARCH-058-COMMERCE-001`: publication after its other declared dependencies complete.
- `ARCH-058-BACKGROUND-001`: grounded conversation product/discount use.
- `ARCH-058-SYSTEM-TEST-001`: real service-boundary validation after all prerequisites.

## Acceptance Criteria

- [ ] Shared 5.0.0 matches the SHARED-006 receipt; MCP's direct Zod dependency was not changed by ARCH-058; canonical built-ins/grants contain no `contractHash`, the removed payload/context exports are absent, and real consumer schema composition typechecks.
- [ ] The actual provider/document guard accepts text/category/browse requests; guards and versioned public outputs remain intact.
- [ ] Exact membership, all-path publication qualification and selected-source stock/purchasability/currency rules produce only qualified current-shop facts; invalid input causes zero provider I/O. Known ineligible exact reads return product null; malformed required qualifiers stay hard errors.
- [ ] A product with 45 variants, caller limit 2, filtered middle pages and an empty unfinished page resumes without dropped/repeated records under static fixtures, within 3 Shopify/12 Woo request ceilings.
- [ ] Old/tampered/cross-shop/cross-connection/filter-drift cursors are rejected; a shifted Woo page or retained Shopify parent is explicitly stale, not exhausted.
- [ ] Generic discovery has exactly the specified five delegate calls and no discount/workflow-state reads; irrelevant opaque context cannot change tenant, tool-list or catalogue data scope.
- [ ] Built-in list/resource projection matches canonical Shared identities and stays stable after current mode changes; calls still use the current configured mode/selection and active shop/plan.
- [ ] Catalogue outputs preserve accepted facts and no-provider-call behavior; NONE/nonpermitted FIXED details deny before lookup, permitted absence stays null, and NONE never accepts a non-null cursor.
- [ ] Built-in calls use the same policy/deadline/cancellation/result-byte mechanism as published calls; abort/expiry/missing executor/oversized data remain hard, no extra policy/capability read or provider request is introduced, and no late database completion exposes data or starts another batch.
- [ ] Only the three specified post-authorization catalogue query boundaries produce the successful unavailable branch after rollback, identically for every caller; authorization, transaction-boundary and unexpected failures remain hard.
- [ ] Original failures remain in redacted Shared logs and not in model/customer data. Required fast checks and the separately owned database evidence are accurately reported.

## Validation

Use the launcher-provided implementation worktree/preparation evidence. Before the first Node command use `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. No source download, deployment URL or persistent database is needed.

The reported 69/71 product group and 72/73 generic group are intermediate evidence, not accepted results. Rerun these existing focused groups after alignment, complete the unfinished fixtures/integration scenario and execute the required typecheck, integration typecheck, lint and build below. The previously corrected but unrerun product failures still require evidence. Preserve the developer-owned Docker execution boundary.

**Agent-owned focused checks.** Add `tests/unit/execution/policy/{product-search-composition,product-search-cursor}.test.ts` and `tests/unit/execution/reference-taxonomy/category-membership.test.ts`; extend the existing generic capability/discount/protocol tests listed in these commands:

```bash
npm exec -- tsx --test tests/unit/execution/policy/shopify-core.test.ts tests/unit/execution/policy/product-search-composition.test.ts tests/unit/execution/policy/product-search-cursor.test.ts tests/unit/execution/reference-taxonomy/category-membership.test.ts tests/unit/connections/shopify/provider.test.ts tests/unit/connections/prisma-reader.test.ts tests/unit/connections/resolver.test.ts tests/unit/connections/woocommerce/direct-product-reader.test.ts tests/unit/connections/woocommerce/provider.test.ts
npm exec -- tsx --test tests/unit/execution/discount-tools.test.ts tests/unit/execution/discount-catalogue.test.ts tests/unit/capabilities/manifest.test.ts tests/unit/capabilities/prisma-reader.test.ts tests/unit/mcp/capability-invocation.test.ts tests/unit/mcp/execution-policy.test.ts tests/unit/mcp/resources.test.ts tests/unit/mcp/structured-results.test.ts tests/unit/runtime/ports.test.ts tests/unit/runtime/prisma.test.ts tests/unit/runtime/service-ports.test.ts
npm run typecheck
npm run typecheck:integration
npm run lint
npm run build
git diff --check
```

`product-search-composition.test.ts` must invoke the registered policy executor through the real connection resolver, provider and document guard with injected HTTP/session fixtures. Include query-grammar injection strings, literal query bounds, exact category plus query, default/mixed browse rejection, zero/unknown currency, category mismatch beyond the first 20 category entries, optional/mismatching parent_id, variable parent with an empty variation-ID list, mid-page limits, exhausted/unfinished empty pages and all bounded cursor states. Assert exact fixed provider query strings and ordinary `_fields`, no extra API calls or forbidden request keys. Validate the actual assembled search/category/exact GraphQL documents against the prepared pinned schema and the unchanged document guard. Existing query names/arguments, literal bounds and exact-get public definition/output contract remain unchanged; update real guard/session fixtures for the added private status selection rather than bypassing them.

Across **text, category, browse and exact get**, include in-stock Shopify DRAFT/ARCHIVED/UNLISTED products with plausible safe links and Woo nonpublished/hidden parents or unpublished variants. They must be excluded or product null even with availableOnly false. Shopify ACTIVE with null/foreign URL is also excluded; missing/unknown/wrong-type required qualifier is a hard malformed result. Woo search-only visibility succeeds in explicit text/category/exact reads but is excluded from browse. Cover the complete purchasable/stock table, missing/null/invalid purchasable, and a variable parent with purchasable false whose separately published purchasable variation remains eligible. Assert parent ineligibility avoids a variation request, all excluded scan positions advance, filters/visibility identity/cross-mode cursor replay cannot weaken qualification, and a newly unpublished/unlisted/hidden product yields null on the final exact read after an earlier successful discovery. Preserve ordinary URL normalization and native price/sale evidence. These tests use provider response fixtures with the new fields, not a stubbed already-normalized Product. Native shipping facts remain outside these product-result tests.

Update the existing private-connection fixtures in `tests/fixtures/capabilities.ts` and the named connection/runtime tests with the real sourceIdentity inputs and the generic records shape; do not bypass sourceIdentity validation. Capability-reader fixtures expose only the five declared delegates and assert zero settings/override/catalogue reads. They expose no conversation/grant/recovery/attempt delegate; adding one to satisfy a test is a failure of this boundary. Through real `createMcpService` list/resource/call routes and the accepted dispatcher, compare omitted toolContext with opaque outreach/conversation/irrelevant objects, including misleading nested shop/turn/grant fields: the outer authenticated shop alone controls identical listing/data scope. Malformed non-object headers and model-supplied extra arguments still fail the existing structural validators. Cover two shops; ACTIVE/TRIALING versus inactive/missing plans; inactive shops/revoked Woo installations; canonical name/version/list collisions; stable descriptors under NONE→AI and AI→NONE; NONE empty options and denied details; changed FIXED selection/override expiry; valid pagination and cross-mode cursor rejection. Inject each permitted transient failure separately at the generation/page/details query boundary under every opaque context and assert the same unavailable-data result after rollback. Assert settings/override/FIXED-selection/transaction-start/transaction-close/parse failures stay hard, and capture original error causes in the actual Shared sink. Extend `tests/unit/mcp/execution-policy.test.ts` with built-in calls: one selected-policy read, request abort, SDK abort, deadline, oversized output, absent executor, no provider reservation and late resolve/reject. Use injected clocks, abort controllers and deterministic barriers; retain the existing published-call assertions. In reader tests assert the exact private signal/deadline and remaining transaction options, no query before an already expired call, no next batch after cancellation, NONE with non-null cursor rejected, and denied details with zero detail query. Initial-outreach zero-client NONE and hard-unavailable host behavior are Background-owned regressions, not reasons to add an MCP purpose branch. Use actual Shared logger sinks with credential/PII sentinels and original errors.

**Required developer-owned PostgreSQL run.** Add `tests/integration/shop-product-discovery.integration.test.ts` to the existing `scripts/test-postgres.mjs` wildcard harness, using `tests/helpers/disposable-postgres.ts` and the existing fixture helpers. Exercise the category exact join, generic shop/active-plan descriptor projection, two-shop isolation and the accepted current mode/selection catalogue semantics without creating any conversation, workflow grant or recovery attempt. Preserve and run the existing persisted catalogue scenario; update its intentionally changed generic-context, denied-details and private signal/deadline expectations while retaining provider facts, pagination and current-policy coverage. Do not replace it with mocks or another database runner.

```bash
npm run test:integration:docker
```

Ownership is explicit under `docs/agent-validation-execution-policy.md`: the implementation agent runs the fast/typecheck checks above and supplies this command for the developer's disposable run; it does not autonomously launch/wait on the long integration suite without a task-specific override after claim. The harness owns its local database URL and cleanup. Do not substitute an environment DATABASE_URL, `db push`, shared container, or external service. Record worktree/HEAD, database gitlink, exact command, task scenario results, overall exit status and owned-container cleanup. An unavailable/unrun database suite is `NOT_RUN / developer validation required`, never a pass. Submit review with that evidence pending; acceptance requires the actual required scenario results. Report unrelated existing failures separately without claiming the full suite passed.

## Stop Condition

Stop for an actual prepared-source/artifact mismatch against the current observed composition, a contract/schema change outside this ownership, an unregistered provider field/query or a failed authorization invariant. Report the observed path/value and owning prerequisite; do not research a replacement feature or widen permissions. After scoped implementation and fast validation, set status to `review`, record the required developer database handoff/result accurately and return to the architect. Do not mark complete, publish, deploy, mutate a persistent environment or start another task.

## Implementation Notes

This is an extension of the existing composition. Reference categories describe meaning; provider products establish the store's assortment; the existing catalogue reports current shop-configured options and discount conditions. Background owns conversation state, persisted grants, current-turn checks, tool-use decisions, applicability and customer prose. MCP receives no new workflow authority. A bounded page with no match and a continuation is not evidence that the store has no matching product.

## Completion Report

### Current Status — Shared Contract Mismatch

Attempt 1 remains `in_progress`, stopped at the explicit frozen-contract/prepared-artifact gate. The earlier Database mismatch is resolved at the accepted pin. **The implementation is not review-ready or complete.** At the developer's explicit request, the unfinished implementation draft is now committed and pushed as **`4bffa87ed4af0fb40513ad75d38df49c51746360`** (`wip(ARCH-058-MCP-002): preserve product and discount discovery draft`). The earlier authorized Database update remains `229ffe402a3ef36c420cff6a26746b05ca61cd3d`. Publishing this draft does not resolve the Shared blocker or certify completion.

### Developer-Authorized Draft Publication

Committed and pushed all 40 task-owned source/test draft files on the existing implementation `task/ARCH-058-MCP-002` branch. Source commit `4bffa87ed4af0fb40513ad75d38df49c51746360` contains 858 insertions and 637 deletions; it adds the private search cursor, exact category reader and three named unit-test files alongside the existing implementation/fixture changes. No other repository implementation, dependency version, frozen descriptor hash or parent implementation gitlink was included. `git diff --check` and `git diff --cached --check` passed before commit. No test suite was rerun for this publication-only request; the intermediate failures and unfinished validation below remain applicable. Task metadata stays `in_progress`, Attempt 1. No review submission, acceptance, merge or deployment is claimed.

### New Concrete Prerequisite Failure

The task requires verifying canonical built-in hashes against the installed schemas with Node SHA-256. That assertion fails for **both** frozen Shared 4.0.0 discount descriptors. The independent fresh-process calculation uses only installed package exports:

```js
import { createHash } from 'node:crypto';
import {
  commerceDiscountBuiltInDescriptors,
  commerceBuiltInToolContractPayload,
} from '@modainteract/moda-interact-shared/commerce';
for (const descriptor of commerceDiscountBuiltInDescriptors) {
  const observed = createHash('sha256')
    .update(commerceBuiltInToolContractPayload(descriptor)).digest('hex');
  if (observed !== descriptor.contractHash) process.exitCode = 1;
}
```

Observed proof (exit **1**, Node 24.19.0, exact installed/locked Shared 4.0.0, Zod 4.6.5):

```json
{
  "sharedVersion": "4.0.0",
  "node": "v24.19.0",
  "results": [
    {
      "name": "commerce_get_discount_options",
      "definitionVersion": "1.0.0",
      "recorded": "a0a4a88c7920a25a31657a03761b6556419189aeab251261a58e2dfb83a3bdcb",
      "observed": "6371003b0ade970987dabed9603d4efbfa8b653f801956252a86e5a3d7cca2b0",
      "matches": false,
      "trustedByInstalledShared": true
    },
    {
      "name": "commerce_get_discount_details",
      "definitionVersion": "1.0.0",
      "recorded": "776f6bc6ac1800c75744c2ffa7357f07a32be2b61309b1d71abf0493a2de316f",
      "observed": "62c8d17c53d8a99add784e7c9d7a1226aaafb9b297592fee45c0c107ad508d38",
      "matches": false,
      "trustedByInstalledShared": true
    }
  ]
}
```

Shared's installed `isTrustedCommerceBuiltInDescriptor` returns true for these same constants because it compares them with the installed canonical descriptors; that does not resolve their payload hash mismatch. Shared declares Zod `^4.0.0`; this consumer's existing exact Zod 4.6.5 was not changed. The observed mismatch is recorded without asserting whether schema serialization or descriptor constants caused it. Shared package/lock integrity still matches the accepted receipt. No alternative version, replacement hash, modified output schema, dependency downgrade or trust bypass was selected.

**Required owning reconciliation:** `moda_architect` / `moda_shared` must reconcile the frozen descriptor identities with the actual exported contract payloads and supply an accepted consumer artifact/version or explicit architecture decision. This task cannot change Shared constants or remove the mandated hash assertion. The task's Stop Condition explicitly requires stopping for a contract/schema change outside MCP ownership. No new task or dependency state is invented here.

### Resumed Work and Observed Validation

Under the existing codex Attempt 1 claim, continued the local MCP-owned draft with generic canonical built-in projection; the five-delegate capability reader; built-in execution policy/deadline/cancellation/result-size reuse; catalogue query-scoped unavailable classification; provider-specific category/browse/publication/availability/cursor changes; exact taxonomy membership; and relevant fixtures/tests. The accepted source schema artifact and Database pin remain unchanged. These edits remain **unfinished and unvalidated as a complete task**, but are now durably preserved on the remote implementation task branch at the WIP commit above.

- Product-focused group: **71 tests reported, 69 passed, 2 failed**, zero skipped. Log `/tmp/mcp058-002-products.log`. The failures were in connection-projection fixture expectations and a guard test supplying undeclared variables; local corrections were made but the group has not been rerun. No final product-group pass is claimed.
- Generic catalogue/capability/protocol/runtime group (including service tests): **73 tests, 72 passed, 1 failed**, zero skipped. Log `/tmp/mcp058-002-discounts.log`. The sole failure is the required canonical Shared descriptor hash assertion above. Passing cases include all three post-authorization transient data boundaries, every opaque context, genuine Prisma errors, hard authorization/transaction failures, after-rollback diagnostics, NONE/FIXED denials, and built-in cancellation/late-result/size/policy behavior. These are observed intermediate results, not acceptance evidence for the unfinished task.
- Independent installed-package hash proof: **failed, exit 1**, both descriptors; `/tmp/mcp058-002-shared-hash-proof.json`.
- An intermediate typecheck failed on then-unfinished fixture updates, now locally revised; no final typecheck, integration typecheck, lint or build pass is claimed.
- Required new `tests/integration/shop-product-discovery.integration.test.ts` and existing integration fixture updates remain unfinished. Developer-owned `npm run test:integration:docker` remains **NOT RUN**. No Docker, database migration/import, live provider traffic, publication, deployment, customer send or main merge occurred.

### VCS and Ownership Boundary

Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-MCP-002`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-002`; both dedicated `task/ARCH-058-MCP-002`. The attempted `/moda-task --prepare` correctly returned `TASK_NOT_READY` because the durable existing claim was already `in_progress`; no new attempt or claim was created. The user requested resumption and work continued under claim `f4250e2e68a71626b36c456e901077fec656fb96`, Attempt 1. Database remains `ded8f14a60182f6b1443640f012caf0089b8a44c`. No shared checkout, other repository source, task index, architecture document, parent implementation gitlink or Architect Review was edited. Downstream tasks remain gated.

## Prior Dependency Reconciliation Report (historical; Database blocker resolved)

### Current Status — Dependency Reconciled

The developer explicitly authorized updating the submodule after the recorded prerequisite failure. The Database pin is now accepted **`ded8f14a60182f6b1443640f012caf0089b8a44c`**, published in implementation commit **`229ffe402a3ef36c420cff6a26746b05ca61cd3d`** on `task/ARCH-058-MCP-002`. Only the Database gitlink was staged in that commit; the unfinished implementation draft remains local, unstaged and uncommitted.

Verified `aa3fd024db3a1484f72f8033b87f56ad27f4640d` is an ancestor of `ded8f14a60182f6b1443640f012caf0089b8a44c` (exit 0), so this is a forward update preserving the previous revision. The accepted taxonomy migration and both models are present. `npm run prisma:generate` passed with Prisma 6.19.3; a read-only generated-client DMMF assertion confirmed `ReferenceTaxonomyGeneration` and `ReferenceTaxonomyCategory`. No database connection, migration or import was performed. The Database worktree is clean.

**The specific missing-schema preparation blocker is resolved.** The task remains `in_progress` at Attempt 1 because implementation, fixtures and full validation are unfinished. No task-wide typecheck, unit suite, integration suite or acceptance is claimed by this dependency-only update. Continue the existing draft under the same claim; do not treat the earlier missing-schema report below as the current dependency state. Parent implementation gitlinks and Architect Review are unchanged.

## Initial Preparation Mismatch Report (historical; dependency resolved above)

### Status

Attempt 1 stopped on the task's explicit prepared-artifact mismatch condition; **not review-ready and not complete**. Metadata remains `in_progress` with the durable launcher claim. Architect reconciliation is required before implementation can continue. No source implementation commit was published.

### Concrete Prerequisite Failure

The launcher initialized this implementation's recorded Database gitlink at **`aa3fd024db3a1484f72f8033b87f56ad27f4640d`**. The task requires accepted taxonomy Database `ded8f14a60182f6b1443640f012caf0089b8a44c` or an accepted descendant/equivalent that retains its schema and migration. Observed:

- `git -C database merge-base --is-ancestor ded8f14a60182f6b1443640f012caf0089b8a44c HEAD`: **exit 1**.
- `database/prisma/migrations/20261104120000_reference_taxonomy_and_core_product_discovery/migration.sql`: **absent**.
- `database/prisma/schema.prisma`: **both `ReferenceTaxonomyGeneration` and `ReferenceTaxonomyCategory` models absent**.
- `npm run typecheck`: **exit 2**. The already accepted taxonomy store references `TransactionClient.referenceTaxonomyGeneration`, which the generated client from this pin does not contain. Log `/tmp/mcp058-002-typecheck.log`. The unfinished MCP-002 edits also have expected unresolved fixture/interface type errors; they are not claimed as an accepted baseline.

This is a content mismatch as well as an ancestry mismatch, not rejection of a harmless squash/rebase. No Database files/gitlink were changed, no accepted descendant was downgraded and no replacement schema/migration was authored. Section 1 and the Stop Condition require returning this observed mismatch to `moda_architect`, rather than selecting another dependency commit.

**Required owning reconciliation:** provide/record a Database revision preserving the accepted taxonomy schema/migration alongside all later accepted changes, and reconcile the MCP task's Database gitlink through the normal owner workflow. No new public contract is requested. Resume only once that exact dependency is supplied and the preparation failure is resolved.

### Preparation and Draft Work Preserved

Verified the existing `createPrismaDiscountCatalogueReader` -> persisted ports -> service composition -> `executeDiscountTool` chain and accepted Woo `safeException` / `sourceProviderError` diagnostics are present; no catalogue or diagnostic source omission was found.

The package/lock remains exact Shared **4.0.0**, integrity `sha512-Zv78WX/AsN1lZWyaMirO2Ml/rOZknSv0cnJnxYBuyc368kzDZzswauKRPSe8GSXFfjkk3cQnr3wi4n49d9HTzw==`. `npm ci --no-audit --no-fund` completed. The MCP-local Shopify schema artifact was absent; the supplied canonical Commerce artifact at `/Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce/lib/discovery/artifacts/admin-2026-07.json` matched approved SHA256 `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`. The existing `npm run schema:install:shopify -- <that absolute path>` installed it locally, with no download/regeneration or Commerce edit.

An initial implementation draft was underway before typecheck exposed the missing accepted models. Those **unfinished, unvalidated, uncommitted local edits** are preserved only in the isolated implementation worktree. They cover generic capability/built-in projection, bounded built-in call reuse, catalogue query classification, private connection identity/Woo fields, category membership and search/cursor changes. They are not delivered or certified, and tests/fixture integration remain unfinished. New draft files are `src/execution/policy/product-search-cursor.ts` and `src/execution/reference-taxonomy/category-membership.ts`; existing edits are confined to this task's listed capability, connection, execution, MCP and runtime touchpoints. Do not treat the local draft as an accepted implementation or revert others' work.

### Validation and Operational Limits

- PASS: local pinned schema checksum/install and locked dependency installation.
- FAILED: initial `npm run typecheck`, as detailed above.
- NOT RUN: focused unit suites, integration typecheck, lint, build and disposable PostgreSQL suite. No successful task validation is claimed.
- Required later developer-owned command, **not run**: `npm run test:integration:docker` from `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-002`, after code/fixtures and the dependency correction. The existing owned harness must create its own URL and clean up its own resources; no deployment URL substitution. Acceptance still requires actual scenario results and cleanup evidence.
- No taxonomy download/import, persistent database access/migration, live provider request, customer send, publication, deployment or main merge occurred.

### Launcher / Physical Worktree Evidence

Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; newly created parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-MCP-002` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-002`, both `task/ARCH-058-MCP-002`. No other task worktree or shared implementation checkout was used for edits. Parent/implementation remote task fast-forward: not needed; origin/main: already current. Recursive submodule sync/init/update verified ready at the recorded pin above, which subsequently failed the task-specific content/ancestry check.

Dependency gate passed MCP-001 Complete. Parent prepared head `bb7f06ccc391b8d6bf82142abd6bf0478a9e0c56`; claim **`f4250e2e68a71626b36c456e901077fec656fb96`**, pushed, executor codex, Attempt 1 at `2026-11-04T15:08:56Z`. Implementation HEAD remains **`469a00fbbbf1e5fb4499b19c92c158f156786633`** with the local draft described above. Only this task report is committed in the parent; no implementation gitlink/index/architecture/Architect Review change is made. Downstream tasks are not promoted.

## Definition-time Completion Report (historical)


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

Shared 4.0.0 and the accepted Database artifact are already recorded. The prepared MCP-001 base and the explicit accepted-source integration gates above must be present before this task runs.

### Unresolved Issues

The 09:49:47 snapshot lacks the accepted catalogue/dispatcher and Woo diagnostic integration. The common implementation handoff records this specific preparation prerequisite; no replacement implementation is authorized.

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

## Architect Dependency Reconciliation (2026-11-04)

MCP-001 Attempt 3 is accepted and Complete at `1dd5430b9d3108bf93bba86c1fb9233736f606d3`. Its sole prerequisite is satisfied; this task is ready, unclaimed, at Attempt 0. Use normal launcher preparation and accepted-source integration gates. No implementation is started by this promotion.
