---
id: ARCH-052
title: Checkout-personalised initial outreach with direct MCP product reads and AI alternative promotions
status: proposed
coordinator: moda_architect
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052: Checkout-personalised WhatsApp initial outreach

## Status

Proposed — **Attempt 8 Shared contract definition review** from 29 October 2026 08:07 source snapshot. Pre-production breaking work; definitions are portable and **not materialised**. No historical backfill, legacy compatibility, provider-product persistence or new Prisma schema. Merchant selections continue to use `ShopifyDiscount.isAvailable`. No new attempt policy/sent-offer snapshot is added: confirmed `ConversationMessage.content` and `RecoveryOutreachAttempt.outboundMessageId` already record the actual sent template.

## Problem

Initial outreach needs verified, checkout-personalised WhatsApp messages. Merchant modes NONE/FIXED/AI must produce an eligible checkout discount where possible; if none applies, the AI should attempt a **separate, real promotion on another relevant product**. Merchant-defined instructions and product categories influence ranking, not eligibility. Product search is provider-backed and should run **directly inside the existing MCP service**, without calling the hosted Moda API or creating a product database. The conversation CommerceAgent is not appropriate before a customer has replied.

## Goals

- Shared merchant-selected discount semantics: `ShopifyDiscount.isAvailable` means *merchant selected*, never provider availability. FIXED only selected IDs; AI searches provider-current catalogue independent of selection; NONE makes no discount MCP/AI calls.
- Use `CommerceModelInvoker` via one **dedicated Background `InitialOutreachOfferAgent`**; do not modify `runCommerceTurn`, fabricate a conversation, build another model framework or duplicate MCP transport.
- Built-in read-only discount MCP tools require no Commerce Studio authoring/release. Code-defined product search and exact-item MCP tools are prepared in Commerce and published once through the approved versioned release mechanism; no manual Studio authoring.
- MCP calls Shopify GraphQL and WooCommerce REST **directly** for product search and exact product/variant details, using existing encrypted Woo credentials from PostgreSQL and Shared crypto/security primitives, with hardened DNS/TLS/SSRF protections. MCP must not call Moda hosted API for product search or Woo native coupon proof.
- MCP is the generic feature capability server and retains the existing `CommerceToolResultSchema` for **all** tools. The agent receives checkout/merchant context from Background, makes no database/provider calls and dynamically chooses MCP discount/product calls through LangGraph. No exhaustive eligibility scan is required before the model. Stage 1 seeks a discount supported by provider evidence on the abandoned basket. Stage 2, only when Stage 1 has no provable checkout offer, discovers verified discounts on genuinely available related or other products, then promotes a **distinct product opportunity** rather than claiming it discounts existing checkout lines. When no offer can be positively verified, use approved no-offer/no-send.
- Preserve existing `shop.categoryName`, deterministic basket summary, optional runtime product image, immutable approved Meta template variants, checkout CTA backed by the **already-populated** `CheckoutRecovery.checkoutUrl` for Shopify and WooCommerce, consent/STOP/moderation, marketing approval for cross-sell, billing, human handover and Support notification without a new send pipeline.

## Non-Goals

No new database tables/columns/migrations, replicated product catalogue or product-image table; no MCP-to-API product proxy; no Commerce Studio manually authored discount tool; no Commerce conversation-runner outreach mode; no invented coupon or automatic offer creation, no unauthorised cart mutation. **No checkout URL capture/creation, refresh, restore-link issuance, short-lived token, hosted API proxy or customer-click cart restoration implementation**: `CheckoutRecovery.checkoutUrl` is an upstream prerequisite for both platforms. No guarantee of a discount if none genuinely exists or if provider verification is unavailable; partial scans cannot imply global absence.

## Inspected current architecture

