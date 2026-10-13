---
id: ARCH-036
title: Reuse existing discount catalogue with PostgreSQL-leased Woo coupon dispatch
status: proposed
coordinator: moda_architect
created: 2026-10-12
updated: 2026-10-13
---

# ARCH-036 — WooCommerce coupon catalogue and merchant configuration

## Status and session boundary

**Proposed — task refinement Attempt 9 (13 October 2026).** This session authorises **five implementation tasks**: the narrowly scoped `ARCH-036-DATABASE-003` global-lease enum migration, `ARCH-036-BACKGROUND-001`, `ARCH-036-API-002`, `ARCH-036-WOOCOMMERCE-003`, and `ARCH-036-ADMIN-001`. Their purpose is to synchronise existing Woo coupons into the current database, display them and persist merchant settings, without modifying CommerceAgent or recovery execution. A separate terminal `ARCH-036-SYSTEM-TEST-001` validates these outcomes; it is not an implementation task.

**Outside this session:** all CommerceAgent/evaluator/tools/conversation behaviour, recovery processing or coupon application in outbound messages, send-time provider proof, WhatsApp, Shopify UI/synchronisation changes, and changes to coupon redemption. The historical `COMMERCE-001` and `SYSTEM-TEST-002` task definitions remain **unchanged and deferred outside this four-task session**: their current `pending` metadata must not be mistaken for authorisation to execute them. Revisit them only in a separately agreed initiative/session; neither is part of the execution/dependency graph below.

No ARCH-036 branches or worktrees have been materialised in the supplied snapshot. Do not change `docs/decisions/**/_index.md` until the developer confirms that architecture refinement is complete.

## Current state and problem

The existing PostgreSQL `ShopifyDiscountCatalogue`, `ShopifyDiscount` and `ShopSettings` provide the durable structures for coupon records and merchant settings; no new catalogue tables, fields or indexes are authorised. The **only schema exception** is adding `WOO_COUPON_SYNC_DISPATCH` to the existing `public.BackgroundRuntimeLeaseName` enum, owned by `DATABASE-003`. Shopify synchronisation currently uses `ShopifyDiscount.isAvailable` as provider availability, and Shopify's single merchant choice is stored in `ShopSettings.fixedShopifyDiscountId`. **Both Shopify behaviours remain unchanged.**

WooCommerce needs a read-only synchronisation path and a merchant-facing interface for selecting several coupon records. For **WooCommerce rows only**, `isAvailable` stores the merchant's checkbox selection; provider availability is derived separately from `providerStatus`, `fixedSelectable`, catalogue status/generation and validity dates. Consumers must branch on `Shop.platform`, not assume that `isAvailable` has the same meaning for both providers.

`ARCH-026-API-007` owns acquisition and encryption of the merchant-approved WooCommerce REST read grant; it is `pending` in the supplied snapshot. Background may consume that grant only after its task is accepted. `ARCH-026-API-008` is not a dependency for coupon pages.

## Goals

- Fetch a complete, bounded, paginated Woo `/wp-json/wc/v3/coupons` catalogue into existing Shop-scoped discount rows without Woo plugin uploads or an API provider-proxy endpoint.
- Retain stable Woo external identity `woo:coupon:<positive-provider-id>` in `shopifyDiscountNodeId`; use actual internal `ShopifyDiscount.id` values for existing FKs. No fabricated IDs or coupon-storage schema changes; only the global lease enum addition is approved.
- Persist Woo coupon metadata and provider lifecycle independently of merchant checkbox selection. New Woo coupons start unselected; ordinary and failed synchronisation must not automatically select/deselect coupons. Do not delete referenced historical rows.
- Provide tenant-authorised, paginated coupon reads and an atomic, conflict-checked Save of the Woo selected set and `ShopSettings.recoveryOfferMode` (`NONE`, `FIXED`, `AI_BEST_APPLICABLE`). These values are configuration only within ARCH-036, not a claim that outbound policy execution has been implemented.
- Show all current, ACTIVE, supported, in-date coupons (checked and unchecked). Clearly distinguish unavailable or stale records. Preserve selection drafts across pages and failed Saves.
- Retain existing Admin single-discount overrides and audit semantics. Display provider lifecycle independently of Woo selected status, without changing Shopify semantics.
- Preserve existing WordPress two-stage navigation and administrator-localised 20-language UI.

## Non-goals and invariants

- No **coupon/selection-schema** migrations, new selection tables or columns, shared npm contracts/publication, commerce/tool changes, recovery workers, Meta messaging, provider coupon detail verification, coupon redemption or checkout mutation. **Exception:** one additive Prisma/PostgreSQL global lease enum migration in `DATABASE-003`.
- No Shopify selection-flag migration, Shopify synchronisation refactor, Shopify merchant UI update, or reinterpretation of Shopify `isAvailable`. Regression coverage must prove Shopify is unaffected.
- No new Admin/merchant permission model. The Woo plugin and browser must not access Moda PostgreSQL or read-grant secrets directly.
- A configured coupon is **not** a verified promise or guarantee of customer eligibility. WooCommerce remains authoritative on redemption; no task in this session implements when/how a configured coupon is offered.

