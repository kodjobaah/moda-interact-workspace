---
id: ARCH-036
title: Reuse existing Shopify discount tables and provider-safe Woo coupon retrieval
status: proposed
coordinator: moda_architect
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036 — Shared Shopify/WooCommerce discount catalogue without database changes

## Status and developer decision

**Proposed — revised task contracts, 12 October 2026 (Attempt 4).** No implementation or schema change authorised by this documentation patch. These tasks are defined but **not materialised** into developer worktrees. Do not edit `docs/decisions/**/_index.md` until the architecture session has been explicitly reconciled.

**Non-negotiable constraint:** Reuse the existing `shopify.ShopifyDiscountCatalogue`, `shopify.ShopifyDiscount`, `shopify.ShopSettings`, `shopify.ShopRecoveryPolicyOverride` and `commerce.RecoveryOutreachAttempt` models and actual SQL tables, fields, foreign keys, check constraints, indexes, Prisma enum definitions and historical migrations **unchanged**. No new coupon, selection, staging, audit or proof tables; **no additional JSONB or boolean columns; no Prisma schema changes or migrations of any kind** for ARCH-036. Existing `providerSnapshot` is JSONB.

## Problem and inspected implementation

Current Shopify catalogue ingestion in `moda-interact-background/src/services/shopify-discount-catalogue.service.ts` upserts every seen row with `isAvailable=true`, marks missing/outage rows `isAvailable=false`, and merchant readers use this as provider availability. This conflicts with the merchant's intended checkbox semantics for WooCommerce.

The user-set meanings are:

| Existing column | New authoritative meaning | Writer |
|---|---|---|
| `providerStatus` | Provider lifecycle (`ACTIVE`, `EXPIRED`, `REMOVED`, `INACTIVE`, `EXHAUSTED`, or bounded documented provider-specific state) | Background normaliser |
| `fixedSelectable` | Whether type/restrictions are supported as a merchant-selectable fixed offer | Background normaliser |
| `isAvailable` | **Merchant selected for Moda recovery** (`true` checked, `false` unchecked). Never provider presence. | Merchant API; Background may clear on verified terminal invalidation, never auto-select |
| `providerSnapshot` | Safe, bounded provider-specific JSONB rules, amount and restrictions | Background normaliser |
| `ShopifyDiscountCatalogue.status` | Whether the shop's complete catalogue is CURRENT/stale/ERROR/SYNCING | Background synchronisation |

The actual `ShopSettings` and `ShopRecoveryPolicyOverride` ARCH-016 SQL CHECK constraints require a non-null `fixedShopifyDiscountId` FK for `recoveryOfferMode=FIXED`; `RecoveryOutreachAttempt` has an analogous single-chosen-FK CHECK. These remain unchanged. A Woo `FIXED` configuration must therefore maintain a legitimate existing discount-row FK anchor, not an arbitrary Woo string. Shopify's existing one-discount experience must continue to work.

## Goals and non-goals

- Preload Woo coupon data by Background-driven, bounded `GET /wp-json/wc/v3/coupons` through the API-owned Woo REST read connection (`ARCH-026-API-008`). Worker never receives Woo credentials.
- Reuse the existing table names, Prisma models and constraints for both provider platforms; no new database schema whatsoever.
- Expose only ACTIVE, in-date, CURRENT-catalogue, supported (`fixedSelectable`) coupon rows as selectable, whether checked or unchecked. Keep inactive historical rows for existing FK/outreach references; do not hard-delete them.
- Support multiple **merchant checkbox** selections via existing `ShopifyDiscount.isAvailable`, with manual Save and optimistic concurrency; do not conflate them with coupon provider status.
- Preserve Shopify single FIXED coupon setting and Admin single-override FK, using an explicit safe transition of historical Shopify selected flags.
- Send at most one verifiably eligible coupon per recovery; fail closed when no provider/checkout-specific proof is available.
- Keep WordPress's existing two-stage menu navigation, all 20 merchant locales, and modular React components.

Non-goals: schema/DDL changes, a new Woo coupon database, plugin-pushed sync, alternative queue/storage, direct Woo credentials outside API, changing Shopify discounts into Woo GIDs, historic outbound attempt rewrites, or automatically persisting the preview-only ARCH-035 coupon picker.