- `moda-interact-mcp/src/connections/ports.ts` already includes Woo `products.list` and `products.retrieve`; `connections/woocommerce/provider.ts` currently delegates to an injected `ApprovedWooProductReader`, and `runtime/ports.ts` only installs Woo provider when one is injected. Thus direct Woo REST implementation and hardened credential/transport wiring are required **in MCP**.
- `moda-interact-mcp/src/runtime/prisma.ts` owns MCP Prisma composition; existing grant validator `connections/woocommerce/grant-reader.ts` is only an eligibility reader, not a credential decryptor.
- `moda-interact-api/src/woocommerce/rest-read/provider-connection.service.ts`, `credential-verifier.ts`, `envelope.ts` demonstrate secure Woo provider behavior (encryption, grant rotation, DNS pinning, TLS and bounded GET). They are reference behavior, **not an HTTP broker or imports** for MCP. Shared `security/credentials/node` already exports canonical keyring/decrypt/AAD primitives.
- `moda-interact-mcp/src/execution/policy/shopify-core.ts` already has bounded Shopify GraphQL product search and signed cursors. `moda-interact-shared/src/commerce/schemas.ts` has `commerce_search_products` and product schema, but lacks Woo-relevant photo/category/sale-evidence projection and exact-item tool.
- `moda-interact-commerce/src/commerce/bootstrap/merchant-knowledge.ts` already demonstrates idempotent code-defined tool bootstrap/release publication; use it for product tools. `runCommerceTurn` is conversation-scoped, but `CommerceModelInvoker` and production factory can be used independently in Background.
- Provider coupon verification must remain read-only: Commerce owns Shopify proof, WooCommerce plugin owns native coupon rules; MCP calls private Commerce proof and Woo plugin directly via its authenticated Woo REST grant (not hosted API).
- WooCommerce checkout URL generation and customer-click restoration are **out of scope**: both WOOCOMMERCE-002 and API-004 are superseded, without claiming that this upstream feature has already been implemented. `ShopifyDiscount.isAvailable` must be merchant-only across Shopify sync. Existing ARCH-047/048/049/050 systems remain unchanged beyond approved integration points.

## Current merchant settings and durable outbound message

- PostgreSQL is the source of truth for the **current** merchant discount mode and selections. `ShopifyDiscount.isAvailable=true` is the merchant checkbox for both platforms; the existing single `fixedShopifyDiscountId` may remain as a deterministic settings projection, never as a substitute for the full selected set. Shopify sync/lifecycle writers never reset merchant choices. WooCommerce's existing multi-selection API continues unchanged; API-001 is superseded.
- Background's existing recovery workflow loads current checkout line items, merchant settings and active platform/shop instructions, then passes that trusted context to `InitialOutreachOfferAgent`. The agent itself has no Prisma, PostgreSQL, Shopify or WooCommerce connector. MCP uses **its own** existing PostgreSQL access for commerce discount catalogues and current authorisation, not to retrieve agent context.
- **Do not freeze merchant settings** inside `RecoveryOutreachAttempt.offerSnapshot`. MCP reads current shop policy at `tools/list` and `tools/call`, including effective Admin override and FIXED merchant-selected IDs; a changed setting makes old offers unauthorised. Before send, Background checks current settings and refuses/reselects an offer no longer permitted. Do not add new policy hashes, permission JSON or migrations.
- The approved template plus its populated parameters (including its existing checkout URL button) and `recoveryPromise` are already persisted in the outbound `ConversationMessage.content`; the first sent message is linked through `RecoveryOutreachAttempt.outboundMessageId`. Extend the existing message promise only if needed to identify a separately promoted product. The actual message record, with provider-confirmed send state, is authoritative for what the customer was told and what a follow-up may reference. Background reads the already-populated `CheckoutRecovery.checkoutUrl` for both platforms and binds its exact stored value to the existing approved checkout CTA. ARCH-052 does **not** add a checkout URL validation step (including URL format, scheme, host, prefix, expiry or reachability checks) and does not introduce URL-specific fallback handling. Checkout URL availability/correctness is an upstream precondition. Do not create another URL, copy it into policy/offer snapshots, add a new table or log the raw URL. **No second `offerSnapshot.sentOffer` field** or duplicate audit table is created.
- The initiative is pre-production: no backfill, old proposal compatibility or historical policy snapshot migration. Existing idempotency, consent/STOP/moderation and billing admission still apply.

## Shared contract boundaries — Attempt 8

`ARCH-052-SHARED-002`, `SHARED-005`, `SHARED-006` and `SHARED-008` now contain exact **proposed** TypeScript/Zod source snippets, package exports and structural fixtures. The contract proposals are for developer/architect review before implementation; their currently Ready task statuses are planning eligibility, not acceptance of a runtime implementation.

