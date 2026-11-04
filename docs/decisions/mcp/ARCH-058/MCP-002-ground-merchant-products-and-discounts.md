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

This amendment changes the existing task definition without claiming or starting MCP-002, creating its implementation worktree or certifying deployment/provider behavior. After its declared dependencies are Complete, use the normal `/moda-task ARCH-058-MCP-002` launcher and its supplied implementation worktree/workspace root; do not derive paths from the MCP-001 worktree.

## Objective

Extend the accepted MCP tool provider with exact category search, explicit catalogue browse and the existing shop-scoped discount catalogue. MCP resolves the authenticated shop, advertises executable tools and returns current source facts. Background owns conversation state, retained workflow grants, turn admission, offer applicability and customer wording.

## Context

**Definition revision 6.** This revision is grounded in the supplied `moda-interact-workspace-ARCH-058-MCP-001.zip`, including its current MCP source and MCP-001 report. Read the common [execution baseline](../../../architecture/ARCH-058/execution-baseline.json) and [implementation handoff](../../../architecture/ARCH-058/implementation-handoff.md). MCP-001's eventual accepted implementation is the base for this task; do not repeat its importer, source selection or dependency preparation. The earlier 09:49:47 snapshot remains historical provenance, not the current source-presence gate.

The snapshot establishes these implementation gaps:

- `shopify-core.ts:SEARCH_DOCUMENT` uses variable `first: $first`, rejected by `connections/shopify/document.ts`. Its `SearchInput.query` and provider composition are text-only.
- Woo request keys are independently checked in `connections/resolver.ts`, `connections/woocommerce/provider.ts` and `direct-product-reader.ts`; changing only the port type cannot enable a category/browse request.
- Woo list/exact mapping unconditionally requires `parent_id`, although native variation ownership is established by the verified parent endpoint. The search loop also advances some variation indexes only after validation, leaving filtered records able to repeat.
- `discount-tools.ts` and `runtime/service-ports.ts` expose discount descriptors only for an outreach purpose and current non-NONE mode. The generic capability reader performs the associated settings/selection reads. These must become context-independent tool discovery; the accepted catalogue executor retains current shop configuration checks on actual calls. `mcp/snapshot.ts` also needs exact canonical descriptor/manifest equality.
- The current upload contains `src/execution/discount-catalogue.ts`, its unit/PostgreSQL coverage and the production `executeDiscountTool` wiring. Its `execute` still rejects callers without the outreach purpose; remove that gate at the existing reader as well as in discovery/registration. Preserve its fact projection and keyset cursor.
- The built-in branch in `mcp/registration.ts` currently calls `ports.executeDiscountTool` directly. Unlike `executePublishedTool`, that branch has no per-call deadline/cancellation/result-byte wrapper; the service's HTTP envelope bound is a separate limit. Section 7 specifies the narrow reuse of the existing execution mechanics needed to close that gap.
- The accepted Woo diagnostic path is present in `direct-product-reader.ts`, including `safeException`, `sourceProviderError`, provider status/request ID and original bounded error/cause logging. Preserve that implementation. The older missing-catalogue/missing-diagnostics statements in the untouched initial report below are superseded by this source inspection.

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
| `src/capabilities/{records,prisma-reader,manifest,resolve}.ts` | Keep the exact generic shop/release/plan projections; remove discount settings/selection reads from this capability reader. Project the canonical pair independently of caller context/current mode and build the provider manifest tool union with `deduplicateTools(capabilities, builtInTools)`; read no retained grant. Preserve MCP-001 required-feature selection. |
| Existing `src/execution/{discount-tools,discount-catalogue}.ts` | Replace purpose-dependent descriptor projection and remove the reader's outreach-purpose gate. Preserve the existing factory, current mode/FIXED selection/override checks, condition mapping and keyset cursor. Apply section 7's exact NONE/details/cursor ordering and section 8's query-scoped unavailable-data classification for every caller. |
| `src/mcp/{ports,snapshot,registration,execution}.ts` | Use the canonical descriptor DTO and exact manifest/list equality. Remove the purpose/list-time mode gate; route built-in calls through the bounded wrapper in section 7. Share the existing call-policy/deadline/cancellation/result-byte mechanism within `execution.ts`, preserving published-call behavior. |
| `src/runtime/{ports,prisma,service-ports}.ts` | Add the category reader to the existing composition and remove the outreach-only listing call. Preserve the existing `createPrismaDiscountCatalogueReader` -> `ports.discounts` -> `ShopifyServiceComposition.discounts` -> `executeDiscountTool` chain; forward the added private RPC signal/deadline through its existing spread. The published execution registry retains its generic shop/environment authorization read. |
| Tests named in Validation | Add/extend focused fixtures and the existing disposable database harness. No new test framework or runtime dependency is required. |

## Out of Scope

