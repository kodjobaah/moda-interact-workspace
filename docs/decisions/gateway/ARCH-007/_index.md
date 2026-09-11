# ARCH-007 Gateway Tasks

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_gateway`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| GATEWAY-001 | Deploy independently scalable billing worker in Render blueprints | Complete | BACKGROUND-008 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

ARCH-007 rollout is pre-production/breaking: no ARCH-007 data migrations/backfills are required. Repository agents execute exactly one task per invocation, commit/push both mirrored `task/<TASK_ID>` branches, return it to `review`, and STOP. Developer/user owns merges into `main`, pushes/updates of `main`, and final submodule-pointer integration after architect acceptance.

`ARCH-007-GATEWAY-001` Attempt 1 is architect-accepted Complete. `ARCH-007-SYSTEM-TEST-002` and `ARCH-007-SYSTEM-TEST-003` remain Pending / manual-terminal-gated.
