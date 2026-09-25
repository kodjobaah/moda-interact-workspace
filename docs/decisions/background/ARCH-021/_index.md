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
| [BACKGROUND-001](BACKGROUND-001-simplify-commerce-mcp-client-authentication.md) | Remove MCP assertion signing and send private-link context only | Complete | ARCH-021-COMMERCE-030 |

### BACKGROUND-001 Attempt 1 architect review — 2026-09-24

The context-only private-MCP client change is accepted in substance, but BACKGROUND-001 remains **Ready** for a bounded Attempt 2 because the required host fixture is currently 38/40 rather than green. The two failing concurrency cases were previously recorded as passing in the architect-accepted ARCH-020 Background validation and therefore require root-cause evidence rather than an unsupported "pre-existing" classification. Attempt 2 must expose the local fixture's swallowed server exception, restore the focused host fixture to 40/40 or return a concrete out-of-scope blocker, reconcile the task checklists/report, and stop. GATEWAY-001 remains Pending.

### BACKGROUND-001 Attempt 2 accepted — 2026-09-24

BACKGROUND-001 is **Complete / Accepted, Attempt 2**. Background now sends only the validated bounded `X-Moda-Commerce-Context` over the private Commerce MCP link, with no task-owned RSA/JWT signing, MCP `Authorization` header, service token, API key or shared secret. Attempt 2 restored the required host fixture to 40/40 and exposed fixture exceptions deterministically without changing production error semantics. `ARCH-021-GATEWAY-001` is promoted to **Ready**.
