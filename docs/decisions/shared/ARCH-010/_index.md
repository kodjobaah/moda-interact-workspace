# ARCH-010 — Shared

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-SHARED-001 | Ready | Define the canonical BullMQ subscription-reconciliation queue/job payload/deterministic job ID and App Pricing billing-period drain constant. |
| ARCH-010-SHARED-002 | Pending | Publish the accepted Shared reconciliation contract for Shopify/Background consumers. |
| ARCH-010-SHARED-003 | Pending | Add the canonical recovery-capacity-exhausted merchant system-message code/source-key contract. |
| ARCH-010-SHARED-004 | Pending | Publish the accepted recovery-capacity-exhausted Shared contract for consumers. |
| ARCH-010-SHARED-005 | Ready | Add canonical merchant billing system-message codes for top-up refund request/completion/rejection. |
| ARCH-010-SHARED-006 | Pending | Publish the accepted top-up refund Shared message contract for Admin/Shopify consumers. |

ARCH-010 uses one five-minute `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` for cycle-bound App Event safety across both Free and Paid plans; Free lifetime recovery admission is not itself period-scoped.
`SHARED-005/006` own only merchant refund message codes/publication. They do not define provider monetary/refund APIs or a refund queue.

