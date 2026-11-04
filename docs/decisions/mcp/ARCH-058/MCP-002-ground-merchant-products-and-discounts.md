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

Extend the accepted MCP composition with exact category search, explicit catalogue browse and conversational use of the existing discount catalogue. Implement the concrete changes below; do not create a replacement taxonomy, discount reader, pricing engine, provider proxy or response pipeline.

## Context

This revision is grounded in `moda-interact-workspace(20261104-094947).zip`. Read the common [execution baseline](../../../architecture/ARCH-058/execution-baseline.json) and [implementation handoff](../../../architecture/ARCH-058/implementation-handoff.md). MCP-001 is under development according to the developer; its accepted implementation is the base for this task, not work to repeat here.

The snapshot establishes these implementation gaps:

- `shopify-core.ts:SEARCH_DOCUMENT` uses variable `first: $first`, rejected by `connections/shopify/document.ts`. Its `SearchInput.query` and provider composition are text-only.
- Woo request keys are independently checked in `connections/resolver.ts`, `connections/woocommerce/provider.ts` and `direct-product-reader.ts`; changing only the port type cannot enable a category/browse request.
- Woo list/exact mapping unconditionally requires `parent_id`, although native variation ownership is established by the verified parent endpoint. The search loop also advances some variation indexes only after validation, leaving filtered records able to repeat.
- `runtime/execution-registry.ts:execute` drops `toolContext` when it constructs the fresh capability-reader context. `mcp/snapshot.ts` does not match built-in descriptors to the manifest and rejects every `mode: NONE` tool, including a retained identity whose execution has since been revoked.
- The snapshot lacks the accepted `src/execution/discount-catalogue.ts` and still has the unavailable built-in stub. This is a concrete integration prerequisite, not authority to recreate the accepted catalogue.

## Scope

Only `moda-interact-mcp` source, tests and its task report. Public input/output contracts are the already published Shared **4.0.0**, runner **1.1.0**. Product-search definition is **2.0.0**, operation `products.search` **1.0.0**. Exact product definition/operation remain **1.0.0**. Shipping implementation belongs to MCP-003.

### Exact implementation map

Paths in this table are relative to the MCP implementation worktree. Test fixtures must exercise these implementations, not alternative helpers that reproduce the intended answers.

| Path | Required change |
| --- | --- |
| `src/execution/policy/shopify-core.ts` | Extend `SearchInput`; replace search document/filter composition; add the category document and provider parsers; implement the three bounded search branches below; correct optional Woo `parent_id` handling in search and exact get. Keep basket behavior and public product output unchanged. |
| `src/execution/policy/product-search-cursor.ts` — new | Own only the signed version-2 search cursor, normalized filter fingerprint and strict provider progress parsing described below. Move the existing product-search cursor mechanics here; no other cursor protocol changes. |
| `src/execution/reference-taxonomy/category-membership.ts` — new | Export `createPrismaProductCategoryReader` and the narrow `ProductCategoryReader` port below. Read the already accepted taxonomy tables by exact ID; no embedding/import/source download. |
| `src/execution/policy/shopify-core-executor.ts` | Add `category`/`browse` only to `products.search` mappings; inject the category reader and trusted environment into its adapter. Keep the legacy `shopify.searchProducts` mapping text-only. Preserve actual output-schema validation and rendering. |
| `src/connections/{ports,resolver,prisma-reader}.ts` | Add the exact private list fields and trusted cursor connection identity below; forward fields through the resolver and extend its strict key checks. Select Woo installation `id`/`credentialVersion` alongside the already selected fields; no extra connection query. |
| `src/connections/woocommerce/{provider,direct-product-reader}.ts` | Extend `approvedRequest`, `validRequest` and `pathFor` together; add list status/visibility projection and fixed ordering; preserve accepted credential/transport/original-error work. |
| `src/capabilities/{records,prisma-reader,manifest,resolve}.ts` | Carry trusted conversation/retained-grant projection, current discount policy and canonical built-ins; extend the existing consistent read and use Shared grant deduplication. Preserve MCP-001 required-feature selection. |
| `src/execution/conversation-discount-context.ts` — new | Own the narrow domain context/lease/grant checks below. This is not generic header authentication and owns no token, conversation write or new table. |
| Accepted `src/execution/{discount-tools,discount-catalogue}.ts` | Extend the existing authorization/projection/reader for conversation purpose. Preserve its catalogue query, condition mapping and cursor; add only the narrowly classified optional read failure branch. |
| `src/mcp/{ports,snapshot,registration}.ts` | Carry canonical built-in identity separately from mutable permission, validate manifest/list equality, and invoke the accepted built-in dispatcher. Remove no generic request/size checks. |
| `src/runtime/{ports,prisma,service-ports,execution-registry}.ts` | Wire the exact reader/context additions into production composition; forward `call.toolContext` into the fresh registry authorization read. Retain the accepted built-in execution port and call wrapper. |
| Tests named in Validation | Add/extend focused fixtures and the existing disposable database harness. No new test framework or runtime dependency is required. |

