# ARCH-061 shared tasks

Architecture: ../../../architecture/ARCH-061-shopify-offline-token-refresh-coordination.md

| Task | Status | Dependencies |
|---|---|---|
| ARCH-061-SHARED-001 | Complete | - |
| ARCH-061-SHARED-002 | Complete | ARCH-061-SHARED-001 |

ARCH-061-SHARED-001 Attempt 2 is complete after Accepted review; ARCH-061-SHARED-002 Attempt 1 publication is Complete after Accepted review; ARCH-061-SHOPIFY-001 is Ready.

Revision 2 fixes exact Shared API/SQL/budgets, SDK wrapper/storage/transport integration, all-reader/writer inventories and task-specific assertions; no implementation or claim.

Selected-shop revision: consumer APIs take commerce.Shop ID; trusted stored integration/session supplies refresh host and actual session ID. Existing SDK domain rules retained; no new domain regex or alias remapping.

Completion frontier — 2026-11-06: all ARCH-061 implementation prerequisites are Complete. SYSTEM-TEST-001 is dependency-ready and remains manually gated; no execution or rollout is implied.
