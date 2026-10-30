---
id: ARCH-053
title: WooCommerce generation-bound checkout recovery links and cart restoration
status: in_progress
coordinator: moda_architect
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053 — WooCommerce checkout recovery URL and basket restoration

## Status

**In Progress.** ARCH-053-DATABASE-001, SHARED-001, SHARED-002, BACKGROUND-001, BACKGROUND-002 and API-001 are Complete. API-002 and WOOCOMMERCE-001 are Ready; BACKGROUND-003 is Ready for a narrowly scoped Attempt 2 validation correction after an architect decision resolving its installation-revocation blocker. Remaining implementation tasks stay gated by their explicit dependencies. No consumer deployment or production activation is implied. **ARCH-052 is separately owned dynamic discount discovery and personalised offers** and is not renamed, appropriated or edited here.

## Problem and inspected baseline

The attached 2026-10-30 07:59 workspace snapshot contains:

- `moda-interact-woocommerce/includes/Checkout/CheckoutSnapshot.php`: `items`, `currency`, `total`, optional contact; no applied coupons, variation-attribute restoration data or restoration-readiness signal. CheckoutCapture uses a cart fingerprint and suppresses identical revisits.
- `moda-interact-api/src/woocommerce/activity/contract.ts`: strict `woo.activity.v1` / v2 phone-normalized ingest, no restoration fields. `src/woocommerce/activity/producer.ts` writes strict `woo-checkout-capture-v1` jobs.
- `moda-interact-background/src/events/woo-checkout-capture.ts`: strict v1 queue validator; pending candidates retain the original validated `checkout` snapshot only.
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission.service.ts`: inserts `CheckoutRecovery.checkoutUrl: null`, lineItems display JSON, first generation only in the snapshot.
- `moda-interact-database/prisma/schema.prisma`: existing `CheckoutRecovery.checkoutUrl String?`, `lineItems Json?`, `generation Int` and `@@unique([shopId, checkoutToken, generation])`, but no distinct restoration representation.
- Background template preparation / conversation wrappers already consume `recovery.checkoutUrl` if it is trusted HTTPS on the merchant's host, but they need link-specific regression coverage.
- `WooCommerceInstallation.canonicalSiteUrl` is derived from WordPress `home_url('/')`, not from Woo's checkout slug, and may contain a subdirectory. `wc_get_checkout_url()` is the **redirect destination after restoration**, never a complete recovery URL.

Baseline ARCH-048 Background implementation remains one-generation-only. The **task files** ARCH-048-BACKGROUND-007..011 are present in the 2026-10-30 snapshot: BG007 is Ready and BG008..011 are Pending; none is accepted Complete. Their implementation and architect acceptance must precede ARCH-053 generation-bound issuance/certification. ARCH-046-WOOCOMMERCE-003 returning consent remains a separate prerequisite for final integrated certification; links cannot grant consent.

## Goals

1. Send one unique, authenticated, generation-bound URL for an **eligible restorable** Woo recovery, with no product/coupon/customer identity embedded in URL arguments.
2. Cross-device restoration of the original core Woo simple/variation products and quantities, plus up to ten original applied coupons, with Woo revalidating products, stock, coupon expiry, usage/stacking/eligibility and current prices/taxes/shipping.
3. Avoid silently replacing any existing visitor cart; a genuine customer must explicitly confirm replacement. GET visits, link previews and scanners are entirely nonmutating and do not close recovery.
4. Preserve the same original `(shopId, checkoutToken)` across a confirmed cross-device restoration so ARCH-048 may close the old generation and restart delayed-candidate scheduling; manual unchanged-basket resume also emits activity.
5. Reject stale/older-generation, terminated, wrong-shop, invalid-token, mismatched-host and unknown/unsupported basket links; never silently perform partial restoration.
6. Preserve historical recovery snapshots, billing/outreach and consent/STOP rules. A valid new generation independently qualifies for initial outreach under ARCH-048.

## Non-goals

- ARCH-052 dynamic discount discovery, merchant-selected recovery incentives, AI/MCP offer generation or creation/automatic replacement of coupons. ARCH-053 may read **what was confirmed sent**; it does not choose which offer to send.
- Overriding expired coupon policy, fixing prices to old captured totals or guaranteeing an unavailable product/extension can be restored.
- Shopify checkout URL changes, Woo coupon-proof MCP tooling, new agent messages, a provider send enablement switch or changes to WhatsApp consent.
- Inventing migration/backfill for historical test-only events; active queue/recovery data is preserved or explicitly drained as part of controlled pre-production rollout.

## Architecture decisions

**R1 — Canonical restoration snapshot.** `@modainteract/moda-interact-shared/woocommerce` publishes `WooCartRestoreSnapshotV1Schema`, `WooCartRestoreSnapshotV1`, checkout v1 restoration extension schema and strictly bounded resolver request/response contracts; plugin PHP implements the same JSON wire with golden vectors. A snapshot has `schemaVersion: 'woo.cart-restore.v1'`, `kind: 'supported' | 'unsupported'`, `appliedCouponCodes: string[]` (max ten, each 1–128 safe characters), and either `lines` (1–50) or bounded `reason`. Each supported line has positive decimal **integer** `productId`, optional integer `variationId`, quantity 1–100000 and optional bounded `attributes: Record<string,string>` populated from Woo's canonical `variation` map. Unsupported has no `lines` and no restorable CTA. No billing name, address, phone, email, calculated tax, currency conversion or cart-session token is carried in the restore payload. Coupons are *original applied* codes, not ARCH-052 proposed promotions.

**R2 — Single canonical pre-production checkout activity contract (v1).** The inspected API currently accepts `woo.activity.v1` checkout/order events and an HTTP-only `woo.activity.v2` checkout variant for normalized phone proof; both project to the v1 BullMQ job. This initiative **consolidates the checkout HTTP input to `woo.activity.v1`** and extends its existing `CHECKOUT_UPDATED.checkout` shape with optional `restoration: WooCartRestoreSnapshotV1`, as well as the already-existing phone proof fields `contact.canonicalPhone` and optional `contact.verifiedCountryCode` when a phone is supplied. `woo.activity.v2` and proposed `woo.activity.v3` are **not** retained as alternate HTTP contracts in the target. The API validates HTTP v1 using the existing `normalizeRecipientPhone` logic: `phone` requires a matching `canonicalPhone` (digits only) and valid optional verified country; no phone means neither proof field is allowed. If the plugin cannot verify a phone it must **omit that phone** while still publishing the safely captured basket; no false contact eligibility or marketing consent is inferred. The API strips the two HTTP-only phone proof fields, replaces `contact.phone` with the verified E.164 value and enqueues the **same canonical `woo.activity.v1`** `woo-checkout-capture-v1` job with its optional validated restoration snapshot. ORDER_* v1 events/queue remain untouched. No new event version, separate activity endpoint, queue, dual-parser compatibility shim, migration/backfill or additional merchant credentials are authorised. Absence of restoration means unknown/unrestorable, never coupon-free. Preserve `eventId`, `occurredAt`, existing job ID/contentDigest/replay policy, tenant authentication, strict unknown-field rejection and the 65,536-byte limit. Consumers must be accepted before the coordinated pre-production plugin/API rollout.

**R3 — Durable snapshot storage.** A new nullable `CheckoutRecovery.wooRestoreSnapshot Json?` is written with the recovery's display `lineItems` in the SAME admission transaction from the mature, watermark-verified candidate. `lineItems` remains the display schema and must not be repurposed for coupons. Historical snapshots/generation values are immutable after creation; only the owning architect-approved ARCH-048 transitions may close them. Unsupported/unknown snapshots do not produce a restore link. No temporary WordPress transient becomes the authoritative snapshot.

**R4 — Stable idempotent generation URL.** Background creates a cryptographically random 32-byte base64url bearer token once at successful recovery admission, and stores a **full merchant HTTPS URL** in the existing `checkoutUrl` column within the admission transaction. Format: `<canonicalSiteUrl>/?moda_interact_resume=1&r=<recoveryId>&t=<43-char-base64url-token>`, with safe URL joining supporting a merchant home subpath. Source host/path MUST come only from verified `WooCommerceInstallation.canonicalSiteUrl`; require the resolved hostname to agree with `Shop.domain` and fail closed when not compatible. Never place PII, coupons, items or a live Woo session identifier in the URL. On retries/unique conflicts, reuse stored URL; never rotate/mint a different one for the same recovery. `checkoutUrl` is a bearer capability (already permitted in the existing schema): restrict DB access, never log it, and set `Cache-Control: no-store`, `Referrer-Policy: no-referrer` on landing. The URL expires for resolution on terminal/superseded recovery or beyond existing **seven-day checkout-freshness window from last external activity** (and if installation/shop becomes inactive); no 30-minute transient/hard expiry. **An inactive/revoked installation is an admission denial, not an otherwise-admitted recovery with a null URL:** deny before admission and recheck installation/consent under the insertion transaction. Only otherwise eligible active installations with missing/unsupported restore evidence or invalid/mismatched site configuration may persist `checkoutUrl:null` with a bounded omission reason. When installation is revoked after a successful earlier admission, preserve historical records and fail closed on subsequent link resolution/outreach. Link is never proof of consent or payment.

**R5 — Authenticated resolution.** New installation-authenticated API `POST /v1/woocommerce/recovery-restore/resolve` body `{schemaVersion:'woo.restore.resolve.v1', recoveryId, token}` (no query auth). API derives `shopId` from `WooInstallationAuthenticator`, selects `CheckoutRecovery` by `id` plus `shopId`, validates random token against the **stored URL** using bounded parsing and constant-time hash comparison, requires the latest generation for that `(shopId, checkoutToken)` and status `DETECTED|MESSAGE_SENT|ENGAGED`, no terminal/completed flags, valid current shop/installation and valid freshness, and `wooRestoreSnapshot.kind === 'supported'`. On success return the **sole, complete v1 response** `{schemaVersion:'woo.restore.resolve.v1', status:'eligible', recoveryId, checkoutKey, snapshot, outreachOffer}`; NEVER send contact/recipient/outreach/credit information. For denial return uniform `404 {error:'restore_unavailable'}`; malformed request `400`; unavailable dependency `503`, no sensitive info in logs. A read does **not** change recovery status or mark activity. If live order evidence exists, it must suppress checkout restoration; missing/unreceived external order activity cannot be called definitive proof of safety.

**R6 — Customer-confirmed Woo restoration.** Customer GETs the link on the merchant origin; WordPress renders a minimal no-store, no-referrer, no-third-party-resource confirmation landing. GET and any preview are **business-state read-only**: they may establish only the minimal WC session/CSRF nonce cookie needed for a subsequent secure POST, but never modify the cart, checkout key, recovery state, consent or activity queue. The confirmation POST carries valid recovery ID/token, a nonce tied to the current Woo session, and an explicit consent action to **replace** that browser's current basket. PHP resolves with the authenticated Moda API server-to-server; verifies installed shop and strict Shared JSON contract representation; validates products/variations/attributes and current purchasability before mutation; rejects unsupported extension metadata/noncore product types *without partial restoration*. On confirmed success it uses supported `WC()->cart` methods to rebuild the whole basket; suppress intermediate checkout-capture hooks, reapply each original coupon via `apply_coupon()`, calculate current totals, and surface individual rejected-coupon notices. For expired or invalid coupons, preserve products and show checkout with recalculated total—never reissue/force discounts. Persist WC session cookie, set original `CheckoutKey::SESSION_FIELD=checkoutKey`, clear last snapshot fingerprint, queue exactly one fresh checkout activity, then `wp_safe_redirect(wc_get_checkout_url())` for Classic/Blocks. Do not copy former shopper contact, marketing consent or billing data to the clicking browser. Preflight and failure rollback protect existing cart, with explicit diagnostic when rollback cannot be guaranteed.

**R6a — Dedicated original-coupon work.** Restorable original coupons are captured and carried as one immutable per-generation `appliedCouponCodes` list. WOOCOMMERCE-001 captures the list in a complete snapshot; WOOCOMMERCE-004 specifically emits checkout activity when codes are applied/removed even if items/totals are unchanged. API-001, BACKGROUND-001/002 and DATABASE-001 must preserve the exact list end to end without defaulting an unknown missing list to `[]` or creating a second coupon table. WOOCOMMERCE-002 initially accepts only proven coupon-free snapshots; WOOCOMMERCE-005 restores original coupons with native `WC_Cart::apply_coupon()` and fresh totals; WOOCOMMERCE-006 ensures rejected/expired coupon notices are visible after redirect in both Classic and Blocks. SYSTEM-TEST-002 independently certifies original-coupon capture, invalidity, expiry, restrictions and notices. No ARCH-052 dynamic discount is issued or extended. These are **separate review gates**, not unassigned subclauses of a generic basket task.

**R7 — Manual return.** Independent frontend user-interaction capture on existing cart/checkout with a valid original Woo checkout session key emits a fresh `CHECKOUT_UPDATED` **even when the snapshot fingerprint is unchanged**. The signal requires a real browser interaction/confirmed checkout engagement and is once-per-view bounded; a homepage hit, automated price calculation, link preview or passive GET is not sufficient. This reuses the canonical activity ingress; do not add `CHECKOUT_RESUMED` event or create a recovery inside WordPress. ARCH-048 Background decides whether a newer event closes the old generation and starts a new BullMQ delayed candidate.

**R8 — Native vs custom Woo.** Woo's `/checkout-link/` can reconstruct native products and one coupon, but exposes basket parameters and cannot express Moda generation identity/revocation safely. Therefore ARCH-053 uses a small confirmation/restoration endpoint backed by native Woo **cart APIs**; `wc_get_checkout_url()` remains only its final redirect. Avoid independently copying WooCommerce pricing/coupon validation into Moda.


**R9 — Confirmed outreach offer restoration (new; independent of ARCH-052 discovery).** The historical `WooCartRestoreSnapshotV1.appliedCouponCodes` contains **only original customer-applied codes**, and must remain immutable. The existing provider-confirmed initial `RecoveryOutreachAttempt(sequence=1, sentAt, outboundMessageId)` joined to its `ConversationMessage.content` (`moda.whatsapp.automated-template-parameters.v1`) is the single durable source of **what was offered**. A narrow ARCH-053-BACKGROUND-004 task requires an explicit `promotionTarget: CHECKOUT | ALTERNATIVE_PRODUCT` in the existing `recoveryPromise` for new sends, and becomes evidence-only (reviewed Complete without code churn) if ARCH-052-BACKGROUND-008 already proves it. Do not copy the promise into `offerSnapshot.sentOffer`, invent a new offer table, or read currently selected discounts as proof of a historical message. Missing/unconfirmed/corrupt/untagged evidence cannot auto-apply a coupon.

**R10 — Single first-release, offer-aware resolver v1.** The restoration resolver has **never been implemented**; therefore the first and only wire protocol is `woo.restore.resolve.v1`, with one mandatory `outreachOffer` discriminated union on **every eligible response** (including `NONE`). SHARED-001 defines/export/tests the complete v1 contract; SHARED-002 publishes it once, after acceptance. API-002 authenticates and authorizes the link and initially returns `NONE/NO_CONFIRMED_OFFER`; API-003 enriches the **same v1 response** using the confirmed initial outbound message and returns `CHECKOUT_CODE`, `CHECKOUT_AUTOMATIC`, `ALTERNATIVE_PRODUCT` or `NONE/UNVERIFIABLE` as appropriate. No v2 resolver, adapters, dual request parsing, extra Shared implementation task or legacy-v1 compatibility gate. A denied recovery returns only uniform 404, never a coupon; a database outage returns 503. Original codes remain in `snapshot.appliedCouponCodes`. The recommended code must never be accepted from the link, caller-provided JSON or merchant settings. The original offer promised in confirmed sequence-one WhatsApp outreach remains the only selected discount for this link; new selections in follow-up require a separate future architecture.

**R11 — Woo remains the final coupon authority.** After a human confirms restore POST, the plugin restores products, attempts the **original** codes first, then attempts a confirmed `CHECKOUT_CODE` with `WC()->cart->apply_coupon()` and current Woo validity/stacking rules. Expired/invalid recommendations do not block the product checkout or force original prices. If applying the recommendation would remove a valid original code, automatically **restore the original applied set**, show a no-discount-guarantee notice and offer an explicit nonce-protected shopper choice to try the offered code instead. The choice uses a bounded, single-use Woo-session record tied to the restored cart hash and expires after ten minutes or state change; no bearer link or raw code in browser POST. Both Classic Checkout and Checkout Blocks must display the correct recalculated total/notices. `CHECKOUT_AUTOMATIC` never triggers artificial coupon/price rules, and `ALTERNATIVE_PRODUCT` never applies its code or changes the original basket. GET/HEAD previews still do not mutate cart, mark activity or create choice state.

**Cross-architecture dependency:** ARCH-052 owns offer discovery/send choice and the existing confirmed message receipt; ARCH-053 owns **resolving and attempting redemption** of that sent offer. ARCH-048 owns active recovery closure and subsequent-generation admission. New ARCH-053 sent-receipt / API v1 enrichment / Woo tasks must be accepted before integrated CERTIFICATION; never make an ARCH-052 implementation task depend on an ARCH-053 system test or edit ARCH-052 task files to implement restore. `ARCH-053-SHARED-002` is a **single publication gate**, dependent on SHARED-001 only; do not run code validation again during publication.

## Request and event flow

```mermaid
sequenceDiagram
    autonumber
    participant W as Woo plugin
    participant A as Hosted API
    participant Q as Redis / BullMQ
    participant B as Background
    participant D as PostgreSQL
    participant X as WhatsApp
    participant C as Customer
    W->>A: Authenticated woo.activity.v1 checkout snapshot incl. coupons/restore
    A->>Q: Validated v1 capture job with optional restoration
    Q->>B: Capture / delayed candidate maturity
    B->>D: Admit recovery generation N + immutable wooRestoreSnapshot + checkoutUrl
    B->>X: Eligible message with generation-specific opaque link
    X-->>C: WhatsApp button
    C->>W: GET merchant recovery link
    Note over C,W: GET shows confirmation only; preview makes no state changes
    C->>W: POST explicit Replace and Continue
    W->>A: Authenticated restore resolve (recoveryId, token)
    A->>D: Check shop, generation, status, age, snapshot and exact token
    D-->>A: Current eligible restore snapshot
    A-->>W: v1: original basket/coupons + verified sent outreach offer
    W->>W: Confirm, preflight, rebuild cart, validate original + offered coupon, recalculate
    W->>A: Fresh CHECKOUT_UPDATED (via Action Scheduler)
    W-->>C: Redirect wc_get_checkout_url()
    A->>Q: Checkout capture job
    Q->>B: New activity, ARCH-048 closes prior recovery and schedules next candidate
