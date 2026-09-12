# ARCH-010 Database Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_database`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Superseded tasks are retained as history and must not be executed. System-test tasks are terminal/manual-gated.

Current counts: `complete` 12, `superseded` 1

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `DATABASE-001` | Add durable subscription reconciliation scheduling state | Complete | ARCH-007-DATABASE-006, ARCH-009-DATABASE-001 |
| `DATABASE-002` | Add period-scoped paid included-credit reservation state | Complete | ARCH-010-DATABASE-001, ARCH-007-DATABASE-005 |
| `DATABASE-003` | Persist authenticated reinstall reconciliation state | Complete | ARCH-010-DATABASE-001 |
| `DATABASE-004` | Strengthen recurring App Pricing BillingPeriod ownership and close/open lifecycle integrity | Complete | ARCH-010-DATABASE-002 |
| `DATABASE-005` | Persist recovery-capacity blocks on detected recoveries | Complete | — |
| `DATABASE-006` | Move the one-time lifetime Free recovery grant to platform policy and snapshot it per shop | Complete | ARCH-007-DATABASE-002, ARCH-007-DATABASE-003 |
| `DATABASE-007` | Add purchased-credit lot accounting and multi-partial-refund durability | Complete | — |
| `DATABASE-008` | Persist Shopify subscription freeze projection and lifecycle evidence | Complete | — |
| `DATABASE-009` | Add durable promotional recovery-credit grants and aggregate entitlement counter | Complete | ARCH-007-DATABASE-002 |
| `DATABASE-010` | Persist opt-in promotional campaigns, targeting and lifecycle audit | Complete | ARCH-010-DATABASE-009 |
| `DATABASE-011` | Persist merchant promotion selection and exact promotional grant-lot accounting | Complete | ARCH-010-DATABASE-009, ARCH-010-DATABASE-010 |
| `DATABASE-012` | Persist upgrade economics policy, plan edges and audited Shopify pricing snapshots | Superseded | ARCH-010-DATABASE-006 |
| `DATABASE-013` | Materialise the clean ARCH-010 first-production database baseline | Complete | ARCH-010-DATABASE-001, ARCH-010-DATABASE-002, ARCH-010-DATABASE-003, ARCH-010-DATABASE-004, ARCH-010-DATABASE-005, ARCH-010-DATABASE-006, ARCH-010-DATABASE-007, ARCH-010-DATABASE-008, ARCH-010-DATABASE-009, ARCH-010-DATABASE-010, ARCH-010-DATABASE-011 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority.
