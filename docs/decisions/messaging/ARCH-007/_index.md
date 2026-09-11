# ARCH-007 Messaging Tasks

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_messaging`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| MESSAGING-001 | Publish canonical WhatsApp provider-status events for billing/accounting consumers | Complete | SHARED-002, SHARED-004 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

ARCH-007 rollout is pre-production/breaking: normal Prisma migration artifacts are required for database schema changes, but production-preservation backfills, dual reads and compatibility adapters are not required. The current architect-accepted/published Shared release is `@modainteract/moda-interact-shared@0.8.0`; MESSAGING-001 was accepted against provider-status release 0.7.4. Repository agents execute exactly one task per invocation, commit/push both mirrored `task/<TASK_ID>` branches, return it to `review`, and STOP. Developer/user owns merges into `main`, pushes/updates of `main`, and final submodule-pointer integration after architect acceptance.

`ARCH-007-MESSAGING-001` Attempt 3 is architect-accepted Complete.
