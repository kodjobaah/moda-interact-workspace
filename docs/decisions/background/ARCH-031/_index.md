# ARCH-031 Background Tasks

Architecture:

`docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`

Assigned Agent:

`moda_background`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| BACKGROUND-001 | Execute durable Merchant Pricing translation runs | Complete | DATABASE-001 |
| BACKGROUND-002 | Automatically finalize translation publication | Complete | BACKGROUND-001, DATABASE-002, ADMIN-003 |

The individual task file is authoritative for task state. This index was created during final ARCH-031 implementation reconciliation on 2026-10-11 after the session-specific deferment on `_index.md` updates was lifted.
