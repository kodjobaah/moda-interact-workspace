---
id: ARCH-053
title: WooCommerce generation-bound checkout recovery links and cart restoration
status: proposed
coordinator: moda_architect
created: 2026-10-29
updated: 2026-10-29
---

# ARCH-053 — WooCommerce checkout recovery URL and basket restoration

## Status

**Proposed; task definitions are portable, defined but not materialised.** This is a NEW initiative. **ARCH-052 is separately owned dynamic discount discovery and personalised offers** and is not renamed, appropriated or edited here. In particular, previously superseded ARCH-052-WOOCOMMERCE-002 / ARCH-052-API-004 designs are not reused. Neither this snapshot nor this patch proves the developer created or pushed task worktrees/branches.

## Problem and inspected baseline

The 2026-10-29 uploaded snapshot contains:

- `moda-interact-woocommerce/includes/Checkout/CheckoutSnapshot.php`: `items`, `currency`, `total`, optional contact; no applied coupons, variation-attribute restoration data or restoration-readiness signal. CheckoutCapture uses a cart fingerprint and suppresses identical revisits.
- `moda-interact-api/src/woocommerce/activity/contract.ts`: strict `woo.activity.v1` / v2 phone-normalized ingest, no restoration fields. `src/woocommerce/activity/producer.ts` writes strict `woo-checkout-capture-v1` jobs.
- `moda-interact-background/src/events/woo-checkout-capture.ts`: strict v1 queue validator; pending candidates retain the original validated `checkout` snapshot only.
- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission.service.ts`: inserts `CheckoutRecovery.checkoutUrl: null`, lineItems display JSON, first generation only in the snapshot.
- `moda-interact-database/prisma/schema.prisma`: existing `CheckoutRecovery.checkoutUrl String?`, `lineItems Json?`, `generation Int` and `@@unique([shopId, checkoutToken, generation])`, but no distinct restoration representation.
- Background template preparation / conversation wrappers already consume `recovery.checkoutUrl` if it is trusted HTTPS on the merchant's host, but they need link-specific regression coverage.
- `WooCommerceInstallation.canonicalSiteUrl` is derived from WordPress `home_url('/')`, not from Woo's checkout slug, and may contain a subdirectory. `wc_get_checkout_url()` is the **redirect destination after restoration**, never a complete recovery URL.

Baseline ARCH-048 Background is still one-generation-only. New ARCH-048-BACKGROUND-007..011 were separately defined as a portable proposal, **not present or accepted in this snapshot**. Their exact materialisation/acceptance state must be checked before ARCH-053's generation-bound issuance/system certification. ARCH-046-WOOCOMMERCE-003 returning consent remains a separate prerequisite for final integrated certification; links cannot grant consent.

## Goals

1. Send one unique, authenticated, generation-bound URL for an **eligible restorable** Woo recovery, with no product/coupon/customer identity embedded in URL arguments.
2. Cross-device restoration of the original core Woo simple/variation products and quantities, plus up to ten original applied coupons, with Woo revalidating products, stock, coupon expiry, usage/stacking/eligibility and current prices/taxes/shipping.
3. Avoid silently replacing any existing visitor cart; a genuine customer must explicitly confirm replacement. GET visits, link previews and scanners are entirely nonmutating and do not close recovery.
4. Preserve the same original `(shopId, checkoutToken)` across a confirmed cross-device restoration so ARCH-048 may close the old generation and restart delayed-candidate scheduling; manual unchanged-basket resume also emits activity.
5. Reject stale/older-generation, terminated, wrong-shop, invalid-token, mismatched-host and unknown/unsupported basket links; never silently perform partial restoration.
6. Preserve historical recovery snapshots, billing/outreach and consent/STOP rules. A valid new generation independently qualifies for initial outreach under ARCH-048.

## Non-goals

- ARCH-052 dynamic discount discovery, merchant-selected recovery incentives or automatic coupon replacements.
- Overriding expired coupon policy, fixing prices to old captured totals or guaranteeing an unavailable product/extension can be restored.
- Shopify checkout URL changes, Woo coupon-proof MCP tooling, new agent messages, a provider send enablement switch or changes to WhatsApp consent.
- Inventing migration/backfill for historical test-only events; active queue/recovery data is preserved or explicitly drained as part of controlled pre-production rollout.

## Architecture decisions

**R1 — Canonical restoration snapshot.** `@modainteract/moda-interact-shared/woocommerce` publishes `WooCartRestoreSnapshotV1Schema`, `WooCartRestoreSnapshotV1`, checkout v3 extension schema and strictly bounded resolver request/response contracts; plugin PHP implements the same JSON wire with golden vectors. A snapshot has `schemaVersion: 'woo.cart-restore.v1'`, `kind: 'supported' | 'unsupported'`, `appliedCouponCodes: string[]` (max ten, each 1–128 safe characters), and either `lines` (1–50) or bounded `reason`. Each supported line has positive decimal **integer** `productId`, optional integer `variationId`, quantity 1–100000 and optional bounded `attributes: Record<string,string>` populated from Woo's canonical `variation` map. Unsupported has no `lines` and no restorable CTA. No billing name, address, phone, email, calculated tax, currency conversion or cart-session token is carried in the restore payload. Coupons are *original applied* codes, not ARCH-052 proposed promotions.

**R2 — Explicit compatibility and delivery.** Woo plugin emits authenticated HTTP `woo.activity.v3` checkout envelopes with the existing canonical phone/identity behaviour plus optional `checkout.restoration`. The API validates v3 using Shared and projects into the existing `woo-checkout-capture-v1` BullMQ job shape with an additive **optional** `checkout.restoration` field (retain canonical `woo.activity.v1` job envelope and digest/order identity). API still supports existing v1/v2 producers during controlled preproduction adoption; absent restoration means **unknown/unrestorable**, NOT empty coupons. Background validator is deployed before the v3 producer starts publishing. The Shared snapshot schema has one owner; API and Background import it rather than copy its TypeScript validator. No new queue or merchant credentials. Existing HTTP size limit 65,536 bytes remains enforced.

**R3 — Durable snapshot storage.** A new nullable `CheckoutRecovery.wooRestoreSnapshot Json?` is written with the recovery's display `lineItems` in the SAME admission transaction from the mature, watermark-verified candidate. `lineItems` remains the display schema and must not be repurposed for coupons. Historical snapshots/generation values are immutable after creation; only the owning architect-approved ARCH-048 transitions may close them. Unsupported/unknown snapshots do not produce a restore link. No temporary WordPress transient becomes the authoritative snapshot.

**R4 — Stable idempotent generation URL.** Background creates a cryptographically random 32-byte base64url bearer token once at successful recovery admission, and stores a **full merchant HTTPS URL** in the existing `checkoutUrl` column within the admission transaction. Format: `<canonicalSiteUrl>/?moda_interact_resume=1&r=<recoveryId>&t=<43-char-base64url-token>`, with safe URL joining supporting a merchant home subpath. Source host/path MUST come only from verified `WooCommerceInstallation.canonicalSiteUrl`; require the resolved hostname to agree with `Shop.domain` and fail closed when not compatible. Never place PII, coupons, items or a live Woo session identifier in the URL. On retries/unique conflicts, reuse stored URL; never rotate/mint a different one for the same recovery. `checkoutUrl` is a bearer capability (already permitted in the existing schema): restrict DB access, never log it, and set `Cache-Control: no-store`, `Referrer-Policy: no-referrer` on landing. The URL expires for resolution on terminal/superseded recovery or beyond existing **seven-day checkout-freshness window from last external activity** (and if installation/shop becomes inactive); no 30-minute transient/hard expiry. Link is never proof of consent or payment.

**R5 — Authenticated resolution.** New installation-authenticated API `POST /v1/woocommerce/recovery-restore/resolve` body `{schemaVersion:'woo.restore.resolve.v1', recoveryId, token}` (no query auth). API derives `shopId` from `WooInstallationAuthenticator`, selects `CheckoutRecovery` by `id` plus `shopId`, validates random token against the **stored URL** using bounded parsing and constant-time hash comparison, requires the latest generation for that `(shopId, checkoutToken)` and status `DETECTED|MESSAGE_SENT|ENGAGED`, no terminal/completed flags, valid current shop/installation and valid freshness, and `wooRestoreSnapshot.kind === 'supported'`. On success return `{schemaVersion, status:'eligible', recoveryId, checkoutKey, snapshot}`; NEVER send contact/recipient/outreach/credit information. For denial return uniform `404 {error:'restore_unavailable'}`; malformed request `400`; unavailable dependency `503`, no sensitive info in logs. A read does **not** change recovery status or mark activity. If live order evidence exists, it must suppress checkout restoration; missing/unreceived external order activity cannot be called definitive proof of safety.

**R6 — Customer-confirmed Woo restoration.** Customer GETs the link on the merchant origin; WordPress renders a minimal no-store, no-referrer, no-third-party-resource confirmation landing. GET and any preview are **business-state read-only**: they may establish only the minimal WC session/CSRF nonce cookie needed for a subsequent secure POST, but never modify the cart, checkout key, recovery state, consent or activity queue. The confirmation POST carries valid recovery ID/token, a nonce tied to the current Woo session, and an explicit consent action to **replace** that browser's current basket. PHP resolves with the authenticated Moda API server-to-server; verifies installed shop and strict Shared JSON contract representation; validates products/variations/attributes and current purchasability before mutation; rejects unsupported extension metadata/noncore product types *without partial restoration*. On confirmed success it uses supported `WC()->cart` methods to rebuild the whole basket; suppress intermediate checkout-capture hooks, reapply each original coupon via `apply_coupon()`, calculate current totals, and surface individual rejected-coupon notices. For expired or invalid coupons, preserve products and show checkout with recalculated total—never reissue/force discounts. Persist WC session cookie, set original `CheckoutKey::SESSION_FIELD=checkoutKey`, clear last snapshot fingerprint, queue exactly one fresh checkout activity, then `wp_safe_redirect(wc_get_checkout_url())` for Classic/Blocks. Do not copy former shopper contact, marketing consent or billing data to the clicking browser. Preflight and failure rollback protect existing cart, with explicit diagnostic when rollback cannot be guaranteed.

**R6a — Dedicated original-coupon work.** Restorable original coupons are captured and carried as one immutable per-generation `appliedCouponCodes` list. WOOCOMMERCE-001 captures the list in a complete snapshot; WOOCOMMERCE-004 specifically emits checkout activity when codes are applied/removed even if items/totals are unchanged. API-001, BACKGROUND-001/002 and DATABASE-001 must preserve the exact list end to end without defaulting an unknown missing list to `[]` or creating a second coupon table. WOOCOMMERCE-002 initially accepts only proven coupon-free snapshots; WOOCOMMERCE-005 restores original coupons with native `WC_Cart::apply_coupon()` and fresh totals; WOOCOMMERCE-006 ensures rejected/expired coupon notices are visible after redirect in both Classic and Blocks. SYSTEM-TEST-002 independently certifies original-coupon capture, invalidity, expiry, restrictions and notices. No ARCH-052 dynamic discount is issued or extended. These are **separate review gates**, not unassigned subclauses of a generic basket task.

**R7 — Manual return.** Independent frontend user-interaction capture on existing cart/checkout with a valid original Woo checkout session key emits a fresh `CHECKOUT_UPDATED` **even when the snapshot fingerprint is unchanged**. The signal requires a real browser interaction/confirmed checkout engagement and is once-per-view bounded; a homepage hit, automated price calculation, link preview or passive GET is not sufficient. This reuses the canonical activity ingress; do not add `CHECKOUT_RESUMED` event or create a recovery inside WordPress. ARCH-048 Background decides whether a newer event closes the old generation and starts a new BullMQ delayed candidate.

**R8 — Native vs custom Woo.** Woo's `/checkout-link/` can reconstruct native products and one coupon, but exposes basket parameters and cannot express Moda generation identity/revocation safely. Therefore ARCH-053 uses a small confirmation/restoration endpoint backed by native Woo **cart APIs**; `wc_get_checkout_url()` remains only its final redirect. Avoid independently copying WooCommerce pricing/coupon validation into Moda.

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
    W->>A: Authenticated woo.activity.v3 checkout snapshot incl. coupons/restore
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
    A-->>W: Products/variations/attributes + original coupon codes
    W->>W: Preflight, rebuild cart, native coupon validation, recalculate
    W->>A: Fresh CHECKOUT_UPDATED (via Action Scheduler)
    W-->>C: Redirect wc_get_checkout_url()
    A->>Q: Checkout capture job
    Q->>B: New activity, ARCH-048 closes prior recovery and schedules next candidate
```