## Out of Scope

No Shared/Database changes or package publication; no edits to MCP-001, accepted ARCH-052 reports, Admin taxonomy or decision indexes. No new taxonomy source, native category-discovery endpoint, Shopify-to-Woo category translation, descendant expansion, product mirror, discount proof API, basket eligibility engine, coupon application, checkout/cart mutation, shipping fields in product results, tool publication, environment setup or customer send. Runtime filenames and symbols must not contain architecture task IDs.

## Requirements

### 1. Consume the known prerequisites once

The prepared MCP-001 result must already contain exact `@modainteract/moda-interact-shared@4.0.0`, its lockfile, the accepted Database revision `ded8f14a60182f6b1443640f012caf0089b8a44c` or an accepted descendant, and the taxonomy resolver/required-feature implementation. Use that prepared packet and the recorded SHARED-002 registry integrity; do not repeat release discovery, choose a version, redownload the taxonomy or downgrade an accepted descendant. A package/submodule mismatch is a concrete preparation failure with the observed value in the report.

Before modifying discount code, the prepared base must contain the accepted ARCH-052-MCP-002 catalogue implementation and tests: `src/execution/discount-catalogue.ts`, `tests/unit/execution/discount-catalogue.test.ts`, its real dispatcher wiring and the PostgreSQL scenario recorded in `tests/integration/prisma.integration.test.ts`. The accepted report identifies correction commit `89e9ad3` after `7cbceee89b2ae0115bd2b948418b4169b977ea8f`; the abbreviated correction is report provenance, not an invented full SHA. The accepted Woo error implementation is `1d18e6c866311d0a3238a919f335643ffbefd8c1` under ARCH-052-MCP-006. Preserve its diagnostic path. If either accepted implementation is absent, record the missing path/behavior and return an integration handoff to the developer/architect. Do not implement a competing reader/logger or check out an old task commit over MCP-001. The common handoff owns this integration prerequisite.

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

Keep API `2026-07` and `inspectShopifyReadQuery` unchanged. Use literal connection bounds, fixed sort `ID`, `reverse: false`, and trusted GraphQL documents. `SEARCH_DOCUMENT` becomes `CommerceSearchProducts($query: String!, $after: String)` with `productVariants(first: 20, after: $after, query: $query, sortKey: ID, reverse: false)`. Remove `$first` and the `first` variable. Retain its existing variant/product field selections and add parent `status` to the search-only projection; do not alter exact-get document content merely to support browse.

For text, escape backslash and double quote in the trimmed customer text and enclose it as one quoted Shopify search term. Do not interpolate raw search grammar. For browse, use exactly `product_status:ACTIVE`. Evaluate availability, maximum price and currency locally from observed fields; remove the current guessed `variants.price`/`available_for_sale` filter construction instead of relying on undocumented filter keys. The ordinary text branch retains its existing eligibility behavior; only browse additionally requires `product.status === ACTIVE` and an actual non-null storefront URL passing existing current-shop/verified-primary-domain HTTPS rules. Do not synthesize a URL from `handle`.

Add `CATEGORY_SEARCH_DOCUMENT` with this exact selection (reuse the existing `productFields` constant for identical fields when assembling the trusted string, adding status for the search-only parser); no fragments or caller-provided selections:

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

