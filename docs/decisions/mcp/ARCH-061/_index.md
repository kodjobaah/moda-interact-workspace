# ARCH-061 mcp tasks

Architecture: ../../../architecture/ARCH-061-shopify-offline-token-refresh-coordination.md

| Task | Status | Dependencies |
|---|---|---|
| ARCH-061-MCP-001 | Complete | ARCH-061-SHARED-002, ARCH-061-SHOPIFY-001 |

Developer definitions only; no execution claims.

Revision 2 fixes exact Shared API/SQL/budgets, SDK wrapper/storage/transport integration, all-reader/writer inventories and task-specific assertions; no implementation or claim.

Selected-shop revision: consumer APIs take commerce.Shop ID; trusted stored integration/session supplies refresh host and actual session ID. Existing SDK domain rules retained; no new domain regex or alias remapping.

## Completion — 6 November 2026

MCP-001 Attempt 1 is explicitly developer-completed after passing scoped review
`7f61bde93`, implementation `c9ca303`. Claim cleared; full-suite discount/fixture
failures remain documented under the accepted bounded scope disposition.
SYSTEM-TEST-001 remains Pending on Background and Commerce completion and its
manual execution gates. No deployment or main merge is authorized by completion.
