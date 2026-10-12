---
id: ARCH-036
title: Reuse existing discount catalogue with direct WooCommerce Background reads
status: proposed
coordinator: moda_architect
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036 — Direct Woo coupon synchronisation, shared existing catalogue, no schema changes

## Status and scope decision

**Proposed — task revision Attempt 5 (12 October 2026).** The developer has requested the smallest repository-owned implementation: Background reads WooCommerce directly using its authorised read-only grant and the same PostgreSQL schema; Background also resolves and verifies discounts before outbound messages. There are **no ARCH-036 API coupon proxy/proof endpoints, new Shared contracts, Shared publication tasks, Woo plugin coupon uploads, or new discount tables/columns/migrations**. API owns only the merchant-facing read/selection write boundary. All tasks remain **portable definitions, not materialised branches**, and no implementation has been approved.

Do not update `docs/decisions/**/_index.md` until the developer explicitly declares the architecture session complete.

## Problem and current architecture

`ShopifyDiscountCatalogue` and `ShopifyDiscount` already persist per-Shop catalogue generations, provider status, timestamps, selectable metadata and `providerSnapshot` JSONB. `ShopSettings`, `ShopRecoveryPolicyOverride` and `RecoveryOutreachAttempt` already reference individual discount rows. The Shopify synchronisation service currently writes `isAvailable` as provider presence; the agreed cross-provider meaning is instead **merchant selected for Moda recovery**. We must correct those writers/readers without breaking Shopify's existing single-discount settings and immutable attempts.

WooCommerce offers `GET /wp-json/wc/v3/coupons` (paginated) and `GET /wp-json/wc/v3/coupons/{id}`. The approved encrypted read-only REST grant is created and managed by `ARCH-026-API-007` and stored on the existing Woo installation/read-grant models. The Background service has direct PostgreSQL access and a reusable AES-GCM decryption primitive. It can own a narrowly scoped Woo read client without a coupon proxy endpoint; **database access by itself does not authorise decryption or outbound calls**.

## Goals and invariants

- Preserve the existing physical PostgreSQL tables, Prisma models, field types, foreign keys, CHECK constraints, indexes and migration history without modification.
- Keep `shopifyDiscountNodeId` populated with the deterministic identifier `woo:coupon:<positive-provider-id>` for Woo records; preserve Shopify GraphQL IDs for Shopify rows. Never use this external identifier in a database foreign key.
- `providerStatus` is provider lifecycle (ACTIVE, EXPIRED, REMOVED, INACTIVE, EXHAUSTED where verifiably supported); `fixedSelectable` is a supported-rule projection; `providerSnapshot` stores bounded Woo-specific JSON facts; `isAvailable` means **merchant checked/selected**. Coupon sync never auto-selects.
- The merchant UI shows all ACTIVE, current, supported, unexpired coupons (checked and unchecked); it does **not** filter out unchecked rows.
- `NONE` sends no coupon; `FIXED` considers checked, eligible coupons; `AI_BEST_APPLICABLE` considers all supported ACTIVE eligible coupons independent of checkbox flags. Exactly one verified coupon may be offered per recovery, never a stack.
- A Woo FIXED policy stores one **real selected same-Shop `ShopifyDiscount.id`** in `ShopSettings.fixedShopifyDiscountId` to satisfy the unchanged PostgreSQL CHECK/FK. All checkbox choices remain in `ShopifyDiscount.isAvailable`. An Admin FIXED override retains its separate single-FK precedence.
- No unverified or unsupported coupon is promised. Failed full scans, stale catalogue, revoked credentials, missing checkout facts and unsupported customer-specific restrictions fail closed.
- No changes to Shopify settings data, billing, recipient snapshots or historical recovery attempts except explicitly reviewed compatibility alignment of selected flags.

## Non-goals

