---
id: ARCH-077-SHOPIFY-003
architecture_id: ARCH-077
title: Render and activate Shopify cart-page WhatsApp consent App Block
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-11-18T01:22:58Z
attempt: 2
depends_on: [ARCH-077-SHOPIFY-002]
enables: [ARCH-077-SHOPIFY-005, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-18
---

# Render and activate Shopify cart-page WhatsApp consent App Block

**Architect Changes Requested (18 November 2026); returning for Attempt 2.** The S002 stateless issuer is accepted. This task must correct verified current-cart display before acceptance. Follow the [ARCH-077 checkout-attribute receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). This task **does not** request Redis marker preparation, Redis GRANT/REVOKE writes, or checkout correlation. Non-Plus merchants get this cart checkbox, Plus merchants get **only S004** checkout checkbox.

## Owning source touchpoints

- Create `extensions/moda-whatsapp-consent/shopify.extension.toml` (theme extension), `blocks/cart-consent.liquid` (`target: section`, `enabled_on.templates: [cart]`) and only needed assets/locales under `extensions/moda-whatsapp-consent/`. Use supported Shopify CLI scaffold, no injected theme scripts or extra phone fields.
- Create/maintain Shopify cart activation link/status helpers under `app/services/shopify-consent/theme-activation-url.server.ts` and `theme-activation-status.client.ts`; S005 consumes their verified merchant activation state.
- Use the authenticated App Proxy `GET cart/status` + `POST cart/receipt` owned by S002. **Architect-authorised narrow S003 exception:** extend the existing Shopify-owned S002 App Proxy route with read-only `POST cart/verify`, exactly as frozen below and in the ARCH-077 v1 contract; do not change issuer semantics. No new app, queue or storage. Never call obsolete `cart/prepare` or `cart/choice` endpoints or write any Redis consent key.

## Deterministic shopper flow

1. Check that the merchant's selected plan/placement is non-Plus and published cart App Block is active. Do not display both S003/S004 on any one merchant. Load `/cart.js` using Shopify locale-aware routes; require a real current cart and normalize the private `?` suffix for binding as S002 defines.
2. On first render, ask S002 for verified returning-customer SQL status; inspect **only the current cart** `attributes.moda_wa_consent_v1`, and if a nonempty attribute exists, require authenticated server verification before showing the checkbox. Verification is **not optional**: after an accepted GRANT, display checked on reload; after an accepted REVOKE, display unchecked. Do not substitute an unchecked default for an unverified existing receipt. When an existing receipt cannot be verified (including tampering, stale/cart/customer mismatch or backend failure), hide the Moda control silently and leave checkout usable. When no current-cart attribute exists, use the verified returning-customer SQL status. Do not assume browser attribute text alone is a verified grant; unchecked default/render is neutral. Display exact English copy `Send me WhatsApp shopping updates, reminders and offers.` and Shopify locale equivalent.
3. On **explicit check/uncheck only**, call S002 `POST cart/receipt` with `GRANT`/`REVOKE`, verified current cart locator and shopper locale; S002 issues one signed receipt. Write **only** `attributes:{moda_wa_consent_v1:receipt}` to locale-aware `/cart/update.js`, and confirm via Shopify response or a single re-fetch of `/cart.js` that the exact receipt is current. Do not overwrite unrelated attributes or change cart contents. Receipt on an unsubmitted checkout is merely temporary Shopify attribute state; no SQL or proactive suppression occurs.
4. If request, issuer, cart update or readback fails, silently restore last confirmed state or hide *only* Moda control, never display an unacknowledged choice as saved and never interrupt checkout/payment. No repeated automatic action, global retries or leaking raw receipt/cart token into logs.
5. A visitor changing carts must read the new cart and never copy a valid prior checkout's receipt to it. Express/accelerated routes bypassing the cart do not create consent. A non-Plus guest whose `cart_token` differs from the signed cart receipt at Background evaluation fails closed; do not add marker fallback, user matching or product/time heuristics.

## Frozen read-only verification interface (S003 owns this integration)

- Shopify app server adds one action path **`POST /shopify/consent/cart/verify`**, exposed via the *existing* signed App Proxy URL **`/apps/moda-consent/cart/verify`**. Follow S002's installed `authenticate.public.appProxy` signature/shop/signed-customer verification, `write_app_proxy` scope, timestamp freshness, configured safe proxy-prefix handling, origin validation and bounded JSON parser. Do **not** add a second authentication scheme or persist the receipt.
- Request exactly `{ "cartToken": string, "receipt": string }`; do not accept client-supplied shop ID, customer ID, decision or provenance. Obtain shop and optional Shopify customer from authenticated proxy context. Invoke existing `verifyConsentReceipt(receipt, {shopId,kind:"c",token:cartToken,customerId:shopifyCustomerId})`, preserving original Shared keyring/AAD and existing accepted same-cart replay limitation. No new cryptography or Redis.
- Successful response exactly `{ "source": "verified_receipt", "decision": "GRANT" | "REVOKE" }` (map signed `G`/`R`); `Cache-Control: no-store`. Rejected receipts return a bounded non-2xx response with no plaintext, raw receipt, decrypted claims or token in logs. Server preserves redacted original error diagnostics using existing logging.
- The browser reads `/cart.js` first and sends only the receipt that is currently present on **that cart**. On valid verification, set checked for GRANT and unchecked for REVOKE; do **not** issue or overwrite a receipt on initial render. A missing attribute falls back to SQL status. If a present attribute fails verification, **do not** fall back to a potentially contradictory old SQL GRANTED state; hide only this App Block and allow ordinary shopping/checkout.
- If the theme editor rerenders/replaces the cart App Block after initial `DOMContentLoaded`, initialise the new element on Shopify's section-load event without duplicate handlers on an existing root; no repeated grant from render.

## Tests and stop

- Theme App Block schema/cart-template limitation, published-theme save, unavailable/incompatible theme and no false activation claims.
- New cart unchecked with **zero receipt issued**; returning verified SQL GRANTED checked but no new receipt until deliberate change; real browser choice -> signed attribute -> `CHECKOUTS_CREATE/UPDATE` and `AbandonedCheckout.customAttributes`, preserving one exact receipt.
- Verified existing GRANT renders checked after reload and verified existing REVOKE renders unchecked after reload, **without creating any receipt**; modified/cross-cart/cross-customer receipt, verification endpoint error or lost network hides the control without blocking checkout. Test signed App Proxy checks on the new read-only endpoint, including guest and authenticated customer, custom storefront origin and timestamp freshness. Test dynamic theme editor section-load reinitialisation without duplicate writes.
- GRANT then REVOKE same cart replaces key; reading last valid receipt returns REVOKE; copied signed receipt to another cart denied by binding at B002. Missing/broken issuer/readback, cart replacement, two tabs, custom domain, locale and express checkout fail silently, no checkout block.
- Do not modify S002 receipt issuance logic beyond the narrowly authorised `cart/verify` read-only action, or change Background, Shared, Woo/API, existing BullMQ or `_index.md` from S003. Stop if the receipt cannot be written/read or the approved app-proxy path cannot be deployed; report exact blocker.

## Completion Report

- Implemented the cart-only `target: section` Theme App Block, 20 storefront locales, explicit-only receipt issuance, locale-aware Ajax cart requests, exact receipt/cart-token confirmation, and fail-closed theme activation helpers.
- The block is gated by the boolean app-data metafield `moda_interact.cart_consent_enabled`; S005 must set it only for non-Plus plan placement and keep it false for Plus. The block remains unavailable until that plan gate is configured.
- The current S002 route does not expose `verifyConsentReceipt`. A nonempty receipt already on the cart is therefore treated as unverified and displayed neutrally (unchecked); raw cart attribute text is never trusted as a grant.
- Validation passed: 12 focused Vitest cases, targeted ESLint, all 20 locale JSON labels, `shopify app build --config moda-interact` including Theme Check, and `npm run build`.
- `npm run typecheck` still reports five implicit-`any` errors in the unchanged `app/routes/webhooks/root/route.jsx`. No live dev-store operation was run; published-theme activation and Shopify cart-to-checkout receipt propagation remain unverified and require a separately confirmed remote validation.

## Architect Review — Attempt 1 (18 November 2026)

### Review Status

**Changes Requested.** Reclaimable task: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1` preserved. Agent claims Attempt 2 via the normal launcher. The existing implementation commits and Completion Report must remain in history.

### Review Notes / Verified deficiencies

1. **Blocking display correctness:** `extensions/moda-whatsapp-consent/assets/cart-consent.js` currently sets `initialChecked = false` for *every* nonempty pre-existing `moda_wa_consent_v1` value, without invoking the existing S002 `verifyConsentReceipt`. This displays a previously GRANTED selection as unchecked after reload, and treats a tampered receipt as an ordinary unchecked selection. The user's last confirmed explicit choice must be shown accurately, not falsely interpreted as a new default.
2. **Missing integration surface:** `app/routes/shopify/consent/route.ts` has `GET cart/status` and `POST cart/receipt`, but no authenticated receipt-read endpoint. The existing task text forbids changing S002's route. This review resolves that conflict by authorising **only** the read-only `POST cart/verify` action above under this same Shopify S003 task. Use the existing S002 verifier and authenticated proxy contract; no new key-management, SQL write, queue or marker logic.
3. **Theme editor lifecycle:** the JS initialiser runs at DOMContentLoaded and relies on a WeakSet for existing roots but does not register Shopify's section-load event, so dynamically replaced cart blocks cannot be assumed initialised. Add bounded section-load reinitialisation tests. No additional global theme script or framework.

### Reviewed Files

- `extensions/moda-whatsapp-consent/blocks/cart-consent.liquid`, `assets/cart-consent.js`, `assets/cart-consent.css`, `shopify.extension.toml`, 20 extension locale JSONs
- `app/services/shopify-consent/theme-activation-url.server.ts`, `theme-activation-status.client.ts`, `app/routes/shopify/consent/route.ts`, `app/services/shopify-consent/consent-receipt.server.ts`
- `tests/unit/extensions/moda-whatsapp-consent.test.js`, `tests/unit/services/shopify-consent-theme-activation.test.ts`, current S003 Completion Report

### Positive Findings / Validation Reviewed

- Bounded cart-only App Block with `target: section`/cart-template scope, locale-aware Ajax calls, server-issued AEAD receipts on explicit actions, readback confirmation and silent failure; uses the existing merchant app-data metafield placement gate.
- Existing SQL status is read for a cart without a receipt. The browser does not try to decrypt Shared ciphertext or write click-time SQL/Redis state.
- Agent reports 12 focused tests, targeted ESLint, 20 valid locale labels, Shopify CLI/theme check and production build passing; **these were not independently executed from the ZIP**. Architect independently ran `node --check` on `cart-consent.js` and parsed all 20 locale JSONs successfully. `npm run typecheck` retains five reported pre-existing errors in unchanged `app/routes/webhooks/root/route.jsx`; distinguish these from any newly introduced errors.
- No live dev-store/published-theme signed-receipt transport was demonstrated. Keep this a **S005 / terminal SYSTEM-TEST-001 integration gate**, not a requirement to invent merchant metafield activation in S003 before S005 is implemented.

### Architecture Conformance

**Partial.** Attribute transport, explicit-only issuance, plan-specific placement, no Redis consent and Shared cryptography reuse conform. Current-cart verified display does **not** conform to the accepted S003 task and v1 receipt-read semantics.

### Required Resubmission / Stop

- Correct only the specified UI/display, read-only Shopify App Proxy verification integration, theme-editor reinit and their focused tests. Keep receipt issuance and Shared AEAD untouched; do not modify other repositories or `docs/decisions/**/_index.md`.
- Provide exact modified paths, current task worktree/branch SHA and implementation commit, `git diff --check`, focused App Proxy/cart reload tests, targeted lint, relevant Shopify build/Theme Check, `npm run build`, and `npm run typecheck` with baseline-vs-new error classification. Report real test results without calling mocked tests live Shopify proof.
- On success, agent sets SHOPIFY-003 back to `review`, completes its report and stops. Architect independently re-reviews before marking `complete` or promoting SHOPIFY-005. Retain downstream gates until then.