No Shared/Database changes or package publication; no edits to MCP-001, accepted ARCH-052 reports, Admin taxonomy or decision indexes. No conversation context parser, conversation/retained-grant/recovery-lifecycle reader, lease/takeover check or workflow authorization module in MCP. Existing unrelated execution adapters may still consume their established opaque toolContext. No new taxonomy source, native category-discovery endpoint, Shopify-to-Woo category translation, descendant expansion, product mirror, discount proof API, basket eligibility engine, coupon application, checkout/cart mutation, shipping fields in product results, tool publication, environment setup or customer send. Runtime filenames and symbols must not contain architecture task IDs.

## Requirements

### 1. Consume the known prerequisites once

The prepared MCP-001 result must already contain exact `@modainteract/moda-interact-shared@4.0.0`, its lockfile, the accepted Database revision `ded8f14a60182f6b1443640f012caf0089b8a44c` or an accepted descendant, and the taxonomy resolver/required-feature implementation. Use that prepared packet and the recorded SHARED-002 registry integrity; do not repeat release discovery, choose a version, redownload the taxonomy or downgrade an accepted descendant. A package/submodule mismatch is a concrete preparation failure with the observed value in the report.

The current upload already includes the ARCH-052 catalogue source, `tests/unit/execution/discount-catalogue.test.ts`, its production wiring and the persisted-snapshot scenario in `tests/integration/prisma.integration.test.ts`. The existing factory is `createPrismaDiscountCatalogueReader(database, {cursorSecret?, now?}): DiscountCatalogueReader`, whose method is `execute(call: DiscountSystemToolCall): Promise<CommerceToolResult>`. `runtime/ports.ts:createPersistedMcpPorts` constructs it once; `runtime/prisma.ts` passes `ports.discounts` to `createShopifyServicePorts`; `runtime/service-ports.ts` supplies the existing logger and invokes `options.discounts.execute`. Preserve this chain and its existing `COMMERCE_CURSOR_SECRET` source. The catalogue is no longer a missing-source blocker.

Historical provenance remains ARCH-052-MCP-002's correction `89e9ad3` after `7cbceee89b2ae0115bd2b948418b4169b977ea8f`, plus ARCH-052-MCP-006's accepted diagnostic correction `1d18e6c866311d0a3238a919f335643ffbefd8c1`. An abbreviated recorded commit is not a fabricated full SHA. At normal task preparation, verify the observed source/composition is still present in the accepted MCP-001 base. Only an actual missing path or changed incompatible signature is a new prerequisite failure. Do not recreate the reader/logger, repeat integration already present in this upload or check out an old task commit over MCP-001.

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

Use Shared `commerceDiscountBuiltInDescriptors`, `commerceBuiltInToolContractPayload`, `isTrustedCommerceBuiltInDescriptor`, `deduplicateTools` and `isBuiltInTool`. Verify canonical hashes against the installed schemas in tests using Node SHA-256. `McpSystemTool` contains only the canonical descriptor; remove its old mode/allowedDiscountIds listing fields. Keep the existing `resolveDiscountAuthorizationPolicy` helper for the accepted executor's current shop configuration; it is not a conversation grant reader.

Extend `projectCommerceManifest(release, selected, positions, builtInTools = [])` with `builtInTools: readonly CommerceBuiltInToolDescriptor[]`. `resolveShopCapabilities` computes the pure shop-plan descriptor set once, supplies it to the manifest and exposes that same set as systemTools. Build `grantedTools` with Shared `deduplicateTools(capabilities, builtInTools)` and validate the actual Shared manifest. Remove `runtime/service-ports.ts`'s separate `projectInitialOutreachDiscountTools` call so list/resource projection cannot diverge. Feature snapshots, response hash, release identity, selected published capabilities and their provenance remain unchanged.

In `validateSnapshot`, require exact canonical name/version/hash/description/input-schema correspondence between systemTools and manifest.builtInTools. Reject duplicate names, collisions with published advertised/underlying names, unknown descriptors and a combined advertised list above 32; do not silently remove a descriptor to fit. Remove the mode-based snapshot rejection. Every eligible shop sees the same pair before/after NONE/FIXED/AI changes, independently of opaque caller context. `grantedTools` in this provider manifest describes its advertised capability union; Background owns any persisted workflow grant and model availability check. MCP never reads or mutates that workflow grant.

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

- [ ] Verify the prepared MCP-001 source/artifacts once against the current supplied catalogue/diagnostic composition; report only an actual new mismatch.
- [ ] Implement the exact input/category reader, literal Shopify documents, three search branches and version-2 cursor.
- [ ] Update all three Woo guards/projections and optional parent-ID validation; preserve transport and ordinary product contracts.
- [ ] Remove purpose/policy discovery coupling; retain the five generic capability reads and exact canonical descriptor DTO/projection.
- [ ] Advertise both canonical built-ins for eligible shops; remove both purpose gates, reuse the bounded call mechanism and implement the exact current-shop catalogue/error branches.
- [ ] Run agent-owned checks, prepare the exact required developer database run, complete the report and submit for review.

