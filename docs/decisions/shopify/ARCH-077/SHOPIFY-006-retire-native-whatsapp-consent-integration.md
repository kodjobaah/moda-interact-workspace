---
id: ARCH-077-SHOPIFY-006
architecture_id: ARCH-077
title: Remove obsolete Shopify WhatsApp marketing-consent integration
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-BACKGROUND-002, ARCH-077-SHOPIFY-005]
enables: [ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Retire Shopify-native WhatsApp consent integration — preproduction cleanup

**Pending; execute after accepted S002/S005/B002 and before final SYSTEM-TEST-001.** The [v1 attribute-based consent contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md) replaces Shopify-native marketing consent and temporary Redis selection paths.

## Scope

- Remove unused Shopify `customers_whats_app_marketing_consent/update` subscriptions from the active `shopify.app.moda-interact.toml`, legacy native WhatsApp consent producer/projection/sync callers from Shopify/Background under B002 ownership, unused diagnostics and stale S002 Redis marker/choice producers. Preserve unrelated customer, order, cart, checkout and Shopify privacy webhooks.
- Do not add a compatibility adapter for obsolete preproduction native-consent jobs or remodel existing `CustomerPhone` enum. Keep `SHOPIFY_NATIVE` as approved identifier for Moda-verified Shopify receipt consent **after recoverability** only; no native provider read required.
- Any old **preproduction** `shopify:consent:*` marker/choice keys must be cleaned up only in a bounded, scoped operation that neither scans/deletes shared BullMQ data nor clears existing database STOP/customer permission.
- Retire temporary `ARCH077_S001_DIAGNOSTICS` after proof; never log raw receipts/cart/checkout tokens. Preserve original useful SDK diagnostic context redacted.

## Acceptance

No production native-marketing consent read/ingress writer remains, no S002 Redis cart/marker/choice writer remains; webhook queue still handles carts/checkouts/orders with unchanged job identity; new receipt path works only through Shopify attributes and verified Background lookup. No schema changes, new queue or `_index.md` edits.