## Reuse of required existing fields

For a Woo coupon with provider numeric ID `719` and code `MODATEST20`, map real values into the required `ShopifyDiscount` fields:

| Existing field | Woo data/meaning |
|---|---|
| `shopId` | Actual authenticated Woo Shop ID (existing `Shop.platform=WOOCOMMERCE`) |
| `shopifyDiscountNodeId` (non-null) | Deterministic `woo:coupon:719` identifier; unique with `shopId`. Code is mutable, so code must not be the identity |
| `providerType` (non-null) | Bounded Woo type identifier, e.g. `WOOCOMMERCE_FIXED_CART` |
| `method` (non-null enum) | Existing `CODE` enum; no enum extension |
| `providerStatus` (non-null) | Verified normalised provider lifecycle, not merchant selection |
| `title` (non-null) | Sanitised Woo coupon code/title |
| `providerSnapshot` (non-null JSONB) | Bounded real provider amount/type, expiry and supported restrictions; no secrets or full customer email lists |
| `lastSeenSyncGeneration`, `lastSyncedAt` (non-null) | Actual fenced catalogue generation and UTC observation timestamp |
| `isAvailable` (non-null boolean) | Initially false; merchant's selected state, not set true by Background |
| `fixedSelectable` (non-null boolean) | Background-owned supported-rule projection |
| `singleRedeemCode`, dates, summary (nullable) | Actual Woo coupon code/expiry/summary where available |

Do **not** fabricate data for required business fields merely to satisfy NOT NULL constraints. Use the Woo source's real, normalised facts. `shopifyDiscountNodeId` is a regular unique string, not a foreign key, so its Woo namespaced value is appropriate. `ShopSettings.fixedShopifyDiscountId`, `ShopRecoveryPolicyOverride.fixedShopifyDiscountId` and `RecoveryOutreachAttempt.fixedShopifyDiscountId` are **real FKs to `ShopifyDiscount.id`**: they MUST use an existing, same-Shop internal discount ID, never the provider coupon ID or `woo:coupon:719`.

## Existing-constraint compatible selection

1. All selections reside in `ShopifyDiscount.isAvailable`. An ACTIVE row may be selected or unselected; both must be visible to the selector if current and fixedSelectable.
2. For Woo `FIXED`, the merchant may check 1–50 same-Shop active selectable discounts. A single real checked `ShopifyDiscount.id` (chosen deterministically) is stored in `ShopSettings.fixedShopifyDiscountId` as a **compatibility anchor**, while the full set is the rows with `isAvailable=true`. This satisfies the unmodified ARCH-016 FIXED FK and CHECK. The anchor is not the only permitted coupon.
3. For `NONE` or `AI_BEST_APPLICABLE`, `ShopSettings.fixedShopifyDiscountId` must be NULL as required by the current CHECK. Selected flags may be retained as a dormant merchant preference but do not control NONE or AI sending.
4. A Woo FIXED Save containing zero selections is rejected (or the merchant explicitly changes mode to NONE/AI). API selection writes and anchor/mode/revision changes are one Shop-locked transaction. Existing Shopify single selected-FK path and Admin single FK override remain separate and valid.
5. For Admin FIXED, the admin's existing single override FK is authoritative for that override, independent of merchant-selected checkbox flags; the pointed discount must still be same-Shop active/eligible at use time.
6. Historical/current recovery outreach attempts store **one** chosen real internal discount FK and an immutable `offerSnapshot`, not multiple checked IDs. If a configured FIXED mode has no valid candidate, do not insert a FIXED attempt with a NULL FK or fake a coupon; return a fail-closed resolution and escalate any requested no-coupon fallback as a separate architect decision.

## Provider availability, freshness and selection lifecycle

