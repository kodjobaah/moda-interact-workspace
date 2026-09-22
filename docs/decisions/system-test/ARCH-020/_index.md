# ARCH-020 system-test tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_system_test. Repository: moda-interact-system-test. Coordinator: moda_architect.

Definitions are on local main for review by explicit developer request. Individual task YAML is authoritative; no task is claimed or launched. Commerce submodule provisioning remains a prerequisite; the owner and route are defined in this packet.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-SYSTEM-TEST-001](SYSTEM-TEST-001-validate-merchant-configured-mcp-conversations-end-to-end.md) | Validate merchant-configured MCP conversations end to end | pending | ARCH-020-COMMERCE-012, ARCH-020-BACKGROUND-001, ARCH-020-BACKGROUND-002, ARCH-020-COMMERCE-001, ARCH-020-COMMERCE-002, ARCH-020-COMMERCE-003, ARCH-020-COMMERCE-004, ARCH-020-COMMERCE-005, ARCH-020-COMMERCE-006, ARCH-020-COMMERCE-007, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-009, ARCH-020-COMMERCE-010, ARCH-020-COMMERCE-011, ARCH-020-DATABASE-001, ARCH-020-GATEWAY-001, ARCH-020-SHARED-001, ARCH-020-SHOPIFY-001, ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-014, ARCH-020-COMMERCE-015, ARCH-020-COMMERCE-016, ARCH-020-COMMERCE-017, ARCH-020-COMMERCE-018, ARCH-020-COMMERCE-019 |
| [ARCH-020-SYSTEM-TEST-002](SYSTEM-TEST-002-validate-external-api-tools-end-to-end.md) | Validate external API tools end to end | pending | ARCH-020-COMMERCE-024, ARCH-020-GATEWAY-003, ARCH-020-BACKGROUND-002 |


## GATEWAY-002 supersession dependency reconciliation — 2026-09-22

GATEWAY-002 is no longer an implementation prerequisite for SYSTEM-TEST-001.
SYSTEM-TEST-001 remains Pending behind COMMERCE-012, SYSTEM-TEST-002 and its other
implementation dependencies. Manual Grafana dashboard/alert creation is not a system
test dependency.