## Existing data model and ownership

| Existing storage | WooCommerce meaning | Writer |
|---|---|---|
| `ShopifyDiscountCatalogue.shopId`, `status`, generation | Shop-scoped provider catalogue and freshness | Background-001 |
| `ShopifyDiscount.shopifyDiscountNodeId` | Stable `woo:coupon:<id>` external identity | Background-001 |
| `providerType`, `method`, `title`, `singleRedeemCode` | Real bounded Woo type, code, title and method | Background-001 |
| `providerStatus`, `startsAt`, `endsAt`, `fixedSelectable`, `providerSnapshot` | Provider-derived lifecycle, supported-rule projection and bounded facts | Background-001 |
| `ShopifyDiscount.isAvailable` | **Woo only:** persisted merchant checkbox (`false` on new rows) | API-002 |
| `ShopSettings.recoveryOfferMode` | Saved NONE/FIXED/AI configuration | API-002 |
| `ShopSettings.fixedShopifyDiscountId` | Existing real same-Shop FK anchor required for FIXED by current SQL constraint | API-002 |
| `ShopRecoveryPolicyOverride.fixedShopifyDiscountId` | Existing independent single-discount Admin override | Existing Admin workflow |

For **Shopify** rows, `isAvailable` continues to mean provider availability and the existing single-FK setting is the merchant selection. The shared table does not mean shared field semantics. No **discount-catalogue** schema/constraint/index/history changes are authorised; `DATABASE-003` only extends the global lease enum.

The existing FIXED database constraint requires a non-null actual discount FK despite Woo's multiple selected checkboxes. On Woo FIXED Save, choose a deterministic real member of the selected same-Shop set as the compatibility anchor (for example the smallest internal ID); the complete set remains in the Woo rows' `isAvailable` flags. The anchor does **not** choose the customer-facing coupon, which is outside this session. For NONE/AI, clear the compatibility anchor while preserving the merchant's dormant checked flags as desired. Never fabricate a provider or database ID.

## Data and request flows

1. **DATABASE-003:** add `WOO_COUPON_SYNC_DISPATCH` to Prisma `BackgroundRuntimeLeaseName` and apply one additive enum migration; no lease table, catalogue schema or runtime-config change.
2. **BACKGROUND-001:** use the existing `startDynamicLeasedScheduler()` with a single global `WOO_COUPON_SYNC_DISPATCH` PostgreSQL lease and a matching 60-second `background-runtime-lease.ts` SQL cadence branch. Each successful dispatch cycle discovers Woo installations, ensures missing catalogue rows **even without read permission**, and enqueues a bounded batch of **one-off shop jobs**; it does **not** wait for each shop's Woo API calls. Workers verify current read permission at execution, fetch all bounded pages of `GET /wp-json/wc/v3/coupons`, normalise supported data and commit a fenced complete generation. Preserve Woo merchant selections on refresh/outage. Fail incomplete/revoked/malformed scans closed as non-current without treating them as empty successes. Keep Shopify sync untouched.
3. **API-002:** expose authenticated Woo Shop-scoped catalogue and offer-setting GET/PUT endpoints through the existing privileged WordPress REST facade. Read checked and unchecked eligible coupon rows. Save a full selected set and settings in one transaction with Shop lock and a revision covering both settings and catalogue generation/status; recheck validity within that transaction. Return 409 for concurrent changes, without partial mutation.
4. **WOOCOMMERCE-003:** present three mutually exclusive configuration modes plus accessible multi-checkbox coupon selection with manual Save/Cancel, paging/search and failure/conflict handling. Keep the existing two-stage WordPress navigation and 20-language localisation.
5. **ADMIN-001:** show provider and catalogue status separately from Woo's checked state, preserve independent one-FK Admin override and Shopify's existing single-choice semantics; no new provider fetch or checkbox-write mechanism.

## Credential and synchronisation requirements

`BACKGROUND-001` depends on architect acceptance and developer completion of **both** `DATABASE-003` (global lease enum) and `ARCH-026-API-007` (Woo read grant), and reuses the actual API-owned AES-GCM encrypted grant format and AAD (including Shop/installation/authorisation/credential version). It must verify active scope, revocation, origin and key rotation; decrypt only in authorised Background code with securely configured keyring. Bound pagination, retries, response size and time; enforce HTTPS, safe DNS/peer checks and no redirects. Report an unmet transport/keyring dependency instead of bypassing protections or inventing new credentials. A private LocalWP address is not an acceptable hosted production target.

A failed/partial scan must not remove unseen coupons or erase saved selections. A verified terminal provider state may make a row ineligible for new selections without deleting historical rows; the provider state remains separate from checkbox state. Expiry is checked on reads and Saves, not inferred from selected flags. No new infrastructure task is required unless actual deployment evidence identifies a missing capability.