- Background sync sets `providerStatus` and `fixedSelectable`; it does not auto-check coupons. New rows default to false. Active coupon updates preserve existing selected flags.
- In a **verified, successfully completed** full sync, confirmed expired/removed/inactive/exhausted rows become non-ACTIVE and may have their selected flags cleared false so reactivation requires deliberate merchant re-selection. They remain in the database for history and FK integrity.
- A failed/incomplete/unstable scan or revoked read grant does **not** mark unseen coupons REMOVED and does **not** erase merchant selections. Catalogue status becomes non-current; retrieval and outreach fail closed.
- A coupon can expire between sync runs; all reads and send-time resolution re-check dates and supported rules in addition to normalised providerStatus and catalogue freshness.
- `isAvailable=true` alone is never enough for retrieval/send-time eligibility. Catalogue selection UI filters ACTIVE + fixedSelectable + dates + CURRENT; FIXED outreach adds selected, AI ignores selected, and both require live checkout-specific proof.

## Request and event flow

```text
Background scheduled job
  -> API internal Woo coupon-page read (approved encrypted read grant)
  -> WooCommerce wc/v3/coupons, bounded pages and stable completed scan
  -> Background generation-fenced normalisation
  -> EXISTING ShopifyDiscountCatalogue / ShopifyDiscount (no migration)
       providerStatus := provider availability
       isAvailable   := merchant selected (never auto true)
  -> Woo Recovery Settings: ACTIVE selectable rows, selected checkboxes
  -> API selected-flag + real-FK anchor transaction
  -> Background FIXED/AI candidate resolution
  -> API live coupon detail proof + checkout facts
  -> one valid existing RecoveryOutreachAttempt or fail closed
```

## Repository ownership and cross-service contracts

| Owner | Task(s) | Responsibility |
|---|---|---|
| moda_database | DATABASE-001/002 (Superseded) | No Prisma/schema/migration implementation |
| moda_shared | SHARED-001/002/003 | Bounded API-to-Background coupon-read and send-time proof wire contracts; **no recovery-policy schema change**; publish after review |
| moda_api | API-001/002/003 | Woo provider read grant adapter; merchant selected-flag CAS with real FK; live proof |
| moda_background | BACKGROUND-004 then BACKGROUND-001/002/003 | Stop Shopify auto-selection; background Woo pull; candidates and verified outreach |
| moda_app | SHOPIFY-001 | Preserve Shopify single FK and selection behavior |
| moda_woocommerce | WOOCOMMERCE-003 | Three mode cards and checkbox UI; preserve navigation/locales |
| moda_commerce | COMMERCE-001 | Support Woo provider evaluation, one coupon, fail-closed rules |
| moda_admin | ADMIN-001 | Distinguish provider status from merchant-selected flags, preserve override FK |
| moda_system_test | SYSTEM-TEST-001/002 | Terminal end-to-end, no-DDL and cross-provider certification |

Shared runtime contracts are justified only at the **actual separately deployed API↔Background/Commerce boundaries** (coupon page/proof). Existing `@modainteract/moda-interact-shared/recovery-policy` schema remains unchanged because the SQL-valid compatibility FK is still populated for FIXED. API-owned merchant GET/PUT DTOs remain API contracts; do not publish duplicate selection-storage wire types.

## Constraints, consistency, and failure handling

- Shop-locked and revision-guarded merchant selection write updates flags, `ShopSettings.recoveryOfferMode`, real anchor FK and settings `updatedAt` atomically. Validate 1–50 unique IDs on Woo FIXED; reject wrong Shop, inactive, unsupported, stale, duplicate or malformed selections. Repeated identical saves are idempotent.
- Woo coupon code rename updates one row using stable `woo:coupon:<id>` key, not a newly generated ID. A missing provider coupon is REMOVED only after a validated complete stable generation, not a provider outage.
- Provider read credentials remain solely in API; `ARCH-026-API-008` currently gates additional coupon list/detail operations and requires a public HTTPS reachable provider. Do not invent a LocalWP `.local` connection without a tunnel.
- Background may process duplicated/out-of-order jobs; existing catalogue generation and sync token fencing prohibit older jobs from clearing current selected flags or rolling back newer provider status.
- Existing SQL FKs/CHECK constraints remain strict, including `RecoveryOutreachAttempt` single chosen FK, and must be tested directly on unchanged migrated PostgreSQL.
- Existing Shopify data needs a bounded, rerunnable one-time **data-only** flag alignment from its saved `ShopSettings.fixedShopifyDiscountId`; no schema migration. Coordinate deployment of sync semantics and Shopify merchant readers so user settings are preserved.
- Customer-specific restrictions, usage limit race, stale data and live API outages fail closed; never promise an unprovable coupon. Outbound recipient snapshots, idempotency and billing semantics stay as already accepted.

