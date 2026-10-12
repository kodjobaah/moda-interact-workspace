---
id: ARCH-032-COMMERCE-004
architecture_id: ARCH-032
title: Delete embedded Commerce MCP runtime and local provider execution wiring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-COMMERCE-002
  - ARCH-032-COMMERCE-003
enables:
  - ARCH-032-COMMERCE-005
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-COMMERCE-004 — Delete embedded Commerce MCP runtime and local provider execution wiring

**Authoritative phase:** mock-first removal of embedded Commerce MCP. Supersedes earlier remote-client/snapshot task plan. Breaking changes to the obsolete embedded integration are explicitly allowed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Objective

Physically delete the embedded MCP server, its Commerce-only authorization/runtime and obsolete provider execution wiring after all Studio tool callbacks have been switched to mocks. **This is a breaking removal, not a deprecation.** No shim, proxy, redirect, alternate route or MCP client.

## Exact inventory to reconcile

- **Delete:** `app/api/mcp/route.ts`; embedded `src/commerce/mcp/` tree once no retained type/import depends on it.
- **Remove from integration:** `src/commerce/integration/backend.ts` imports `parseMcpRequestContext`, `createMcpService`, `McpRuntime` and returned `mcp`, `runtime`, `execution`, `createFixtureExecution` fields; remove runtime assembly at current ~605-636.
- **Delete if unreferenced:** `src/commerce/integration/backend/authorization.ts`, `src/commerce/integration/backend/executors.ts`, `src/commerce/execution/executor.ts` and other Commerce-only provider adapter implementations.
- **Type migration:** inspect imports of `AuthorizedToolCall`, `DefinitionExecutionPort`, `McpError` from `src/commerce/mcp/ports` in `src/commerce/external-http/`, `src/commerce/merchant-knowledge/`, `src/commerce/execution/ports.ts`, tool-authoring and preview adapters. Keep only actually needed authoring contracts by moving them to appropriate non-MCP modules, or delete now-obsolete runtime interfaces. Do not create an `mcp/ports` alias merely for compatibility.
- **Test dependencies:** existing `tests/mcp-service.test.ts`, `tests/mcp-authorization.test.ts`, `tests/mcp-compatibility.test.ts`, `tests/definition-execution-mcp.test.ts`, `tests/local-external-mcp-diagnostic.test.ts` and `tests/fixtures/mcp-app/` must be removed or replaced by **relevant** surviving authoring/preview tests. Review before deleting.

## Required implementation

1. Run a repository-wide reference inventory first (static and dynamic imports, `next` route, tests, package scripts, service assembly). Document keep/delete decision by functional ownership, **not** indiscriminate deletion of every filename containing `execution` or `MCP`.
2. Remove HTTP `/api/mcp` route entirely. Expected outcome is Next's not-found response (404), with no JSON-RPC handler reachable in Commerce.
3. Remove server creation and local MCP authorization/execute registrations from `CommerceBackend`. Retain the backend methods serving authoring, saved selections, feature composition, shop settings, publication and preview orchestration.
4. Delete provider adapters and runtime-only ports that have zero remaining legitimate consumers after COMMERCE-002/003. If a pure authoring validator/compiler is still used, retain it in an authoring-appropriate location without a provider executor dependency.
5. Refactor all imports and test harnesses to the smaller backend shape. No deprecated exports, no compatibility redirects, no sandboxed second execution engine.
6. Do not delete any standalone `moda-interact-mcp` source or the Background `CommerceMcpClient`.

## Acceptance criteria

- [ ] `app/api/mcp/route.ts` and Commerce `src/commerce/mcp/` are absent. Requests to Commerce `/api/mcp` cannot call a tool (404).
- [ ] No Commerce production code path can reach `DefinitionExecutor`, `createMcpService`, `createFixtureExecution`, `backend.execution.execute`, provider credential reads for Studio tools or a new MCP client.
- [ ] Retained authoring, feature selection, model preview and publication compile and pass focused tests.
- [ ] Any remaining uses of terms `MCP name` or execution *definition* are documented as authoring schema fields, not runtime dependencies.
- [ ] Negative route and import-boundary regressions enforce the removal.

## Focused verification

Add a negative test for no `/api/mcp` handler (or a build/route proof), plus static-import boundary test; rerun `tests/backend-integration.test.ts`, `tests/studio-integration.test.ts`, `tests/feature-preview-composition.test.ts`, relevant publication/authoring tests. Removing obsolete embedded-MCP tests is permitted and expected.

## Validation and evidence

- [ ] `git apply --check --whitespace=error-all` (when applying an implementation patch), `git diff --check` and a review of the exact changed-file list.
- [ ] `npm run typecheck`, `npm run lint`, `npm test`, and `npm run build` from `moda-interact-commerce`, except if a documented pre-existing environmental blocker prevents one command; record exact logs and rerun focused tests.
- [ ] Record focused test names, counts, commits, clean/upstream worktree state and any baseline failures in the task Completion Report. Do not claim unrun tests.
- [ ] Re-run authoring and publication regressions when touching service wiring; retained Studio behaviour must work after deliberate breaking removal of the old MCP integration.

## Explicit exclusions

- Do **not** create a Commerce MCP client, remote preview reference, MCP proxy, local MCP server or provider-execution fallback.
- Do **not** change `runCommerceTurn()` in Shared, standalone MCP, Background, provider authorisation, the MCP execution-policy tasks or Admin policy UI.
- Do **not** create compatibility routes, obsolete interface shims, alias modules or migrations for the removed local MCP implementation. This is a development environment; obsolete code may be deleted outright.
- Do **not** edit any `docs/decisions/**/_index.md` during this architecture session.

## Completion handoff

Use the normal isolated task-worktree and launcher workflow. Submit changed-file details, focused test evidence and a Completion Report; return to architect review and STOP. An architect acceptance decision is separate. This document only defines the work; no task was claimed, committed, pushed or executed by this patch.

## Completion Report

### Status
Not started

### Files Changed
None

### Validation Results
Not run

### Deviations / Blockers
None reported

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed
