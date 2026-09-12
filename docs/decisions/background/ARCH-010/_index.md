# ARCH-010 Background Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_background`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Superseded tasks are retained as history and must not be executed. System-test tasks are terminal/manual-gated.

Current counts: `complete` 6, `ready` 2, `pending` 10, `superseded` 2

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `BACKGROUND-001` | Reconcile pending subscription activation with durable BullMQ recovery | Complete | ARCH-010-DATABASE-006, ARCH-010-DATABASE-001, ARCH-010-DATABASE-004, ARCH-010-SHARED-002, ARCH-007-BACKGROUND-008 |
| `BACKGROUND-002` | Enforce concurrency-safe paid included-credit admission | **Complete** | ARCH-010-BACKGROUND-011, ARCH-010-DATABASE-013, ARCH-007-BACKGROUND-003, ARCH-007-BACKGROUND-009 |
| `BACKGROUND-003` | Reconcile first paid activation and create the first paid period | Pending | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-001, ARCH-010-BACKGROUND-007, ARCH-010-SHARED-008, ARCH-007-BACKGROUND-008 |
| `BACKGROUND-004` | Stop queued recovery work for inactive shops | Complete | — |
| `BACKGROUND-005` | Stop WhatsApp business execution for inactive shops | Complete | — |
| `BACKGROUND-006` | Reconcile reinstalled shops before business execution resumes | Pending | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-001, ARCH-010-BACKGROUND-003, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005 |
| `BACKGROUND-007` | Implement canonical same-plan App Pricing BillingPeriod rollover for Paid and Free | Pending | ARCH-010-BACKGROUND-001, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-008, ARCH-010-BACKGROUND-009, ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-008-BACKGROUND-001 |
| `BACKGROUND-008` | Make paid recovery initiation safe across the billing-cycle boundary | Pending | ARCH-010-BACKGROUND-002, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-019 |
| `BACKGROUND-009` | Persist recovery exhaustion and resume blocked recoveries when capacity returns | Pending | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-011, ARCH-007-BACKGROUND-003, ARCH-007-BACKGROUND-009, ARCH-010-BACKGROUND-019 |
| `BACKGROUND-010` | Apply Shopify-authoritative plan changes without resetting lifetime credit history | Pending | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-003, ARCH-010-BACKGROUND-007, ARCH-010-SHARED-008 |
| `BACKGROUND-011` | Make the lifetime Free recovery entitlement plan-independent and consume it after purchased credits | **Complete** | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-001, ARCH-007-BACKGROUND-003, ARCH-007-BACKGROUND-009 |
| `BACKGROUND-012` | Reconcile Shopify cancellation, freeze and unfreeze lifecycle state | Pending | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-009, ARCH-010-BACKGROUND-010, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-015 |
| `BACKGROUND-013` | Enforce NO_CONTRACT and FROZEN business-execution gates | Pending | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005, ARCH-010-BACKGROUND-012 |
| `BACKGROUND-014` | Make purchased recovery reservations FIFO lot-aware | **Ready** | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-011 |
| `BACKGROUND-015` | Read Shopify live subscription plus latest lifecycle event for reconciliation | **Ready** | — |
| `BACKGROUND-016` | Reconcile Shopify subscription freeze and unfreeze without losing entitlement history | Superseded | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-007, ARCH-010-BACKGROUND-010, ARCH-010-BACKGROUND-015, ARCH-010-SHARED-008 |
| `BACKGROUND-017` | Gate all shop business execution while the Shopify subscription is frozen | Superseded | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005, ARCH-010-BACKGROUND-013, ARCH-010-BACKGROUND-016 |
| `BACKGROUND-018` | Stop Shopify checkout/cart event processing early for frozen subscriptions | Pending | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-012 |
| `BACKGROUND-019` | Reserve selected promotional campaign credits before every other capacity source | Pending | ARCH-010-DATABASE-013, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-011, ARCH-010-BACKGROUND-014 |
| `BACKGROUND-020` | Remove pre-publication Background consumers of retired Shared billing contracts | Complete | ARCH-010-SHARED-006 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority.
