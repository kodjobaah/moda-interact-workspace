# ARCH-010 Admin Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_admin`

Coordinator:

`moda_architect`

> Synchronized 2026-09-13 from individual task YAML. Individual task files are authoritative. Superseded tasks are retained as history and must not be executed. System-test tasks are terminal/manual-gated.

Current counts: `complete` 8, `ready` 1, `pending` 1

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `ADMIN-001` | Move lifetime Free grant configuration from plan catalogue to platform billing controls | Complete | ARCH-010-DATABASE-006 |
| `ADMIN-002` | Review merchant recovery-credit purchase refund requests | **Ready** | ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-022, ARCH-010-SHOPIFY-025, ARCH-010-SHARED-008, ARCH-010-ADMIN-010 |
| `ADMIN-003` | Lock and settle withdrawn recovery-credit purchases through Shopify Partner Dashboard | Pending | ARCH-010-ADMIN-002, ARCH-010-BACKGROUND-022, ARCH-010-SHARED-008, ARCH-010-DATABASE-014, ARCH-010-BACKGROUND-021 |
| `ADMIN-004` | Create and activate GLOBAL, PLAN and SHOP promotion campaigns | Complete | ARCH-010-DATABASE-013, ARCH-010-ADMIN-010 |
| `ADMIN-005` | Manage promotion catalogue, close campaigns and reopen by expiry only | Complete | ARCH-010-ADMIN-004 |
| `ADMIN-006` | Report campaign merchant selection and promotional-credit usage | Complete | ARCH-010-ADMIN-005, ARCH-010-DATABASE-013 |
| `ADMIN-007` | Implement the supplied upgrade economics guardrail as a deterministic pure evaluator | Complete | — |
| `ADMIN-008` | Manage verified Shopify economics evidence, upgrade edges and guardrail policy | Complete | ARCH-010-DATABASE-013, ARCH-010-ADMIN-001, ARCH-010-ADMIN-010 |
| `ADMIN-009` | Hard-enforce upgrade economics on plan and recovery-pack configuration | Complete | ARCH-010-ADMIN-007, ARCH-010-ADMIN-008 |
| `ADMIN-010` | Conform Admin billing controls to the clean first-production baseline | Complete | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-ADMIN-001 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority.
