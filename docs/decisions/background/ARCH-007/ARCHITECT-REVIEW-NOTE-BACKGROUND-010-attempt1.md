# ARCH-007 BACKGROUND-010 Attempt 1 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 1 received **Changes Requested**.

The overall delayed-turn / conversation-lease architecture is retained.

Attempt 2 must correct four bounded areas:

1. do not convert ambiguous provider-send outcomes into `failPrepared`;
2. preserve the accepted deterministic same-owner multi-recovery clarification path after coalescing;
3. make `pendingTurnStartedAt` first-fragment establishment concurrency-safe;
4. add executable coverage for the task's 15 required coalescing/worker scenarios, plus provider ambiguity and concurrent first-fragment receipt.

This task was initially implemented before task feature branches became mandatory. That is not a defect for Attempt 1.

Attempt 2 should continue on:

```text
task/ARCH-007-BACKGROUND-010
```

and may commit/push that feature branch under `docs/agent-vcs-ownership-policy.md`. It must not merge into main.

The Background `_index.md` and canonical parent frontier are intentionally omitted from this selective review overlay because B009 and B010 were completed/reviewed from overlapping pre-branch working-tree snapshots. Regenerate shared state from the live workspace after the task overlays are applied.