- **Zod = transport structure only.** New schemas describe field names, required/nullable types, literals, discriminated results, established lexical formats and unknown-key rejection. No new business-policy `.refine`, `.superRefine`, `.transform` or `.check` is authorised.
- **SHARED-002:** Admin/Background share checkout/promotion semantic bindings and immutable projection structure. Approval, target/variable compatibility, image roles, Meta parameter ordering, marketing suitability and button semantics are service-layer concerns; ARCH-052 adds **no** checkout URL validation.
- **SHARED-005:** MCP/provider adapters exchange optional on-demand discount evidence, without requiring an exhaustive scan. Provider eligibility, matching shop/attempt/product, evidence freshness, redeemable-code consistency and monetary calculations remain in their owning services.
- **SHARED-006:** A minimal `INITIAL_RECOVERY_OUTREACH` discriminator is carried in existing trusted MCP `toolContext`; top-level shop identity remains part of the current private ingress, not AI tool arguments. No new envelope or context-retrieval tool is introduced.
- **SHARED-008:** Extend the existing `CommerceProductSchema` with optional observed categories, image and sale-price data; add exact-product input/output to existing commerce tool dictionaries. Provider connection/URL trust and promotion claims remain MCP/Background concerns.
- **SHARED-003:** Publish accepted cross-service schemas only after SHARED-002/005/006/008 are individually reviewed Complete; do not rerun implementation validation during release.

No frozen merchant policy, custom HMAC, conversation runner extension, product persistence or Background-owned AI decision schema is added to Shared.

## Offer discovery, MCP budget and availability semantics

- MCP `tools/list` merges **built-in discount tools** `commerce_get_discount_options`/`commerce_evaluate_discount` (source-controlled and authorised only for `INITIAL_RECOVERY_OUTREACH`) and separately **published** `commerce_search_products`/`commerce_get_product` tools (immutable Commerce release, active feature entitlement, pinned definition version). There is no manual discount Studio authoring or publication.
- For every tools/call, MCP re-reads shop, recovery, attempt and **current** policy and validates published-product tool grants. FIXED tool lists only currently selected discount IDs; AI lists provider-current catalogue independently of checkboxes. Page <=50, signed scoped cursor, typed incomplete/timeout when all discounts cannot be inspected; no silent 8/24-candidate truncation.
- MCP owns direct Woo provider REST, credentials and grant recheck, same DB tables and Shared crypto as API. It does NOT call hosted API for product search or native coupon verification. Shopify product search uses existing MCP GraphQL connector; both providers use the same Shared product response contract.
- MCP evaluates only by provider-native proof. Checkout-target and alternative-product-target proofs are distinct, read-only and TTL/fingerprint bound. Woo plugin GET endpoint supports both; Shopify Commerce private POST supports both. If alternate product is on sale but an eligible associated merchant discount cannot be proved, do not invent or apply coupon; a native sale-price claim may be used only when provider price evidence directly proves a real current promotion and merchant mode permits it.
- BACKGROUND-010 implements a dedicated Background LangGraph StateGraph. Background assembles trusted checkout, current merchant discount mode/IDs and active platform/shop instruction context *before* invoking the agent; the agent and its MCP adapter perform no PostgreSQL or provider reads. For enabled modes the agent discovers the MCP tool set once, asks `CommerceModelInvoker` which existing discount/product tool to call, and loops model → MCP tools/call → model within explicit budgets. It first seeks a positive checkout discount with targeted proof calls (no Background bulk eligibility scan). Where no checkout offer has been established, it may search related products and request targeted alternative-product proof. It finalises with identifiers only, validated against positive same-shop MCP evidence; no model-authored coupon, amount, URL or provider proof. On model failure prefer deterministic verified fallback; absent proof return typed no-offer/unavailable. Incomplete exploration is not proof of global catalogue exhaustion. No conversation history, inbound version, turn lease or conversation-runner extension is involved.
- The consumer must not use shopper personal data beyond authorised necessary inputs or allow prompt injection from untrusted product/merchant strings.

## Runtime product image and template semantics

