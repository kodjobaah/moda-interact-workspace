---
id: ARCH-052
title: Checkout-personalised WhatsApp initial outreach, shared merchant selection
  and live provider eligibility
status: proposed
coordinator: moda_architect
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052: Checkout-personalised WhatsApp initial outreach

## Status

Proposed. **Pre-production breaking change.** The 29 October 2026 08:07 snapshot is the reference. These are portable definitions, **not materialised** in the developer Git workspace. No production/backwards compatibility, historical backfill, or legacy adapters are required. No implementation code or migrations are delivered by this planning patch.

## Problem

Initial WhatsApp recovery outreach should describe the abandoned items and merchant category, show an optional real checkout-product photo, provide an authenticated return-to-checkout CTA, and choose between NONE, FIXED multiple selected discounts, or AI selecting among genuinely checkout-applicable discounts. Shopify uses `ShopifyDiscount.isAvailable` as provider health today; Woo already uses it as merchant checkbox selection. This must become one shared selection meaning without extra tables or columns.

## Goals

- For both Shopify and WooCommerce, `ShopifyDiscount.isAvailable` means the merchant checked this discount for recovery outreach; **no** provider sync or reinstall operation writes the selection after record creation.
- `ShopifyDiscount.providerStatus`, `unavailableAt`, `ShopifyDiscountCatalogue.status`, syncGeneration, dates and native provider eligibility define whether an offer may actually be advertised. A checked coupon alone is never proof.
- NONE makes no discount-catalogue, discount-eligibility or LLM calls (optional checkout-product image reads remain allowed); FIXED considers only 1..50 merchant-selected IDs; AI enumerates the whole current catalogue within explicit bounds irrespective of checkboxes and only proposes independently verified options.
- Use `CheckoutRecovery.lineItems` product/variant IDs for readable basket summary and runtime product-image lookup. Reuse the already implemented `shop.categoryName` translation binding; no new merchant-description or image database model.
- Preserve existing consent/STOP/moderation/credit/recovery-age/template approval/human-handover/merchant Support notification enforcement, not historical development-only data.

## Non-Goals

No Prisma schema/migration, `ShopRecoverySelectedDiscount` table, media metadata table, backfill or legacy policy parser. No direct cart modification during discount eligibility testing. No unapproved Meta template mutation; no alternative messaging pipeline. No reimplementation of the ARCH-049 ShopBrand R2 pipeline. No globally guaranteed highest-saving offer when provider evaluation budgets require a shortlist.

## Inspected current architecture

- `moda-interact-database/prisma/schema.prisma`: existing `ShopSettings.fixedShopifyDiscountId`, `ShopifyDiscount.isAvailable`, `ShopRecoveryPolicyOverride.fixedShopifyDiscountId`, and `RecoveryOutreachAttempt.offerSnapshot Json?`.
- `moda-interact-api/src/merchant/discount-offers/service.ts`: Woo already atomically toggles up to 50 `isAvailable` rows with a first-selected FIXED anchor.
- `moda-interact-background/src/services/shopify-discount-catalogue.service.ts`: Shopify currently sets selection flags during provider sync and unavailable updates. `billing-subscription-reconciliation/reinstall-reconciliation.service.ts` also clears it.
- `moda-interact-background/src/services/recovery-offers/`: resolver currently uses 8-candidate cap, `isAvailable` as provider eligibility, default unavailable adapters and no AI recommender.
- `moda-interact-api/src/woocommerce/rest-read/product-operation.ts`: API-only product projection currently lacks images or variation operation.
- `moda-interact-commerce/src/commerce/products/index.ts`: Shopify product/variant reader exists; extend image-only projection.
- `moda-interact-background/src/services/recovery-template-preparation/`: `shop.categoryName` and Meta URL-button binding already exist.
- Existing ARCH-047, ARCH-048, ARCH-049 and ARCH-050 messaging, brand-media, Woo recovery, Support notifications and final-send admission remain the established components.

## Canonical selection and snapshot

