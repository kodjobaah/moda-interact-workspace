# ARCH-028 Database Tasks

Architecture: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Assigned Agent: `moda_database`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| DATABASE-001 | Persist message failure, reachability, suppression policy and admission block state | Ready | - |
| DATABASE-002 | Persist committed recovery compensation lineage/disposition | Pending | DATABASE-001 |

## Current frontier

`ARCH-028-DATABASE-001` is Ready and independent of Shared work. DATABASE-002 and DATABASE-003 wait only for DATABASE-001. DATABASE-003 is intentionally separate so BACKGROUND-001 can consume DATABASE-001 before recovery attempt creation is updated.

## Boundary

Database owns strict pre-production persistence/integrity only. It does not classify provider codes, perform compensation, suppress recovery sends, render Admin UI or notify merchants.
