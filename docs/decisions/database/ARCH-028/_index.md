# ARCH-028 Database tasks

Architecture: [`ARCH-028`](../../../architecture/ARCH-028-whatsapp-delivery-failure-convergence.md).

Assigned agent: `moda_database`.

Repository: `moda-interact-database`.

Coordinator: `moda_architect`.

The ARCH-028 database stream has two additive durable-state tasks. DATABASE-001 records bounded outbound WhatsApp provider-failure evidence and tenant-scoped recipient reachability evidence with finite suppression windows. A later source review proved that generic `UsageEvent.correctionOfUsageEventId` is sufficient for correction lineage but not for reconstructing purchased-credit/refund provenance after a committed recovery, so DATABASE-002 adds only that missing compensation provenance.

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| DATABASE-001 | Persist WhatsApp delivery-failure and recipient reachability evidence | Ready | - |
| DATABASE-002 | Persist recovery usage-compensation provenance | Pending | DATABASE-001 |

The individual task file is authoritative for task state.

DATABASE-002 enables `ARCH-028-BACKGROUND-003`, which captures the purchase/refund provenance at the only point it is authoritative: the purchased reservation commit transaction.