Use exact MCP `commerce_get_product` for the first eligible abandoned checkout item or chosen alternative product; prefer variation/variant image then product featured image. **No Shopify Commerce or Woo hosted API image route.** Background validates HTTPS, DNS/SSRF, redirects, max 5 MB, JPEG/PNG bytes and image identity before attaching optional media. Never persist image rows, new R2 objects, product catalogue, or other media schema. Unsafe/unavailable image falls back to a separately Meta-approved text-only variant. `shop.categoryName` already exists with translation and approved missing-category fallback. Basket summary is deterministic (<=160 characters), not LLM generated. Alternative product promotion uses separately approved wording/CTA and must not claim the coupon applies to the abandoned basket.

## Private Woo read contract

MCP directly reads WooCommerce REST through its **own secure provider adapter**, not through the hosted Moda API. MCP loads the existing shop installation and current encrypted Woo read grant from PostgreSQL (connection data only), decrypts through Shared `@modainteract/moda-interact-shared/security/credentials/node` keyring/AAD functions, validates shop/grant/credential rotation and uses bounded **GET-only** transport with public origin HTTPS, pinned DNS/TLS, no redirects and SSRF defence. MCP executes Woo `products.list`/`products.retrieve` and Woo plugin's native read-only coupon-proof endpoint directly. Shopify product search/get use MCP's existing authorised Shopify GraphQL connection. Only COMMERCE-003 exposes a private-only **Shopify discount-proof** route to MCP; hosted Moda API is not required for checkout URL generation, product discovery, media or coupon eligibility in ARCH-052. Gateway maintains secure per-environment MCP credential keyring configuration and private-only Commerce service connectivity; no bespoke Shared-004 HMAC or Redis nonce machinery; no plaintext keys in Render YAML. Failed grant/tenant/provider proof is unavailable/ineligible, never a sendable coupon.

## Repository responsibilities

- **Shared**: only genuinely cross-service template bindings, on-demand discount evidence, minimal MCP outreach identity and generic commerce/product schemas; SHARED-003 publishes these. No policy freeze, AI decision result or new HMAC contract. Existing conversation runner and generic MCP envelope are unchanged.
- **MCP**: attempt-scoped authorisation; built-in discount tools; **direct Shopify GraphQL and WooCommerce REST product/search/exact-item** adapters using existing connections and secure encrypted grant; live provider discount proof through Commerce's private Shopify route or Woo plugin's native read-only REST. No MCP-to-hosted-API product/coupon broker.
- **Commerce**: Shopify checkout and separate-product discount proof; one private authenticated proof route; code-owned product-search and exact-item tool definitions and idempotent bootstrap; separate reviewed TEST publication through existing Commerce lifecycle. No manually authored discount tools or manual product-tool drafts.
- **Background**: Shopify flag-sync correction, current merchant context, one focused InitialOutreachOfferAgent using existing model invoker/MCP client, deterministic items, runtime MCP images, direct binding of existing `CheckoutRecovery.checkoutUrl` in BACKGROUND-008 for both platforms, and existing message persistence/final-send/credit/consent gates. No separate discount engine, conversation runner or restore-link client.
- **Shopify**: merchant multi-select writes to existing shop-scoped `ShopifyDiscount.isAvailable` rows.
- **API**: existing Woo multi-select behaviour remains unchanged. API-001/002/003/004 are superseded for ARCH-052; no new hosted API endpoint is required for checkout-link issuance, product search or coupon proof.
- **WooCommerce**: native read-only coupon proof covering checkout and alternative products; customer-click restoration is an upstream prerequisite, not an ARCH-052 implementation task.
- **Admin**: locale/provider-approved checkout, alternate-promotion and no-offer templates, with approved image/text fallback.
- **Gateway**: private-only Commerce Shopify discount-proof routing, MCP credential keyring and secure outbound Woo access; no new Woo restore-link route, public private-read route or HMAC/replay secret.
- **System Test**: terminal integrated Shopify/Woo validation only after all implementation/publication dependencies are Complete.

## Failure handling, ordering and security

Provider-ineligible, unavailable, incomplete, timeout and revoked are distinct typed outcomes. Only current positive proof may support a customer-facing promotion. MCP rechecks recovery/attempt and current merchant selection on each tool call, keeps published product tools release/feature pinned and built-in discount tools limited to trusted outreach identity. Product URLs, images and customer-specific merchant claims cannot be supplied by the model. Existing merchant instructions may rank candidates but never override eligibility, tenant identity or safety. Retry classified failures with shared bounded logger and no secret/PII logs; prevent cross-shop data, replay or SSRF. Existing WhatsApp final send retains Meta template approval, marketing permission for cross-sell, explicit STOP/consent, moderation, admission, billing/credit and one-send CAS. Confirmed outbound template parameters and `recoveryPromise`, not a second attempt JSON field, are the durable sent-offer evidence. An incomplete scan never becomes a false assertion that no eligible discount exists; model errors only fall back to **already verified** offers. Any customer-click Woo cart restoration behind an upstream `checkoutUrl` is separate from and not implemented or certified by ARCH-052.

