# ARCH-028 Database tasks

Architecture: [`ARCH-028`](../../../architecture/ARCH-028-whatsapp-delivery-failure-convergence.md).

Assigned agent: `moda_database`.

Repository: `moda-interact-database`.

Coordinator: `moda_architect`.

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| DATABASE-001 | Persist WhatsApp delivery-failure and canonical recipient reachability evidence | Ready | - |
| DATABASE-002 | Persist generic recovery usage-compensation lineage/disposition | Pending | DATABASE-001 |

DATABASE-002 deliberately contains no purchased/refund-cancellation provenance. It enables BACKGROUND-004 compensation directly.
