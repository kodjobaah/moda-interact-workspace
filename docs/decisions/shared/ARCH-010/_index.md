# ARCH-010 Shared Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_shared`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Superseded tasks are retained as history and must not be executed. System-test tasks are terminal/manual-gated.

Current counts: `complete` 8

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `SHARED-001` | Define subscription reconciliation BullMQ contract | Complete | ARCH-007-SHARED-006 |
| `SHARED-002` | Publish subscription reconciliation Shared contract | Complete | ARCH-010-SHARED-001 |
| `SHARED-003` | Add generic recovery-capacity-exhausted billing system code | Complete | ARCH-010-SHARED-001 |
| `SHARED-004` | Publish recovery-capacity-exhausted Shared contract | Complete | ARCH-010-SHARED-003 |
| `SHARED-005` | Add merchant top-up refund billing message contracts | Complete | — |
| `SHARED-006` | Publish top-up refund Shared message contracts | Complete | ARCH-010-SHARED-005 |
| `SHARED-007` | Remove superseded pre-production billing compatibility contracts | Complete | ARCH-010-SHARED-006, ARCH-010-BACKGROUND-020, ARCH-010-SHOPIFY-024 |
| `SHARED-008` | Publish the clean first-production Shared billing contract | Complete | ARCH-010-SHARED-007 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority.