Its trusted search string is `category_id:<verified-short-token>`, followed by ` AND <quoted-text>` only when a query was supplied. Verify the returned `Product.category.id` equals the requested canonical GID. A different assigned category is consumed and excluded; it is not an automatic descendant match.

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

In `pathFor`, add `category=<id>` for category reads. For all list branches set fixed `orderby=id&order=asc`; for browse also set `status=publish` and omit `search`. Add `status,catalog_visibility` to product list `_fields` and `status` to variation list `_fields`; preserve the existing identity, prices, stock, category, image, permalink and variation fields. Do not add `include_children`, arbitrary query parameters or raw URLs. Non-browse product outputs remain unchanged.

For a category request, inspect the **full returned** categories array before the bounded public projection: a product matches only when one observed native ID equals the requested ID. A child-only membership does not match. For browse, require parent `status: publish` and `catalog_visibility: visible|catalog` before any variation read. A variation additionally requires `status: publish`. Draft/private/pending/hidden/search-only/unknown visibility is excluded regardless of stock. Apply availableOnly and price filtering afterward.

For every `type: variable` parent, use its verified parent-scoped variation list; do not depend on the incidental `variations` ID array being populated and do not emit the parent as a simple purchasable variant. Native variation `parent_id` is optional: when absent, the authenticated `/products/{verifiedProductId}/variations` endpoint establishes parent authority; when present, validate it with the native ID parser and require equality. List/exact variation IDs must be valid, and an exact read must equal the requested variation ID. Malformed/conflicting relationship evidence is an outer error for search; exact get retains its existing `{product: null}` missing/mismatch outcome. Never coerce `"1e2"`, blank or an unsafe number into an ID.

Keep product/variation page size 20, at most three newly fetched product pages and at most twelve total Woo provider reads per invocation, subject to the existing lower execution-policy ceiling. Freeze progress as the existing product page/index and variation page/index, plus retained parent ID and hashes of the ordered IDs on partially consumed pages. When a resumed page is re-read, changed page identities are `MCP_PRODUCT_CURSOR_STALE` / retryable outer `UNAVAILABLE`; do not silently skip/repeat records after a shifted catalogue. Advance a scanned index before filtering, so a bad or unpublished entry cannot trap the cursor. When the output limit/budget is reached, retain the exact next unconsumed position. Reset variation progress only after its parent is finished. A provider claim of more data beyond the existing maximum page 1000 is outer `UNAVAILABLE` with `MCP_PRODUCT_SEARCH_PAGE_LIMIT`, not false exhaustion or an unusable page-1001 cursor. Live catalogue changes do not create a snapshot/exhaustiveness guarantee.

### 5. Cursor identity, prices and exact-product preservation

Use existing HMAC-SHA256 mechanics and `COMMERCE_CURSOR_SECRET`, minimum 32 characters; no new secret or storage. The version-2 payload is strict `{version: 2, bindingHash, expiresAt, progress}`. `bindingHash` is SHA-256 of Shared `canonicalJson` over trusted environment, shop ID, provider, connection identity, branch, normalized query/category, verified taxonomy generation/version where applicable, browse, fixed order/visibility version, maximumPrice, availableOnly, limit, established market and currency. TTL stays 60,000 ms. Validate signature before parsing bounded progress, and reject all old-version/tampered/expired/cross-shop/cross-connection/cross-mode/filter-drift cursors as `INVALID_INPUT`. The final encoded cursor must fit Shared's **2048-character** bound; an oversized provider cursor is a hard result failure, never truncation or a dropped continuation.

Expose required readonly `sourceIdentity: string` only on the private resolved connection. Construct it with Shared `canonicalJson`: Shopify `{platform: "SHOPIFY", shopDomain}` using the verified canonical domain; Woo `{platform: "WOOCOMMERCE", installationId, credentialVersion, canonicalSiteUrl}` using the verified existing installation (nonempty ID, positive safe-integer version and canonical origin). Read Woo values in the existing shop projections in `connections/prisma-reader.ts` and `capabilities/prisma-reader.ts`; do not add a query or put this identity in public product data. Reinstallation/credential-version changes therefore cannot reuse a prior connection's continuation.

