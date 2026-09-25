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
| [SYSTEM-TEST-001](SYSTEM-TEST-001-validate-simplified-studio-and-private-mcp.md) | Validate reduced configuration, dynamic Storefront schema authoring, readable Shopify documentation, unified authorization and context-only private MCP | Ready | DATABASE-002, COMMERCE-025..030, COMMERCE-032..035, BACKGROUND-001, GATEWAY-001 |

### SYSTEM-TEST-001 ready — 2026-09-25

COMMERCE-035 Attempt 3 is architect-accepted Complete. Every implementation task
listed under SYSTEM-TEST-001 `depends_on` is now Complete, so the terminal
architecture-validation task is **Ready**.

The developer may intentionally leave it Ready while manually exercising the
completed checkpoint. Phase-3 implementation remains paused until terminal
checkpoint validation/reconciliation.

### SYSTEM-TEST-001 returned Pending — 2026-09-24

Manual validation exposed the Storefront schema-builder contract defect after
COMMERCE-029 acceptance. SYSTEM-TEST-001 is therefore Pending again and now depends
on COMMERCE-032, COMMERCE-033, COMMERCE-034 and COMMERCE-035. This preserves the invariant that
terminal system validation runs only after all required implementation corrections
are architect-accepted Complete.