## Ownership and public infrastructure

- `moda_shared`: canonical snapshot/schema and REST contract, separately published reusable version.
- `moda_database`: additive nullable Prisma JSON + migration, no schema updates by other agents.
- `moda_woocommerce`: capture coupons/variation support, confirmation endpoint and manual engagement detection.
- `moda_api`: authenticated checkout v3 acceptance and restoration resolution, no Redis or Woo session writes on resolve.
- `moda_background`: carry snapshot to candidates/recovery, generate idempotent URL and existing template binding; never call a merchant-controlled site to mint a link.
- `moda_system_test`: final integration across actual Woo, Meta sender mocks, BullMQ, Postgres, API, coupon rules and order/consent lifecycle.
- `moda_gateway`: no new task **based on inspected topology**; existing `/v1/woocommerce/*` passes through the current public API service. Before integration, verify endpoint routing in deployed environment; if not supported, return to architect for bounded Gateway task, not an ad hoc implementation.

## Idempotency, ordering and failure handling

The Woo eventId/digest and queue deduplication remain unchanged. An updated full basket fingerprint includes coupon/restoration changes; candidates use event ordering/watermark and validated entire snapshot, not incremental coupons. Admission transaction writes historical `wooRestoreSnapshot`, `checkoutUrl` and status together. Under ARCH-048, generation links are never reattached to later generations. Old events, retries, two devices, concurrent confirmation attempts and orders must not let a stale link overwrite the newly active session. API checks eligibility at time of confirmation; asynchronous activity-to-closure is **eventually consistent**, not an invented atomic cross-site transaction. Woo queues a durable post-restoration activity with existing Action Scheduler; delivery failure is logged/retriable and is an explicit residual risk. A customer browsing the website without a session key cannot be assumed to have resumed the original recovery.

