# ARCH-010 Gateway Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_gateway`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Complete/Review task files are immutable accepted/in-flight evidence; their historical `enables:` fields are not rewritten when later correction tasks are added.

Current counts: `complete` 1

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `GATEWAY-001` | Wire Redis into deployed billing workers | Complete | ARCH-002-GATEWAY-001 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority. System-test tasks are terminal/manual-gated and are not auto-started.