## Observability and scalability

Reuse `@modainteract/moda-interact-shared/logging`, existing OpenTelemetry/framework/BullMQ signals and domain-specific bounded events. Correlate shop/recovery/attempt IDs, mode, search page counts, verified checkout/alternative counts, typed provider result, model fallback, safe media fallback, Meta send result and retries—never coupon codes, raw complete URLs, credentials or customer PII. Throughput depends on actual actionable recoveries and bounded provider reads rather than raw Shopify ingress. Measure provider request budget, timeouts and queue lag under TEST; no claimed measured throughput.

## Development-only cutover (no preservation)

This initiative is a **breaking pre-production cutover**. No backfill, legacy adapters, migration of historical selected IDs, or preservation of old provider-driven `isAvailable` meaning. No schema migration. **Do not run destructive statements in production or shared environments.** After BG009 is deployed and **before enabling Shopify multi-select**, an authorised developer runs the following against a disposable/approved **development** database only, after taking any desired backup:

```sql
BEGIN;
UPDATE "shopify"."ShopifyDiscount" AS d
SET "isAvailable" = FALSE
WHERE EXISTS (
 SELECT 1 FROM "commerce"."Shop" AS s
 WHERE s."id" = d."shopId" AND s."platform" = 'SHOPIFY'
);
UPDATE "shopify"."ShopSettings" AS st
SET "fixedShopifyDiscountId" = NULL
WHERE EXISTS (
 SELECT 1 FROM "commerce"."Shop" AS s
 WHERE s."id" = st."shopId" AND s."platform" = 'SHOPIFY'
);
COMMIT;
```

Development-only `RecoveryOutreachAttempt` records with old single-discount `offerSnapshot` JSON must be deleted/reseeded using the established isolated seed/fixtures, **not** parsed through legacy adapter or deleted automatically by runtime code. Do not reset Woo selected flags. Mark the dev reset as manual deployment prerequisite; neither patch application nor an agent silently wipes user data. The current persisted Prisma models remain untouched.

## Rollout and validation

1. Implement and architect-accept SHARED-002/005/006/008, then publish those four accepted contracts through SHARED-003. SHARED-001/004/007 remain superseded; no snapshot/HMAC or conversation-runner changes.
2. Implement and accept Shopify merchant selection/sync. Treat an already-populated `CheckoutRecovery.checkoutUrl` for each Shopify/WooCommerce recovery as an upstream integration precondition, **not** an ARCH-052 restoration task. A developer may perform the documented one-time *development-only* selected-flag/attempt reset at cutover; **no database migration/backfill, legacy compatibility or automatic destructive reset**.
3. Implement COMMERCE-001 and COMMERCE-008 provider proof and COMMERCE-003 private Shopify proof route; WooCommerce-001 owns native read-only coupon proof. COMMERCE-006 prepares two code-owned product tool descriptors; MCP-003 implements direct Shopify GraphQL and Woo REST search/exact reads using the existing connection grants; developer-executed publication-only COMMERCE-007 then activates an accepted TEST release.
4. MCP-001 authorises an outreach attempt, MCP-002 registers built-in discount tools and supports targeted checkout proof on request, MCP-004 supports alternative-product evidence. Gateway-001 provisions MCP Woo keyring and private-only Commerce proof connectivity without bespoke HMAC; **no MCP-to-API product, coupon-proof or checkout-link generation call**. Commerce-002/004/005 and API-002/003 remain superseded.
5. BACKGROUND-010 implements the dedicated LangGraph InitialOutreachOfferAgent with `CommerceModelInvoker` and generic MCP tools. BACKGROUND-007 gets optional media via MCP; ADMIN-001/002 approve distinct checkout/alternative/text-image variants; BACKGROUND-008 binds the existing `CheckoutRecovery.checkoutUrl` and selected offer outcome into existing Meta send gates, persisting only the actual template receipt. Background-002/003/004/006 remain superseded; no Woo link-generation step is required.
6. After all implementation, publication, deployment and related observability tasks are Complete and architect accepted, developer may manually exercise features and then invoke terminal SYSTEM-TEST-001/002. TEST publication does not authorise production deployment. A provider outage must fail closed to an approved no-offer fallback or no-send, never a fictional promotion.