Preserve observed native IDs, native sale evidence and safe URLs. `availableOnly: true` accepts only `available === true`; false does not relax browse visibility. Numeric maximum-price comparison uses the existing decimal/BigInt logic only when price and its currency are known and compatible with any trusted price context; unknown/mismatched context cannot pass that filter. Shopify `shop.currencyCode` establishes base currency, not customer-market pricing. Woo runtime currency remains null unless its existing trusted provider/store context actually establishes denomination; do not copy recovery currency, locale or model text. A non-null unsupported market context remains unable to certify matching prices. No new currency or price-context public field is added.

Keep product get/search output schemas and `commerce_get_product` definition unchanged. In particular, existing Shopify exact get with variantId null returns the observed first variant from its current document; this task does not redefine that behavior. Background must select/confirm an observed native Shopify variant, and must not treat a null selection as authorization for the first variant. Woo simple products retain null variant IDs. Shipping's product-only `VARIANT_REQUIRED` belongs solely to MCP-003.

### 6. One domain authorization read for conversation discounts

Keep `parseMcpRequestContext` opaque. In the domain reader, a context claiming `CONVERSATION` must parse `CommerceConversationToolContextSchema`; one claiming `INITIAL_RECOVERY_OUTREACH` must parse the unchanged outreach schema. Invalid claimed-purpose fields are hard `INVALID_INPUT`. An absent/unrelated opaque context remains the generic shop caller and receives no conversational discount privileges or soft-unavailable behavior.

Extend `PrismaShopCapabilityTransaction` with `conversation.findUnique` and `commerceConversationGrant.findUnique`. Export `readConversationDiscountContext` from the new context module and invoke it inside the existing RepeatableRead transaction. It makes exactly these two reads for an approved CONVERSATION purpose; other purposes make neither:

```typescript
tx.conversation.findUnique({
  where: {id: context.conversationId},
  select: {id: true, shopId: true, checkoutRecovery: {select: {shopId: true}},
    controlMode: true, inboundVersion: true, processingInboundVersion: true,
    processingStartedAt: true}
});
tx.commerceConversationGrant.findUnique({
  where: {conversationId: context.conversationId},
  select: {id: true, shopId: true, conversationId: true, initialInboundVersion: true,
    releaseId: true, selectedCapabilityKeys: true, grantedTools: true,
    runnerVersion: true, createdAt: true, expiresAt: true}
});
```

The conversation's direct/recovery ownership must resolve to the authenticated shop; if both ownership values exist they must agree. Require `controlMode === "AI"`, current inboundVersion and processingInboundVersion equal the positive context version and a non-null finite lease timestamp with `0 <= now - processingStartedAt < 120000`, matching the existing Background lease. This checks existing state; it creates no conversation/recovery or lease policy. Absent/wrong-shop conversation or human control is `McpRequestError(FORBIDDEN, 403, false)`; stale inbound/lease/cancellation is `McpRequestError(DEADLINE, 409, true)`.

A null context grantId is allowed only before any retained grant exists. A non-null ID must match the stored grant, shop and conversation; its initialInboundVersion must not exceed the current turn, runnerVersion must equal the installed runner, expiresAt must be null/future and releaseId must equal the currently resolved immutable release. Project selected Date fields to ISO strings and parse the full row with installed `CommerceConversationGrantSchema`; derive retained built-in identities from this parsed storage only. Missing/mismatching/expired grants or null-ID bypass attempts are FORBIDDEN/403/false. Malformed stored JSON/timestamps, runner mismatch or release mismatch is INCOMPATIBLE_VERSION/503/false. Preserve current published-release/entitlement checks. Do not turn any of these failures into optional absence.

Read current settings/active override and FIXED selection in that existing snapshot for either approved purpose; keep `resolveDiscountAuthorizationPolicy` semantics. Extend the accepted catalogue's call-time authorization path with the same domain helper and fresh current policy; list-time authorization alone is insufficient. `runtime/execution-registry.ts` must include opaque `call.toolContext` in its fresh reader context so published product calls also retain the approved conversation checks. Do not add a new header or model argument for this data.

