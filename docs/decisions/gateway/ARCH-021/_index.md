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
| [GATEWAY-001](GATEWAY-001-simplify-private-commerce-mcp-secret-wiring.md) | Remove MCP assertion-key wiring and preserve private link | Ready | ARCH-021-COMMERCE-030, ARCH-021-BACKGROUND-001 |

### GATEWAY-001 promoted — 2026-09-24

COMMERCE-030 and BACKGROUND-001 are architect-accepted Complete. GATEWAY-001 is therefore **Ready** to remove obsolete MCP assertion-key Blueprint/runtime wiring while preserving the existing private-only Commerce MCP topology and adding no replacement credential.