## Decisions / Tasks

All tasks are portable definitions; **Ready** means dependency-eligible but not claimed. Superseded tasks are not executable. No database schema task is required.

| Task | Owner | Status | Depends on |
|---|---|---|---|
| [ARCH-052-ADMIN-001](../decisions/admin/ARCH-052/ADMIN-001-author-six-initial-outreach-template-variants.md) | `moda_admin` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-ADMIN-002](../decisions/admin/ARCH-052/ADMIN-002-author-optional-checkout-product-image-headers.md) | `moda_admin` | Pending | `ARCH-052-SHARED-003`, `ARCH-049-ADMIN-002` |
| [ARCH-052-API-001](../decisions/api/ARCH-052/API-001-align-existing-woo-selection-with-shared-contract.md) | `moda_api` | Superseded | — |
| [ARCH-052-API-002](../decisions/api/ARCH-052/API-002-expose-private-woo-checkout-product-image-read.md) | `moda_api` | Superseded | — |
| [ARCH-052-API-003](../decisions/api/ARCH-052/API-003-proxy-woo-native-coupon-proof-through-private-api.md) | `moda_api` | Superseded | — |
| [ARCH-052-API-004](../decisions/api/ARCH-052/API-004-proxy-woo-restore-link-through-private-api.md) | `moda_api` | Superseded | — |
| [ARCH-052-BACKGROUND-001](../decisions/background/ARCH-052/BACKGROUND-001-snapshot-authorised-discount-policy-at-attempt.md) | `moda_background` | Superseded | — |
| [ARCH-052-BACKGROUND-002](../decisions/background/ARCH-052/BACKGROUND-002-discover-bounded-offer-candidates.md) | `moda_background` | Superseded | — |
| [ARCH-052-BACKGROUND-003](../decisions/background/ARCH-052/BACKGROUND-003-connect-shopify-woo-live-eligibility-providers.md) | `moda_background` | Superseded | — |
| [ARCH-052-BACKGROUND-004](../decisions/background/ARCH-052/BACKGROUND-004-wire-bounded-ai-offer-selector.md) | `moda_background` | Superseded | — |
| [ARCH-052-BACKGROUND-005](../decisions/background/ARCH-052/BACKGROUND-005-bind-basket-summary-and-merchant-context.md) | `moda_background` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-BACKGROUND-006](../decisions/background/ARCH-052/BACKGROUND-006-resolve-fresh-woo-resume-checkout-links.md) | `moda_background` | Superseded | — |
| [ARCH-052-BACKGROUND-007](../decisions/background/ARCH-052/BACKGROUND-007-resolve-verified-product-image-at-runtime.md) | `moda_background` | Pending | `ARCH-052-SHARED-003`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-007`, `ARCH-049-BACKGROUND-001`, `ARCH-049-BACKGROUND-004` |
| [ARCH-052-BACKGROUND-008](../decisions/background/ARCH-052/BACKGROUND-008-integrate-three-modes-into-initial-whatsapp-send.md) | `moda_background` | Pending | `ARCH-052-BACKGROUND-010`, `ARCH-052-BACKGROUND-005`, `ARCH-052-BACKGROUND-007`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-GATEWAY-001` |
| [ARCH-052-BACKGROUND-009](../decisions/background/ARCH-052/BACKGROUND-009-preserve-shopify-merchant-selection-during-sync.md) | `moda_background` | Ready | — |
| [ARCH-052-BACKGROUND-010](../decisions/background/ARCH-052/BACKGROUND-010-implement-langgraph-initial-outreach-offer-agent.md) | `moda_background` | Pending | `ARCH-052-MCP-002`, `ARCH-052-MCP-004`, `ARCH-052-COMMERCE-007`, `ARCH-052-SHARED-003` |
| [ARCH-052-COMMERCE-001](../decisions/commerce/ARCH-052/COMMERCE-001-verify-shopify-discount-against-current-checkout.md) | `moda_commerce` | Ready | — |
| [ARCH-052-COMMERCE-002](../decisions/commerce/ARCH-052/COMMERCE-002-read-authoritative-shopify-checkout-product-image.md) | `moda_commerce` | Superseded | — |
| [ARCH-052-COMMERCE-003](../decisions/commerce/ARCH-052/COMMERCE-003-serve-authenticated-private-shopify-recovery-reads.md) | `moda_commerce` | Pending | `ARCH-052-COMMERCE-001`, `ARCH-052-COMMERCE-008`, `ARCH-052-SHARED-003` |
| [ARCH-052-COMMERCE-004](../decisions/commerce/ARCH-052/COMMERCE-004-author-published-discount-mcp-tools.md) | `moda_commerce` | Superseded | — |
| [ARCH-052-COMMERCE-005](../decisions/commerce/ARCH-052/COMMERCE-005-publish-approved-mcp-discount-capabilities.md) | `moda_commerce` | Superseded | — |
| [ARCH-052-COMMERCE-006](../decisions/commerce/ARCH-052/COMMERCE-006-bootstrap-product-search-and-get-product-tools.md) | `moda_commerce` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-COMMERCE-007](../decisions/commerce/ARCH-052/COMMERCE-007-publish-code-defined-product-tool-release.md) | `moda_commerce` | Pending | `ARCH-052-COMMERCE-006`, `ARCH-052-MCP-003` |
| [ARCH-052-COMMERCE-008](../decisions/commerce/ARCH-052/COMMERCE-008-verify-shopify-alternative-product-promotion.md) | `moda_commerce` | Pending | `ARCH-052-COMMERCE-001`, `ARCH-052-SHARED-003` |
| [ARCH-052-GATEWAY-001](../decisions/gateway/ARCH-052/GATEWAY-001-configure-private-recovery-product-read-transport.md) | `moda_gateway` | Pending | `ARCH-052-COMMERCE-003`, `ARCH-052-MCP-003`, `ARCH-052-SHARED-003` |
| [ARCH-052-MCP-001](../decisions/mcp/ARCH-052/MCP-001-authorize-initial-recovery-outreach-tool-context.md) | `moda_mcp` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-MCP-002](../decisions/mcp/ARCH-052/MCP-002-execute-published-discount-options-and-proof.md) | `moda_mcp` | Pending | `ARCH-052-MCP-001`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-003`, `ARCH-052-WOOCOMMERCE-001`, `ARCH-052-GATEWAY-001`, `ARCH-052-SHARED-003` |
| [ARCH-052-MCP-003](../decisions/mcp/ARCH-052/MCP-003-direct-provider-product-search-and-exact-read.md) | `moda_mcp` | Pending | `ARCH-052-SHARED-003`, `ARCH-052-COMMERCE-006` |
| [ARCH-052-MCP-004](../decisions/mcp/ARCH-052/MCP-004-verify-alternative-product-discount-promotions.md) | `moda_mcp` | Pending | `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-008`, `ARCH-052-WOOCOMMERCE-001` |
| [ARCH-052-SHARED-001](../decisions/shared/ARCH-052/SHARED-001-define-canonical-selected-discount-contract.md) | `moda_shared` | Superseded | — |
| [ARCH-052-SHARED-002](../decisions/shared/ARCH-052/SHARED-002-define-checkout-template-binding-contract.md) | `moda_shared` | Ready | — |
| [ARCH-052-SHARED-003](../decisions/shared/ARCH-052/SHARED-003-publish-initial-outreach-shared-contracts.md) | `moda_shared` | Pending | `ARCH-052-SHARED-002`, `ARCH-052-SHARED-005`, `ARCH-052-SHARED-006`, `ARCH-052-SHARED-008` |
| [ARCH-052-SHARED-004](../decisions/shared/ARCH-052/SHARED-004-define-private-read-authentication-contract.md) | `moda_shared` | Superseded | — |
| [ARCH-052-SHARED-005](../decisions/shared/ARCH-052/SHARED-005-define-discount-proof-wire-contract.md) | `moda_shared` | Ready | — |
| [ARCH-052-SHARED-006](../decisions/shared/ARCH-052/SHARED-006-define-outreach-mcp-discount-tool-contracts.md) | `moda_shared` | Ready | — |
| [ARCH-052-SHARED-007](../decisions/shared/ARCH-052/SHARED-007-reuse-commerce-runner-for-outreach-offer-choice.md) | `moda_shared` | Superseded | — |
| [ARCH-052-SHARED-008](../decisions/shared/ARCH-052/SHARED-008-define-product-search-and-alternative-promotion-contracts.md) | `moda_shared` | Ready | — |
| [ARCH-052-SHOPIFY-001](../decisions/shopify/ARCH-052/SHOPIFY-001-select-multiple-authorised-recovery-discounts.md) | `moda_app` | Pending | `ARCH-052-BACKGROUND-009` |
| [ARCH-052-SYSTEM-TEST-001](../decisions/system-test/ARCH-052/SYSTEM-TEST-001-certify-shopify-initial-outreach-modes.md) | `moda_system_test` | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-SHOPIFY-001`, `ARCH-052-BACKGROUND-009`, `ARCH-052-COMMERCE-001`, `ARCH-052-COMMERCE-008`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-SHARED-003`, `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-MCP-003`, `ARCH-052-MCP-004`, `ARCH-052-COMMERCE-006`, `ARCH-052-COMMERCE-007`, `ARCH-052-BACKGROUND-010`, `ARCH-052-GATEWAY-001` |
| [ARCH-052-SYSTEM-TEST-002](../decisions/system-test/ARCH-052/SYSTEM-TEST-002-certify-woocommerce-initial-outreach-modes.md) | `moda_system_test` | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-GATEWAY-001`, `ARCH-052-WOOCOMMERCE-001`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-SHARED-003`, `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-MCP-003`, `ARCH-052-MCP-004`, `ARCH-052-COMMERCE-006`, `ARCH-052-COMMERCE-007`, `ARCH-052-BACKGROUND-010` |
| [ARCH-052-WOOCOMMERCE-001](../decisions/woocommerce/ARCH-052/WOOCOMMERCE-001-expose-read-only-native-coupon-verification.md) | `moda_woocommerce` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-WOOCOMMERCE-002](../decisions/woocommerce/ARCH-052/WOOCOMMERCE-002-create-secure-customer-initiated-checkout-resume.md) | `moda_woocommerce` | Superseded | — |

## Open Questions

None delegated to implementation agents. Unknown provider-specific customer restrictions must return `unavailable` rather than a guessed promotion. Live operator approvals and Meta template/marketing-consent prerequisites remain required; no provider discount is guaranteed to exist.

## Change History

- 2026-10-29 **Attempt 8 (proposed Shared contracts):** Write actual Zod/TypeScript wire contracts in the four retained Shared implementation tasks. Keep Zod structural; move offer eligibility, authorisation, product suitability, expiry and template/send policy to their owning services. SHARED-003 remains release-only and the previously superseded Shared tasks stay superseded.

- 2026-10-29 **Attempt 7**: Treat `CheckoutRecovery.checkoutUrl` as an upstream precondition for both platforms; supersede WOOCOMMERCE-002 and API-004; remove Woo restore-link issuance from BACKGROUND-008, Gateway and system tests; bind the stored checkout URL unchanged to the existing approved CTA with no added checkout URL validation or URL-specific fallback. No new endpoint, token or URL storage.

- 2026-10-29 Attempt 1: Initial outreach task breakdown.
- 2026-10-29 Attempt 2: Reused merchant `isAvailable`, eliminated database and image persistence, no legacy compatibility.
- 2026-10-29 Attempt 3: Began MCP discount integration; superseded Background independent discount candidate/eligibility/model implementations.
- 2026-10-29 **Attempt 4**: Dedicated InitialOutreachOfferAgent (no conversation runner), built-in discount MCP tools, code-defined published product tools, direct Woo/Shopify provider product searches inside MCP, optional cross-sell promotions after checkout proof fails, no hosted API broker for MCP product/coupon proof. Superseded COMMERCE-002/004/005, API-002/003, SHARED-007.

- 2026-10-29 **Attempt 6**: Removed frozen merchant-policy and duplicate sent-offer snapshot; superseded SHARED-001/004, BACKGROUND-001/006 and redundant API-001; consolidated Woo restore-link adapter into BACKGROUND-008; retained current-settings MCP policy and existing generic tool envelope/confirmed outbound message receipt.
