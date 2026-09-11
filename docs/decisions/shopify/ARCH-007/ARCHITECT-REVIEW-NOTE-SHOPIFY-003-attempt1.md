# ARCH-007 SHOPIFY-003 Attempt 1 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 1 uninstall behavior is correct.

Changes Requested are limited to restoring the previously architect-accepted Shopify repository dependency baseline:

```text
@modainteract/moda-interact-shared
accepted SHOPIFY-002 baseline: package ^0.7.4 / lock 0.7.4
submitted SHOPIFY-003 bundle:  package 0.7.3 / lock 0.7.3
```

Return the SAME task for Attempt 2 after restoring 0.7.4 and revalidating.

Do not redesign the uninstall implementation and do not opportunistically upgrade this task to Shared 0.8.0.
