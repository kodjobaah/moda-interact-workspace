# ARCH-021 Gateway Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_gateway`

Coordinator:

`moda_architect`

## Pre-Phase-3 simplification checkpoint

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [GATEWAY-001](GATEWAY-001-simplify-private-commerce-mcp-secret-wiring.md) | Remove MCP assertion-key wiring and preserve private link | Complete | ARCH-021-COMMERCE-030, ARCH-021-BACKGROUND-001 |

### GATEWAY-001 promoted — 2026-09-24

COMMERCE-030 and BACKGROUND-001 are architect-accepted Complete. GATEWAY-001 is therefore **Ready** to remove obsolete MCP assertion-key Blueprint/runtime wiring while preserving the existing private-only Commerce MCP topology and adding no replacement credential.

### GATEWAY-001 accepted — 2026-09-24

Attempt 3 completed the report-only reconciliation after the context-only private MCP implementation had passed architect review. `ARCH-021-GATEWAY-001` is architect-accepted **Complete**.

The private Commerce MCP topology remains unchanged: `COMMERCE_MCP_URL` is the messaging worker's Render-managed private service input, public `/api/mcp` remains denied, and no application-layer MCP credential replaces the removed RSA/JWT assertion keys.

`ARCH-021-SYSTEM-TEST-001` remains Pending until all of its checkpoint implementation dependencies are Complete.