## Security and privacy

Bearer token is 256-bit unpredictable, compared with bounded constant-time digest; no PII or coupons in URL. Redact URL/token from diagnostics, telemetry, request logs and referrer. Bind API resolution to installation principal + authoritative shop. Prevent cross-merchant leaks, open redirects, host/path mismatches, SSRF, query injection, replay of stale generations and WordPress CSRF. Do not grant consent on link access. GET/HEAD and robots have no mutating effects; require explicit POST confirmation, session-tied nonce and current Woo cart/server-side checks. If link is stale, show safe merchant checkout/home navigation without restoring historical products. Do not trust a caller-supplied product set, checkout key or shop ID.

## Observability

Node uses `@modainteract/moda-interact-shared/logging` for generic structured events, domain event codes and bounded ids; PHP reuses existing safe plugin logging without adding a generic logger. Track received v3 snapshots, unsupported baskets, link issued/omitted, failed tenant/eligibility/token checks (no token values), coupon reapplied/rejected counts, restore success/failure, resumption-event acceptance and queue delays. Do not recreate standard HTTP metrics. Never expose raw URL/token or customer contact in logs. Telemetry failure must not affect business correctness.

## Rollout and compatibility

**Pre-production proposal**, conditional on developer confirming there is no production state requiring compatibility. Preserve/deliberately drain existing Redis test events before activating producer v3. Implementation order: Shared contract implementation → Shared publish → Database migration + Background consumer → API v3 acceptance → Woo v3 producer → authenticated resolution + plugin restore → ARCH-048 generation integration → terminal system test. The existing v1/v2 HTTP paths remain during transition; only v3 can produce a restore snapshot. Do not deploy partially composed tasks or turn on Woo live outbound sending. Revert by disabling issuance/restore entrypoint without rewriting historical recovery records; rollback database column only after safe data-retention review.

