# ARCH-028 Database tasks

Architecture: [`ARCH-028`](../../../architecture/ARCH-028-whatsapp-delivery-failure-convergence.md).

Assigned agent: `moda_database`.

Repository: `moda-interact-database`.

Coordinator: `moda_architect`.

The ARCH-028 database stream begins with one additive durable-state task. It records bounded outbound WhatsApp provider-failure evidence and tenant-scoped recipient reachability evidence with finite suppression windows. Recovery-usage compensation is deliberately not included in DATABASE-001 because the current billing schema already has `UsageEvent.correctionOfUsageEventId`; later Background design must first prove whether another database change is actually required.

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| DATABASE-001 | Persist WhatsApp delivery-failure and recipient reachability evidence | Ready | - |

The individual task file is authoritative for task state.
