# ARCH-007 BACKGROUND-009 Attempt 1 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 1 received **Changes Requested**.

The core purchased-credit reservation/activation/admission implementation is
sound and should be preserved.

Attempt 2 is limited to:

1. prevent terminal RecoveryCreditPurchase reconciliation from being starved by
   an older page of non-terminal purchases;
2. keep post-REPORTED credit-activation failures out of the Shopify provider
   retry/attention state machine;
3. add the missing explicit recovery-pack concurrency/replay/lifecycle and
   publisher/reconciliation regressions.

The Background `_index.md` and canonical parent frontier are intentionally not
included because ARCH-007-BACKGROUND-010 has already been started in the live
workspace after this B009 review snapshot was created. Applying an older index
would risk overwriting that active claim.
