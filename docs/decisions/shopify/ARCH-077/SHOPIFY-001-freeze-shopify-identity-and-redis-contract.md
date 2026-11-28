---
id: ARCH-077-SHOPIFY-001
architecture_id: ARCH-077
title: Shopify consent identity evidence and accepted checkout-attribute transport
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  [
    ARCH-077-SHARED-001,
    ARCH-077-BACKGROUND-001,
    ARCH-077-SHOPIFY-002,
    ARCH-077-SHOPIFY-004,
  ]
created: 2026-11-17
updated: 2026-11-17
---

# Shopify consent identity and integration contract — accepted evidence, superseded transport

**Status remains `complete`.** S001 proved the non-Plus cart -> checkout attribute transition. Its historical Redis marker contract is **superseded for production** by [signed checkout attribute v1](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). Do not repeat the accepted marker experiment, relaunch S001, or carry `m1_` marker/Redis state into the new consent path.

## Evidence retained

- Ajax base cart token matched `CARTS_CREATE`/`CARTS_UPDATE` in the diagnostic tests; direct equality to `checkout.cart_token` differed across some observed sessions, so a guest receipt whose canonical cart-token binding cannot be verified at maturity is **denied** rather than guessed.
- The non-Plus attribute `moda_s001_probe` was written by `/cart/update.js`, appeared in authenticated checkout create/update webhooks and appeared in `AbandonedCheckout.customAttributes` with SHA-256 marker prefix `ef5dbf7582291225` (checkout `gid://shopify/AbandonedCheckout/67330154594377`). This demonstrates a Shopify-preserved attribute **only**, not signed receipt integrity.
- S001's completed status denotes accepted investigation, not completion of the pending S002 new receipt implementation or live Plus extension proof.

## New frozen downstream handoff

- Standard Shopify non-Plus: one cart checkbox, server-issued Shared-authenticated receipt, one Shopify cart attribute. Plus: one checkout checkbox, same attribute and signed receipt format, checkout-token binding. Neither placement runs simultaneously for one merchant.
- Background uses the authoritative checkout's `customAttributes` with independently validated source/event token and customer/recipient. No new marker index, consent Redis TTL, cart-to-checkout Redis lookup, Shared event-version change, or independent consent API call.
- The exact v1 issuer/verifier, key, wire format, plan gating and fail-closed outcome rules are in the linked specification. S002 and B001/B002 accept that contract; implementing agents may not invent a different one.