**Persisted authority**: `ShopifyDiscount.isAvailable` belongs to the merchant checkbox state, across both platforms. A new provider discount is created unchecked. Provider refresh updates provider status/generation/unavailableAt but NEVER `isAvailable`. Removing a provider discount from the remote catalogue preserves the checked state but prevents a positive eligibility result. `ShopSettings.fixedShopifyDiscountId` is derived as the alphabetically first checked discount only while merchant mode is FIXED (otherwise NULL); it is not a source of authority. Admin overrides remain separate: active FIXED override authorises one `ShopRecoveryPolicyOverride.fixedShopifyDiscountId`, never the merchant set.

**Mode policy**: NONE -> `authorisedDiscountIds=[]`, zero discovery/provider/AI calls. MERCHANT FIXED -> sorted IDs with `isAvailable=true`, 1..50 required; only these may be tried. AI -> `authorisedDiscountIds=[]` (checkboxes dormant), discover provider-current catalogue independent of `isAvailable`. ADMIN_OVERRIDE FIXED -> exactly one override ID, no merging. No discount is promoted without current checkout-specific provider verification.

**Frozen attempt**: the existing `RecoveryOutreachAttempt.offerSnapshot` holds `{ "contract":"moda.recovery.offer-selection.v1", "source":"MERCHANT", "recoveryOfferMode":"FIXED", "authorisedDiscountIds":["idA","idB"] }` (or ADMIN_OVERRIDE). The initial attempt inserts it once and `upsert.update` never changes it. Follow-up copies the exact frozen JSON. The **actual promised discount** comes independently from confirmed outbound message receipt, not mutable preferences or this policy snapshot. Historical development snapshots are not parsed.

## Offer discovery and budgets

Actionable recovery only, not raw ingress hot path: at most 100 catalogue records/page, at most 5,000 records scanned, `id ASC` keyset cursor, 50 selected IDs FIXED, at most 24 live eligibility checks per attempt with concurrency <=4, per-check timeout 2 seconds, total 15 seconds. A >5,000/incomplete scan returns `CATALOGUE_INCOMPLETE` and NO_OFFER; provider unknown/unsupported means no positive claim. AI can choose only a validated catalogue ID among positive verified offers within budget; if >24 plausible options, a deterministic first-24 shortlist is explicitly partial and must not be claimed as globally optimal. Provider mutation forbidden. Required protected outcomes: `eligible`, `ineligible`, `unavailable`; errors must be logged and retried/handled at the existing owning boundary.

## Runtime product image and template semantics

Select first 3 checkout line items in persisted order, prefer exact variant/variation image, then product featured image. Shopify Commerce read and Woo API-private read supply only image candidates matched to exact tenant/product/variation identity. Background must validate public HTTPS, DNS/SSRF, no redirects, <=5MB JPEG/PNG magic bytes and reasonable dimensions before using a verified URL. **No image DB rows, columns, image R2 objects, product-media cache or schema migration.** Missing/invalid/media-provider-error yields separately approved text-only initial template. Media verification TTL <=5 minutes; retries re-verify. Existing ShopBrand media can remain a separate approved header role. `shop.categoryName` already exists; use translation and an approved category-absent fallback. `checkout.itemsSummary` <=160 characters, deterministic, no model. A WhatsApp Meta IMAGE template cannot be converted in place to TEXT: Admin authors separately approved frozen variants.

## Private Woo read contract

Woo product reader is API-process-only. API-002 adds only `/internal/v1/recovery/product-image` (POST) using dedicated Shared-004 HMAC sign/verify contract, Redis nonce replay store, strict shop/checkout/product identity checks and existing Woo read grant. Commerce-003 exposes the Shopify counterpart and API-003 exposes native Woo discount proof. Gateway-001 declares both private origins and separately provisioned `MODA_RECOVERY_PRIVATE_READ_HMAC_KEYS`/caller active kid, with no secret values committed. Wrong-shop, invalid credentials, grant revocation or unavailable provider => denial/no image. This is a scoped image metadata read; no arbitrary URL proxy or Woo write permission.

