---
id: ARCH-032-MCP-001
architecture_id: ARCH-032
title: Establish standalone private MCP service foundation
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 1
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-032-GATEWAY-001
created: 2026-10-10
updated: 2026-10-10
---

# Standalone private MCP foundation

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`

## Objective

Build a minimal independently runnable Node/TypeScript process in the
existing `moda-interact-mcp` repository. Do not copy protocol or tool
handlers yet. Commerce Studio and Background must remain unchanged.

## Scope

- Node runtime pinned to workspace Node 24; package scripts and build/test.
- Typed configuration with strict bind-address and PORT validation.
- HTTP server, `GET /health/live`, fail-closed `GET /health/ready`, graceful
  shutdown and bounded readiness probe support.
- `/api/mcp` explicitly unavailable (503) until a subsequent task wires
  transport and authorization.
- Shared structured logging and early shared observability preload.
- Focused tests for startup, config, health, readiness, shutdown, unmounted MCP.
- No Commerce/Background/Gateway/API/Shared/Database source edits.

## Acceptance criteria

- Build, typecheck, lint and tests pass on the declared toolchain.
- Default readiness is 503, including on error or timeout; 200 only when
  an injected healthy dependency probe succeeds.
- POST `/api/mcp` cannot execute or advertise MCP tools in this task.
- SIGTERM/SIGINT shutdown is idempotent; health responses are non-cacheable.
- README clearly states the scope, safe deployment boundary and next tasks.
- No duplicate logger or NodeSDK; no credentials or cross-repo imports.

## Validation

In `moda-interact-mcp` run:

```sh
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

Record actual results; developer applies/reviews the delivered patch using
the developer execution workflow before changing task status.

## Completion report

Pending developer application, validation and review. Do not mark complete
based solely on a generated patch.
