# ARCH-010 Admin Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_admin`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Complete/Review task files are immutable accepted/in-flight evidence; their historical `enables:` fields are not rewritten when later correction tasks are added.

Current counts: `complete` 1, `pending` 8, `ready` 1

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `ADMIN-001` | Move lifetime Free grant configuration from plan catalogue to platform billing controls | Complete | ARCH-010-DATABASE-006 |
| `ADMIN-002` | Triage merchant support into exact partial top-up refund requests | Pending | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-ADMIN-010 |
| `ADMIN-003` | Approve, hold and settle partial top-up refunds through Shopify Partner Dashboard | Pending | ARCH-010-ADMIN-002, ARCH-010-BACKGROUND-014, ARCH-010-SHARED-008 |
| `ADMIN-004` | Create and activate GLOBAL, PLAN and SHOP promotion campaigns | Pending | ARCH-010-DATABASE-013, ARCH-010-ADMIN-010 |
| `ADMIN-005` | Manage promotion catalogue, close campaigns and reopen by expiry only | Pending | ARCH-010-ADMIN-004 |
| `ADMIN-006` | Report campaign merchant selection and promotional-credit usage | Pending | ARCH-010-ADMIN-005, ARCH-010-DATABASE-013 |
| `ADMIN-007` | Implement the supplied upgrade economics guardrail as a deterministic pure evaluator | **Ready** | — |
| `ADMIN-008` | Manage verified Shopify economics evidence, upgrade edges and guardrail policy | Pending | ARCH-010-DATABASE-013, ARCH-010-ADMIN-001, ARCH-010-ADMIN-010 |
| `ADMIN-009` | Hard-enforce upgrade economics on plan and recovery-pack configuration | Pending | ARCH-010-ADMIN-007, ARCH-010-ADMIN-008 |
| `ADMIN-010` | Conform Admin billing controls to the clean first-production baseline | Pending | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-ADMIN-001 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority. System-test tasks are terminal/manual-gated and are not auto-started.
