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

Execute the fourth standard product capability, `commerce_get_shipping_information`, through existing tenant-bound provider reads, returning independently qualified native policy and exact product shipping facts. Expected policy absence must remain usable information without disabling ordinary product discovery or erasing actual authorization/provider failures.

## Context

- `src/execution/policy/shopify-core.ts` supplies current product reads but no shipping facts. ARCH-058-MCP-002 extends search/discount execution and preserves the ordinary product output contracts; this task adds a separate read operation.
- `src/connections/shopify/provider.ts` pins Admin `2026-07`, uses the real read-only document guard and owns token access, request/response bounds and source-error logging. Its session reader currently returns only an access token even though the existing `shopify.Session.scope` column contains the persisted grant.
- Shopify Admin policy access is `shop.shopPolicies` filtered in trusted code to `SHIPPING_POLICY`, and requires `read_legal_policies`. `shop.shippingPolicy` is a different Storefront field. Variant shipping facts come from `inventoryItem.requiresShipping` and `inventoryItem.measurement.weight`; existing product-read permission is sufficient.
- `src/connections/woocommerce/direct-product-reader.ts` and `provider.ts` already own authorized bounded product/variation reads. Their requested projections omit shipping fields. Woo product and variation payloads differ, and their measurement values do not establish units from the existing context.
- A selected policy body can exceed the new model-facing bound even when the provider response fits the transport budget. An absent policy, ungranted policy scope, oversized selected body and failed provider request are distinct outcomes.

## Scope

In `moda-interact-mcp` only:

1. Register and execute the frozen `shipping.getInformation` policy operation `1.0.0` for `commerce_get_shipping_information` definition `1.0.0` through the existing published-capability registry.
2. Read Shopify native policy and exact variant shipping facts with trusted offline-scope preflight, preserving ordinary product-query behavior.
3. Add bounded Woo shipping projections through existing product/variation reads and normalize only actually observed fields; native Woo policy remains explicitly unsupported.
4. Validate the exact Shared shipping input/output, including independent policy/product states, HTML trust/bounds, current-shop identities and actual error semantics.
5. Exercise the composed provider, query-guard, capability and result-rendering boundaries with deterministic fixtures and redacted original-error evidence.

## Out of Scope

No Shopify app scope configuration, Shared implementation/publication, Commerce authoring/publication, Background response composition, Database schema/migration, Admin/Gateway/API/Woo plugin implementation, policy mirror/vector ingestion, new Merchant Knowledge entitlement, crawl/URL fetch, shipping-zone/profile scan, rate calculator, Storefront/Store API cart, cart/address/checkout mutation, coupon application, promised ETA, live shipping quote or customer send. Do not change existing product get/search output schemas, republish `commerce_get_product`, revive a discount proof engine, edit accepted task histories or modify decision indexes.

## Requirements

### Accepted source and frozen contract

- Reconcile the accepted MCP-002 provider, cursor, registry, discount and diagnostic implementation before extending it. Preserve its accepted changes and the Shopify task's existing installation-lifecycle contract; do not duplicate readers because a supplied snapshot differs from accepted source.
- Consume the exact package accepted and published by ARCH-058-SHARED-002, targeting `4.0.0` only while the recorded accepted source/registry baseline remains `3.1.0`. Use an architect-reconciled exact version if the baseline changed. No sibling-source import, copied wire schema or assumed local version is permitted.
- Import `CommerceShippingInformationInputSchema`, `CommerceShippingInformationSchema` and their types from `@modainteract/moda-interact-shared/commerce`; use the corresponding `CommerceToolInputs.commerce_get_shipping_information` and `CommerceToolOutputs.commerce_get_shipping_information` entries. Section 2.3 owns every public field, literal, nullability and size bound. Do not create a local competing output contract or add an unapproved status/reason field.
- Keep `commerce.v1`, its existing outer result envelope, deadline, result-byte limits and terminal error/referral rules. The tool is a published `product_search` capability, not a third discount built-in. `commerce_get_product` definition/operation remains unchanged at `1.0.0`.

