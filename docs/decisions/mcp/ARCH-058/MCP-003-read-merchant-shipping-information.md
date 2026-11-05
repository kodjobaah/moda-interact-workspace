---
id: ARCH-058-MCP-003
architecture_id: ARCH-058
title: Read native merchant shipping policy and exact product shipping facts
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-058-MCP-002
- ARCH-058-SHOPIFY-001
enables:
- ARCH-058-COMMERCE-001
- ARCH-058-BACKGROUND-001
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: 2026-11-05
---

# ARCH-058-MCP-003: Read native merchant shipping policy and exact product shipping facts

## Architecture

Architecture ID: `ARCH-058`. Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Normative contracts: `docs/architecture/ARCH-058/contracts.md`, especially section 2.3. Coordinator: `moda_architect`.

This amendment changes the existing task definition without claiming or starting MCP-003, creating its implementation worktree or certifying deployment/provider behavior. After its declared dependencies are Complete, use the normal `/moda-task ARCH-058-MCP-003` launcher and its supplied implementation worktree/workspace root; do not derive paths from the MCP-001 worktree.

## Objective

Add `commerce_get_shipping_information` definition **1.0.0**, operation `shipping.getInformation` **1.0.0**, to the existing published policy executor. Return the current store's native shipping policy and exact requested product/variant facts through the already authorized Shopify/Woo connections. This task implements the selected private interfaces and mappings below; consume the corrected public schemas from exact Shared 5.0.0 after SHARED-006 acceptance through the accepted MCP-002 base.

## Context

**Definition revision 10.** Shipping behavior and scope remain unchanged. The [execution baseline](../../../architecture/ARCH-058/execution-baseline.json) and [implementation handoff](../../../architecture/ARCH-058/implementation-handoff.md) record the accepted prerequisites and current source. SHARED-001/002 and SHOPIFY-001 remain historical Complete tasks; SHARED-003/004/005/006 and DATABASE-002 correct the contract identity/storage boundary before MCP-002 completes. MCP-003 consumes that accepted result transitively through MCP-002 and must not repeat Shared/Database implementation or publication. The Shopify scope task accepted `c3b580cec5acc46e5c53386dd94279ad97b02ee9`; its configuration acceptance does not establish a live merchant grant.

The current uploaded MCP source still has three specific missing shipping seams: `ShopifyOfflineSessionReader.read` returns only a token; the resolver's GraphQL request allowlist drops any other key; and both Woo exact-read guards/projections omit shipping fields. `shopify-core-executor.ts` also assumes every non-basket/non-get policy operation is search and requires a cursor secret. Registering an authoring operation alone cannot execute shipping. The current upload already includes the accepted Woo `safeException`/`sourceProviderError` diagnostics in `direct-product-reader.ts` and the existing discount catalogue/composition; preserve them through MCP-002. Neither is a missing-source integration blocker in this upload.

## Scope

Only `moda-interact-mcp`, its tests and this report. Consume accepted MCP-002 as the task base and keep its product, generic shop-catalogue, original-error and canonical no-hash tool-identity changes. Retain MCP-002's accepted exact **Shared 5.0.0** package/lock and runner **1.1.0**; do not change MCP's direct Zod dependency for ARCH-058, select another Shared version, regenerate taxonomy, edit database schema or update the completed Shopify task.

### Exact implementation map

| Path relative to MCP worktree | Required change |
| --- | --- |
| `src/execution/policy/shipping-information.ts` — new | Export `createShippingInformationAdapter`, the three fixed named query documents, native fact parsers and independent policy/product projection. Its sole execution method is `getShippingInformation(context, parsedInput)`. Inject the resolved connection and trusted clock; no Prisma/provider client inside this adapter. |
| `src/execution/policy/shopify-core-executor.ts` | Add the shipping output/template-path entry and allowed arguments; use the shipping Shared parser explicitly; extend provider support and no-cursor-secret eligibility; dispatch to the new adapter and validate with `CommerceShippingInformationSchema`. |
| `src/connections/ports.ts` | Add GraphQL `requiredScope?: "read_legal_policies"`; add `projection?: "SHIPPING"` on the two Woo **exact** operations only. Public MCP arguments remain unchanged. |
| `src/connections/shopify/session-reader.ts` | Return one validated `{accessToken, scope}` value from the same existing offline row; include scope in the existing select and preserve original database error causes. Export the narrow missing-scope error class described below. |
| `src/connections/resolver.ts` | Validate/forward requiredScope and the Woo exact projection key. Keep opaque shop/context handling and provider-budget reservation. |
| `src/connections/shopify/provider.ts` | Consume the paired session, perform exact trusted policy-scope preflight, and otherwise preserve document guard, API pin, fetch/cancellation/response bounds and original-error logging. |
| `src/connections/woocommerce/{provider,direct-product-reader}.ts` | Extend strict exact-read key checks and `pathFor` shipping projection; reuse the accepted grant/credential/transport and parent endpoint path. List/search requests do not gain shipping projection. |
| `src/runtime/{ports,service-ports,prisma}.ts` | Pass existing connection/clock/logger dependencies through the registered core executor and update paired-session test/type seams. No second shipping handler, Prisma client or environment setting. |
| Existing `src/execution/policy/shopify-core.ts` | Reuse its PolicyContext/PolicyResult types; export its existing `safeStoreUrl` helper unchanged and import it in the shipping adapter after validating the primary-domain candidate; do not change product output, product get document/version or search cursor semantics. |
| Tests named in Validation | Add focused adapter/composition fixtures and update every session fixture from a token string to the paired value. |

## Out of Scope

No live grant/install/deploy operation; no Shared publication, Commerce authoring/publication, Background customer composition or migration. No policy/vector mirror, Merchant Knowledge entitlement change, page crawler, arbitrary URL fetch, shipping-zone/profile scan, rate calculator, Storefront/Store API cart, address/checkout mutation, coupon application, delivery promise or customer send. Keep Admin intact and leave decision indexes and accepted task histories unchanged. Runtime filenames and symbols use semantic names without architecture IDs.

## Requirements

### 1. Exact input, ordering and error outcomes

Parse the installed `CommerceShippingInformationInputSchema`. Both optional nullable IDs default to null. A variant without a product is `INVALID_INPUT` before provider I/O. Shopify native IDs must be complete `gid://shopify/Product/<positive-decimal>` and `gid://shopify/ProductVariant/<positive-decimal>` strings, respectively, within the Shared 128-character bound; preserve strings rather than coercing numeric suffixes. Woo native IDs use the accepted positive decimal/safe-integer parser. Extra query/shop/URL/scope/cart/address/credential arguments fail the strict Shared input parse.

Execute in this order: validate input/provider/native identity; if a product is requested, read and validate product/variant facts; only after that succeeds read the Shopify policy (or construct Woo's no-read UNSUPPORTED policy); validate the full result and return it. A product failure therefore makes no additional policy HTTP call. A missing policy permission is the one specifically classified preflight outcome that can coexist with successful product facts. Abort/deadline after either await is a hard outer error, never a partial successful result. Set root observedAt once from the injected trusted clock after the required reads complete.

| Condition | Public product outcome / outer error |
| --- | --- |
| productId null and variantId null | `NOT_REQUESTED`, every product ID/fact null. Never select a product to populate the response. |
| Shopify productId alone; exact product exists | `VARIANT_REQUIRED`, observed productId, variantId/facts null. |
| Woo type variable alone; exact parent exists | Same VARIANT_REQUIRED mapping. |
| Shopify exact selected variant belonging to requested product | AVAILABLE with both observed IDs and native variant facts. |
| Woo type simple, no variation | AVAILABLE, observed productId, variantId null, native product facts. |
| Woo type variable with verified requested variation | AVAILABLE with both observed IDs and effective variation facts. |
| Invalid native ID, simple Woo product with variant, unsupported/custom/grouped/external Woo shipping type | Outer `INVALID_INPUT`, retryable false. Do not add a new error enum or alter ordinary get/search type behavior. |
| Missing exact product/variant | Outer `NOT_FOUND`, retryable false. |
| Returned ID/parent relationship contradicts the requested identity | Outer `DENIED`, retryable false; never echo an unchecked ID as fact. |
| Malformed provider shape/field/value, unsafe policy URL or invalid timestamp | Outer `UNAVAILABLE`, retryable false, with original safe parse/validation diagnostics. |
| Existing provider/authorization/rate-limit/cancellation failure | Preserve the existing outer error classification and retryability. No conversion to NOT_CONFIGURED/UNSUPPORTED/SCOPE_NOT_GRANTED. |

Use the existing `commerce.v1` envelope, typed error enum and result-byte limit. Background owns conversation admission and the response to a tool failure. Do not return model-authored shipping prose or eligibility judgments.

### 2. Paired offline token/scope and the precise preflight seam

Change `ShopifyOfflineSessionReader.read(shopDomain, signal)` to return `Promise<{accessToken: string; scope: string | null} | null>`. Keep the same existing `session.findFirst` ownership query:

```typescript
{
  where: {shop: shopDomain, isOnline: false},
  select: {shop: true, isOnline: true, accessToken: true, scope: true}
}
```

Validate shop/isOnline/token exactly as before. Scope is a string of at most 4096 characters or null; an invalid type or control character (`[\u0000-\u001F\u007F]`) is a hard session-validation error. Preserve a blank string so preflight can classify it as absent permission. Retain the original Prisma cause when wrapping a database read failure. Do not log/return token or scope contents, and do not make a second scope query or credential cache.

Add only `requiredScope?: "read_legal_policies"` to `ShopifyAdminGraphqlRequest`. The resolver and provider reject any other value/extra key; copy this value when forwarding the request. Only the fixed policy adapter sets it. No model schema, authored argument mapping or generic header exposes it.

After validating the document and paired session and before fetch, the provider checks this exact scope against comma-separated, trimmed tokens in the paired scope string. Null, blank or an otherwise valid list lacking the exact `read_legal_policies` token throws `ShopifyPolicyScopeNotGrantedError`, a private `McpRequestError` subtype constructed with code FORBIDDEN, status 403, retryable false and reason `MCP_SHOPIFY_POLICY_SCOPE_NOT_GRANTED`. Construct this subtype only at this positive preflight check; distinguish it with `instanceof`, not reason-message parsing. The resolver preserves it because it is an McpRequestError. The shipping adapter catches it **only around its policy request** and produces SCOPE_NOT_GRANTED. Every other error propagates normally.

No policy HTTP request occurs in that branch. The existing call-scoped provider-budget reservation still occurs at the resolver's admitted read attempt; do not redesign budget charging to turn a missing scope into an unlimited operation. Expected scope absence is not a failed-provider log. A missing session, invalid token/scope value, DB exception, tenant denial or deadline is hard. Once a query is attempted, HTTP 401/403, GraphQL errors, throttling, response overflow and fetch failures cannot instantiate this private preflight subtype.

Ordinary Admin calls omit requiredScope and continue using the same paired session token without a legal-policy check. Update all session mocks/callers atomically; do not keep a second token-only reader interface.

### 3. Fixed Shopify query documents and mapping

Use exactly these three documents through the real resolver/provider, one operation per request:

```graphql
query CommerceShippingPolicy {
  shop {
    primaryDomain { url }
    shopPolicies { type title body url updatedAt }
  }
}
```

```graphql
query CommerceShippingProduct($productId: ID!) {
  product(id: $productId) { id }
}
```

```graphql
query CommerceShippingVariant($variantId: ID!) {
  productVariant(id: $variantId) {
    id
    product { id }
    inventoryItem {
      requiresShipping
      measurement { weight { value unit } }
    }
  }
}
```

The product-only query proves existence and exact ID before VARIANT_REQUIRED. The variant query proves both exact native IDs; do not fetch/select a first variant or make an additional parent query. Parse a null root product/productVariant as NOT_FOUND. A non-null variant must have its queried product and inventoryItem/measurement structure; `requiresShipping` must be the native boolean. Weight null remains unknown; a non-null weight must have a finite nonnegative value and one of GRAMS/KILOGRAMS/OUNCES/POUNDS. Project those values unchanged. Set virtual, dimensions, shippingClassId and shippingClassSlug null.

A call makes at most two Shopify GraphQL read attempts: one product/variant alternative, then one policy attempt; policy-only makes at most one. Keep Admin version 2026-07, the document guard's depth/field/literal bounds and all existing transport/time/response limits. These documents require no pagination, guard bypass, extra permission discovery query or schema regeneration. Product reads do not require the optional policy scope. The accepted Shopify configuration is reused; MCP neither changes scopes nor initiates OAuth.

### 4. Policy selection and exact successful states

The Shopify policy response must contain a valid shop object and shopPolicies array. Select the entry whose type is exactly SHIPPING_POLICY. More than one matching policy is an invalid response; do not pick whichever comes first. Do not substitute another legal policy or Storefront's `shop.shippingPolicy` field.

For a selected native policy, validate the queried fields: body/title are strings, url is a valid current-shop HTTPS URL, and updatedAt is a valid source ISO timestamp. Blank title maps to null; a nonblank title must fit 512 characters and is preserved. Missing/null/malformed queried required fields are malformed provider data, not ordinary absence. Verify the primary domain is itself a valid HTTPS URL without credentials/nondefault port before using its hostname as an additional allowed policy host; otherwise do not expand the authenticated-shop host set. Never guess a `/policies/shipping-policy` URL, normalize an unsafe value into one or fetch the returned URL.

| Policy observation | Frozen output |
| --- | --- |
| Successful authorized read with no SHIPPING_POLICY entry | status NOT_CONFIGURED; trust UNTRUSTED_REFERENCE; bodyStatus NOT_AVAILABLE; title/bodyHtml/url/updatedAt null. |
| Private missing-scope preflight subtype | Same null payload, status SCOPE_NOT_GRANTED; zero policy HTTP calls. |
| Woo native provider | Same null payload, status UNSUPPORTED; zero policy HTTP calls. |
| Existing policy whose `body.trim()` is empty | status AVAILABLE; bodyStatus EMPTY; bodyHtml null; retain verified URL, nullable title and source timestamp. |
| Existing nonblank body within both limits | status AVAILABLE; bodyStatus AVAILABLE; preserve exact original bodyHtml bytes. |
| Existing nonblank body exceeds either limit | status AVAILABLE; bodyStatus TOO_LARGE; bodyHtml null; retain verified URL/title/timestamp. |

The selected-body limits are 8000 JavaScript string code units (the installed Shared string-length check) and 16384 UTF-8 bytes. Check both; do not trim or truncate a nonblank retained body. Whole-provider response overflow stays hard under the existing transport bound and is never TOO_LARGE. Preserve all required nullable fields. Validate with `CommerceShippingInformationSchema` after the adapter's cross-field/UTF-8 rules; do not copy a local public schema.

`UNTRUSTED_REFERENCE` applies to all states. Policy HTML is inert source data: no execution, link following, fetch, translation guess, new customer intent or permission. Background owns any qualified customer wording and the separately entitled Merchant Knowledge path.

### 5. Fixed Woo exact projections and normalization

Add `projection?: "SHIPPING"` only to private `products.retrieve` and `products.variations.retrieve` request branches. Preserve the ordinary request when it is absent. Update strict checks in `connections/resolver.ts:validWooProductRead`, `woocommerce/provider.ts:approvedRequest` and `direct-product-reader.ts:validRequest`; a list request, false/arbitrary projection or unknown key is rejected before transport.

`pathFor` uses the existing authenticated exact endpoint with `context=view` and these fixed `_fields`:

```text
products.retrieve + SHIPPING:
  id,type,virtual,shipping_required,weight,dimensions,shipping_class,shipping_class_id
products.variations.retrieve + SHIPPING:
  id,parent_id,virtual,weight,dimensions,shipping_class,shipping_class_id
```

No model-selected field list, settings endpoint or new credential. `parent_id` remains optional native data: request/projection compatibility does not make it required in a returned variation. For a variation request, first retrieve and verify its parent with SHIPPING projection, require type variable, then retrieve the requested variation from that parent-scoped endpoint. At most two native exact reads occur. The parent response proves the parent; the endpoint plus exact returned variation ID proves the relationship when parent_id is absent. If present, validate it with the native ID parser and require equality. Never use unchecked caller parent ID alone as evidence.

For simple products, requiresShipping comes only from a returned boolean shipping_required; virtual comes only from its returned boolean. For variations, requiresShipping is always null: neither a false virtual flag nor a parent shipping flag establishes the filterable effective requirement. Preserve a returned virtual boolean independently. Missing/null optional native booleans map to null; a supplied nonboolean is malformed. Do not request/synthesize variation shipping_required.

Normalize measurements with a shared **private helper in this shipping adapter**, not a general conversion package. Missing/null/empty-string values map to null; otherwise require a string matching `^[0-9]+(?:\.[0-9]+)?$`, convert to Number and require a finite value. Reject whitespace/exponent/sign/comma/hex/negative/nonstring values; zero is a known value. A null weight maps to null; otherwise emit `{value, unit:null}`. A missing/null dimensions object yields null; when present it must be an object with length/width/height processed by that helper. Return dimensions null when all three are null, otherwise preserve each nullable component with unit null. Never derive units from locale, schema descriptions, names or defaults.

Normalize shipping_class_id missing/null/0 to null; otherwise require a positive safe native integer and return its decimal string. A malformed/negative/fractional ID is an error. shipping_class missing/null/empty string maps to null; otherwise require a string within 512 characters and preserve it. Use the exact endpoint-returned variation values/classes; do not invent a second inheritance layer or class description/rate. Root provider is WOOCOMMERCE and policy is the no-read UNSUPPORTED object above.

### 6. Real registry, rendering and failure preservation

In `shopify-core-executor.ts`, add shipping to `SHOPIFY_CORE_OUTPUT_SCHEMAS`, `allowedKeys`, `CoreOperation`, supported-provider checks, input-validator selection, dispatch and output-validator selection. The allowed mapped keys are exactly productId/variantId. `supportsConfiguredShopifyCoreExecutor` must classify it with exact get/basket as **not requiring COMMERCE_CURSOR_SECRET**. Resolve the existing current shop connection before the adapter; both Shopify and Woo are supported. Use the same already registered core handler, not a standalone handler omitted from `createShopifyServicePorts` and not a third discount built-in.

The short standard shipping template is exactly `Shipping information checked.` with unavailable text `Shipping information unavailable.`; Commerce publishes these same strings. Construct the private shipping template-path entry with the existing `object`/`str` helpers, mirroring the full Shared non-null field tree and required keys; nullable fields use their non-null path type and each string bound is `Math.min(4096, sharedMaxLength)`. In particular, bodyHtml has private path metadata maxLength 4096, matching Commerce's existing projector. This entry is path/type metadata, not a replacement for the actual Shared wire validator; never apply its string clamp to returned data. No bodyHtml interpolation, 8000-character renderedText or result-size-limit widening is needed. An 8000-character qualified body remains intact in structured data after Shared validation; renderPolicyResult must not truncate/rewrite it. Keep isError/outer-status equality and both MCP result representations aligned.

Missing policy scope/configuration, unsupported Woo native policy and a blank/oversized selected body are normal data only after authenticated shop, active plan, published-capability and provider-connection checks pass. They never remove the shipping descriptor, disable ordinary product tools or authorize Merchant Knowledge. Within this invocation, a product/provider failure cannot be overwritten by a subsequent policy read. MCP does not read conversation state, workflow grants, inbound versions or leases; Background owns those checks.

Use the already accepted Shared structured logger and original source-error handling. For new session/parse failures retain the original safe error/cause at the owning boundary with operation/stage and a separate Moda reason; no raw credential/scope/policy/customer bodies in logs or output. Do not rebuild the accepted Woo logger or disguise HTTP/GraphQL 401/403 as a missing-scope normal result. Logger failures remain isolated from tool behavior.

## Work Items

- [x] Verify the prepared accepted MCP-002 base and exact published shipping exports; reuse completed Shopify scope work.
- [x] Change paired-session/request interfaces, all strict guards and provider preflight together.
- [x] Implement the fixed Shopify documents and Woo exact SHIPPING projections with the selected mappings/errors.
- [x] Register, dispatch, validate and render shipping through the existing production core executor without a cursor-secret requirement.
- [x] Run the focused real-boundary tests, record actual outcomes and submit for architect review.

## Interfaces / Contracts

Public owner after accepted SHARED-006 publication is `@modainteract/moda-interact-shared/commerce@5.0.0`: `CommerceShippingInformationInputSchema`, `CommerceShippingInformationSchema`, inferred types and both `commerce_get_shipping_information` dictionary entries. `docs/architecture/ARCH-058/contracts.md` section 2.3 remains normative. No wire/status/field/version choice is left open in this task.

Provider references: [Admin 2026-07 ShopPolicy](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPolicy) requires read_legal_policies and supplies policy fields; [InventoryItem](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItem) / [measurement](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItemMeasurement) supply exact variant shipping fields. [Woo products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/) and [variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/) have different field sets; the variation contract does not establish shipping_required or units. These are schema/semantics references, not live merchant execution evidence.

## Dependencies

- `ARCH-058-MCP-002`: accepted provider/search/generic shop-catalogue/diagnostic composition, canonical descriptor identity and bounded tool execution, with its already installed Shared/Database artifacts. No conversation context, retained-grant lookup or lease check belongs to this prerequisite.
- `ARCH-058-SHOPIFY-001`: completed declared-scope configuration and existing grant-lifecycle runbook. No live grant is inferred from this acceptance.

## Enables

- `ARCH-058-COMMERCE-001`: publish all four executable standard tools and exact short shipping template.
- `ARCH-058-BACKGROUND-001`: qualify shipping responses and recommendations through its existing host.
- `ARCH-058-SYSTEM-TEST-001`: exercise native scope/absence/unsupported states through real service boundaries after all prerequisites.

## Acceptance Criteria

- [x] Both providers list and execute the pinned published shipping tool through the actual registry; it works without a cursor secret and preserves current authenticated-shop, active-plan, published-capability and provider-permission checks.
- [x] Invalid request shape/native IDs fail before provider I/O; an unsupported Woo type or simple-product variation request fails after its one necessary parent read. The selected product/policy ordering and maximum read counts are observed.
- [x] The exact offline select returns paired token/scope; only the private positive scope-preflight outcome yields SCOPE_NOT_GRANTED and zero policy fetches. Attempted authorization/provider failures stay outer errors.
- [x] Product-only requests verify existence then return VARIANT_REQUIRED where specified; exact identities, optional Woo parent_id and native facts follow the mapping table.
- [x] Policy states/nullability/UTF-8 limits and Woo measurement/class/unknown-unit rules exactly match the contract, without guesses or truncation.
- [x] Qualified structured HTML survives the real rendering/result route unchanged while the standard renderedText remains the fixed short string; unsafe/instructional content is not executed or fetched.
- [x] Ordinary product definitions/output, accepted diagnostics, provider credential/read-permission validation and typed errors remain intact. No live quote, extra page/settings read, environment mutation or customer send is introduced.

## Validation

Use the launcher worktree and its preparation evidence. Before Node use `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. These are bounded agent-owned fixture checks; no live credential or merchant store is required.

Add `tests/unit/execution/policy/shipping-information.test.ts` for native mapping and `shipping-information-composition.test.ts` for real execution. The latter must construct the actual `createMcpService`/service ports/registered executor/resolver/provider/document guard and result renderer, injecting only HTTP/session/Prisma fixtures and clock. Stubbing adminGraphql or returning an already normalized shipping object is insufficient. Use the generic capability-reader fixture without conversation/workflow-grant delegates and verify that absent versus irrelevant opaque toolContext leaves shipping authorization and facts unchanged.

```bash
npm exec -- tsx --test tests/unit/execution/policy/shipping-information.test.ts tests/unit/execution/policy/shipping-information-composition.test.ts tests/unit/execution/policy/shopify-core.test.ts
npm exec -- tsx --test tests/unit/connections/shopify/session-reader.test.ts tests/unit/connections/shopify/provider.test.ts tests/unit/connections/shopify/document.test.ts tests/unit/connections/resolver.test.ts tests/unit/connections/woocommerce/direct-product-reader.test.ts tests/unit/connections/woocommerce/provider.test.ts tests/unit/runtime/ports.test.ts tests/unit/runtime/prisma.test.ts tests/unit/runtime/service-ports.test.ts tests/unit/mcp/capability-invocation.test.ts tests/unit/mcp/structured-results.test.ts
npm run typecheck
npm run typecheck:integration
npm run lint
npm run build
git diff --check
```

The fixtures must include:

- Policy-only; verified product-only; exact physical/virtual variant; Woo simple/variable/custom/grouped/external; nonexistent/wrong product/variant; inactive/wrong shop, inactive plan, revoked native provider permission and no cursor secret. Assert precise errors, IDs and zero/one/two provider read counts.
- Exact paired offline select; null/blank/unrelated scope; matching token/scope row; invalid scope/token/session; missing scope with independently valid product; granted HTTP 401/403/GraphQL failure; cancellation and DB failure. Only the private preflight subtype may produce normal missing-scope data.
- No policy versus one empty policy; duplicate SHIPPING_POLICY entries; nonblank exact HTML; character bounds 7999/8000/8001 and multibyte UTF-8 bounds 16383/16384/16385; TOO_LARGE retains safe URL/title/timestamp; whole-response overflow is hard. Unsafe/foreign/custom-domain URL, bad timestamp and malformed required fields remain hard. Script/instruction/link text stays inert and causes zero follow-on fetches.
- Woo missing/null/empty/zero/decimal measurements; malformed/sign/exponent/negative/nonstring values; partial/all-unknown dimensions; class 0/null/positive/negative/fractional; missing/blank/oversized slug; absent/matching/conflicting parent_id; effective variation values without a second parent inheritance read. Variation virtual false must still produce requiresShipping null and unit null.
- A valid bodyHtml longer than 4096 and within 8000 passes the full provider→Shared→renderer→MCP result path byte-for-byte, with exactly the short standard renderedText. Published product outputs remain unchanged.
- Actual Shared logger sink assertions for distinct HTTP/GraphQL/SDK/Prisma sources with redaction sentinels. Preserve source messages/codes safely, no credential/scope/policy payload leakage, and logger-failure isolation.

Record exact commands, exit outcomes, prepared worktree/HEAD, package version and database gitlink. These tests prove adapter behavior; live selected-app deployment, merchant approval/granted permission and real merchant responses remain operator checks under the completed Shopify runbook and are NOT_RUN unless actually performed. This task does not require another autonomous Docker suite; terminal integration remains separately owned.

## Stop Condition

Stop if the prepared MCP-002 source/artifact gate is absent, the installed published schema differs, the selected native field/query cannot be validated against the pinned schema, or implementation would need a new settings/cart/credential/Shared/Database contract. Report the exact observed mismatch and owner. After scoped implementation and required fast checks, complete the report, set status to `review`, return to the architect and stop. Do not mark complete, publish tools, deploy, change another repository or send a customer message.

## Implementation Notes

Native facts and policy availability are independent within one qualified response. Scope absence is established before HTTP by the credential owner; it is not inferred from a provider failure. Product shipping requirement/measurement does not establish a destination rate or delivery time, and a policy URL does not establish a quote. Background owns the final qualified wording and any verified recommendation.

## Completion Report

### Status

Attempt 1 submitted for architect review. Implementation `69b64669a621c899f3b764fb92004f27f249b9e7` is committed and pushed to `origin/task/ARCH-058-MCP-003`. Status is Review, claim cleared, Attempt 1 preserved. No architect acceptance, deployment or live merchant verification is claimed.

### Files Changed and Work Completed

- Added `src/execution/policy/shipping-information.ts`: the three fixed named Admin queries, exact product/variant identity checks, product-before-policy ordering, native Shopify facts, Woo simple/variable mappings, private decimal measurement/class normalization, independent policy outcomes and both policy body limits. Successful undefined/null policy responses remain malformed; only the private scope-preflight subtype produces SCOPE_NOT_GRANTED.
- Extended the registered core executor with shipping input/output/template-path metadata, real connection resolution, both provider branches and no cursor-secret requirement. Shared validates actual returned data; a 7000-plus-character inert body survives the real MCP/renderer route unchanged while renderedText remains `Shipping information checked.`. Exported existing safeStoreUrl unchanged for reuse; no product query/output/cursor behavior changed.
- Paired Shopify offline token/scope comes from the same existing select. Scope and token are bounded/validated. The provider performs exact comma-token policy-scope preflight before fetch; ordinary calls omit it. The resolver preserves the private subtype and existing admitted-read budget charging. Original session DB causes survive wrapping and are safely diagnosed at the provider boundary. All existing token-only session fixtures were updated.
- Added private SHIPPING on the two Woo exact operations and all three strict guards. The real direct credential reader uses only the prescribed parent/variation endpoint projections; list requests do not gain the flag. Parent/optional parent_id identity is checked, variation requiresShipping remains null, and units are never inferred.
- Reused existing Shared logging and the existing safe domain diagnostic projection for adapter validation; no generic serializer/logger was introduced. Tests capture actual Shared output for HTTP/GraphQL/SDK/Prisma and native validation, retained source/cause/code/request ID, privacy sentinels, nonmutation of thrown source exceptions and failing sinks. Provider diagnostics are not relabelled as missing-scope success.
- Added the two declared focused shipping test modules and updated session/provider/product-composition fixtures. New modules are below 300 physical lines. Runtime ports/Prisma composition already consume the paired reader structurally and required no parallel reader or second handler. No package, lockfile, schema, dependency, credential format, other repository or parent gitlink changed.

### Validation Results

Node 24.19.0/npm 11.17.0 from the workspace bootstrap; Prisma 6.19.3, exact Shared 5.0.0 and runner 1.1.0 retained. All checks ran in the dedicated implementation worktree.

- `npm ci --no-audit --no-fund`: passed; locked dependencies installed for this new worktree.
- `npm run schema:install:shopify -- /Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce/lib/discovery/artifacts/admin-2026-07.json`: passed from the approved local artifact; SHA256 gate `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`. No schema download/regeneration.
- Exact required shipping/core command: **59 tests passed**, zero failures/skips. Covers native identity/ordering/errors, actual registry/provider/renderer for both providers, no cursor secret, irrelevant opaque contexts, native scope absence, body/UTF-8 bounds and raw HTML preservation, measurement/class normalization, cancellation, original source diagnostics and sink isolation.
- Exact required provider/resolver/runtime/protocol command: **71 tests passed**, zero failures/skips. Existing ordinary product and transport regressions remain covered; these 71 are not counted as additional shipping-only cases.
- `npm run typecheck`, `npm run typecheck:integration`, `npm run lint`, `npm run build`: passed on final source. Final affected-source checks were rerun after diff review caught and corrected an undefined-policy-payload sentinel edge. Initial implementation type/lint errors were fixed and are not presented as baseline limitations.
- `git diff --check`: passed before commit.
- All three fixed queries pass the real document guard/provider paths and pinned Admin schema validation in composition. Shopify AI Toolkit documentation search and schema validation also passed for the three Admin 2026-07 queries; policy validator reports read_legal_policies, product/variant validators report native product/inventory scope requirements. Toolkit telemetry was opted out.

Final local evidence logs: `/tmp/mcp003-shipping-release.log` (59), `/tmp/mcp003-regressions-final.log` (71), `/tmp/mcp003-types-release.log`, `/tmp/mcp003-integration-types-release.log`, `/tmp/mcp003-lint-release.log`, `/tmp/mcp003-build-release.log`, `/tmp/mcp003-toolkit-search.log`, `/tmp/mcp003-toolkit-validate.log`, `/tmp/mcp003-toolkit-product.log`, `/tmp/mcp003-toolkit-variant.log`. These local logs are not committed artifacts.

### Limits, Deviations and Unresolved Issues

No implementation-scope deviation or known blocker. The task does not require an autonomous Docker suite; none was run. No live provider/merchant response, selected-app deployment, granted live policy permission, tool publication, settings/cart mutation, quote calculation or customer send was performed. Those remain operator/consumer/terminal system-validation checks; fixture success is not a live grant or production compatibility claim.

Source references used by the toolkit: [ShopPolicy](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPolicy) and [InventoryItemMeasurement](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItemMeasurement). The supplied fixed queries and approved artifact remain the execution contract.

### Physical Worktree and Synchronization Evidence

```text
canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-MCP-003
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-003
both branches: task/ARCH-058-MCP-003
parent prepared head: 4a920137d95abe443a09a3522930aa0a8dc6f466
implementation prepared head: c22148dbcb38d2462ff7e59fc16b599f6ba83c7c
claim: 2a4ae9eae12b910df12cd3cdab2b6438206e1106; pushed
claim executor/time: codex / 2026-11-05T08:12:53Z; Attempt 1
parent/implementation worktrees: newly created by launcher
parent/implementation remote task fast-forward: not-needed
parent/implementation origin/main incorporation: already-current
dependency gate: MCP-002 and SHOPIFY-001 Complete
recursive submodule sync/update/init/verification: passed; ready
recorded/working Database pin: bd2d09066a8eb178a56f48fbbf88df637c411059 (unchanged)
implementation submitted: 69b64669a621c899f3b764fb92004f27f249b9e7; pushed
shared/default checkouts switched or mutated for implementation: no
another task worktree reused: no
```

No second preparation/claim, main merge/push, parent gitlink update or downstream task execution. The parent submission changes only this task report/state; architect review/reconciliation history below is preserved.

### Architectural Concerns

No new cross-repository requirement. Background retains conversation/lease/grant/human-control ownership; MCP shipping reads only the authenticated shop/provider and exact requested native facts. Commerce publication and consumer adoption remain separately owned.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not assessed.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Architect Dependency Gate — MCP-002 Attempt 2 (2026-11-04)

MCP-002 remains in Review, not Complete or accepted, at implementation `b95c397d840568a5481c9332517e6ee3dc3713e1`. Its required developer-owned disposable PostgreSQL validation is NOT_RUN. This task remains Pending with its existing dependency list, attempt and claim unchanged; do not execute it until all explicit prerequisites are Complete and architect-accepted. Independent MCP-002 unit checks passed but do not replace the database acceptance gate.

## Architect Dependency Reconciliation — 5 November 2026

MCP-002 Attempt 3 is architect-accepted and Complete at `11fba27`, with developer PostgreSQL evidence of 30 passed, 0 failed and 1 opt-in live test skipped. This supersedes the earlier pending-validation gate note. All explicit prerequisites (MCP-002 and SHOPIFY-001) are Complete. Promoted to Ready, Attempt 0 preserved, no executor/claim. No execution is started.

## Architect Acceptance — 5 November 2026

**Accepted — Attempt 1.** Reviewed implementation `69b64669a621c899f3b764fb92004f27f249b9e7` and parent submission `75e2315fae144e4707dea4d75bedace53c18a753`. No blocking findings identified. Task marked Complete under automatic completion mode; Attempt 1 preserved and executor/claim remain empty. This supersedes the earlier pending review and pre-execution snapshots.

### Source Review and Conformance

Reviewed shipping adapter, paired offline-session/scope validation, provider preflight and strict request/projection guards, existing core-executor registration/rendering, native mappings, source diagnostics and real composition tests against the task contract. Tenant/provider authorization remains authoritative; only the private missing-scope preflight subtype becomes SCOPE_NOT_GRANTED, while attempted provider failures remain outer errors. Product facts precede policy work, exact native identities and Woo parent relationships are checked, units are not guessed, and policy HTML remains inert structured source data. The shipping operation uses the existing published executor without requiring a cursor secret. No blocking implementation defect was identified in inspected paths.

### Independent Validation and Limits

Independently reran the exact required shipping/core command with the prescribed Node bootstrap:

```bash
npm exec -- tsx --test tests/unit/execution/policy/shipping-information.test.ts tests/unit/execution/policy/shipping-information-composition.test.ts tests/unit/execution/policy/shopify-core.test.ts
```

**59/59 tests passed**, zero failures/skips. Implementation comparison whitespace check passed and checkout was clean. Local independent log: `/tmp/mcp003-architect-review.log` (not a committed artifact).

Reviewed the submitted **71 provider/resolver/runtime/protocol regression passes**, main/integration typechecks, lint, build and all three fixed-query validations. Those were not rerun during this architect review. Native fields and long policy-body preservation are exercised through actual service/registry/resolver/provider/renderer paths with controlled transports. Live merchant approval/grants, provider responses and deployment remain NOT_RUN operator checks; this acceptance makes no live-store or system-wide readiness claim. No additional Docker suite is required by this bounded task.

### Isolation and Downstream

Reviewed the prepared worktree/synchronization evidence. Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-MCP-003`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-003`, both on `task/ARCH-058-MCP-003`. No implementation source, schema, dependency, gitlink or main branch is changed by this review.

COMMERCE-001 now has all three explicit prerequisites Complete: MCP-002, MCP-003 and SHARED-006. Promoted to Ready at Attempt 0 with empty executor/claim. BACKGROUND-001 remains Pending on COMMERCE-001, and SYSTEM-TEST-001 retains its remaining consumer prerequisites. No downstream task is executed; ARCH-058 remains incomplete until its required consumer/system validation is accepted. The known optional Commerce projection compatibility issue remains a consumer-validation coordination item.

The developer explicitly authorized committing/pushing acceptance and downstream reconciliation on 5 November 2026.
