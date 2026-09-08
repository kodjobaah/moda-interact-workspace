# ARCH-007 Gateway Tasks

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_gateway`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| GATEWAY-001 | Deploy independently scalable billing worker in Render blueprints | Pending | BACKGROUND-008 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

ARCH-007 rollout is pre-production/breaking: no ARCH-007 data migrations/backfills are required. Repository agents execute exactly one task per invocation, return it to `review`, and STOP. Developer/user owns git commit/push after architect acceptance.
