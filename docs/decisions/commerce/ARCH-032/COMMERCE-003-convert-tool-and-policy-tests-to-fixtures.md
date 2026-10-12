---
id: ARCH-032-COMMERCE-003
architecture_id: ARCH-032
title: Convert individual tool tests and Policy Operation tests to simulation-only
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-COMMERCE-001
enables:
  - ARCH-032-COMMERCE-004
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-COMMERCE-003 — Convert individual tool tests and Policy Operation tests to simulation-only

**Authoritative phase:** mock-first removal of embedded Commerce MCP. Supersedes earlier remote-client/snapshot task plan. Breaking changes to the obsolete embedded integration are explicitly allowed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Objective

Remove runtime provider execution from **single-tool and tool-authoring tests** without removing tool authoring/validation/publication. Synthetic fixtures and supplied response samples may be inspected and validated locally, but must not call Commerce's real executor or the standalone MCP service.

## Exact existing path

- `src/commerce/integration/preview/adapters.ts`: `createPreviewToolExecutor()` -> `backend.createFixtureExecution()` -> `DefinitionExecutionPort.execute()`.
- `src/commerce/preview/service.ts`: `PreviewService.runToolTest()` / tool test resolution and output/trace recording.
- `src/studio/tools/policy-operation-live-test-server-actions.ts`: `testPolicyOperationCandidateAction()` currently passes `backend.execution` to `createPolicyOperationLiveTest()`.
- `src/commerce/tool-authoring/policy-operation-live-test.ts`: currently builds an `AuthorizedToolCall` and invokes `dependencies.execution.execute()`.
- `src/commerce/external-preview/`: External HTTP response samples; preview routes under `app/api/studio/preview/tool-tests`.

## Required implementation

1. Route saved revision/draft tests through COMMERCE-001's pure mock interface using explicit fixtures. Preserve revision selection and Shared descriptor/input validation; no `backend.createFixtureExecution` or real provider port.
2. Preserve submitted response-sample parsing and **pure validation/transform inspection** only if independent of the removed Commerce production executor. Mark the output as simulated, not a real provider response. Avoid invoking outbound HTTP or credential readers from response-sample tests.
3. Replace the Policy Operation **live-test** server action with a fixture-backed, clearly labelled simulated test, or remove/disable the live-only action and button with a visible explanation until real remote testing is redesigned. Do not leave a clickable action that still uses `backend.execution`.
4. Keep draft editing, GraphQL query compilation/validation, capability authoring, revision persistence and publication paths. Do not delete pure authoring helpers merely because they mention an `execution` *definition* or an MCP tool *name*.
5. If a fixture is unsupported or omitted, fail visibly instead of pretending the operation succeeded. Fixture tests do not raise production ARCH-033 incidents for missing test data.
6. Keep fixture data bounded by existing preview schema/size limits; avoid a new cross-service contract or preview snapshot table.

## Acceptance criteria

- [ ] Tool draft/saved tests use declared synthetic fixtures only; no Shopify, Woo, External HTTP, embedding or policy live invocation occurs.
- [ ] External HTTP response-sample test never performs the outbound HTTP request; pure deterministic sample validation is retained or explicitly retired with UI indication.
- [ ] Policy Operation test path is either simulation-only or intentionally disabled; zero `backend.execution` usage.
- [ ] Studio create/edit/validate/publish flows for all existing supported tool types remain functional.
- [ ] Tests cover unsupported fixture, invalid input, response-sample mismatch and no-provider-call guarantees.

## Focused verification

Update `tests/external-preview.test.ts`, `tests/preview-service.test.ts`, `tests/tool-authoring-server-actions.test.ts`, `tests/preview-routes.test.ts` and focused policy-operation editor/action tests. Record which pure transforms remain as authoring dependencies, rather than deleting by filename alone.

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
