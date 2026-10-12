---
id: ARCH-036
title: Shared provider-neutral commerce discount catalogue and WooCommerce offers
status: proposed
coordinator: moda_architect
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036: Shared provider-neutral commerce discount catalogue and WooCommerce offers

## Status and architecture boundary

**Proposed, awaiting agreement on this complete task plan.** Portable definitions are authored against the `moda-interact-workspace(20261012-161540).zip` code snapshot; they are **defined but not materialised**, not claimed or implemented. No worktree, branch, commit or push has occurred.

This initiative implements **one existing Moda discount catalogue** for Shopify and WooCommerce. It is separate from the **ARCH-035 merchant Admin UI-only parity** initiative. ARCH-035-WOOCOMMERCE-011's local, read-only Woo coupon preview remains valid and is the UI foundation for this initiative; its preview-only radio selection does not constitute persisted coupon configuration. Do not reactivate the superseded ARCH-035 database/background coupon proposals.

### Binding decision

**No new database tables** for Woo coupons, coupon sync staging, merchant selections or offer proofs. Reuse the existing physical PostgreSQL `shopify.ShopifyDiscountCatalogue` and `shopify.ShopifyDiscount` tables, and existing `ShopSettings`, `ShopRecoveryPolicyOverride` and `RecoveryOutreachAttempt.offerSnapshot`. Additive columns/migrations on those **existing** tables are allowed. Existing Shopify IDs/data/foreign keys must be preserved.

## Problem and inspected current state

In `moda-interact-database/prisma/schema.prisma`:

- `Shop.platform` distinguishes `SHOPIFY` and `WOOCOMMERCE`.
- `ShopifyDiscountCatalogue` is one row per Shop with `status`, `syncGeneration`, `activeSyncToken`, sync/last-success timestamps and errors.
- `ShopifyDiscount` holds `shopId`, `shopifyDiscountNodeId`, `providerType`, `method`, `providerStatus`, start/end, code and normalized availability, `providerSnapshot`, and last-seen generation. Its existing composite uniqueness is Shop-scoped; existing policy and outreach FKs reference its `id`.
- `ShopSettings.recoveryOfferMode` is `NONE | FIXED | AI_BEST_APPLICABLE` and `fixedShopifyDiscountId` stores **one** selected Shopify discount; policy overrides mirror this; outreach attempts have immutable offer snapshot JSON.

In `moda-interact-background/src/services/shopify-discount-catalogue.service.ts`, Shopify full sync already uses generation/token fencing, provider read, shop-scoped `upsert`, mark-missing unavailable and a raw SQL lock against the physical `shopify.ShopifyDiscountCatalogue` table. It requires a live Shopify session with `read_discounts`, onboarding and ACTIVE/TRIALING subscription. None of those requirements may be accidentally imposed on Woo installations.

In `moda-interact-woocommerce/includes/Rest/RecoveryCouponCatalogueController.php`, the plugin already supports a privileged, bounded **local** read-only coupon preview via `WC_Coupon`; this preview does not synchronise Moda PostgreSQL or persist an offer selection. It uses code, type, decimal amount, expiry and preliminary restrictions. The Woo plugin has no approved background coupon upload process in the inspected snapshot.

`ARCH-020-COMMERCE-016` already owns deterministic normalized discount eligibility/evidence; the Woo operation authoring catalogue contains `coupons.list` / `coupons.retrieve` but authoring declarations are not proof of an operational live provider connection. `ARCH-026-API-008` provides a planned hardened Woo read-only connection, still `pending` in the inspected task file, with product reads initially allowlisted. It is a hard external prerequisite for live coupon proof.

## Goals

1. One provider-aware discount catalogue in the existing database tables, preserving Shopify behaviour and current physical rows.
2. Woo coupons preloaded by the self-hosted plugin through authenticated, bounded, paginated full-generation snapshot uploads.
3. Changes/deletes/expiry cause reconciliation and unavailability; no partially received generation becomes usable.
4. Merchant Recovery Settings: mutually exclusive `NONE`, `FIXED`, `AI_BEST_APPLICABLE`. In `FIXED` the merchant checks **multiple** permitted Woo coupons; the system offers **at most one** provably applicable coupon per recovery, never stacks codes. AI mode considers supported applicable coupons from the shop's entire current catalogue.
5. Strict shop/provider isolation, durable selection revision, admin override precedence, readable catalogue freshness and fail-closed send-time proof.
6. Preserve existing Shopify GraphQL sync, single-fixed discount selection, stored IDs, recovery billing/WhatsApp ordering and published Shared contracts.

## Non-goals

