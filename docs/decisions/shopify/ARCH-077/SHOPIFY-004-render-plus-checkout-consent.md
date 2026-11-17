---
id: ARCH-077-SHOPIFY-004
architecture_id: ARCH-077
title: Render Shopify Plus checkout WhatsApp consent checkbox
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHOPIFY-002]
enables: [ARCH-077-SHOPIFY-005, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Render Shopify Plus checkout WhatsApp consent checkbox

**Pending; depends on accepted S002.** Plus uses **only this checkout checkbox**, while non-Plus uses S003 cart checkbox. Do not run both, and do not implement old S003 cart-selection precedence. The shared temporary choice is one signed `moda_wa_consent_v1` **Shopify checkout attribute**; see [receipt contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md).

## Source, extension and authentication

- Create separate Checkout UI Extension at `extensions/moda-whatsapp-checkout-consent/` with supported Shopify CLI manifest, supported `purchase.checkout.contact.render-after` target and `network_access` capability, Shopify-owned 20 locales and tests. Never use theme script injection, Shopify native marketing checkbox or a second phone field.
- Use Shopify checkout extension's **signed session token** obtained from `shopify.sessionToken.get()` to call S002 `POST checkout/receipt`; verify by SDK `authenticate.public.checkout` or installed equivalent on server. The extension's `checkoutToken` is a stable checkout locator and may be undefined: do not offer an actionable Moda checkbox if unavailable or if app verification fails. Do not invent verified JWT claims or use unauthenticated checkoutToken alone as authority.
- Only after verifying `instructions.attributes.canUpdateAttributes`, supported plan/target and signed server response, call `shopify.applyAttributeChange({type:'updateAttribute',key:'moda_wa_consent_v1',value:receipt})`. Confirm `type:'success'` and read the current checkout attribute. Accelerated checkouts or unavailable attribute mutations hide Moda control and do not block payment.

## Explicit action and status

- Show exact English wording `Send me WhatsApp shopping updates, reminders and offers.` with Shopify locale meaning. On verified returning customer, S002 reads current PostgreSQL consent for display; for current checkout read/verify current signed receipt and show its decision. No auto-GRANT on render/default, no write without explicit check/uncheck.
- Each deliberate GRANT/REVOKE obtains a fresh `kind=x` receipt bound to current checkout token and replaces the **same attribute key**; no Redis, cart marker or SQL consent write at click time. A failed issuer or Shopify mutation does not show saved state; hide or restore control silently.
- A Plus merchant's cart App Block is disabled by the merchant installation/plan configuration in S005; no precedence between cart and checkout choices exists for Plus. Unsupported express routes are uncovered, not auto-granted.

## Tests/stop

- Real eligible Plus development-store test: verified session JWT/shop/customer, actual checkoutToken, attribute write, authoritative `AbandonedCheckout.customAttributes` retrieved later, malformed/copy/replay scenarios, GRANT->REVOKE replacement, Plus-only placement, readback, 20 locales, accessibility and silent failure.
- SDK mocks are not proof of a working Plus checkout extension. If supported checkout token cannot be established/verified, attribute mutation denied, or extension unavailable under merchant plan, stop with evidence. Never substitute a cart checkbox on Plus or add a new Redis/SQL consent store.
