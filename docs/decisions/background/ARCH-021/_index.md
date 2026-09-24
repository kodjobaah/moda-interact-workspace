# ARCH-021 Background Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_background`

Coordinator:

`moda_architect`

## Pre-Phase-3 simplification checkpoint

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-simplify-commerce-mcp-client-authentication.md) | Remove MCP assertion signing and send private-link context only | Ready | ARCH-021-COMMERCE-030 |

### BACKGROUND-001 Attempt 1 architect review — 2026-09-24

The context-only private-MCP client change is accepted in substance, but BACKGROUND-001 remains **Ready** for a bounded Attempt 2 because the required host fixture is currently 38/40 rather than green. The two failing concurrency cases were previously recorded as passing in the architect-accepted ARCH-020 Background validation and therefore require root-cause evidence rather than an unsupported "pre-existing" classification. Attempt 2 must expose the local fixture's swallowed server exception, restore the focused host fixture to 40/40 or return a concrete out-of-scope blocker, reconcile the task checklists/report, and stop. GATEWAY-001 remains Pending.
