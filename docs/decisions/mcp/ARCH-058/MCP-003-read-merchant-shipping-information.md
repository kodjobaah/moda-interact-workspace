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
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-058-MCP-002
- ARCH-058-SHOPIFY-001
enables:
- ARCH-058-COMMERCE-001
- ARCH-058-BACKGROUND-001
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-058-MCP-003: Read native merchant shipping policy and exact product shipping facts

## Architecture

Architecture ID: `ARCH-058`. Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Normative contracts: `docs/architecture/ARCH-058/contracts.md`, especially section 2.3. Coordinator: `moda_architect`.

**Defined but not materialised.** This portable definition does not establish a task branch, worktree, commit, installed merchant grant, published tool or successful provider call. Materialise through `/moda-task ARCH-058-MCP-003 --definition <path-to-this-file>`; use the implementation worktree and canonical workspace root supplied by that launcher.

## Objective

Add `commerce_get_shipping_information` definition **1.0.0**, operation `shipping.getInformation` **1.0.0**, to the existing published policy executor. Return the current store's native shipping policy and exact requested product/variant facts through the already authorized Shopify/Woo connections. This task implements the selected private interfaces and mappings below; the public Shared 4.0.0 contract is already complete.

## Context

The [execution baseline](../../../architecture/ARCH-058/execution-baseline.json) and [implementation handoff](../../../architecture/ARCH-058/implementation-handoff.md) record the accepted prerequisites. SHARED-001/002 and SHOPIFY-001 are Complete; do not implement/publish them again. The Shopify scope task accepted `c3b580cec5acc46e5c53386dd94279ad97b02ee9`; its configuration acceptance does not establish a live merchant grant.

The 09:49:47 snapshot has three specific missing seams: `ShopifyOfflineSessionReader.read` returns only a token; the resolver's GraphQL request allowlist drops any other key; and both Woo exact-read guards/projections omit shipping fields. `shopify-core-executor.ts` also assumes every non-basket/non-get policy operation is search and requires a cursor secret. Registering an authoring operation alone cannot execute shipping.

## Scope

Only `moda-interact-mcp`, its tests and this report. Consume accepted MCP-002 as the task base and keep its product, catalogue, conversation-context, original-error and built-in identity changes. Shared package remains exact **4.0.0**, runner **1.1.0**; do not select another version, regenerate taxonomy, edit database schema or update the completed Shopify task.

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

Use the existing `commerce.v1` envelope, typed error enum, result-byte limit and terminal-referral behavior. Do not return model-authored shipping prose or eligibility judgments.

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

Missing policy scope/configuration, unsupported Woo native policy and a blank/oversized selected body are normal data only after current shop/turn/grant/capability checks pass. They never remove the shipping descriptor, mutate a retained grant, disable ordinary product tools or authorize Merchant Knowledge. A terminal provider error remains terminal through any later successful read.

Use the already accepted Shared structured logger and original source-error handling. For new session/parse failures retain the original safe error/cause at the owning boundary with operation/stage and a separate Moda reason; no raw credential/scope/policy/customer bodies in logs or output. Do not rebuild the accepted Woo logger or disguise HTTP/GraphQL 401/403 as a missing-scope normal result. Logger failures remain isolated from tool behavior.

## Work Items

- [ ] Verify the prepared accepted MCP-002 base and exact published shipping exports; reuse completed Shopify scope work.
- [ ] Change paired-session/request interfaces, all strict guards and provider preflight together.
- [ ] Implement the fixed Shopify documents and Woo exact SHIPPING projections with the selected mappings/errors.
- [ ] Register, dispatch, validate and render shipping through the existing production core executor without a cursor-secret requirement.
- [ ] Run the focused real-boundary tests, record actual outcomes and submit for architect review.

## Interfaces / Contracts