## Decisions / Tasks

See the machine-readable YAML of each `docs/decisions/*/ARCH-053/*.md` task and domain indexes. **Only DATABASE-001 and SHARED-001 are independently Ready** in the supplied snapshot; all other tasks remain Pending on prerequisites, notably ARCH-048-BACKGROUND-011 (portable only).

| Task | Owner | Status | Depends on |
|---|---|---|---|
| ARCH-053-DATABASE-001 | moda_database | Ready | — |
| ARCH-053-SHARED-001 | moda_shared | Ready | — |
| ARCH-053-SHARED-002 | moda_shared | Pending | SHARED-001 |
| ARCH-053-API-001 | moda_api | Pending | SHARED-002 |
| ARCH-053-BACKGROUND-001 | moda_background | Pending | SHARED-002 |
| ARCH-053-BACKGROUND-002 | moda_background | Pending | BACKGROUND-001, DATABASE-001 |
| ARCH-053-WOOCOMMERCE-001 | moda_woocommerce | Pending | API-001, BACKGROUND-001 |
| ARCH-053-WOOCOMMERCE-004 | moda_woocommerce | Pending | WOOCOMMERCE-001 |
| ARCH-053-API-002 | moda_api | Pending | SHARED-002, DATABASE-001 |
| ARCH-053-BACKGROUND-003 | moda_background | Pending | BACKGROUND-002, ARCH-048-BACKGROUND-011 |
| ARCH-053-WOOCOMMERCE-002 | moda_woocommerce | Pending | WOOCOMMERCE-001, API-002 |
| ARCH-053-WOOCOMMERCE-005 | moda_woocommerce | Pending | WOOCOMMERCE-002, WOOCOMMERCE-004 |
| ARCH-053-WOOCOMMERCE-006 | moda_woocommerce | Pending | WOOCOMMERCE-005 |
| ARCH-053-WOOCOMMERCE-003 | moda_woocommerce | Pending | WOOCOMMERCE-001 |
| ARCH-053-SYSTEM-TEST-001 | moda_system_test | Pending | BACKGROUND-003, WOOCOMMERCE-002, WOOCOMMERCE-003, ARCH-048-BACKGROUND-011, ARCH-046-WOOCOMMERCE-003 |
| ARCH-053-SYSTEM-TEST-002 | moda_system_test | Pending | WOOCOMMERCE-004, WOOCOMMERCE-006, BACKGROUND-003, WOOCOMMERCE-003, ARCH-048-BACKGROUND-011, ARCH-046-WOOCOMMERCE-003 |