No new discount/coupon/selection tables, columns, JSONB fields, enums, indexes, migration scripts or historical SQL edits. No plugin-driven coupon upload, local browser requests to Woo REST, direct private API coupon-proxy route, Shared npm schema/contract/pub task, unrelated infrastructure refactor, or new LLM decision-making system. No new merchant/admin permission model.

## Data mapping and ownership

| Existing field | Meaning for WooCommerce | Writer |
|---|---|---|
| `ShopifyDiscountCatalogue.shopId` | Existing Woo Shop; `Shop.platform` differentiates provider | Background |
| `shopifyDiscountNodeId` | `woo:coupon:<id>` stable provider identity, not mutable coupon code | Background |
| `providerType`, `method`, `title`, `singleRedeemCode` | Real normalized Woo type, existing `CODE`, safe code/title | Background |
| `providerStatus`, `startsAt`, `endsAt`, `fixedSelectable` | Provider-derived activity, dates and supported-rule projection | Background |
| `providerSnapshot` (existing JSONB) | Bounded Woo amount/type/restrictions, with secrets and customer lists excluded | Background |
| `lastSeenSyncGeneration`, `lastSyncedAt`, catalogue `status` | Fenced complete scan and freshness | Background |
| `isAvailable` | Merchant's saved checkbox selection, initially false | API-002; Background may clear verified terminally invalid selection |
| `ShopSettings.recoveryOfferMode` | `NONE` / `FIXED` / `AI_BEST_APPLICABLE` | API-002 |
| `ShopSettings.fixedShopifyDiscountId` | Real same-Shop selected row ID anchor for Woo FIXED | API-002 |
| `ShopRecoveryPolicyOverride.fixedShopifyDiscountId` | Existing Admin single chosen row (not the Woo checkbox set) | Existing Admin workflow |
| `RecoveryOutreachAttempt.fixedShopifyDiscountId`, `offerSnapshot` | One chosen real discount-row ID and immutable offer evidence | Background |

No fabricated required business values to satisfy NOT NULL rules. Preserve historical discount rows referenced by FK/outreach; non-current or removed records must not be shown as selectable or used in outreach. Recheck dates at read/send time because expiry can occur between scans. `isAvailable=true` alone is never proof of provider or checkout applicability.

## Direct Background WooCommerce REST access

**Owner: `moda_background`, task `ARCH-036-BACKGROUND-001`.** Preconditions: `ARCH-026-API-007` accepted and a valid, verified Woo read-only grant exists for the Shop. The task must consume the existing `WooCommerceRestReadGrant` ciphertext, nonce, auth tag, key ID and exact shop/installation/authorisation/credential-version context. Use the approved Background AES-256-GCM primitive and **match the actual API envelope format and authenticated AAD byte-for-byte** with cross-repository fixtures; no plaintext storage, copy-pasted independent crypto or forged access grant. Securely configure only the required key IDs for the designated Background runtime and document rotation/revocation; never put Woo keys into queue payloads or logs.

Authenticate and recheck shop/installation/grant `ACTIVE` state, `read` scope, current versions and canonical site before and after each outbound operation. Enforce the API-approved canonical URL, public-HTTPS/DNS-pinning/peer/TLS/SSRF/no-redirect/size/timeouts rules; a private LocalWP hostname is not a reachable hosted-service test and must never relax production protections. Only bounded, paginated GET `/wp-json/wc/v3/coupons` is used by catalogue sync, and direct bounded GET `/wp-json/wc/v3/coupons/{id}` by send-time proof. Do not create a proxy route just to let Background call its own provider.

If the keyring format, TLS transport, or revocation checks cannot be implemented safely within Background ownership, **stop and return the precise gap to the architect** rather than exposing credentials, adding an undocumented proxy, or implementing a competing crypto/security framework. Deployment must explicitly provision the approved Background keyring via secrets; a separate Gateway task is required only if real infrastructure evidence shows an unmet deployment capability.

## Catalogue reconciliation and failure behaviour

