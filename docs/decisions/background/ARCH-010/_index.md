# ARCH-010 — Background

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-BACKGROUND-001 | Pending | Add BullMQ pending-subscription reconciliation, retry scheduling, stale-job guards and PostgreSQL queue reconstruction to the existing billing worker; first verified Free activation creates the one-time lifetime Free grant. |
| ARCH-010-BACKGROUND-002 | Pending | Replace paid included-allowance aggregate routing with concurrency-safe current-period reservations and delegate included exhaustion into the canonical shop-level fallback chain without automatic overage. |
| ARCH-010-BACKGROUND-003 | Pending | Extend subscription reconciliation to complete first paid activation, create the first paid BillingPeriod/included counter, and create the one-time lifetime Free grant when absent. |
| ARCH-010-BACKGROUND-004 | Ready | Gate queued Shopify/recovery work on current Shop.status so pre-uninstall jobs become terminal no-ops without breaking pre-uninstall accounting finalisation. |
| ARCH-010-BACKGROUND-005 | Ready | Stop inbound WhatsApp/conversation business execution after ownership resolves to an inactive shop while preserving historical provider-status bookkeeping. |
| ARCH-010-BACKGROUND-006 | Pending | Extend the canonical reconciliation worker with the narrow authenticated-reinstall exception, durable retry/rebuild, safe null/Free/same-paid-period restoration, and delegation of same-plan cycle advance to BACKGROUND-007. |
| ARCH-010-BACKGROUND-007 | Pending | Implement canonical same-plan Free/Paid Shopify billing-cycle pre-close/rollover; Paid replenishes period included entitlement, Free rotates App-Event billing scope only, and neither resets lifetime Free credits. |
| ARCH-010-BACKGROUND-008 | Pending | Make paid recovery initiation boundary-safe with the drain window, pre-provider revalidation, period-specific source identity and bounded WhatsApp sends. |
| ARCH-010-BACKGROUND-009 | Pending | Persist full capacity exhaustion, notify once per exhaustion epoch and resume blocked recoveries after any higher-priority capacity source becomes available. |
| ARCH-010-BACKGROUND-010 | Pending | Apply Shopify-authoritative paid/free plan changes at the proven effective boundary while preserving promotional, purchased and lifetime Free balances. |
| ARCH-010-BACKGROUND-011 | Ready | Make lifetime Free recovery capacity plan-independent and provide the final fallback after promotional/purchased capacity is exhausted. |
| ARCH-010-BACKGROUND-012 | Pending | Reconcile Shopify-scheduled/effective full cancellation, close the final provider BillingPeriod and transition the installed merchant to NO_CONTRACT without touching lifetime balances. |
| ARCH-010-BACKGROUND-013 | Pending | Extend shop execution gates so NO_CONTRACT stops new recovery and WhatsApp/conversation business execution while preserving bounded historical bookkeeping. |
| ARCH-010-BACKGROUND-014 | Pending | Make purchased recovery reservations FIFO lot-aware and keep provider top-up activation reconciliation stable across partial/manual refund history. |
| ARCH-010-BACKGROUND-015 | Ready | Add one canonical Partner reconciliation snapshot containing live activeSubscription plus the latest bounded subscription lifecycle event. |
| ARCH-010-BACKGROUND-016 | Pending | Reconcile FROZEN/UNFROZEN, preserve entitlement state, retry hourly and catch up safely to Shopify current cycle on restoration. |
| ARCH-010-BACKGROUND-017 | Pending | Gate recovery, WhatsApp, CommerceAgent and new billable business work while Subscription is FROZEN. |
| ARCH-010-BACKGROUND-018 | Pending | Stop checkout/cart Shopify event processing at the high-volume Background boundary while FROZEN, while retaining only bounded order-completion terminal safety bookkeeping. |
| ARCH-010-BACKGROUND-019 | Pending | Add promotional-credit reservation/commit/release and make the final order Paid included -> promotional -> purchased -> lifetime Free / Free promotional -> purchased -> lifetime Free. |

Dependency notes:

- `BACKGROUND-011` depends on DATABASE-006 and the accepted ARCH-007 lifetime/purchased reservation foundations.
- `BACKGROUND-002` establishes the included-first Paid reservation boundary; `BACKGROUND-019` composes the final shop-level promotional insertion, producing `included -> promotional -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION`.
- `BACKGROUND-009` depends on both and therefore treats exhaustion as absence of every source in that order.
- `BACKGROUND-008` builds on BACKGROUND-002 plus the Shared drain constant.
- `BACKGROUND-007` depends on DATABASE-004 and BACKGROUND-008 and owns canonical same-plan Free/Paid provider-period rollover.
- `BACKGROUND-003` depends on BACKGROUND-007 so first paid activation schedules into an already-available rollover path.
- `BACKGROUND-006` delegates same-plan changed-cycle reinstall to BACKGROUND-007 instead of duplicating rollover.

- `BACKGROUND-012` owns Shopify-observed full cancellation; it never calls a cancellation mutation and reuses the existing subscription-reconciliation queue.
- `BACKGROUND-013` depends on BACKGROUND-012 plus the existing uninstall gates and makes NO_CONTRACT stronger than ordinary capacity exhaustion.
`BACKGROUND-014` depends on DATABASE-007 and BACKGROUND-011 and owns FIFO selection inside the purchased bucket. `BACKGROUND-019` composes the final cross-bucket order: Paid included -> promotional -> purchased -> lifetime Free / Free promotional -> purchased -> lifetime Free.


Final provider-state rule: `activeSubscription=null` is not sufficient cancellation proof for an established merchant. `BACKGROUND-015` supplies lifecycle evidence; `BACKGROUND-016` owns FROZEN/UNFROZEN; `BACKGROUND-012` may finalize cancellation only with effective CANCELED evidence. `BACKGROUND-017` keeps frozen execution blocking distinct from NO_CONTRACT.
`BACKGROUND-018` depends on BACKGROUND-004 and BACKGROUND-016. It owns the early `checkout-events` / `order-events` FROZEN gate; BACKGROUND-017 remains the downstream business-execution gate. Raw Shopify webhook ingress remains unchanged.

Final capacity rule: `BACKGROUND-019` inserts promotional credits ahead of purchased credits and lifetime Free. `BACKGROUND-008`/`BACKGROUND-009` are amended to consume that final ordering. Promotional-funded recovery creates no Shopify normal-recovery meter event and never bypasses lifecycle execution gates.
