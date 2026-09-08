# ARCH-007 Database Tasks

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_database`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| DATABASE-001 | Replace billing plan and subscription catalog with the typed ARCH-007 target schema | Complete | — |
| DATABASE-002 | Add concurrency-safe usage reservation, counters and Shopify reporting ledger | Complete | DATABASE-001 |
| DATABASE-003 | Add platform/shop billing policy, allowance adjustment and audit persistence | Complete | DATABASE-002 |
| DATABASE-004 | Add durable standalone WhatsApp conversation ownership and active-scope identity | Complete | DATABASE-003 |
| DATABASE-005 | Add repeatable prepaid recovery-credit pack persistence | Complete | DATABASE-004 |
| DATABASE-006 | Add durable conversation-turn settling and processing state | Complete | DATABASE-005 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

DATABASE-004 Attempt 1, DATABASE-005 Attempt 2, and DATABASE-006 Attempt 1 are architect-accepted Complete. No further ARCH-007 database implementation task is currently Ready.