- No new coupon or sync staging tables, independent Woo coupon database, promotion-credit ledger, new Redis correctness store, historical migration rewrite or physical table/schema relocation.
- No general Woo coupon creation/update, Woo Store API cart mutation, universal coupon-combination engine, usage-limited/customer/product-restricted coupon promises without provider-verified evidence, or invented Meta WhatsApp template parameters.
- No rewrite of ARCH-035 completed UI work, ARCH-027 Woo billing or ARCH-028 outbound status/capacity policy.
- No claim that local WordPress preview selection alone enables outbound coupon messages.

## Agreed merchant semantics

| Offer mode | UI and persisted state | Runtime behaviour |
|---|---|---|
| `NONE` | No checked coupon set; mutually exclusive radio choice | No coupon appears in outbound recovery message |
| `FIXED` | Merchant may check multiple eligible coupons; IDs persisted as a bounded set | Evaluate only those approved IDs and send **one** verified eligible coupon |
| `AI_BEST_APPLICABLE` | No curated set; all supported current-catalogue candidates may be considered | Existing deterministic Commerce evaluator ranks by provable savings, but proof still required; no invented code |

Selected coupons are **alternatives**, not a stack. When a coupon expires/is deleted later, its saved selection may remain visible as unavailable to the merchant, but is excluded from candidate resolution and sends. `RecoveryOfferMode` enum values are retained for compatibility; shared DTOs make the Woo multiple-choice semantics explicit. Shopify retains its legacy single `fixedShopifyDiscountId` UI and save contract until a separately agreed Shopify UI change.

## Proposed architecture and physical persistence

```text
SHOPIFY (existing)                         WOOCOMMERCE (new)
GraphQL full reconciliation                 WC_Coupon / Action Scheduler
        |                                    | Full initial + change-driven sync
        v                                    v
Shopify Background sync                Woo PHP snapshot producer
        |                                    | Authenticated versioned pages
        |                                    v
        |                               Moda API ingestion
        |                                    |
        +-----------------+------------------+
                          v
          EXISTING shopify.ShopifyDiscountCatalogue
          EXISTING shopify.ShopifyDiscount
          + provider / stable external ID / generation
          + bounded in-place sync progress (NO NEW TABLE)
                          |
            +-------------+------------------+
            |                                |
  ShopSettings / policy override     Commerce rule evaluator
  selectedDiscountIds JSON           (reuse ARCH-020 code)
            |                                |
            +-------------+------------------+
                          v
         Background recovery offer candidate decision
                          |
                          v
       Authenticated API Woo coupon live proof (GET only)
                          |
                  valid for exact checkout?
                    /                 \
                   yes                 no/unknown
                    |                   |
             One immutable offer       No coupon claim
             in existing attempt       / fail closed
                    |
               Existing WhatsApp + recovery billing
```

**Compatibility-first database contract:** DATABASE-001 retains the existing Prisma model names (`ShopifyDiscountCatalogue`, `ShopifyDiscount`), required legacy `shopifyDiscountNodeId` field and `(shopId, shopifyDiscountNodeId)` compound-unique selector, because currently deployed Shopify/Background/Admin/Commerce consumers use them. Add provider-aware fields and a unique `(shopId, provider, externalDiscountId)` identity to those **same** models; backfill existing Shopify IDs, while allowing legacy new Shopify writes to omit the new external ID. Woo rows use a deterministic `woo:coupon:<id>` value in the required **legacy compatibility-key** column and the real positive Woo coupon ID in `externalDiscountId`; never present the compatibility key as a genuine Shopify GID. Physical data remains in the **existing** `shopify` schema and physical tables. Provider-neutral Prisma logical renaming is **deferred** until all existing generated-client consumers can be coordinated; do not create two Prisma models pointing to one physical table or impose a breaking rename inside DATABASE-001.

Multi-coupon selections use a **bounded `selectedDiscountIds` JSONB array (maximum 50 unique discount row IDs)** on **both** existing `ShopSettings` and `ShopRecoveryPolicyOverride`, rather than a new join table. DATABASE-002 must replace the two existing ARCH-016 *policy* fixed-offer CHECK constraints in a **new forward migration**: `FIXED` accepts **exactly one** of the existing Shopify singular FK or a nonempty Woo selected-ID array; `NONE`/`AI_BEST_APPLICABLE` require neither. Retain the existing `RecoveryOutreachAttempt` single chosen-discount FK and its ARCH-016 check; one attempt may claim at most **one** coupon. JSON element membership is **not** a relational FK; API-002/Admin must validate all IDs for shop and provider under the same Shop-row lock and `updatedAt` CAS before saving. Expired/deleted saved IDs remain visible as unavailable, never proof for sending. The existing `RecoveryOutreachAttempt.offerSnapshot` remains immutable evidence; no new attempt table.

