# ARCH-001 Background Tasks

Architecture:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Assigned Agent:

moda_background

Coordinator:

moda_architect

| Task | Description | Status | Dependencies |
|---|---|---|---|
| BACKGROUND-001 | Adopt canonical Shopify webhook contracts | Complete | SHARED-001 |
| BACKGROUND-002 | Manage pending recovery candidates | Complete | BACKGROUND-001 |
| BACKGROUND-003 | Implement bounded Shopify abandoned checkout lookup | Complete | BACKGROUND-001 |
| BACKGROUND-004 | Materialize matured recovery candidates | Complete | BACKGROUND-002, BACKGROUND-003 |
| BACKGROUND-005 | Handle order recovery correlation and cancellation | Complete | BACKGROUND-004 |
| BACKGROUND-006 | Refresh existing recovery on checkout update | Complete | BACKGROUND-003 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task file is authoritative for task state.
