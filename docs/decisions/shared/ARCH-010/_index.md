# ARCH-010 — Shared

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-SHARED-001 | Complete | Define the canonical BullMQ subscription-reconciliation queue/job payload/deterministic job ID and App Pricing billing-period drain constant. |
| ARCH-010-SHARED-002 | Ready | Publish the accepted Shared reconciliation contract for Shopify/Background consumers. |
| ARCH-010-SHARED-003 | Ready | Add the canonical recovery-capacity-exhausted merchant system-message code/source-key contract. |
| ARCH-010-SHARED-004 | Pending | Publish the accepted recovery-capacity-exhausted Shared contract for consumers. Waits for SHARED-003 acceptance. |
| ARCH-010-SHARED-005 | Complete | Add canonical merchant billing system-message codes for top-up refund request/completion/rejection. |
| ARCH-010-SHARED-006 | Ready | Publish the accepted top-up refund Shared message contract for Admin/Shopify consumers. |

ARCH-010 uses one five-minute `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` for cycle-bound App Event safety across both Free and Paid plans; Free lifetime recovery admission is not itself period-scoped.
`SHARED-005/006` own only merchant refund message codes/publication. They do not define provider monetary/refund APIs or a refund queue.

## Current execution frontier

With `ARCH-010-SHARED-001` and `ARCH-010-SHARED-005` architect-accepted Complete:

```text
ARCH-010-SHARED-002  Ready
ARCH-010-SHARED-003  Ready
ARCH-010-SHARED-006  Ready
ARCH-010-SHARED-004  Pending -> Ready only after SHARED-003 is architect-accepted Complete
```

`SHARED-002` and `SHARED-006` are both publication tasks against the same Shared package release line. They are dependency-ready, but actual npm publication must not race. Follow each task's registry/version preflight and stop conditions and serialize package publication if both are being executed concurrently.

`SHARED-003` is implementation-only and may proceed independently in its canonical isolated task worktree. Its publication remains owned by `SHARED-004` after architect acceptance.
