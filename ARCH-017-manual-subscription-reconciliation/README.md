# ARCH-017 manual subscription reconciliation tasks

This portable overlay defines two new tasks only. It does not overwrite existing ARCH-017 task files or parent architecture metadata.

Dependency order:

```text
ARCH-017-BACKGROUND-002
        ↓
ARCH-017-BACKGROUND-003
        ↓
ARCH-017-ADMIN-002
```

Design:

- Admin never reconciles Shopify itself.
- Admin schedules a request by setting `Subscription.nextReconcileAt = now` and writing an audit event.
- Background prioritizes due `nextReconcileAt` shops in the existing global provider reconciliation scan.
- The existing `getSubscriptionReconciliationSnapshot -> applySubscription` path remains authoritative for the outcome.
- UNMAPPED keeps its dedicated mapping-repair workflow.
- No schema change or new queue contract is required.
