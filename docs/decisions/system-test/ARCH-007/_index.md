# ARCH-007 System Test Tasks

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_system_test`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SYSTEM-TEST-001 | Validate Free lifetime entitlement, concurrency and merchant upgrade flow | Pending / manual-gated | SHOPIFY-002, BACKGROUND-003, ADMIN-002 |
| SYSTEM-TEST-002 | Validate paid Shopify App Events, retries, overage and pending downgrade | Pending / manual-gated | SHOPIFY-002, BACKGROUND-008, ADMIN-004, GATEWAY-001 |
| SYSTEM-TEST-003 | Validate outbound safety controls, provider lifecycle, uninstall drain and operational recovery | Pending / manual-gated | SHOPIFY-003, MESSAGING-001, BACKGROUND-005, BACKGROUND-008, ADMIN-004, GATEWAY-001 |
| SYSTEM-TEST-004 | Validate repeatable recovery-credit packs across Free and paid plans | Pending / manual-gated | SHOPIFY-004, BACKGROUND-009, BACKGROUND-008, ADMIN-005 |
| SYSTEM-TEST-005 | Validate fragmented WhatsApp coalescing, inbound abuse admission and conversation safety | Pending / manual-gated | BACKGROUND-010, BACKGROUND-004, BACKGROUND-011 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.
These are terminal/manual-gated validation tasks. No implementation/publication/infrastructure task may depend on them. Do not invoke merely because a task becomes Ready; wait for explicit developer invocation after manual validation.


ARCH-007 rollout is pre-production/breaking: no ARCH-007 data migrations/backfills are required. Repository agents execute exactly one task per invocation, commit/push both mirrored `task/<TASK_ID>` branches, return it to `review`, and STOP. Developer/user owns merges into `main`, pushes/updates of `main`, and final submodule-pointer integration after architect acceptance.