## Interfaces / Contracts

Shared 4.0.0 and `docs/architecture/ARCH-058/contracts.md` sections 2.2–4.1 own the public interfaces. The private fields and algorithms above are now selected implementation decisions, not alternatives for the agent to redesign. Shopify's [pinned products filter](https://shopify.dev/docs/api/admin-graphql/2026-07/queries/products) uses `category_id` with a short taxonomy token; [Product variants](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Product) supports bounded after/first/sortKey traversal. Use the existing pinned Admin schema artifact for schema validation, not a new schema/version download. [Woo products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/) and [variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/) define the native list/exact response shapes. Native payload fields are data, not new execution permission.

## Dependencies

- `ARCH-058-MCP-001`: accepted resolver, required-feature eligibility, exact Shared 4.0.0 package and accepted Database pin. Do not start this task while MCP-001 is under development.

The ARCH-052 catalogue and Woo diagnostic source/composition described in section 1 are present in this upload and must remain in the accepted MCP-001 base. Preserve those completed implementations; do not reopen them or repeat integration. No upstream task depends on terminal system testing.

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
- [ ] Generic discovery has exactly the specified five delegate calls and no discount/workflow-state reads; irrelevant opaque context cannot change tenant, tool-list or catalogue data scope.
- [ ] Built-in list/resource projection matches canonical Shared identities and stays stable after current mode changes; calls still use the current configured mode/selection and active shop/plan.
- [ ] Catalogue outputs preserve accepted facts and no-provider-call behavior; NONE/nonpermitted FIXED details deny before lookup, permitted absence stays null, and NONE never accepts a non-null cursor.
- [ ] Built-in calls use the same policy/deadline/cancellation/result-byte mechanism as published calls; abort/expiry/missing executor/oversized data remain hard, no extra policy/capability read or provider request is introduced, and no late database completion exposes data or starts another batch.
- [ ] Only the three specified post-authorization catalogue query boundaries produce the successful unavailable branch after rollback, identically for every caller; authorization, transaction-boundary and unexpected failures remain hard.
- [ ] Original failures remain in redacted Shared logs and not in model/customer data. Required fast checks and the separately owned database evidence are accurately reported.

## Validation

Use the launcher-provided implementation worktree/preparation evidence. Before the first Node command use `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. No source download, deployment URL or persistent database is needed.

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

`product-search-composition.test.ts` must invoke the registered policy executor through the real connection resolver, provider and document guard with injected HTTP/session fixtures. Include query-grammar injection strings, literal query bounds, exact category plus query, default/mixed browse rejection, Shopify ACTIVE + verified URL versus draft/null/foreign URL, Woo publish/visible/catalog versus hidden/search-only/draft parents and unpublished variants, unknown/false stock, zero/unknown currency, category mismatch beyond the first 20 category entries, optional/mismatching parent_id, variable parent with an empty variation-ID list, mid-page limits, exhausted/unfinished empty pages and all bounded cursor states. Assert no extra API calls or forbidden request keys.

Update the existing private-connection fixtures in `tests/fixtures/capabilities.ts` and the named connection/runtime tests with the real sourceIdentity inputs and the generic records shape; do not bypass sourceIdentity validation. Capability-reader fixtures expose only the five declared delegates and assert zero settings/override/catalogue reads. They expose no conversation/grant/recovery/attempt delegate; adding one to satisfy a test is a failure of this boundary. Through real `createMcpService` list/resource/call routes and the accepted dispatcher, compare omitted toolContext with opaque outreach/conversation/irrelevant objects, including misleading nested shop/turn/grant fields: the outer authenticated shop alone controls identical listing/data scope. Malformed non-object headers and model-supplied extra arguments still fail the existing structural validators. Cover two shops; ACTIVE/TRIALING versus inactive/missing plans; inactive shops/revoked Woo installations; canonical hash/list collisions; stable descriptors under NONE→AI and AI→NONE; NONE empty options and denied details; changed FIXED selection/override expiry; valid pagination and cross-mode cursor rejection. Inject each permitted transient failure separately at the generation/page/details query boundary under every opaque context and assert the same unavailable-data result after rollback. Assert settings/override/FIXED-selection/transaction-start/transaction-close/parse failures stay hard, and capture original error causes in the actual Shared sink. Extend `tests/unit/mcp/execution-policy.test.ts` with built-in calls: one selected-policy read, request abort, SDK abort, deadline, oversized output, absent executor, no provider reservation and late resolve/reject. Use injected clocks, abort controllers and deterministic barriers; retain the existing published-call assertions. In reader tests assert the exact private signal/deadline and remaining transaction options, no query before an already expired call, no next batch after cancellation, NONE with non-null cursor rejected, and denied details with zero detail query. Initial-outreach zero-client NONE and hard-unavailable host behavior are Background-owned regressions, not reasons to add an MCP purpose branch. Use actual Shared logger sinks with credential/PII sentinels and original errors.

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
