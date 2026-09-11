# ARCH-007 SHOPIFY-002 Attempt 2 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 2 received **Changes Requested** for one remaining canonical billing SYSTEM-code mismatch.

The accepted Shared 0.7.4 contract uses:

```text
BILLING_SUBSCRIPTION_ENDED
```

but `billing.service.ts` currently persists:

```text
SUBSCRIPTION_ENDED
```

The latter is rejected by the canonical Shared schema, so subscription-ended merchant messages render without the required billing CTA.

The authoritative Attempt 3 correction contract is the latest `## Architect Review` in:

```text
docs/decisions/shopify/ARCH-007/SHOPIFY-002-merchant-billing-ui-system-actions.md
```

Do not broaden this correction into ARCH-005 full UI translation work.