Background schedules shop-scoped refreshes, fetches a bounded complete coupon page sequence with consistent pagination totals and stable identity, and commits one fenced generation to existing catalogue/discount rows. New discounts have `isAvailable=false`, existing active-row selections are preserved on ordinary refresh. On **verified terminal provider state after a successful complete sync** the selection may be cleared; recovery never offers inactive coupons even before clearing. Failed/incomplete/unreachable scans must not tombstone unseen coupons, mark an empty catalogue CURRENT, or erase selections. Catalogue becomes non-current and consumers fail closed. Retain the existing Shopify generation locking, retry and correlation behaviour, adapting normalization by shop platform rather than changing schema.

## Merchant selection API (only new API task)

**Owner: `moda_api`, task `ARCH-036-API-002`.** Authenticated Woo installation reads CURRENT catalogue rows, with server pagination/search, normalized status and `isAvailable` checked flag; neither browser nor plugin may query Moda PostgreSQL directly. Revision-guarded manual Save updates `isAvailable` for the complete desired same-Shop selected set and updates `ShopSettings` offer mode plus the real selected-row FK anchor within one Shop-locked transaction. Reject foreign, stale, duplicate, unsupported or empty FIXED selection and conflicts atomically. NONE/AI clear the FIXED anchor but may retain dormant selected flags. Shopify's existing one-coupon setting and Admin override remain unchanged. API owns its own versioned HTTP/OpenAPI contract; **no published Shared contract** is added for presentation data.

## Runtime candidate selection and send-time proof

**Owner: `moda_background`, task `ARCH-036-BACKGROUND-003`.** The former standalone BACKGROUND-002 candidate-filtering task is **superseded**: filtering candidates and proving the chosen coupon are stages of one bounded Background send-time capability. NONE yields none; Woo merchant FIXED filters selected ACTIVE supported in-date same-Shop rows; Woo AI filters all ACTIVE supported rows; Admin FIXED retains its authoritative real single FK; Shopify retains its single chosen FK. Resolve one candidate deterministically with bounded work, use the approved Woo grant to GET that coupon's actual provider identity, verify current code/status/usage/restrictions and trusted checkout/customer facts, recheck merchant selection and grant immediately before finalizing, and persist one real `RecoveryOutreachAttempt` FK + immutable `offerSnapshot` only on valid proof.

A provider detail GET alone is **not checkout applicability proof** for coupon rules requiring customer/basket-specific evidence. Absent facts, unknown eligibility, expired/removed coupons, stale catalogue or revoked keys mean no coupon promise. Do not create a FIXED attempt with NULL/fabricated FK or silently assume a discount-free fallback. Retain existing retry, outbox/message ordering, billable action and recipient-snapshot invariants. Do not invent a new Shared proof schema or an API coupon-proof endpoint.

`moda_commerce` task `COMMERCE-001` adapts the **existing CommerceAgent discount evaluation capability** for supported Woo rules where it is actually consumed. It is a separate, parallel repository-owned concern, not a required intermediary for Background send-time verification and not a new Shared contract. Background must not delegate its own correctness to an unverified Commerce call path.

## Rollout, dependencies and security

This is a pre-production extension to WooCommerce coupon support, but **existing Shopify merchant state/discount history must be preserved**. Coordinate `BACKGROUND-004` and `SHOPIFY-001` before enabling new `isAvailable` semantics. Opt-in Shopify single-FK-to-selected-flag alignment must be repeatable and scoped to Shopify shops; it cannot change Woo shops or historical attempts. The credential/read-grant dependency `ARCH-026-API-007` is **Pending in the uploaded snapshot**; Background Woo reads remain gated until it becomes Complete and real grant/transport proof exists. `ARCH-026-API-008` is not a dependency: its current operations are product reads. Any deployment keyring/reachability limitation must be documented and explicitly gated; no provider secret in code/URLs/logs.

