# ARCH-010 — Database

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-DATABASE-001 | Complete | Add nullable `Subscription.nextReconcileAt` plus index so pending subscription verification can be rebuilt after Redis loss. |
| ARCH-010-DATABASE-002 | Complete | Add period-scoped included-credit counter and dual UsageReservation linkage for concurrency-safe paid allowance consumption. |
| ARCH-010-DATABASE-003 | Complete | Add nullable `Shop.reinstallPendingAt` plus index so an authenticated reinstall can remain execution-disabled until subscription reconciliation completes. |
| ARCH-010-DATABASE-004 | Complete | Add Subscription-owned Free/Paid Shopify BillingPeriod history, plan snapshots, Paid-only allowance snapshots, close metadata, reservation release reason, legacy OPEN-period normalization and one-OPEN-period integrity. |
| ARCH-010-DATABASE-005 | Complete | Persist the durable reason/timestamp when a DETECTED recovery is blocked because all recovery-capacity sources are exhausted. |
| ARCH-010-DATABASE-006 | Complete | Move the one-time lifetime Free grant default to platform policy and snapshot/backfill the shop-level `FREE_RECOVERY_LIFETIME` grant independently of current plan. |
| ARCH-010-DATABASE-007 | Complete | Add deterministic purchased-credit lot accounting, reservation ownership and multi-partial-refund durability/backfill. |
| ARCH-010-DATABASE-008 | Complete | Add FROZEN subscription projection plus latest Shopify subscription-lifecycle event state/id/time without changing existing entitlements. |
| ARCH-010-DATABASE-009 | Complete | Add a dedicated promotional-credit counter, positive audited grant-provenance ledger and idempotency key without granting/migrating any existing shop. |

`DATABASE-002` depends on DATABASE-001 and the accepted ARCH-007 repeatable-credit schema. `DATABASE-003` also follows DATABASE-001 because reinstall scheduling reuses `Subscription.nextReconcileAt`. `DATABASE-004` depends on DATABASE-002 and normalizes legacy multiple-OPEN periods before adding the one-OPEN-period invariant. `DATABASE-006` is independent of period accounting and must land before runtime tasks begin treating the five lifetime credits as plan-independent.
`DATABASE-007` is the durability prerequisite for partial purchased-top-up refunds. It does not depend on frozen ARCH-009 refund tasks and must fail rather than guess if existing aggregate purchased balances cannot be reconstructed into deterministic lots.


`DATABASE-008` is the durability prerequisite for Shopify freeze/unfreeze. It adds state vocabulary/evidence only; it never infers frozen status during migration.

`DATABASE-009` introduces the distinct non-refundable promotional bucket. It never reclassifies historical Free allowance adjustments and creates no balances during migration.
