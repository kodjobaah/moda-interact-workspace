# ARCH-010 System Test Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_system_test`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Superseded tasks are retained as history and must not be executed. System-test tasks are terminal/manual-gated.

Current counts: `pending` 5

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `SYSTEM-TEST-001` | Validate core subscription, capacity, top-up and billing-period lifecycle | Pending | ARCH-010-GATEWAY-001, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-009, ARCH-010-BACKGROUND-010, ARCH-010-BACKGROUND-019, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-020 |
| `SYSTEM-TEST-002` | Validate uninstall, reinstall, cancellation and freeze execution gates | Pending | ARCH-010-BACKGROUND-006, ARCH-010-BACKGROUND-012, ARCH-010-BACKGROUND-013, ARCH-010-BACKGROUND-018, ARCH-010-SHOPIFY-006, ARCH-010-SHOPIFY-016 |
| `SYSTEM-TEST-003` | Validate partial top-up refunds and opt-in promotional campaigns | Pending | ARCH-010-BACKGROUND-014, ARCH-010-BACKGROUND-019, ARCH-010-ADMIN-003, ARCH-010-ADMIN-005, ARCH-010-ADMIN-006, ARCH-010-SHOPIFY-017, ARCH-010-SHOPIFY-020, ARCH-010-SHOPIFY-021, ARCH-010-SHOPIFY-022 |
| `SYSTEM-TEST-004` | Final ARCH-010 merchant lifecycle acceptance matrix | Pending | ARCH-010-SYSTEM-TEST-001, ARCH-010-SYSTEM-TEST-002, ARCH-010-SYSTEM-TEST-003, ARCH-010-SYSTEM-TEST-005 |
| `SYSTEM-TEST-005` | Validate Admin upgrade economics guardrail end to end | Pending | ARCH-010-DATABASE-013, ARCH-010-ADMIN-009 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority. System-test tasks are terminal/manual-gated and are not auto-started.