## Snapshot flow, durability and ordering

Proposed wire contract: `woo.discounts.sync.v1`, implemented under Shared ownership. Woo plugin authenticates with the existing installation secret; the hosted API derives the Shop from that credential, not a user-supplied `shopId`. Initial connect triggers a full snapshot; coupon changes/deletes and periodic reconciliation coalesce into additional full snapshots. WP Action Scheduler must not block coupon save or assume WP-Cron is always timely.

The authenticated API owns `start / page / complete` with bounded coupon count, page size, payload, deadline and per-page digest. Start allocates a server-controlled generation/token in the **existing catalogue row** and sets status `SYNCING`. Each page idempotently upserts same-shop Woo coupon rows with that generation, using existing discount rows as staged data; a catalogue that is not `CURRENT` must not be used to authorize offers. Bounded page-progress/fingerprint state remains on the existing catalogue row, **not a new staging table or Redis-only correctness state**.

Completion locks the catalogue, verifies all expected pages/row identities and generation token, atomically makes this generation current and marks rows absent from it unavailable. A partial, aborted, superseded, replayed, reordered or timed-out generation never becomes `CURRENT`, and stale data cannot be treated as valid offer evidence. Periodic reconciliation covers missed WordPress hooks and deletes. A failed sync records bounded error information and must be retried; if stale, offer use is denied even when old row contents remain readable for administrative explanation.

Coupon content may change during paginated enumeration; producers must use stable cursor boundaries, bounded retries or restart rather than silently claim an exact snapshot that they cannot prove. Out-of-order authenticated pages fail without cross-generation writes. Woo coupons are *provider-owned*, and the shared table is a materialized view, not the provider of record.

## Offer resolution, selection and provider proof

`NONE` is absolute. For `FIXED`, resolve only same-Shop IDs from the current effective selection/override; for `AI_BEST_APPLICABLE`, consider all current supported provider coupons. Candidate enumeration, local rule normalization and deterministic ranking are not send-time truth. The existing ARCH-020 Commerce evaluator must be reused, not forked; initial supported coupon types are **positive-value** `percent` and `fixed_cart` without unsupported basket/customer/usage restrictions. Zero-value, expired, disabled, usage-exhausted or restricted coupons are not sent without explicit provable eligibility support.

Before any message offers a coupon, Background must obtain shop-bound provider proof through a narrow API-owned Woo read port using the verified Woo REST grant from `ARCH-026-API-008` (with an explicitly approved `coupons/{id}` GET allowlist). Recheck trusted checkout/basket identity, current coupon rules, currency and status against the prepared candidate. Private LocalWP sites or an unconfigured/revoked provider grant cannot provide remote live proof and must **fail closed**—do not treat cache or an administrator preview as authoritative. Woo checkout still performs final redemption verification at use time. No coupon can be promised based on a rule/evidence category of UNKNOWN. Unverifiable or unsupported offers produce an approved truthful no-coupon outcome, without silent stacking or guessed template parameters.

Keep the existing proactive recovery credit rules, recipient snapshot, template allowlists, Meta retries and attempt immutability. Do not create another billing event or new outbound WhatsApp parameter convention. If supported templates cannot safely carry a coupon code, stop the coupon-claim subtask and return the gap to the architect.

## Repository ownership and contract table

| Boundary | Source of truth / task owner |
|---|---|
| Existing table schema, constraints, migrations | `moda_database` |
| Versioned sync/offer/proof wire schemas | `moda_shared`; publish separately |
| Shopify discount sync worker | `moda_background` |
| Shopify merchant Recovery Settings compatibility | `moda_app` |
| Woo local enumeration, push, event scheduling and merchant UI | `moda_woocommerce` |
| Woo authenticated upload, selected IDs CAS, provider coupon read | `moda_api` |
| Existing rule evaluation and exact eligible savings evidence | `moda_commerce` |
| Final recovery outreach coupon proof and message snapshot | `moda_background` |
| Provider-aware internal Admin recovery panel | `moda_admin` |
| Independent black-box end-to-end testing | `moda_system_test` |

The Woo PHP producer and Node consumer use the Shared v1 schema as the canonical wire definition with golden JSON fixtures for PHP runtime parity. Consumers import published runtime-safe Shared exports rather than maintaining incompatible service-local copies. Shopify's existing webhook sync payload stays on its published `/shopify` contract; this initiative does not replace or mutate it in place.

