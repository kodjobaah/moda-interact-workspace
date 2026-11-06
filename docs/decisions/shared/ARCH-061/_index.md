# ARCH-061 shared tasks

Architecture: ../../../architecture/ARCH-061-shopify-offline-token-refresh-coordination.md

| Task | Status | Dependencies |
|---|---|---|
| ARCH-061-SHARED-001 | Complete | - |
| ARCH-061-SHARED-002 | Ready | ARCH-061-SHARED-001 |

ARCH-061-SHARED-001 Attempt 2 is complete after Accepted review; ARCH-061-SHARED-002 is dependency-ready.

Revision 2 fixes exact Shared API/SQL/budgets, SDK wrapper/storage/transport integration, all-reader/writer inventories and task-specific assertions; no implementation or claim.

Selected-shop revision: consumer APIs take commerce.Shop ID; trusted stored integration/session supplies refresh host and actual session ID. Existing SDK domain rules retained; no new domain regex or alias remapping.