## Repository responsibilities

- **Shared**: bounded selected-ID/attempt-snapshot parser, template/media bindings and Node-only HMAC proof, then separately publish accepted changes.
- **Background**: Shopify sync fix, effective policy/attempt frozen JSON, paginated candidates, provider proof orchestration, bounded AI selection, item text/image and original final-send integration.
- **Shopify**: checkbox UI and transactional existing `ShopifyDiscount.isAvailable` writes with Shop lock + revision.
- **API**: align existing Woo selection validator without storage migration; extend API-process-only Woo product read behind a private route.
- **Commerce**: live read-only Shopify eligibility evidence, exact checkout variant/product image.
- **WooCommerce**: independent read-only native coupon verifier and customer-click secure checkout restore.
- **Admin**: approved initial text/offer templates plus separate approved image/text variants.
- **Gateway**: private route wiring and secret placeholders, no public unsecured ingress.
- **System Test**: terminal cross-platform certification after implementation and manual validation.

## Failure handling, ordering and security

No optimistic offer on unknown/expired provider evidence. Retry on classified provider exceptions with shared logger; do not swallow errors or emit customer PII/coupon codes/tokens/source image URLs. No Meta send without valid approved template, checkout destination, category/text substitutions, consent, STOP, moderation, final billing/credit and message admission. Concurrent Shopify merchant saves serialise on `Shop` row and compare revision before `isAvailable` changes; provider refresh never writes the merchant flag. One frozen attempt selection and one actual outbound promise for follow-ups; identical attempt cannot double-send/double-bill. Cross-tenant product/media/discount lookups fail closed. Public gateway never exposes private product route; HMAC keys are dedicated, rotated and fail closed on configuration or Redis replay-store failure.

## Observability and scalability

Use existing `@modainteract/moda-interact-shared/logging`, existing BullMQ and framework/OpenTelemetry operational signals; add only semantic domain events when generic instrumentation is insufficient. Log bounded shop/recovery IDs, mode, candidate counts, incomplete scans, verification outcomes, image absent/ready and final send status, never raw HTTP tokens or PII. Capacity is actionable recovery and provider proof calls, not the 20,000 Shopify webhooks/minute reference ingress. Benchmark provider read budget and queue lag before production; no measured capacity claim is made here.

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

1. Implement/accept Shared-001, Shared-002, Shared-004, Shared-005 and Background-009 independently; separately publish Shared-003.
2. Implement/accept Shopify-001 and API-001 for existing-row selection semantics; perform the explicit development-data reset at the approved cutover before first new Shopify selection.
3. Background-001 freezes effective selection in existing JSON, Background-002 enumerates candidates. Independently implement Commerce-001 / WooCommerce-001 eligibility proof, and Background-003/004 choose only positive verified offers.
4. Independent UI/checkout description/approved template work. WooCommerce-002 and Background-006 supply secure customer-click checkout restoration.
5. Commerce-002 and API-002 expose item-image facts, Commerce-003 and API-003 provide private provider proof reads and Gateway-001 supplies private authenticated transport, Background-007 verifies one runtime image, Admin-002 approves independent header/fallback. Background-008 integrates already-established send gates.
6. Only after all owning implementations are Complete may the developer manually validate, then invoke terminal System-Test-001/002. No system-test task gates implementation. The rollout can be disabled to approved text/no-offer initial templates if a provider read or image route is unavailable. Schema rollback is unnecessary because no schema changes occur.

## Decisions / Tasks