### Input, registration and identity

- Accept only optional/nullable `productId` and `variantId`, each with the frozen parsed default null and ID bound. Service policy requires a product ID when a variant ID is present. Validate native Shopify GIDs or Woo positive decimal IDs; do not accept a raw query, URL, provider origin, destination, cart, scope, token or shop override.
- With no IDs, return `product.status: NOT_REQUESTED` with null IDs/facts and read only the native merchant policy when supported. Never select a product just to fill this response.
- With a Shopify product ID alone, perform a fixed bounded exact-product existence query and only then return `VARIANT_REQUIRED` with the observed product ID and null variant/facts. Do not select the first variant. A standard Woo variable parent without a requested variation follows the same rule after its verified product read.
- An available result identifies the exact observed product and requested native variant, or an observed simple Woo product with null variant ID. Validate the Shopify variant's returned product relationship and the Woo endpoint-scoped identity/any returned parent ID. Invalid IDs, nonexistent product/variant, mismatched relationships and malformed provider facts retain typed outer errors; do not echo an unchecked ID as product evidence.
- Extend `src/execution/policy/shopify-core-executor.ts` operation/output registries, strict argument mapping, operation dispatch and output validation deliberately. Keep `supportedShopifyCoreDefinition`, `hasShopifyCoreExecutor` and `supportsConfiguredShopifyCoreExecutor` consistent for both providers. This exact read must not depend on a search cursor secret.
- Register the adapter through the real `src/runtime/service-ports.ts` / existing published execution registry, not only a standalone adapter or metadata catalogue. Preserve descriptor/version/input-schema equality, current shop/connection/plan/subscription/release/turn/grant checks and the existing generic-versus-conversation context boundaries.
- The fourth descriptor stays in an otherwise valid immutable feature/grant when native policy is absent, unsupported or lacks optional policy permission. Those data outcomes do not remove all product tools, churn the manifest, grant a new capability or disable ordinary product search/get.

### Shopify offline-scope preflight and fixed queries