### 7. Canonical identities and a stable retained grant

Use Shared `commerceDiscountBuiltInDescriptors`, `commerceBuiltInToolContractPayload`, `isTrustedCommerceBuiltInDescriptor`, `isTrustedCommerceBuiltInGrant`, `deduplicateTools` and `isBuiltInTool`. Verify the canonical hashes against the installed schemas in tests using Node SHA-256; do not generate a self-asserted descriptor or fabricated database ID.

Extend `McpSystemTool` with the exact Shared built-in descriptor identity while keeping its current mode/allowedDiscountIds as **private mutable permission**, outside the manifest descriptor. Replace the outreach-only projection with `projectAuthorizedDiscountTools` in `discount-tools.ts`, using the already validated purpose/grant projection from the reader:

| Context | Descriptor/list projection |
| --- | --- |
| Generic caller | No discount built-ins. |
| Valid outreach; current mode NONE | No discount built-ins. |
| Valid outreach; current mode FIXED or AI_BEST_APPLICABLE | The two canonical built-ins; existing outreach execution semantics. |
| New conversation without a retained grant | The two canonical built-ins only when current mode permits discounts; otherwise none. |
| Conversation with retained grant | Exactly its stored, canonical built-in set, including when the current mode is now NONE. Never widen that set. |

Pass this descriptor set to `projectCommerceManifest` and build grants with Shared `deduplicateTools(capabilities, builtInTools)` instead of treating every grant as published. Keep feature snapshots, release hash, selected capability keys and published provenance unchanged. In `validateSnapshot`, require exact name/version/hash/description/input-schema correspondence between systemTools and manifest.builtInTools; reject duplicate names, collisions with published advertised/underlying names, unknown descriptors and a combined advertised list above 32. Replace the unconditional mode-NONE snapshot rejection with current-permission enforcement **at execution**. Listing a retained descriptor is identity continuity, not permission to execute it.

`registration.ts` must call the existing accepted catalogue dispatcher with its existing deadline/cancellation/result-byte wrapper. Both structuredContent and text must serialize the same validated result; isError is true exactly for outer ERROR. Re-read current policy immediately before lookup. NONE denies execution; FIXED restricts current permitted selection/override; AI scans permitted catalogue independently of selection checkbox. A grant initially created under NONE cannot gain tools after a later mode change. The host skips discount calls under current NONE; do not mutate the stored grant to reflect current policy.

### 8. Catalogue facts and optional operational failure

Keep the accepted shop-scoped PostgreSQL `ShopifyDiscount` snapshot reader, authenticated keyset cursor, generation checks, exact offer identity and completeness mapping. Its normal options/details outputs, native target IDs, threshold currency, Woo zero threshold/quota rules, exclusions, usage/customer/sale restrictions and combination uncertainty remain unchanged. It makes zero Shopify/Woo HTTP calls and receives no basket. `details: null` remains distinct from an unavailable lookup.

Only **after** conversation/lease/grant/current-policy authorization succeeds may a database catalogue-read failure become `OK` with `{outcome: UNAVAILABLE, reasonCode: TEMPORARY_UNAVAILABLE}`. Classify a genuine Prisma error/cause carrying `P1001`, `P1002`, `P1008`, `P1017` or `P2024` at the owning database read boundary; do not classify from error prose or merely outer `UNAVAILABLE`. Authorization/configuration reads, P1000, missing tables/columns, invalid SQL, result parsing, cursor/generation conflicts, unexpected errors and aborted/expired turns remain outer errors. Initial outreach retains its accepted hard-failure behavior for the same failures. No catch-to-empty-offers, fabricated NONE mode or broad retry loop is permitted.

Use the accepted Shared structured logger boundary. Preserve the original sanitized Prisma/SDK/provider error and cause, safe provider status/request ID and separate Moda reason. Do not invent a provider error for a DB-only catalogue read, expose raw failures in tool output, or build another generic redactor/logger. Provider adapters remain responsible for their own source diagnostics.

