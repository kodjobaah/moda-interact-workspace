---
id: ARCH-077-SHOPIFY-005
architecture_id: ARCH-077
title: Returning-customer consent display, merchant activation and locales
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-002, ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004]
enables: [ARCH-077-SHOPIFY-006, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Returning-customer consent display, merchant activation and locales

**Pending; after accepted S002/S003/S004.** Follow the [one-attribute receipt contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). This task owns merchant-facing setup, plan-specific placement guidance, returning verified SQL consent display and Shopify-owned locales, **not** the receipt service or recovery admission.

## Exact ownership

- `app/routes/app/recovery-settings/WhatsAppCustomerConsent.tsx`, recovery-settings integration and existing `app/i18n/locales/*.json` (20 locales); consume S003 theme activation helpers and S004 checkout-extension activation verification.
- **Non-Plus:** explain enable/cart theme editor -> merchant Save -> verify published cart template. **Plus:** explain enable checkout extension at `purchase.checkout.contact.render-after`; ensure merchant plan enables exactly one placement and disable/hide cart activation for Plus. On plan change, do not leave both controls active; report unsupported/unverified as such.
- Replace Shopify-native WhatsApp marketing instructions. Do not imply separate Shopify Messaging integration, native WhatsApp provider consent or a new telephone field.
- A verified signed Shopify customer ID/shop can read current persistent PostgreSQL `CustomerPhone` decision, STOP and no-contact for checkbox initial display; a returning verified GRANTED displays checked, but does not cause a receipt write. Current same cart/checkout *valid signed Shopify attribute* overrides SQL **for local display only**, without materialising. A guest/new unrelated cart never inherits another guest's consent via phone/email.
- Exact English customer-facing wording `Send me WhatsApp shopping updates, reminders and offers.` and same translated meaning. Pass actual displayed shopper locale, not merchant admin locale. Rendering/activation status never issues a signed receipt or SQL decision.
- Unreachable S002 or unsupported Shopify attribute writes: hide only Moda's checkbox, no customer-facing technical error, no checkout block; server original provider diagnostic logged with PII/secret redaction. Merchant may see truthful `Status unavailable` or `Placement unverified`, not an invented enabled badge.

## Tests/acceptance

- Both plan paths exclusive, verified merchant activation/Save and unverified/unsupported case; all 20 locales; returning customer status without action; explicit REVOKE on Cart B remains Shopify attribute only until B recoverable; B paid has no SQL effect; Cart A messages governed by current stored permission/STOP.
- No permanent Redis consent, no status-read writes, no second checkout/cart placement, no Woo translation edits, no `docs/decisions/**/_index.md` changes.