- Extend `src/connections/shopify/session-reader.ts` to read nullable scope and access token together from the same existing validated offline Session row. Retain canonical domain, `isOnline: false`, credential, cancellation and failure checks. No new table, scope cache or alternate source of token authority is needed. Do not expose either token or scope to the model or customer.
- Carry the narrowly typed trusted `read_legal_policies` requirement on the private connection/provider path only. Explicitly update the private request contract in `src/connections/ports.ts`, strict key validation and forwarding in `src/connections/resolver.ts`, and credential-owning preflight in `src/connections/shopify/provider.ts`. Do not accept arbitrary additional request keys, model-set permission flags or a generic caller-controlled scope list.
- Before any policy HTTP request, the provider checks that requirement against the scope paired with the token it would use. Missing/null/blank persisted permission yields a distinct internal preflight outcome that this shipping adapter alone maps to `policy.status: SCOPE_NOT_GRANTED`. The policy request count is zero in that case; an independently permitted exact-product request can still succeed.
- A missing/invalid session, tenant mismatch or failed session read is not missing policy scope. A recorded grant followed by provider 401/403, GraphQL errors, malformed data, rate limiting, cancellation or a response-budget failure remains an actual outer error. Do not convert every `UNAVAILABLE`, every `FORBIDDEN` or provider message containing a scope name into an ordinary absence.
- Keep policy and product queries separate so an expected policy-scope absence cannot suppress independent product facts. Use fixed named Admin `2026-07` queries through the real `adminGraphql` resolver/provider. The approved field selections are:

  ```graphql
  query CommerceShippingPolicy {
    shop {
      primaryDomain { url }
      shopPolicies { type title body url updatedAt }
    }
  }

  query CommerceShippingProduct($productId: ID!) {
    product(id: $productId) { id }
  }

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

  These are separate document alternatives, never a combined multi-operation request. A call uses only the required product existence or variant alternative and the permitted policy query. No query/body/host is accepted from model arguments.
- Project Shopify `requiresShipping` and any non-null native weight/unit exactly. Set `virtual`, dimensions and shipping-class fields to null. Preserve null weight; do not infer a destination, rate, fulfillment promise or product-wide requirement from these variant facts.
- Keep `inspectShopifyReadQuery` and the accepted pinned-query checks active. These documents need no relaxation of named/read-only operation, directives/fragments, field/depth or literal connection-size guards. Preserve provider request, timeout, response-byte and cancellation budgets; no hidden pagination, cross-request credential cache or retries outside existing policy.

### Policy projection, trust and size

- Project only the returned `SHIPPING_POLICY`; never substitute another legal policy or a guessed `/policies/shipping-policy` URL. Validate policy URLs against the authenticated shop and the returned primary domain using existing HTTPS, credential, host and port rules. A malformed/unsafe URL follows current provider-result validation rather than becoming a guessed valid link.
- No shipping-policy object after a successful authorized read yields `NOT_CONFIGURED`. A returned policy object yields `AVAILABLE`, including when its body is blank. Keep its valid title, URL and source `updatedAt`; do not invent an update time.
- For an available policy, a blank body yields `bodyStatus: EMPTY` and null `bodyHtml`. A nonblank body within both 8,000 characters and 16,384 UTF-8 bytes yields `bodyStatus: AVAILABLE` and preserves the exact HTML bytes. Exceeding either selected-body limit yields `bodyStatus: TOO_LARGE`, null bodyHtml and the valid URL/title/timestamp. Never silently truncate HTML or imply that an excerpt is the complete policy.
- All non-AVAILABLE policy statuses have null payload fields and `bodyStatus: NOT_AVAILABLE`. Follow the strict required-field/nullability contract rather than omitting unknown values. The whole provider response still obeys its existing transport limit; exceeding that limit is an outer error, not `TOO_LARGE`, `NOT_CONFIGURED` or permission absence.
- Always mark policy trust as `UNTRUSTED_REFERENCE`. Do not execute HTML, follow embedded links, fetch the returned URL, interpret merchant prose as instructions, infer new customer intent or append HTML to customer output. The existing Background host owns safe language-specific composition from qualified facts.
- Derive root `observedAt` from the trusted read clock. It records observation, not a guarantee of future rate/availability. Keep source update time separate and null when unavailable.

### Woo product and variation projection

- Reuse the existing verified active installation, REST read grant, credential envelope, canonical HTTPS origin, SSRF/DNS/TLS defenses and bounded exact product/variation operations. No settings endpoint, new service broker, WordPress page discovery or additional credential/permission is needed.
- Add a narrowly allowed shipping projection for exact reads through `src/connections/ports.ts`, `src/connections/resolver.ts`, `src/connections/woocommerce/provider.ts` and `src/connections/woocommerce/direct-product-reader.ts`. Keep operation/key validation aligned at every layer. Request only required identity/type and shipping fields; do not broaden arbitrary `_fields`, query grammar or model-provided URLs. Preserve existing search/product projections and public product output schemas.
- Product reads can supply `id`, `type`, `virtual`, `shipping_required`, `weight`, `dimensions`, `shipping_class` and `shipping_class_id`. For a variation request, reuse the bounded exact-parent-then-variation pattern to verify parent identity/type and read the requested variation under that verified product endpoint; at most two native exact reads are needed. Exact variation reads supply their actual identity, `virtual`, weight/dimensions and shipping class. `parent_id` is not a required native variation field: validate it when returned and reject a mismatch, but use the verified parent endpoint relationship when it is absent. Do not request or synthesize an undocumented variation `shipping_required` field.
- Use the actual product endpoint's boolean `shipping_required` when returned. Variation `requiresShipping` remains null even when `virtual` is false, because effective shipping requirement is filterable; preserve the observed virtual flag independently. Do not infer physical shipping from product type or negate virtual into an authoritative requirement.
- Parse supplied nonnegative decimal measurements to finite numbers. Empty/null/missing measurement values remain unknown; zero is known. Reject malformed or negative values, NaN/infinity and unsafe coercions. Dimensions is null when all three values are null; otherwise preserve each known/unknown component.
- Both Woo measurement units remain null throughout this increment; the current product payload/context does not establish them. Do not assume kg/cm, parse a localized schema description as unit configuration or add settings GETs. The host must not present unitless values as known customer measurements.
- Use endpoint-returned effective variation values/classes. Do not add a second guessed parent-inheritance layer. A native `shipping_class_id` of zero means no assigned class and maps to null; a valid positive integer becomes its decimal string. Null/empty slug maps to null, and negative/malformed IDs fail. Preserve independently observed nullable ID/slug facts without inventing a class description or rate.
- Enforce the supported-type rule in this shipping operation: simple products support exact product facts; a standard variable parent requires a verified selected variation for variant facts; unsupported/custom types and a simple product paired with a variant yield typed outer errors using the existing Commerce error enum. Do not add a new outer `UNSUPPORTED` code. The supplied ordinary product adapter does not establish an existing exhaustive type allowlist. Do not silently treat an unsupported type as a simple physical product or change ordinary get/search behavior while implementing this rule.
- Native Woo policy returns `UNSUPPORTED` with null policy payload and no policy HTTP request. The separately entitled `merchant_knowledge_lookup`/`SHIPPING_AND_DELIVERY` path remains independent; standard product capability is not permission to enable Merchant Knowledge, crawl pages or assert a policy from an unrelated passage.

### Original failure evidence

Use `@modainteract/moda-interact-shared/logging` and `docs/observability/shared-logging.md`. Preserve actual sanitized provider messages/codes, HTTP status, request IDs and original SDK/Prisma/parse causes at their existing owning boundary, with a separate Moda classification and operation/stage. Retain existing bounded-redaction and logger-failure isolation. Do not create a competing generic logger, hide attempted authorization errors under normal policy absence, log credential/scope bodies, or return raw provider errors, policy HTML or customer data in public error text.

## Work Items

- [ ] Reconcile accepted MCP-002/provider/error work and consume the exact Shared package with the frozen shipping exports.
- [ ] Register the fourth published policy operation, strict argument mapping and output schema through the actual runtime capability path.
- [ ] Add paired offline token/scope reading and narrow policy preflight without changing ordinary product authorization or emitting credentials.
- [ ] Implement fixed Shopify policy/product/variant queries and exact identity/status mapping through the real document guard.
- [ ] Add bounded Woo shipping projections and truthful native-field/unknown-unit mapping through the existing read grant.
- [ ] Implement independent policy/product outcomes, HTML bounds/trust, source timestamps and verified URLs without a new fetch/crawl path.
- [ ] Add composed provider/capability/error tests, record validation, set status to `review` and return to the architect.

## Interfaces / Contracts

Contract owner: `ARCH-058-SHARED-001`, published by `ARCH-058-SHARED-002`. Consume `CommerceShippingInformationInputSchema`, `CommerceShippingInformationInput`, `CommerceShippingInformationSchema`, `CommerceShippingInformation` and both `commerce_get_shipping_information` dictionary members from `@modainteract/moda-interact-shared/commerce`. Public shape, operation identity and body/status relationships are fixed by `docs/architecture/ARCH-058/contracts.md` section 2.3; do not independently redesign them here.

Primary edit paths: a focused `src/execution/policy/shipping-information.ts` adapter, `src/execution/policy/shopify-core-executor.ts`, `src/connections/{ports,resolver}.ts`, `src/connections/shopify/{session-reader,provider}.ts`, `src/connections/woocommerce/{provider,direct-product-reader}.ts`, `src/runtime/{ports,service-ports}.ts` as required by composition, and their focused tests. Preserve/read `src/connections/shopify/document.ts`, the accepted product adapter and existing result renderer/registry; do not weaken their generic guards. Keep new runtime/test filenames semantic and free of architecture IDs. No database schema or unrelated source refactor is authorized.

Official references: [Admin 2026-07 Shop](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Shop), [ShopPolicy and read permission](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPolicy), [ShopPolicyType](https://shopify.dev/docs/api/admin-graphql/2026-07/enums/ShopPolicyType), [ProductVariant](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ProductVariant), [InventoryItem](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItem), [InventoryItemMeasurement](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItemMeasurement), [Woo REST products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/), [Woo REST product variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/), [Woo variation REST controller](https://woocommerce.github.io/code-reference/files/woocommerce-includes-rest-api-controllers-version3-class-wc-rest-product-variations-controller.html), [Woo product shipping requirement](https://woocommerce.github.io/code-reference/files/woocommerce-includes-abstracts-abstract-wc-product.html), and [Woo variation view getters](https://woocommerce.github.io/code-reference/files/woocommerce-includes-class-wc-product-variation.html). Verify against accepted adapter/source pins during implementation. These references are provider semantics, not certification of a live shop response.

## Dependencies

- `ARCH-058-MCP-002`: accepted current-shop provider execution, published-capability/turn/grant checks and original-error diagnostics; its dependencies provide the approved Shared package.
- `ARCH-058-SHOPIFY-001`: accepted declared-scope configuration and rollout/grant-lifecycle contract. Acceptance does not assert that every installed merchant has approved the permission.

## Enables

- `ARCH-058-COMMERCE-001`: create/version/publish all four standard capabilities and include the shipping action in complete immutable release/setup receipts.
- `ARCH-058-BACKGROUND-001`: compose qualified shipping answers, honest policy absence and grounded recommendations through the existing conversation host.
- `ARCH-058-SYSTEM-TEST-001`: exercise native shipping, policy permission/absence, unsupported provider behavior and preserved product discovery across the real service boundaries.

## Acceptance Criteria

- [ ] The exact shipping name and version are discoverable, granted and executable through the actual published registry for otherwise authorized Shopify/Woo stores; missing optional policy permission does not change immutable grants or disable products.
- [ ] Input is strict; variant requires product, native IDs are validated, returned identities match and no shop/URL/query/scope/cart argument can alter authorization.
- [ ] Shopify product-only requests verify existence before returning VARIANT_REQUIRED; exact variant facts and policy fields use the pinned native field paths through the real query guard.
- [ ] Offline token/scope are read together. Missing policy permission performs zero policy HTTP calls and still permits independent product facts; missing/invalid sessions and attempted 401/403/GraphQL failures remain hard with original evidence.
- [ ] Policy absence, unsupported provider, empty existing policy, bounded exact HTML and oversized selected body have the frozen distinct statuses and null payload rules. Unsafe URLs and whole-response budget failures never become successful fabricated policy facts.
- [ ] Woo exact reads preserve active grant/installation/transport protections, source identity, observed virtual/shipping flags and effective variation values; no inferred requiresShipping or measurement unit appears.
- [ ] All result fields/bytes are validated using Shared. Policy content remains untrusted reference, existing product get/search contracts are unchanged, and no live quote, extra page/settings fetch or cart mutation was added.
- [ ] Scoped composition and error-sink tests pass, proving preserved ordinary product execution and existing terminal-error behavior. No persistent tool publication or customer send occurred.

## Validation

Run from the canonical launcher-provided MCP implementation worktree. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. Inspect the actual `package.json` and use its declared tools.

- [ ] Add `tests/unit/execution/policy/shipping-information.test.ts` and `tests/unit/execution/policy/shipping-information-composition.test.ts`. The composition test must use the real connection resolver, provider preflight, document guard, registered executor and result parser/renderer with injected HTTP/Prisma fixtures; a stub of `adminGraphql` alone is insufficient. Run:

  ```bash
  npm exec -- tsx --test tests/unit/execution/policy/shipping-information.test.ts tests/unit/execution/policy/shipping-information-composition.test.ts tests/unit/execution/policy/shopify-core.test.ts
  ```

- [ ] Extend existing connection and registration fixtures and run:

  ```bash
  npm exec -- tsx --test tests/unit/connections/shopify/session-reader.test.ts tests/unit/connections/shopify/provider.test.ts tests/unit/connections/shopify/document.test.ts tests/unit/connections/woocommerce/direct-product-reader.test.ts tests/unit/connections/woocommerce/provider.test.ts tests/unit/runtime/service-ports.test.ts tests/unit/mcp/capability-invocation.test.ts
  ```

- [ ] Cover policy-only, exact variant, verified product requiring a variant, standard Woo variable parent, simple/virtual Woo product, unsupported type, absent/mismatched product, cross-shop/expired/stale grant and denied current policy. Assert no fabricated first variant, no unverified IDs and no additional model-supplied keys/provider queries.
- [ ] Assert the exact paired offline selection, absent/null/blank/unrelated scope, zero policy fetch for missing scope, product success beside SCOPE_NOT_GRANTED, granted request 401/403/GraphQL errors, cancellation and failed credential reads. Normal scope absence must not depend on parsing provider error prose.
- [ ] Test no shipping-policy object versus an existing empty object; exact retained HTML; both character and multibyte UTF-8 boundaries at and above the limits; body TOO_LARGE retaining a verified URL; response-byte overflow remaining hard; safe/unsafe custom domains; malformed timestamps/fields; and instruction/link/script payloads remaining inert reference data. Include null relationships for every policy/product status.
- [ ] Test Woo measurement zero, empty/missing/null, finite decimals, negative/malformed values, unknown units, partial/all-unknown dimensions, class ID zero/null/positive/negative/malformed and empty/nonempty slug, and effective variation values. Include a valid native variation without parent_id, a conflicting returned parent_id, a simple product paired with a variant, and an unsupported/custom product type. Prove virtual=false does not manufacture variation requiresShipping and that no settings, policy-page, cart or second guessed-parent query occurs.
- [ ] Use real Shared logger-sink assertions for source HTTP/GraphQL/SDK/Prisma errors with credential/PII sentinels; confirm original safe context survives, outputs contain no raw failures, and missing-scope outcomes are distinct from attempted-request errors. Preserve existing logger-failure isolation.
- [ ] Run `npm run typecheck`, `npm run lint`, `npm run build` and `git diff --check`. Record exact accepted dependency versions and actual outcomes. These fixture checks establish adapter behavior, not live merchant permissions, shipping quotes or a production deployment; unperformed live checks remain `NOT_RUN`.

## Stop Condition

Stop for an unreconciled accepted provider/Shared baseline, missing approved schema/export, incompatible provider identity/field semantics, scope authority that cannot be paired safely, or a required settings/cart/schema/endpoint expansion outside the frozen contract. Return that concrete gap to `moda_architect`; do not guess facts or broaden permission. When all scoped work and required validation pass, complete the report, set status to `review` and return to the architect. Do not mark complete, publish tools, deploy, alter another repository, start a dependent task or send a customer message.

## Implementation Notes

This task supplies current provider facts, not a delivery promise. Policy missing-scope/absence states are normal successful data only after the existing caller/shop/capability checks pass. An actual outer error retains the runner's terminal referral behavior. The existing Background host may combine a qualified answer or narrow referral with a separately grounded product recommendation under its frozen response contract; MCP must not invent that final customer prose or a second output pipeline.

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

Accepted MCP-002/provider work and the exact published Shared shipping contract will be present before implementation. Shopify configuration acceptance does not prove an installed offline grant; Woo measurement units remain unknown in this increment.

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
