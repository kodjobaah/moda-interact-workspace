# ARCH-061 system-test tasks

Architecture: ../../../architecture/ARCH-061-shopify-offline-token-refresh-coordination.md

| Task | Status | Dependencies |
|---|---|---|
| ARCH-061-SYSTEM-TEST-001 | Pending | ARCH-061-SHARED-002, ARCH-061-SHOPIFY-001, ARCH-061-BACKGROUND-001, ARCH-061-COMMERCE-001, ARCH-061-MCP-001 |

Developer definitions only; no execution claims.

Revision 2 fixes exact Shared API/SQL/budgets, SDK wrapper/storage/transport integration, all-reader/writer inventories and task-specific assertions; no implementation or claim.

Selected-shop revision: consumer APIs take commerce.Shop ID; trusted stored integration/session supplies refresh host and actual session ID. Existing SDK domain rules retained; no new domain regex or alias remapping.

## Dependency Frontier — 6 November 2026

MCP-001 is now explicitly developer-completed (Attempt 1, review `7f61bde93`,
source `c9ca303`). SYSTEM-TEST-001 remains Pending because BACKGROUND-001 and
COMMERCE-001 are Ready, not Complete. No claim, execution or cutover begins;
terminal/manual gates remain in force.
