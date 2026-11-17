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
status: review
priority: 50
executor: copilot
claimed_at: 2026-11-17T20:11:24Z
attempt: 1
depends_on: [ARCH-077-SHOPIFY-002]
enables: [ARCH-077-SHOPIFY-005, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Render and activate Shopify cart-page WhatsApp consent App Block

**Pending; depends on accepted S002 stateless receipt issuer.** Follow the [ARCH-077 checkout-attribute receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). This task **does not** request Redis marker preparation, Redis GRANT/REVOKE writes, or checkout correlation. Non-Plus merchants get this cart checkbox, Plus merchants get **only S004** checkout checkbox.

## Owning source touchpoints

- Create `extensions/moda-whatsapp-consent/shopify.extension.toml` (theme extension), `blocks/cart-consent.liquid` (`target: section`, `enabled_on.templates: [cart]`) and only needed assets/locales under `extensions/moda-whatsapp-consent/`. Use supported Shopify CLI scaffold, no injected theme scripts or extra phone fields.
- Create/maintain Shopify cart activation link/status helpers under `app/services/shopify-consent/theme-activation-url.server.ts` and `theme-activation-status.client.ts`; S005 consumes their verified merchant activation state.
- Use the authenticated App Proxy `GET cart/status` + `POST cart/receipt` owned by S002. Never call an obsolete `cart/prepare` or `cart/choice` endpoint or write any Redis consent key.

## Deterministic shopper flow

1. Check that the merchant's selected plan/placement is non-Plus and published cart App Block is active. Do not display both S003/S004 on any one merchant. Load `/cart.js` using Shopify locale-aware routes; require a real current cart and normalize the private `?` suffix for binding as S002 defines.
2. On first render, ask S002 for verified returning-customer SQL status; also inspect **only the current cart** `attributes.moda_wa_consent_v1` and use the S002 verifier to establish current-cart display status where available. Do not assume browser attribute text alone is a verified grant; unchecked default/render is neutral. Display exact English copy `Send me WhatsApp shopping updates, reminders and offers.` and Shopify locale equivalent.
3. On **explicit check/uncheck only**, call S002 `POST cart/receipt` with `GRANT`/`REVOKE`, verified current cart locator and shopper locale; S002 issues one signed receipt. Write **only** `attributes:{moda_wa_consent_v1:receipt}` to locale-aware `/cart/update.js`, and confirm via Shopify response or a single re-fetch of `/cart.js` that the exact receipt is current. Do not overwrite unrelated attributes or change cart contents. Receipt on an unsubmitted checkout is merely temporary Shopify attribute state; no SQL or proactive suppression occurs.
4. If request, issuer, cart update or readback fails, silently restore last confirmed state or hide *only* Moda control, never display an unacknowledged choice as saved and never interrupt checkout/payment. No repeated automatic action, global retries or leaking raw receipt/cart token into logs.
5. A visitor changing carts must read the new cart and never copy a valid prior checkout's receipt to it. Express/accelerated routes bypassing the cart do not create consent. A non-Plus guest whose `cart_token` differs from the signed cart receipt at Background evaluation fails closed; do not add marker fallback, user matching or product/time heuristics.

## Tests and stop

- Theme App Block schema/cart-template limitation, published-theme save, unavailable/incompatible theme and no false activation claims.
- New cart unchecked with **zero receipt issued**; returning verified SQL GRANTED checked but no new receipt until deliberate change; real browser choice -> signed attribute -> `CHECKOUTS_CREATE/UPDATE` and `AbandonedCheckout.customAttributes`, preserving one exact receipt.
- GRANT then REVOKE same cart replaces key; reading last valid receipt returns REVOKE; copied signed receipt to another cart denied by binding at B002. Missing/broken issuer/readback, cart replacement, two tabs, custom domain, locale and express checkout fail silently, no checkout block.
- Do not modify S002 route, Background, Shared, Woo/API, existing BullMQ or `_index.md` from S003. Stop if the receipt cannot be written/read or the approved app-proxy path cannot be deployed; report exact blocker.

## Completion Report

- Implemented the cart-only `target: section` Theme App Block, 20 storefront locales, explicit-only receipt issuance, locale-aware Ajax cart requests, exact receipt/cart-token confirmation, and fail-closed theme activation helpers.
- The block is gated by the boolean app-data metafield `moda_interact.cart_consent_enabled`; S005 must set it only for non-Plus plan placement and keep it false for Plus. The block remains unavailable until that plan gate is configured.
- The current S002 route does not expose `verifyConsentReceipt`. A nonempty receipt already on the cart is therefore treated as unverified and displayed neutrally (unchecked); raw cart attribute text is never trusted as a grant.
- Validation passed: 12 focused Vitest cases, targeted ESLint, all 20 locale JSON labels, `shopify app build --config moda-interact` including Theme Check, and `npm run build`.
- `npm run typecheck` still reports five implicit-`any` errors in the unchanged `app/routes/webhooks/root/route.jsx`. No live dev-store operation was run; published-theme activation and Shopify cart-to-checkout receipt propagation remain unverified and require a separately confirmed remote validation.