Public owner is the already published `@modainteract/moda-interact-shared/commerce@4.0.0`: `CommerceShippingInformationInputSchema`, `CommerceShippingInformationSchema`, inferred types and both `commerce_get_shipping_information` dictionary entries. `docs/architecture/ARCH-058/contracts.md` section 2.3 remains normative. No wire/status/field/version choice is left open in this task.

Provider references: [Admin 2026-07 ShopPolicy](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPolicy) requires read_legal_policies and supplies policy fields; [InventoryItem](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItem) / [measurement](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItemMeasurement) supply exact variant shipping fields. [Woo products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/) and [variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/) have different field sets; the variation contract does not establish shipping_required or units. These are schema/semantics references, not live merchant execution evidence.

## Dependencies

- `ARCH-058-MCP-002`: accepted provider/search/context/catalogue/diagnostic composition and its already installed Shared/Database artifacts.
- `ARCH-058-SHOPIFY-001`: completed declared-scope configuration and existing grant-lifecycle runbook. No live grant is inferred from this acceptance.

## Enables

- `ARCH-058-COMMERCE-001`: publish all four executable standard tools and exact short shipping template.
- `ARCH-058-BACKGROUND-001`: qualify shipping responses and recommendations through its existing host.
- `ARCH-058-SYSTEM-TEST-001`: exercise native scope/absence/unsupported states through real service boundaries after all prerequisites.

## Acceptance Criteria

- [ ] Both providers list and execute the pinned published shipping tool through the actual registry; it works without a cursor secret and preserves current shop/turn/grant/entitlement checks.
- [ ] Invalid input makes zero provider calls; the selected product/policy ordering and maximum Shopify/Woo read counts are observed.
- [ ] The exact offline select returns paired token/scope; only the private positive scope-preflight outcome yields SCOPE_NOT_GRANTED and zero policy fetches. Attempted authorization/provider failures stay outer errors.
- [ ] Product-only requests verify existence then return VARIANT_REQUIRED where specified; exact identities, optional Woo parent_id and native facts follow the mapping table.
- [ ] Policy states/nullability/UTF-8 limits and Woo measurement/class/unknown-unit rules exactly match the contract, without guesses or truncation.
- [ ] Qualified structured HTML survives the real rendering/result route unchanged while the standard renderedText remains the fixed short string; unsafe/instructional content is not executed or fetched.
- [ ] Ordinary product definitions/output, accepted diagnostics, grant identity and terminal error behavior remain intact. No live quote, extra page/settings read, environment mutation or customer send is introduced.

## Validation

Use the launcher worktree and its preparation evidence. Before Node use `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. These are bounded agent-owned fixture checks; no live credential or merchant store is required.

Add `tests/unit/execution/policy/shipping-information.test.ts` for native mapping and `shipping-information-composition.test.ts` for real execution. The latter must construct the actual `createMcpService`/service ports/registered executor/resolver/provider/document guard and result renderer, injecting only HTTP/session/Prisma fixtures and clock. Stubbing adminGraphql or returning an already normalized shipping object is insufficient.

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

- Policy-only; verified product-only; exact physical/virtual variant; Woo simple/variable/custom/grouped/external; nonexistent/wrong product/variant; stale/expired/wrong-shop grant and no cursor secret. Assert precise errors, IDs and zero/one/two provider read counts.
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

Shared 4.0.0 and Shopify scope configuration are already accepted. This task consumes the accepted MCP-002 base; configuration acceptance is not a live offline grant, and Woo measurement units remain unknown.

### Unresolved Issues

No live merchant grant, policy, product response or deployment has been verified by this definition. Unsupported native Woo policy and absent measurement units are explicit contract limits.

### Physical Worktree and Synchronization Evidence

Not materialised. Record the actual launcher preparation packet, canonical parent/implementation worktrees and start-of-attempt synchronization when execution begins; do not invent them here.

### Architectural Concerns

None beyond the explicit contract, scope-provenance, provider-semantics and failure-boundary gates above.

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
