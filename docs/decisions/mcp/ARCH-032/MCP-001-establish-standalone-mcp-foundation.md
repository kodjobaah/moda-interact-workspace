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
status: complete
priority: 1
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-032-GATEWAY-001
- ARCH-032-MCP-002
created: 2026-10-10
updated: '2026-10-15'
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

## 2026-10-15 — Architect dependency reconciliation

**Task still ready:** runtime source in the snapshot does not prove the canonical parent/implementation task branches, startup isolation, developer acceptance or `complete` status. Earlier `depends_on`: None. Earlier `enables`: `ARCH-032-GATEWAY-001`.

Active `status`: `ready`. Active `depends_on`: None. Active `enables`: `ARCH-032-GATEWAY-001`, `ARCH-032-MCP-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Standalone server, configuration, health/readiness lifecycle, and unit tests are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/server.ts`
- `src/runtime-config.ts`
- `src/index.ts`
- `tests/unit/server.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
