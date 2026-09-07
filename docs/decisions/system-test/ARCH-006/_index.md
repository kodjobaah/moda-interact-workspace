# ARCH-006 System Test Tasks

Architecture: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Assigned Agent: `moda_system_test`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SYSTEM-TEST-001 | Verify inbox, ownership, language and read semantics | Pending | ADMIN-004, SHOPIFY-003, GATEWAY-001 |
| SYSTEM-TEST-002 | Verify subscription-ended notification | Pending | SHOPIFY-002, SHOPIFY-003, GATEWAY-001 |
| SYSTEM-TEST-003 | Verify Batch idempotency and self-healing | Pending | BACKGROUND-007, GATEWAY-001, ADMIN-001, SHOPIFY-001 |

The individual task file YAML metadata is authoritative. This index is a navigation/planning aid and must be corrected if it drifts.

## Manual invocation gate

These are terminal validation tasks. They do not block any implementation, publication, infrastructure or other non-system-test task. Even after dependencies are Complete, do not invoke `moda_system_test` until the developer has manually reviewed the completed ARCH-006 implementation and explicitly authorises system-test execution. A task becoming eligible/Ready does not mean it should be auto-claimed.
