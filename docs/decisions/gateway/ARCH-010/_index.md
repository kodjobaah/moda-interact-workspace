# ARCH-010 Gateway Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_gateway`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Superseded tasks are retained as history and must not be executed. System-test tasks are terminal/manual-gated.

Current counts: `complete` 1

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `GATEWAY-001` | Wire Redis into deployed billing workers | Complete | ARCH-002-GATEWAY-001 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority.