```

## Ownership and public infrastructure

- `moda_shared`: canonical snapshot/schema and single REST v1 offer-aware contract, separately published reusable version.
- `moda_database`: additive nullable Prisma JSON + migration, no schema updates by other agents.
- `moda_woocommerce`: capture coupons/variation support, confirmation endpoint, native original + confirmed outreach coupon attempts, customer-facing conflict choice/notices and manual engagement detection.
- `moda_api`: authenticated checkout v1 normalization and single restoration v1 resolution; read the confirmed initial outbound message, no Redis or Woo session writes on resolve.
- `moda_background`: carry snapshot to candidates/recovery, generate idempotent URL, preserve explicit offer target in existing confirmed message receipt if not already implemented; never call a merchant-controlled site to mint a link.
- `moda_system_test`: final integration across actual Woo, Meta sender mocks, BullMQ, Postgres, API, coupon rules and order/consent lifecycle.
- `moda_gateway`: no new task **based on inspected topology**; existing `/v1/woocommerce/*` passes through the current public API service. Before integration, verify endpoint routing in deployed environment; if not supported, return to architect for bounded Gateway task, not an ad hoc implementation.

## Idempotency, ordering and failure handling

The Woo eventId/digest and queue deduplication remain unchanged. An updated full basket fingerprint includes coupon/restoration changes; candidates use event ordering/watermark and validated entire snapshot, not incremental coupons. Admission transaction writes historical `wooRestoreSnapshot`, `checkoutUrl` and status together. Under ARCH-048, generation links are never reattached to later generations. Old events, retries, two devices, concurrent confirmation attempts and orders must not let a stale link overwrite the newly active session. API checks eligibility at time of confirmation; asynchronous activity-to-closure is **eventually consistent**, not an invented atomic cross-site transaction. Woo queues a durable post-restoration activity with existing Action Scheduler; delivery failure is logged/retriable and is an explicit residual risk. A customer browsing the website without a session key cannot be assumed to have resumed the original recovery.

## Security and privacy

Bearer token is 256-bit unpredictable, compared with bounded constant-time digest; no PII or coupons in URL. Redact URL/token from diagnostics, telemetry, request logs and referrer. Bind API resolution to installation principal + authoritative shop. Prevent cross-merchant leaks, open redirects, host/path mismatches, SSRF, query injection, replay of stale generations and WordPress CSRF. Do not grant consent on link access. GET/HEAD and robots have no mutating effects; require explicit POST confirmation, session-tied nonce and current Woo cart/server-side checks. If link is stale, show safe merchant checkout/home navigation without restoring historical products. Do not trust a caller-supplied product set, checkout key or shop ID.

## Observability

Node uses `@modainteract/moda-interact-shared/logging` for generic structured events, domain event codes and bounded ids; PHP reuses existing safe plugin logging without adding a generic logger. Track received v1 restoration snapshots, unsupported baskets, link issued/omitted, failed tenant/eligibility/token checks (no token values), coupon reapplied/rejected counts, restore success/failure, resumption-event acceptance and queue delays. Do not recreate standard HTTP metrics. Never expose raw URL/token or customer contact in logs. Telemetry failure must not affect business correctness.

## Rollout and compatibility

**Pre-production breaking refinement**, based on the developer's confirmation that this WooCommerce checkout restoration path is not released into production. The existing v2 HTTP-only phone path is folded into v1, **not** preserved with a compatibility adapter. Implement in isolated repository task branches; do not deploy API-001's removal of HTTP v2 to any still-running v2-producing test WordPress installation. Coordinated integration order: SHARED-001 implementation → architect acceptance → SHARED-002 publication → Background-001 v1 queue consumer → API-001 v1 HTTP validator/projection → WooCommerce-001 v1 producer → database/admission/link resolution + remaining bounded tasks → ARCH-048 integration → terminal system tests. Database work may run independently. Before activating the new pre-production pair, confirm no production messages/installed sites depend on v2; intentionally drain/recreate **development/test-only** retained queue jobs or coordinate a clean test reset. Do not silently delete durable merchant/production state. Reject v2/v3 on the new canonical checkout route after cutover, with tests. The separate `woo.restore.resolve.v1` resolver remains the first and only restore resolver. Do not deploy partially composed tasks or enable production Woo WhatsApp sends. Rollback of the added JSONB field requires an explicit data-retention decision.

## Multi-discount v1 restoration amendment — 30 October 2026

ARCH-052 now permits one immutable initial WhatsApp checkout offer group of 1..3 source-grounded compatible discounts. This does **not** move checkout URL issuance, coupon redemption, cart restoration or browser behavior into ARCH-052. The existing `WooCartRestoreSnapshotV1.appliedCouponCodes` remains the separate, complete original shopper-applied coupon list. Only the verified **confirmed initial** `ConversationMessage.content.recoveryPromise` can provide the recommended group; never derive it from mutable merchant preferences or URL/query parameters.

New ARCH-053-SHARED-003 adds `CHECKOUT_OFFERS` (2..3 ordered CODE/AUTOMATIC entries) to the **same `woo.restore.resolve.v1`** union. Existing singleton `CHECKOUT_CODE` and `CHECKOUT_AUTOMATIC` responses remain correct. No v2 resolver or compatibility adapter; pre-production breaking rollout remains permitted. The new group schema is published once together with the ARCH-052 Shared combination contract through ARCH-052-SHARED-012. ARCH-053-API-003 reads and verifies the complete confirmed set; malformed evidence returns NONE/UNVERIFIABLE with no auto-coupon application. WooCommerce-007 applies original coupons first, attempts the whole sent code group natively after confirmed POST, and rolls back partial/conflicting recommended application to preserve the original successful set. WooCommerce-008 presents native valid totals and permits explicit nonce/session/cart-bound 'Try the offered set instead' choice; unknown/expired/cross-tenant claims are never guaranteed.

The only new task in ARCH-053 is SHARED-003. Existing pending ARCH-053-BACKGROUND-004, API-003, WOOCOMMERCE-007/008 and SYSTEM-TEST-003 are amended under the same task IDs. No modifications to accepted ARCH-053 tasks, Shopify discount selection task, MCP Woo reader, ARCH-049 source sync, checkout-link generation tasks, or `_index.md` files. No cross-architecture system-test dependency points backward to an implementation task.

## Decisions / Tasks

The task YAML files are authoritative for status and dependency eligibility. The current frontier has **DATABASE-001, SHARED-001, SHARED-002, BACKGROUND-001, BACKGROUND-002 and API-001 Complete**; **BACKGROUND-003 (focused validation-only rework), API-002 and WOOCOMMERCE-001 are Ready**. Other tasks remain Pending until their stated dependencies are satisfied. The five new recommended-offer tasks are `BACKGROUND-004`, `API-003`, `WOOCOMMERCE-007`, `WOOCOMMERCE-008` and terminal `SYSTEM-TEST-003`. The existing v1 contract does not cover grouped offers; ARCH-053-SHARED-003 extends that first-release v1 union and ARCH-052-SHARED-012 is its joint publication gate.

| Task | Owner | Status | Depends on |
|---|---|---|---|
| `ARCH-053-DATABASE-001` | `moda_database` | Complete | — |
| `ARCH-053-SHARED-001` | `moda_shared` | Complete | — |
| `ARCH-053-SHARED-002` | `moda_shared` | Complete | SHARED-001 |
| `ARCH-053-SHARED-003` | `moda_shared` | Pending | ARCH-052-SHARED-011 |
| `ARCH-053-API-001` | `moda_api` | Complete | SHARED-002 |
| `ARCH-053-BACKGROUND-001` | `moda_background` | Complete | SHARED-002 |
| `ARCH-053-BACKGROUND-002` | `moda_background` | Complete | BACKGROUND-001, DATABASE-001 |
| `ARCH-053-WOOCOMMERCE-001` | `moda_woocommerce` | Ready | API-001, BACKGROUND-001 |
| `ARCH-053-WOOCOMMERCE-004` | `moda_woocommerce` | Pending | WOOCOMMERCE-001 |
| `ARCH-053-API-002` | `moda_api` | Ready | SHARED-002, DATABASE-001 |
| `ARCH-053-BACKGROUND-003` | `moda_background` | Ready (Attempt 2 validation) | BACKGROUND-002, ARCH-048-BACKGROUND-011 |
| `ARCH-053-BACKGROUND-004` | `moda_background` | Pending | ARCH-052-BACKGROUND-008 |
| `ARCH-053-API-003` | `moda_api` | Pending | API-002, SHARED-002, BACKGROUND-004, ARCH-052-SHARED-012 |
| `ARCH-053-WOOCOMMERCE-002` | `moda_woocommerce` | Pending | WOOCOMMERCE-001, API-002 |
| `ARCH-053-WOOCOMMERCE-005` | `moda_woocommerce` | Pending | WOOCOMMERCE-002, WOOCOMMERCE-004 |
| `ARCH-053-WOOCOMMERCE-006` | `moda_woocommerce` | Pending | WOOCOMMERCE-005 |
| `ARCH-053-WOOCOMMERCE-007` | `moda_woocommerce` | Pending | API-003, WOOCOMMERCE-005, WOOCOMMERCE-006, ARCH-052-SHARED-012 |
| `ARCH-053-WOOCOMMERCE-008` | `moda_woocommerce` | Pending | WOOCOMMERCE-007, WOOCOMMERCE-006 |
| `ARCH-053-WOOCOMMERCE-003` | `moda_woocommerce` | Pending | WOOCOMMERCE-001 |
| `ARCH-053-SYSTEM-TEST-001` | `moda_system_test` | Pending | BACKGROUND-003, WOOCOMMERCE-002, WOOCOMMERCE-003, ARCH-048-BACKGROUND-011, ARCH-046-WOOCOMMERCE-003 |
| `ARCH-053-SYSTEM-TEST-002` | `moda_system_test` | Pending | WOOCOMMERCE-004, WOOCOMMERCE-006, BACKGROUND-003, WOOCOMMERCE-003, ARCH-048-BACKGROUND-011, ARCH-046-WOOCOMMERCE-003 |
| `ARCH-053-SYSTEM-TEST-003` | `moda_system_test` | Pending | SYSTEM-TEST-001, SYSTEM-TEST-002, API-003, WOOCOMMERCE-008, BACKGROUND-003, BACKGROUND-004, WOOCOMMERCE-003, ARCH-052-BACKGROUND-008, ARCH-048-BACKGROUND-011, ARCH-046-WOOCOMMERCE-003, ARCH-053-SHARED-003, ARCH-052-SHARED-012 |

Only system-test tasks may depend on another system test. `SYSTEM-TEST-003` runs after accepted core-link and original-coupon system certification; **no implementation task depends on system validation**.

## Open Questions / explicit constraints

- Cross-ARCH-048 worktree materialisation and acceptance must be checked before issuance and integrated certification. The 2026-10-30 snapshot contains BG007..011 task files, but none is accepted Complete.
- Real WooCommerce extension-specific item options are NOT round-trippable with the existing snapshot. If they cannot be proved safe in plugin-owned unit/integration tests, mark basket unsupported, omit link and use template no-link/no-send fallback. Do not promise arbitrary extension restore.
- Background order evidence is observed-only; if an order never reached Moda there is no cross-provider guarantee. Confirmation checks the strongest available documented state but does not invent a live Woo merchant lookup.
- The existing ARCH-052 task inventory may still contain historical dependencies on its superseded Woo restore tasks; **reconciliation remains within ARCH-052 ownership and must not be used to implement restore under ARCH-052**.

## Change History

- 2026-10-30: ARCH-053-BACKGROUND-003 unblocked by architect ruling: inactive/revoked installation is denied before recovery admission and again under the transaction fence, not admitted with `checkoutUrl:null`. Same task returned Ready for focused revocation regression coverage; code baseline retained and no new repository task or migration required. BACKGROUND-002 and ARCH-048-BACKGROUND-011 prerequisites are Complete in the submitted snapshot.
- 2026-10-30: ARCH-053-DATABASE-001 accepted at Attempt 1; nullable generation-specific JSONB persistence and isolated fresh/upgrade checks are published. No dependent task was promoted while SHARED-002 remained Pending.
- 2026-10-30: SHARED-002, BACKGROUND-001 and API-001 accepted Complete at Attempt 1. BACKGROUND-002, API-002 and WOOCOMMERCE-001 are Ready. API-001 and WOOCOMMERCE-001 still require the coordinated pre-production cutover before deployment. No producer deployment is implied.

- 2026-10-30: Pre-production checkout activity correction: retire proposed `woo.activity.v3`, consolidate existing HTTP-only v2 phone proof into `woo.activity.v1`, preserve the v1 queue envelope and single restoration resolver v1; no compatibility adapters.

- 2026-10-29: Initial standalone ARCH-053 checkout URL architecture; ARCH-052 dynamic discount discovery remains separate.
- 2026-10-29: Added dedicated capture and restoration of original customer-applied coupons.
- 2026-10-30: Reconciled against the 07:59 workspace: ARCH-048 follow-up tasks are defined but not yet accepted, and resolver v1 is not implemented. Integrated confirmed ARCH-052 outreach offers into the single v1 contract; eliminated premature resolver v2/SHARED-003, corrected dependencies and included separate sent-receipt, API enrichment, native coupon, customer-choice and system-test tasks. No ARCH-052 implementation or `_index.md` changes.
