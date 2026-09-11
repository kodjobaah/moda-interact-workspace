# ARCH-007 Admin Tasks

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_admin`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ADMIN-001 | Build SUPER_ADMIN billing plan catalog and Shopify-handle mapping | Complete | SHARED-002, DATABASE-003 |
| ADMIN-002 | Build platform safety, shop overrides and Free allowance adjustment administration | Complete | ADMIN-001 |
| ADMIN-003 | Build billing overview, tenant detail and Shopify reconciliation visibility | **Ready** | ADMIN-002, BACKGROUND-007, SHOPIFY-001, BACKGROUND-008 |
| ADMIN-004 | Add controlled billing-event retry and compensating correction operations | Pending | ADMIN-003, BACKGROUND-008 |
| ADMIN-005 | Add recovery-credit pack fields to billing plan catalog | **Ready** | ADMIN-001, DATABASE-005, SHARED-006 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

ARCH-007 rollout is pre-production/breaking: normal Prisma migration artifacts are required for database schema changes, but production-preservation backfills, dual reads and compatibility adapters are not required. The current architect-accepted/published Shared release is `@modainteract/moda-interact-shared@0.8.0`. Repository agents execute exactly one task per invocation, commit/push both mirrored `task/<TASK_ID>` branches, return it to `review`, and STOP. Developer/user owns merges into `main`, pushes/updates of `main`, and final submodule-pointer integration after architect acceptance.

`ARCH-007-ADMIN-001` Attempt 2 and `ADMIN-002` Attempt 2 are architect-accepted Complete. `ADMIN-005` remains Ready because ADMIN-001, DATABASE-005 and SHARED-006 are Complete. `ADMIN-003` is now Ready because ADMIN-002, BACKGROUND-007, SHOPIFY-001 and BACKGROUND-008 are Complete. `ADMIN-004` remains Pending behind ADMIN-003.