## Work Items

- [ ] Verify the already accepted prepared source/artifact gates; report the specific accepted-source integration gap if still present.
- [ ] Implement the exact input/category reader, literal Shopify documents, three search branches and version-2 cursor.
- [ ] Update all three Woo guards/projections and optional parent-ID validation; preserve transport and ordinary product contracts.
- [ ] Add the conversation domain read and forward its opaque context at the fresh registry read.
- [ ] Project/execute canonical built-ins with retained identity and current policy; extend the existing catalogue only for conversation purpose/classified transient failures.
- [ ] Run agent-owned checks, prepare the exact required developer database run, complete the report and submit for review.

## Interfaces / Contracts

Shared 4.0.0 and `docs/architecture/ARCH-058/contracts.md` sections 2.2–4.1 own the public interfaces. The private fields and algorithms above are now selected implementation decisions, not alternatives for the agent to redesign. Shopify's [pinned products filter](https://shopify.dev/docs/api/admin-graphql/2026-07/queries/products) uses `category_id` with a short taxonomy token; [Product variants](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Product) supports bounded after/first/sortKey traversal. Use the existing pinned Admin schema artifact for schema validation, not a new schema/version download. [Woo products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/) and [variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/) define the native list/exact response shapes. Native payload fields are data, not new execution permission.

## Dependencies

- `ARCH-058-MCP-001`: accepted resolver, required-feature eligibility, exact Shared 4.0.0 package and accepted Database pin. Do not start this task while MCP-001 is under development.

The known ARCH-052 source integration prerequisite in section 1 must be satisfied in the prepared base. It does not authorize reopening/reimplementing those completed tasks. No upstream task depends on terminal system testing.

## Enables

- `ARCH-058-MCP-003`: separate shipping operation on the accepted provider/authorization composition.
- `ARCH-058-COMMERCE-001`: publication after its other declared dependencies complete.
- `ARCH-058-BACKGROUND-001`: grounded conversation product/discount use.
- `ARCH-058-SYSTEM-TEST-001`: real service-boundary validation after all prerequisites.

## Acceptance Criteria

- [ ] The actual provider/document guard accepts text/category/browse requests; guards and versioned public outputs remain intact.
- [ ] Exact membership, publication visibility and stock/currency rules produce only qualified current-shop facts; invalid input causes zero provider I/O.
- [ ] A product with 45 variants, caller limit 2, filtered middle pages and an empty unfinished page resumes without dropped/repeated records under static fixtures, within 3 Shopify/12 Woo request ceilings.
- [ ] Old/tampered/cross-shop/cross-connection/filter-drift cursors are rejected; a shifted Woo page or retained Shopify parent is explicitly stale, not exhausted.
- [ ] Every normal published execution retains toolContext at its fresh read; stale/wrong-shop/missing-grant/expired-lease calls cannot bypass the domain check.
- [ ] Built-in list/manifest/grants match canonical Shared identities and remain stable after current mode changes; execution still honors current policy and never widens an initial grant.
- [ ] Catalogue outputs preserve accepted facts and no-provider-call behavior; only the specified optional conversational DB failures use the new successful unavailable branch.
- [ ] Original failures remain in redacted Shared logs and not in model/customer data. Required fast checks and the separately owned database evidence are accurately reported.

## Validation