## Rollout and infrastructure

This is pre-production for Woo discount support, but existing Shopify settings and persisted outreach history are durable and must be preserved. No schema deployment step. Implement/test BACKGROUND-004 and SHOPIFY-001 as a coordinated change before enabling new selection semantics. Then publish Shared contracts, accept API-owned provider read, sync Woo catalogue, enable Woo selection and finally verify send-time proof. Roll back via provider offer capability gating; do not reset selected flags blindly.

No new Gateway task is assumed; the internal API coupon-page/proof route must be verified private. If the existing infrastructure cannot securely expose it, stop for an explicit gateway task. Existing PostgreSQL/BullMQ remains the runtime. Log only bounded Shop/coupon identities through the approved shared logger; no secrets or sensitive customer restriction lists.

## Architecture execution plan

| Task | Owner | State | Dependencies |
|---|---|---|---|
| DATABASE-001 | moda_database | **Superseded** | — |
| DATABASE-002 | moda_database | **Superseded** | — |
| SHARED-001 | moda_shared | Ready | — |
| SHARED-002 | moda_shared | Ready | — |
| SHARED-003 | moda_shared | Pending | SHARED-001, SHARED-002 |
| BACKGROUND-004 | moda_background | Ready | — |
| SHOPIFY-001 | moda_app | Pending | BACKGROUND-004 |
| API-001 | moda_api | Pending | ARCH-026-API-008, SHARED-003 |
| BACKGROUND-001 | moda_background | Pending | API-001, SHARED-003, BACKGROUND-004 |
| API-002 | moda_api | Pending | SHARED-003, BACKGROUND-001 |
| API-003 | moda_api | Pending | API-001, SHARED-003 |
| BACKGROUND-002 | moda_background | Pending | SHARED-003, BACKGROUND-001, BACKGROUND-004, SHOPIFY-001 |
| COMMERCE-001 | moda_commerce | Pending | SHARED-003 |
| ADMIN-001 | moda_admin | Pending | BACKGROUND-001, SHOPIFY-001 |
| WOOCOMMERCE-003 | moda_woocommerce | Pending | API-002 |
| BACKGROUND-003 | moda_background | Pending | BACKGROUND-002, COMMERCE-001, API-003, WOOCOMMERCE-003 |
| SYSTEM-TEST-001 | moda_system_test | Pending | SHARED-003, API-001/002, BACKGROUND-001/004, SHOPIFY-001, ADMIN-001, WOOCOMMERCE-003 |
| SYSTEM-TEST-002 | moda_system_test | Pending | SYSTEM-TEST-001, API-003, COMMERCE-001, BACKGROUND-002/003 |
| WOOCOMMERCE-001/002 | moda_woocommerce | **Superseded** | — |

No non-system task depends on a system-test. System-test tasks remain terminal and run only after implementation tasks are accepted and manual validation is complete.

## Open questions and change history

- **2026-10-12 Attempt 1:** new generalized catalogue columns and plugin snapshot upload proposed.
- **Attempt 2:** expanded database migration task details.
- **Attempt 3:** reused existing catalogue with Background pull, but proposed JSON selected-ID migration.
- **Attempt 4:** **no database changes of any kind**. Reuse existing required fields with real Woo values and deterministic namespaced provider IDs. `providerStatus` is provider lifecycle; `isAvailable` merchant selection; existing FIXED policy and outreach FKs are satisfied with real discount-row IDs. DATABASE-002 superseded; new BACKGROUND-004 isolates Shopify flag-semantics compatibility work.

Unresolved before deployment: confirm fallback business behavior if a FIXED recovery has no eligible proof. The implementation contract currently fails closed and preserves the unchanged SQL CHECK, rather than inventing a NULL-FK FIXED attempt.