Use the existing logging and telemetry stack; emit bounded sync success/failure/freshness, grant failure and decision evidence without duplicating framework metrics or recording coupon customer lists/credentials. Tests must include same-Shop isolation, key rotation, replay/race handling, lost grant, unstable pagination, expired/removed provider coupons, and Shopify regression checks. The existing shopper-side Woo validation remains authoritative at checkout; a Moda recovery promise cannot bypass it.

## Repository tasks and execution plan

| Task | Owner | State | Dependencies |
|---|---|---|---|
| `ARCH-036-DATABASE-001` | moda_database | Superseded | — |
| `ARCH-036-DATABASE-002` | moda_database | Superseded | — |
| `ARCH-036-API-001` | moda_api | Superseded | — |
| `ARCH-036-API-002` | moda_api | Pending | `ARCH-036-BACKGROUND-001` |
| `ARCH-036-API-003` | moda_api | Superseded | — |
| `ARCH-036-SHARED-001` | moda_shared | Superseded | — |
| `ARCH-036-SHARED-002` | moda_shared | Superseded | — |
| `ARCH-036-SHARED-003` | moda_shared | Superseded | — |
| `ARCH-036-WOOCOMMERCE-001` | moda_woocommerce | Superseded | — |
| `ARCH-036-WOOCOMMERCE-002` | moda_woocommerce | Superseded | — |
| `ARCH-036-BACKGROUND-002` | moda_background | Superseded | — |
| `ARCH-036-BACKGROUND-004` | moda_background | **Ready** | — |
| `ARCH-036-SHOPIFY-001` | moda_app | Pending | `ARCH-036-BACKGROUND-004` |
| `ARCH-036-BACKGROUND-001` | moda_background | Pending | `ARCH-036-BACKGROUND-004`, `ARCH-026-API-007` |
| `ARCH-036-COMMERCE-001` | moda_commerce | Pending | `ARCH-036-BACKGROUND-001` |
| `ARCH-036-ADMIN-001` | moda_admin | Pending | `ARCH-036-BACKGROUND-001`, `ARCH-036-SHOPIFY-001` |
| `ARCH-036-WOOCOMMERCE-003` | moda_woocommerce | Pending | `ARCH-036-API-002` |
| `ARCH-036-BACKGROUND-003` | moda_background | Pending | `ARCH-036-BACKGROUND-001`, `ARCH-036-API-002`, `ARCH-036-SHOPIFY-001` |
| `ARCH-036-SYSTEM-TEST-001` | moda_system_test | Pending | `ARCH-036-BACKGROUND-001/004`, `ARCH-036-API-002`, `ARCH-036-SHOPIFY-001`, `ARCH-036-ADMIN-001`, `ARCH-036-WOOCOMMERCE-003` |
| `ARCH-036-SYSTEM-TEST-002` | moda_system_test | Pending | `ARCH-036-SYSTEM-TEST-001`, `ARCH-036-COMMERCE-001`, `ARCH-036-BACKGROUND-003` |

Table abbreviations for SYSTEM-TEST-001 are only for readability; task YAML dependencies always use fully-qualified task IDs. No non-system-test task depends on a system-test task. Developer manual testing may occur before invoking Ready system tests. No task branches, commits, pushes or `_index.md` changes are made by this definition patch.

## Open questions and change history

- **2026-10-12 Attempt 1:** Generalised database schema plus push-based plugin sync proposed.
- **Attempt 2:** Detailed database migrations proposed.
- **Attempt 3:** Existing catalogue reused; proposed API-owned Woo coupon read proxy.
- **Attempt 4:** All schema changes removed; `providerStatus` provider lifecycle, `isAvailable` merchant selection, real internal FK compatibility anchor.
- **Attempt 5:** Background directly fetches and verifies Woo coupons through a narrowly authorised encrypted REST read grant; API-001/003 and SHARED-001/002/003 superseded; standalone BACKGROUND-002 candidate task folded into BACKGROUND-003. API-002 remains merchant UI read/write boundary only; no new schema, contracts or publication.

The architecture stays Proposed until the developer agrees and the required implementation plus terminal system validation have completed.