| Task | Owner | Status | Depends on |
|---|---|---|---|
| [ARCH-052-BACKGROUND-009](../decisions/background/ARCH-052/BACKGROUND-009-preserve-shopify-merchant-selection-during-sync.md) | `moda_background` | Ready | — |
| [ARCH-052-SHARED-001](../decisions/shared/ARCH-052/SHARED-001-define-canonical-selected-discount-contract.md) | `moda_shared` | Ready | — |
| [ARCH-052-SHARED-002](../decisions/shared/ARCH-052/SHARED-002-define-checkout-template-binding-contract.md) | `moda_shared` | Ready | — |
| [ARCH-052-SHARED-004](../decisions/shared/ARCH-052/SHARED-004-define-private-read-authentication-contract.md) | `moda_shared` | Ready | — |
| [ARCH-052-SHARED-005](../decisions/shared/ARCH-052/SHARED-005-define-discount-proof-wire-contract.md) | `moda_shared` | Ready | — |
| [ARCH-052-COMMERCE-001](../decisions/commerce/ARCH-052/COMMERCE-001-verify-shopify-discount-against-current-checkout.md) | `moda_commerce` | Ready | — |
| [ARCH-052-COMMERCE-002](../decisions/commerce/ARCH-052/COMMERCE-002-read-authoritative-shopify-checkout-product-image.md) | `moda_commerce` | Ready | — |
| [ARCH-052-SHARED-003](../decisions/shared/ARCH-052/SHARED-003-publish-initial-outreach-shared-contracts.md) | `moda_shared` | Pending | `ARCH-052-SHARED-001`, `ARCH-052-SHARED-002`, `ARCH-052-SHARED-004`, `ARCH-052-SHARED-005` |
| [ARCH-052-WOOCOMMERCE-001](../decisions/woocommerce/ARCH-052/WOOCOMMERCE-001-expose-read-only-native-coupon-verification.md) | `moda_woocommerce` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-WOOCOMMERCE-002](../decisions/woocommerce/ARCH-052/WOOCOMMERCE-002-create-secure-customer-initiated-checkout-resume.md) | `moda_woocommerce` | Ready | — |
| [ARCH-052-API-001](../decisions/api/ARCH-052/API-001-align-existing-woo-selection-with-shared-contract.md) | `moda_api` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-SHOPIFY-001](../decisions/shopify/ARCH-052/SHOPIFY-001-select-multiple-authorised-recovery-discounts.md) | `moda_app` | Pending | `ARCH-052-BACKGROUND-009`, `ARCH-052-SHARED-003` |
| [ARCH-052-ADMIN-001](../decisions/admin/ARCH-052/ADMIN-001-author-six-initial-outreach-template-variants.md) | `moda_admin` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-ADMIN-002](../decisions/admin/ARCH-052/ADMIN-002-author-optional-checkout-product-image-headers.md) | `moda_admin` | Pending | `ARCH-052-SHARED-003`, `ARCH-049-ADMIN-002` |
| [ARCH-052-API-002](../decisions/api/ARCH-052/API-002-expose-private-woo-checkout-product-image-read.md) | `moda_api` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-API-003](../decisions/api/ARCH-052/API-003-proxy-woo-native-coupon-proof-through-private-api.md) | `moda_api` | Pending | `ARCH-052-SHARED-003`, `ARCH-052-WOOCOMMERCE-001` |
| [ARCH-052-API-004](../decisions/api/ARCH-052/API-004-proxy-woo-restore-link-through-private-api.md) | `moda_api` | Pending | `ARCH-052-SHARED-003`, `ARCH-052-WOOCOMMERCE-002` |
| [ARCH-052-BACKGROUND-001](../decisions/background/ARCH-052/BACKGROUND-001-snapshot-authorised-discount-policy-at-attempt.md) | `moda_background` | Pending | `ARCH-052-SHARED-003`, `ARCH-052-SHOPIFY-001`, `ARCH-052-API-001`, `ARCH-052-BACKGROUND-009` |
| [ARCH-052-BACKGROUND-002](../decisions/background/ARCH-052/BACKGROUND-002-discover-bounded-offer-candidates.md) | `moda_background` | Pending | `ARCH-052-BACKGROUND-001` |
| [ARCH-052-BACKGROUND-005](../decisions/background/ARCH-052/BACKGROUND-005-bind-basket-summary-and-merchant-context.md) | `moda_background` | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-COMMERCE-003](../decisions/commerce/ARCH-052/COMMERCE-003-serve-authenticated-private-shopify-recovery-reads.md) | `moda_commerce` | Pending | `ARCH-052-COMMERCE-001`, `ARCH-052-COMMERCE-002`, `ARCH-052-SHARED-003` |
| [ARCH-052-BACKGROUND-003](../decisions/background/ARCH-052/BACKGROUND-003-connect-shopify-woo-live-eligibility-providers.md) | `moda_background` | Pending | `ARCH-052-BACKGROUND-002`, `ARCH-052-COMMERCE-003`, `ARCH-052-API-003` |
| [ARCH-052-BACKGROUND-004](../decisions/background/ARCH-052/BACKGROUND-004-wire-bounded-ai-offer-selector.md) | `moda_background` | Pending | `ARCH-052-BACKGROUND-003` |
| [ARCH-052-BACKGROUND-006](../decisions/background/ARCH-052/BACKGROUND-006-resolve-fresh-woo-resume-checkout-links.md) | `moda_background` | Pending | `ARCH-052-API-004`, `ARCH-052-GATEWAY-001` |
| [ARCH-052-GATEWAY-001](../decisions/gateway/ARCH-052/GATEWAY-001-configure-private-recovery-product-read-transport.md) | `moda_gateway` | Pending | `ARCH-052-COMMERCE-003`, `ARCH-052-API-002`, `ARCH-052-API-003`, `ARCH-052-API-004`, `ARCH-052-SHARED-003` |
| [ARCH-052-BACKGROUND-007](../decisions/background/ARCH-052/BACKGROUND-007-resolve-verified-product-image-at-runtime.md) | `moda_background` | Pending | `ARCH-052-SHARED-003`, `ARCH-052-COMMERCE-003`, `ARCH-052-API-002`, `ARCH-052-GATEWAY-001`, `ARCH-049-BACKGROUND-001`, `ARCH-049-BACKGROUND-004` |
| [ARCH-052-BACKGROUND-008](../decisions/background/ARCH-052/BACKGROUND-008-integrate-three-modes-into-initial-whatsapp-send.md) | `moda_background` | Pending | `ARCH-052-BACKGROUND-003`, `ARCH-052-BACKGROUND-004`, `ARCH-052-BACKGROUND-005`, `ARCH-052-BACKGROUND-006`, `ARCH-052-BACKGROUND-007`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002` |
| [ARCH-052-SYSTEM-TEST-001](../decisions/system-test/ARCH-052/SYSTEM-TEST-001-certify-shopify-initial-outreach-modes.md) | `moda_system_test` | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-SHOPIFY-001`, `ARCH-052-BACKGROUND-009`, `ARCH-052-COMMERCE-001`, `ARCH-052-COMMERCE-002`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-SHARED-003` |
| [ARCH-052-SYSTEM-TEST-002](../decisions/system-test/ARCH-052/SYSTEM-TEST-002-certify-woocommerce-initial-outreach-modes.md) | `moda_system_test` | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-API-001`, `ARCH-052-API-002`, `ARCH-052-GATEWAY-001`, `ARCH-052-WOOCOMMERCE-001`, `ARCH-052-WOOCOMMERCE-002`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-SHARED-003` |

No Database implementation tasks. Initial Ready tasks are those with zero dependencies; current status is planning eligibility only, not execution.

## Open Questions

None delegated to repository agents. Provider rule families whose eligibility cannot be fully verified must be reported as unsupported/unavailable rather than guessed. External Meta approval/provider credentials are operator prerequisites for live sending, not license to change task contracts.

## Change History

- 2026-10-29: Attempt 2. Replaced proposed table-based selection and persistent checkout-product media with existing `isAvailable` merchant selection and runtime product image. Removed both Database tasks, introduced the Shopify-sync correction, authenticated private Woo image read and Gateway configuration; explicitly eliminated historical behaviour preservation/backfills.