## Consistency, failure handling and security

- Shop/provider external coupon identity and catalogue generation are durable; use existing unique keys/indices and row locks, with `status=CURRENT` only after full commit.
- Idempotent replay uses bounded page identifiers/digests, not exactly-once network delivery. Incomplete generations do not invalidate/delete existing rows until finalization, but no non-CURRENT catalogue is eligible to send.
- Selection writes use Shop-row locking, expected policy revision and transactional same-shop membership checks. Changes to merchant preferences never overwrite active admin overrides; effective and merchant projections remain distinct.
- Provider proof uses approved public HTTPS/read grant, pinned origin/redirect protection and narrow shop/recovery authorization. Do not expose Consumer Keys, installation secrets, raw customer PII, full provider payloads or internal proofs to React, webhooks or logs.
- Plugin publisher retries with bounded Action Scheduler work; no synchronous coupon-save HTTP dependencies. Expired/disabled/usage-limited coupons are excluded or classified UNKNOWN; no false customer-facing promise.
- Maintain structured event names through the canonical Shared logger on Node services; WordPress uses approved scoped logging without sensitive coupon/customer payloads. Existing OTel/framework instrumentation is reused; no redundant custom HTTP metric.

## Capacity and infrastructure assessment

The Woo coupon **catalogue workload** is separate from raw Shopify checkout webhook throughput. A store may have hundreds or thousands of coupons but only occasional full sync. Use bounded keyset pages, hard payload/total caps and coalescing to avoid a large synchronous WordPress request or unbounded API transaction. PostgreSQL transaction/connection pressure is per completed generation rather than per checkout. Per-tenant fairness and retries prevent one large shop starving others. Redis is not a durable source of coupon sync correctness. The API may use its existing HTTPS host and the plugin uses outbound HTTPS; the inspected snapshot does not justify a new Render service or Gateway task. If the existing gateway cannot route the approved narrowly authenticated private proof, return the concrete deployment dependency for an explicit `moda_gateway` task; do not silently change Gateway infrastructure.

## Rollout / compatibility

**Compatibility-preserving rollout.** Woo coupon delivery is pre-production, but existing Shopify catalogue/selection data and migrations may already be applied and must be preserved. Additive DB migration and existing-row backfill first; release Shared contracts after accepted implementation; adapt/deploy Shopify readers/background without a breaking producer event change; bring up Woo API ingest; then Woo plugin producer/hooks and selectable settings UI; enable provider proof/evaluator only after read grant, background policy and sending tests are accepted. Until final proof gate, default Woo offer is NONE and no cached coupon is promised.

Never edit old Prisma migration files or rely on wiping existing Shopify durable state. Physical table/schema rename is deliberately not part of this rollout; future renaming requires its own agreed architecture. Rollback disables Woo coupon offer sending and sync ingest while preserving existing rows and historical outreach attempts; check schema readers still accept additive columns.

## Decisions / Tasks

