# ARCH-021 System-Test Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_system_test`

Coordinator:

`moda_architect`

## Pre-Phase-3 simplification checkpoint

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SYSTEM-TEST-001](SYSTEM-TEST-001-validate-simplified-studio-and-private-mcp.md) | Validate reduced configuration, dynamic Storefront schema authoring, unified authorization and context-only private MCP | Pending | DATABASE-002, COMMERCE-025..030, COMMERCE-032..034, BACKGROUND-001, GATEWAY-001 |

### SYSTEM-TEST-001 returned Pending — 2026-09-24

Manual validation exposed the Storefront schema-builder contract defect after
COMMERCE-029 acceptance. SYSTEM-TEST-001 is therefore Pending again and now depends
on COMMERCE-032, COMMERCE-033 and COMMERCE-034. This preserves the invariant that
terminal system validation runs only after all required implementation corrections
are architect-accepted Complete.
