# ARCH-007 ADMIN-001 Attempt 1 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 1 received **Changes Requested**.

The catalog, authorization, validation, immutable-handle and transactional audit
structure is retained.

Attempt 2 is limited to:

1. make update audit `beforeValue` come from the actual persisted BillingPlan
   rather than the new form values;
2. stop existing PAID_METERED forms from injecting a Free allowance of `5`;
3. add focused behavioral regressions for both corrections.

Per developer instruction, this task remains under the legacy no-commit/no-push
workflow until ADMIN-001 and BACKGROUND-010 are both architect-accepted.