Use the launcher-provided implementation worktree/preparation evidence. Before the first Node command use `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. No source download, deployment URL or persistent database is needed.

**Agent-owned focused checks.** Add `tests/unit/execution/policy/{product-search-composition,product-search-cursor}.test.ts`, `tests/unit/execution/reference-taxonomy/category-membership.test.ts` and `tests/unit/execution/conversation-discount-context.test.ts`; extend the existing tests listed in these commands:

```bash
npm exec -- tsx --test tests/unit/execution/policy/shopify-core.test.ts tests/unit/execution/policy/product-search-composition.test.ts tests/unit/execution/policy/product-search-cursor.test.ts tests/unit/execution/reference-taxonomy/category-membership.test.ts tests/unit/connections/shopify/provider.test.ts tests/unit/connections/prisma-reader.test.ts tests/unit/connections/resolver.test.ts tests/unit/connections/woocommerce/direct-product-reader.test.ts tests/unit/connections/woocommerce/provider.test.ts
npm exec -- tsx --test tests/unit/execution/conversation-discount-context.test.ts tests/unit/execution/discount-tools.test.ts tests/unit/execution/discount-catalogue.test.ts tests/unit/capabilities/manifest.test.ts tests/unit/capabilities/prisma-reader.test.ts tests/unit/mcp/capability-invocation.test.ts tests/unit/mcp/resources.test.ts tests/unit/mcp/structured-results.test.ts tests/unit/runtime/ports.test.ts tests/unit/runtime/prisma.test.ts tests/unit/runtime/service-ports.test.ts
npm run typecheck
npm run typecheck:integration
npm run lint
npm run build
git diff --check
```

`product-search-composition.test.ts` must invoke the registered policy executor through the real connection resolver, provider and document guard with injected HTTP/session fixtures. Include query-grammar injection strings, literal query bounds, exact category plus query, default/mixed browse rejection, Shopify ACTIVE + verified URL versus draft/null/foreign URL, Woo publish/visible/catalog versus hidden/search-only/draft parents and unpublished variants, unknown/false stock, zero/unknown currency, category mismatch beyond the first 20 category entries, optional/mismatching parent_id, variable parent with an empty variation-ID list, mid-page limits, exhausted/unfinished empty pages and all bounded cursor states. Assert no extra API calls or forbidden request keys.

Update the existing private-connection fixtures in `tests/fixtures/capabilities.ts` and the named connection/runtime tests with the real sourceIdentity inputs; do not bypass sourceIdentity validation in tests. The context/catalogue fixtures must exercise the real `createMcpService` list/resource/call route with the accepted dispatcher. Cover two shops, null context, malformed purpose, initial/retained grant, lease expiry, inbound version change or human takeover between list and call, code-hash drift, collisions, NONE→AI with an empty retained grant, AI→NONE with the unchanged retained descriptor set and denied call, FIXED revocation/override expiry, a classified catalogue timeout versus auth/configuration/parse failure, and the unchanged outreach response for the same failure. Use actual Shared logger sinks with credential/PII sentinels and original errors.

**Required developer-owned PostgreSQL run.** Add `tests/integration/conversation-product-discovery.integration.test.ts` to the existing `scripts/test-postgres.mjs` wildcard harness, using `tests/helpers/disposable-postgres.ts` and the existing fixture helpers. Exercise the category exact join, migrated grant JSON guard, two-shop lease/grant authorization and current discount policy. Preserve and run the accepted catalogue scenario; do not replace it with mocks or another database runner.

```bash
npm run test:integration:docker
```

Ownership is explicit under `docs/agent-validation-execution-policy.md`: the implementation agent runs the fast/typecheck checks above and supplies this command for the developer's disposable run; it does not autonomously launch/wait on the long integration suite without a task-specific override after claim. The harness owns its local database URL and cleanup. Do not substitute an environment DATABASE_URL, `db push`, shared container, or external service. Record worktree/HEAD, database gitlink, exact command, task scenario results, overall exit status and owned-container cleanup. An unavailable/unrun database suite is `NOT_RUN / developer validation required`, never a pass. Submit review with that evidence pending; acceptance requires the actual required scenario results. Report unrelated existing failures separately without claiming the full suite passed.

## Stop Condition

Stop for the specifically missing accepted source/artifact gate, a contract/schema change outside this ownership, an unregistered provider field/query or a failed authorization invariant. Report the observed path/value and owning prerequisite; do not research a replacement feature or widen permissions. After scoped implementation and fast validation, set status to `review`, record the required developer database handoff/result accurately and return to the architect. Do not mark complete, publish, deploy, mutate a persistent environment or start another task.

## Implementation Notes

This is an extension of the existing composition. Reference categories describe meaning; provider products establish the store's assortment; the existing catalogue describes discount conditions. Background remains the sole owner of applicability and customer prose. A bounded page with no match and a continuation is not evidence that the store has no matching product.

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