## Concurrency, isolation and testing

Only an authenticated merchant of the same Woo Shop can change selected flags. Protect full-set Save against overlapping requests and a concurrent catalogue refresh, including a failed/terminal catalogue transition. New unselected coupons must not turn selected merely by resync. Existing Shopify `isAvailable` writers and readers remain unchanged, and no Woo selection operation can write a Shopify row. Use the shared structured logger when emitting new runtime logs; do not log secrets, sensitive customer lists or raw grants.

Terminal `SYSTEM-TEST-001` validates authorised full sync, complete/incomplete scans, two Woo Shops plus Shopify, paginated checked/unchecked display, transactional Save/409 conflicts, real FK constraints, 20-language UI and Shopify no-change regression. It must not validate CommerceAgent decisions, eligibility or outbound recovery behaviour.

## Rollout and task execution

Pre-production Woo coupon feature, but preserve existing Shopify state/history. Apply the **single additive `DATABASE-003` enum migration first**, before deploying or starting Background's new leased dispatcher. No coupon-schema migration, contract publication, Shopify rollout or send-time verification deployment. `DATABASE-003` has no dependencies and is Ready as a portable definition; `BACKGROUND-001` stays Pending until **both** `ARCH-026-API-007` and `ARCH-036-DATABASE-003` are Complete. Then `API-002` follows Background; `ADMIN-001` may run in parallel with `API-002` once Background is Complete; `WOOCOMMERCE-003` follows API-002. `SYSTEM-TEST-001` is terminal after all four implementations are accepted and developer manual validation is possible.

| Task | Owner | Planned status after Attempt 9 | In-session dependencies |
|---|---|---|---|
| `ARCH-036-DATABASE-003` | moda_database | Ready (portable definition) | None |
| `ARCH-036-BACKGROUND-001` | moda_background | Pending | `ARCH-026-API-007`, `ARCH-036-DATABASE-003` |
| `ARCH-036-API-002` | moda_api | Pending | `ARCH-036-BACKGROUND-001` |
| `ARCH-036-WOOCOMMERCE-003` | moda_woocommerce | Pending | `ARCH-036-API-002` |
| `ARCH-036-ADMIN-001` | moda_admin | Pending | `ARCH-036-BACKGROUND-001` |
| `ARCH-036-SYSTEM-TEST-001` | moda_system_test | Pending (terminal validation only) | All four above |
| `ARCH-036-BACKGROUND-003` | moda_background | Superseded | Outbound proof out of scope |
| `ARCH-036-BACKGROUND-004` | moda_background | Superseded | Shopify sync unchanged |
| `ARCH-036-SHOPIFY-001` | moda_app | Superseded | Shopify UI unchanged |
| `ARCH-036-COMMERCE-001` | moda_commerce | Pending (unchanged; **deferred**) | Out of session; NOT executable under this plan |
| `ARCH-036-SYSTEM-TEST-002` | moda_system_test | Pending (unchanged; **deferred**) | Out of session; NOT part of terminal acceptance here |

Already-superseded `DATABASE-001/002` remain unexecutable; the new `DATABASE-003` is a **separate enum-only global-scheduler prerequisite**. Other superseded tasks — `SHARED-001/002/003`, `API-001/003`, `WOOCOMMERCE-001/002` and `BACKGROUND-002` — remain unchanged and unexecutable. Deferred Commerce/outreach definitions are intentionally **not modified** as part of the developer's explicit exclusion. They must be reconciled in a separately authorised scope rather than silently executed or certified. Individual task YAML remains authoritative for status; this session's scope restriction is independent of pending metadata.

## Change history and unresolved boundaries

- 2026-10-12 Attempts 1–5: progressively removed schema, Shared contracts, plugin coupon uploads and API provider proxies; Attempt 5 retained send-time proof and Shopify-wide flag changes.
- 2026-10-13 Attempt 6: proposed correctness refinements for the broader design, before the developer narrowed scope.
- **2026-10-13 Attempt 7:** four-task Woo catalogue/configuration-only scope; Shopify preserves its existing semantics. Background send-time proof and Shopify-specific work superseded; CommerceAgent and outreach system-test definitions frozen outside this session.
- **2026-10-13 Attempt 8:** detailed BACKGROUND-001 plan initially proposed a global BullMQ recurring dispatcher; no code implemented.
- **2026-10-13 Attempt 9:** replace the global BullMQ schedule with the existing PostgreSQL global lease (`WOO_COUPON_SYNC_DISPATCH`), add one enum-only `DATABASE-003` prerequisite, retain one-off BullMQ **shop** jobs and the 30-minute per-shop refresh target. Five in-session implementation tasks plus terminal `SYSTEM-TEST-001`, without altering CommerceAgent, outbound recovery or Shopify behaviour.

ARCH-036 remains Proposed. No implementation is accepted, and the document does not claim that coupon offers can be safely applied or sent.
