# ARCH-061 shopify tasks

Architecture: ../../../architecture/ARCH-061-shopify-offline-token-refresh-coordination.md

| Task | Status | Dependencies |
|---|---|---|
| ARCH-061-SHOPIFY-001 | Complete; Attempt 2 | ARCH-061-SHARED-002 |

SHOPIFY-001 is explicitly developer-completed; downstream consumer tasks are Ready and unclaimed. Historical definition notes below do not override current task YAML.

Revision 2 fixes exact Shared API/SQL/budgets, SDK wrapper/storage/transport integration, all-reader/writer inventories and task-specific assertions; no implementation or claim.

Selected-shop revision: consumer APIs take commerce.Shop ID; trusted stored integration/session supplies refresh host and actual session ID. Existing SDK domain rules retained; no new domain regex or alias remapping.
