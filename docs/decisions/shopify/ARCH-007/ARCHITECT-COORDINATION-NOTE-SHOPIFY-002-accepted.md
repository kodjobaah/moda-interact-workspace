# ARCH-007 SHOPIFY-002 acceptance coordination

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

`ARCH-007-SHOPIFY-002` Attempt 3 is architect-accepted Complete on 2026-09-08.

Immediate cross-architecture promotion:

```text
ARCH-005-SHOPIFY-004 -> Ready
```

Its explicit dependencies are all Complete:

```text
ARCH-005-SHOPIFY-002
ARCH-006-SHOPIFY-003
ARCH-007-SHOPIFY-002
```

The standalone `SHOPIFY-004-i18n-key-manifest.md` remains the deterministic implementation contract for the 32 new keys across all 20 locale catalogues.

ARCH-007-SHOPIFY-004 remains Pending because SHARED-006 and ADMIN-005 are not yet Complete.

ARCH-007 system tests remain terminal/manual-gated and must not be started automatically.

This selective Shopify archive does not contain the current canonical ARCH-007 architecture/handoff files. Reconcile the parent task table/frontier on the next full-workspace pass rather than overwriting it from an older copy.