| Task | Logical owner | Defined status | Depends on |
|---|---|---|---|
| `ARCH-036-DATABASE-001` | `moda_database` | Ready | — |
| `ARCH-036-DATABASE-002` | `moda_database` | Pending | `ARCH-036-DATABASE-001` |
| `ARCH-036-SHARED-001` | `moda_shared` | Ready | — |
| `ARCH-036-SHARED-002` | `moda_shared` | Ready | — |
| `ARCH-036-SHARED-003` | `moda_shared` | Pending | `ARCH-036-SHARED-001`, `ARCH-036-SHARED-002` |
| `ARCH-036-BACKGROUND-001` | `moda_background` | Pending | `ARCH-036-DATABASE-001` |
| `ARCH-036-SHOPIFY-001` | `moda_app` | Pending | `ARCH-036-DATABASE-002`, `ARCH-036-SHARED-003`, `ARCH-036-BACKGROUND-001` |
| `ARCH-036-API-001` | `moda_api` | Pending | `ARCH-036-DATABASE-001`, `ARCH-036-SHARED-003` |
| `ARCH-036-WOOCOMMERCE-001` | `moda_woocommerce` | Pending | `ARCH-036-API-001`, `ARCH-036-SHARED-003` |
| `ARCH-036-WOOCOMMERCE-002` | `moda_woocommerce` | Pending | `ARCH-036-WOOCOMMERCE-001` |
| `ARCH-036-API-002` | `moda_api` | Pending | `ARCH-036-DATABASE-002`, `ARCH-036-SHARED-003`, `ARCH-036-API-001` |
| `ARCH-036-WOOCOMMERCE-003` | `moda_woocommerce` | Pending | `ARCH-036-API-002`, `ARCH-036-WOOCOMMERCE-002` |
| `ARCH-036-API-003` | `moda_api` | Pending | `ARCH-026-API-008`, `ARCH-036-DATABASE-001`, `ARCH-036-SHARED-003` |
| `ARCH-036-COMMERCE-001` | `moda_commerce` | Pending | `ARCH-036-DATABASE-001`, `ARCH-036-SHARED-003` |
| `ARCH-036-BACKGROUND-002` | `moda_background` | Pending | `ARCH-036-DATABASE-002`, `ARCH-036-SHARED-003`, `ARCH-036-BACKGROUND-001` |
| `ARCH-036-BACKGROUND-003` | `moda_background` | Pending | `ARCH-036-BACKGROUND-002`, `ARCH-036-COMMERCE-001`, `ARCH-036-API-003`, `ARCH-036-WOOCOMMERCE-003` |
| `ARCH-036-ADMIN-001` | `moda_admin` | Pending | `ARCH-036-DATABASE-001`, `ARCH-036-BACKGROUND-001`, `ARCH-036-API-001` |
| `ARCH-036-SYSTEM-TEST-001` | `moda_system_test` | Pending | `ARCH-036-DATABASE-001`, `ARCH-036-DATABASE-002`, `ARCH-036-SHARED-003`, `ARCH-036-BACKGROUND-001`, `ARCH-036-SHOPIFY-001`, `ARCH-036-API-001`, `ARCH-036-WOOCOMMERCE-001`, `ARCH-036-WOOCOMMERCE-002`, `ARCH-036-API-002`, `ARCH-036-WOOCOMMERCE-003`, `ARCH-036-ADMIN-001` |
| `ARCH-036-SYSTEM-TEST-002` | `moda_system_test` | Pending | `ARCH-036-SYSTEM-TEST-001`, `ARCH-036-API-003`, `ARCH-036-COMMERCE-001`, `ARCH-036-BACKGROUND-002`, `ARCH-036-BACKGROUND-003` |

## Execution graph and external gates

Independent first definitions: `ARCH-036-DATABASE-001`, `ARCH-036-SHARED-001`, `ARCH-036-SHARED-002`. All other tasks stay Pending until their explicit requirements are Complete. Shared publication follows **accepted** implementation and must not redo tests. `ARCH-026-API-008` is a separately owned *pending* read-grant prerequisite for `ARCH-036-API-003`; source-code presence does not satisfy task completion.

```text
SHARED-001 + SHARED-002 -> SHARED-003 (publish) ------+
DATABASE-001 ----------> DATABASE-002                 |
   |                       |                          |
   v                       v                          v
BACKGROUND-001         API-002 <---- API-001 <---- SHARED-003
   |                      |             |               |
SHOPIFY-001             WOO-003     WOO-001 -> WOO-002  |
                          |                             |
ARCH-026-API-008 ------> API-003       COMMERCE-001      |
                          |              |              |
                 BACKGROUND-002 ----------+--------------+
                          |              |
                          +--> BACKGROUND-003 (proof/send)

ADMIN-001 (provider-aware view) and terminal SYSTEM-TEST-001/002
follow their listed implementation dependencies; no implementation depends
on a SYSTEM-TEST task.
```

The table below, not this schematic, is authoritative for complete task dependencies. All task YAML files carry canonical individual status; indexes are deferred until explicitly authorised.

## Open questions / implementation STOP gates

- `ARCH-026-API-008` must be accepted (and its Woo grant genuinely usable) before API-003. Private/LocalWP cannot be treated as a publicly reachable live provider.
- If Woo does not provide the exact coupon lifecycle hook or live provider fields needed to prove a supported rule, return to the architect and narrow the eligible set instead of guessing.
- `AI_BEST_APPLICABLE` uses existing Commerce deterministic evaluation; if production agent composition lacks that port, the Commerce owner reports the integration gap rather than creating a replacement evaluator.
- If the existing Meta outbound template lacks a verified coupon field, no customer-facing discount claim is permitted until a separately approved template contract exists.
- Default policy for unknown/expired/unverifiable coupons is *no discount claim*. Do not quietly reinterpret selecting several checkboxes as coupon stacking.

## Change history

- 2026-10-12 — Developer approved one provider-neutral catalogue reusing existing Shopify tables, no new discount tables, Woo-specific push sync, FIXED checkbox-permitted set and AI eligibility based on the current catalogue. Created portable implementation, publication, and terminal system-test definitions. No `_index.md` files or implementation source touched.