All abbreviated ARCH-053 refs in this table expand to fully qualified ids. SYSTEM-TEST-001 and SYSTEM-TEST-002 are terminal; no implementation task depends upon either.

## Open Questions / explicit constraints

- Cross-ARCH-048 worktree materialisation and acceptance must be checked before issuance and integrated certification. The 2026-10-29 snapshot does not contain BG007..011.
- Real WooCommerce extension-specific item options are NOT round-trippable with the existing snapshot. If they cannot be proved safe in plugin-owned unit/integration tests, mark basket unsupported, omit link and use template no-link/no-send fallback. Do not promise arbitrary extension restore.
- Background order evidence is observed-only; if an order never reached Moda there is no cross-provider guarantee. Confirmation checks the strongest available documented state but does not invent a live Woo merchant lookup.
- The existing ARCH-052 task inventory may still contain historical dependencies on its superseded Woo restore tasks; **reconciliation remains within ARCH-052 ownership and must not be used to implement restore under ARCH-052**.

## Change History

- 2026-10-29: Initial independent ARCH-053 architecture and portable task definitions; ARCH-052 unchanged.
- 2026-10-29: Added separately reviewable coupon-only activity, native coupon reapplication, rejected-coupon customer notices and terminal coupon certification (WOOCOMMERCE-004/005/006 and SYSTEM-TEST-002).
