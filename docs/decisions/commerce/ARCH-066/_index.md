# ARCH-066 commerce tasks

Architecture: [decisions](../../../architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md). Normative amendments: [consumer contract](../../../architecture/ARCH-066-consumer-contract.md), [outreach contract](../../../architecture/ARCH-066-initial-outreach-contract.md).

| Task | Status | Dependencies |
|---|---|---|
| [ARCH-066-COMMERCE-001](COMMERCE-001-preview-verified-product-details-and-final-whatsapp-message.md) | Complete, Attempt3 | ARCH-066-SHARED-010, ARCH-066-MCP-001 |

2026-11-08: SHARED-003 and MCP-001 Complete; COMMERCE-001 Ready/unclaimed, no automatic execution.

2026-11-08: SHARED-005 explicitly Complete at accepted Attempt1 (verified5.7.0). BACKGROUND-001 and COMMERCE-001 Ready/Attempt0/unclaimed; later consumers and system tests retain remaining dependency/manual gates. No task started.

## Shared correction frontier — 2026-11-08
SHARED009 Complete at accepted source16e3b35; SHARED010 Complete at release5.8.0 (exact integrity in release task), acceptance66c531568. Commerce001 in_progress Attempt2, durable claim889a118de6fd4436e66ff7454566e5eddc34eadb. Completion remains developer; other task histories/manual system gates unchanged.

### Attempt2 publication result
Commerce001 Blocked: implementation4c17318/reporta8ed45ff6 pushed;145 local tests/typecheck/scoped lint pass. Verified TEST deployment configuration/actor and immutable sync/idempotence receipts outstanding. Shared009/010 remain Complete. No consumer completion or downstream promotion.

### Accepted Commerce Attempt3 frontier — 2026-11-08
Commerce001 implementation4723e6f/reportde12408f5 accepted after actual standalone TEST immutable upgrade/default-profile/descriptor/idempotence proof. Task remains Review for explicit developer completion (completion_mode developer), not Complete. Shared009/010 remain Complete; no dependant promoted, protected-main merge, live activation or terminal system-test execution. Prior blocked/in-progress entries above are historical.

### Explicit developer completion frontier — 2026-11-08
COMMERCE001 Complete at accepted Attempt3 by explicit developer decision; Shared009/010 and BACKGROUND001 Complete. BACKGROUND002 remains Ready; COMMERCE002 remains Pending until BACKGROUND002 Complete. SYSTEM-TEST001 becomes dependency-ready/Ready but remains manual-gated and unclaimed; SYSTEM-TEST002 remains Pending. No implementation, live activation, main integration or system-test execution started. Earlier Review/blocked frontier records are historical.

| [ARCH-066-COMMERCE-002](COMMERCE-002-test-checkout-outreach-with-live-products.md) | Blocked, Attempt1; missing public sender identity/live composition | ARCH-066-SHARED-005, ARCH-066-COMMERCE-001, ARCH-066-BACKGROUND-002, ARCH-066-SHARED-012 |
