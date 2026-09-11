# ARCH-007 BACKGROUND-010 Attempt 2 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 2 received **Changes Requested**.

Attempt 2 successfully corrected the broad provider-send ownership structure and
added the settled-turn processor seam.

Attempt 3 is limited to:

1. replace active-job `changeDelay()` with a BullMQ-supported active-job delay
   transition while preserving the deterministic job id;
2. make settled clarification routing distinguish current
   resolved/clarify/unresolved outcomes, including the 11-row fail-closed
   sentinel;
3. add the missing persisted-fragment/dedupe/deterministic recovery-order
   regressions;
4. retain one definitive-provider regression alongside the accepted ambiguous
   provider case.

Per developer instruction, this task remains under the legacy no-commit/no-push
workflow until BACKGROUND-010 and ADMIN-001 are both architect-accepted.
