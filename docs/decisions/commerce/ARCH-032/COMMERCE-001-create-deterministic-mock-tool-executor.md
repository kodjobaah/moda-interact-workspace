---
id: ARCH-032-COMMERCE-001
architecture_id: ARCH-032
title: Implement deterministic Shared-compatible Studio mock tool executor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-032-COMMERCE-002
  - ARCH-032-COMMERCE-003
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-COMMERCE-001 — Implement deterministic Shared-compatible Studio mock tool executor

**Authoritative phase:** mock-first removal of embedded Commerce MCP. Supersedes earlier remote-client/snapshot task plan. Breaking changes to the obsolete embedded integration are explicitly allowed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Objective

Build a **pure simulated tool executor** for Commerce Studio. It returns validated Shared Commerce tool-result objects from explicit fixtures. It never resolves provider credentials, makes outbound HTTP/Shopify/WooCommerce/embedding calls, consults the embedded MCP runtime or changes production release state.

## Existing code and touch points

- `src/commerce/preview/types.ts`: `PreviewFixture`, `PreviewFixtureToolTestExecutionPort`, `PreviewConversationToolExecutionPort`, `ToolResultSchema`, `PreviewFrozenSnapshotSchema`.
- `src/commerce/integration/preview/adapters.ts`: `fixtureValue()`, `fixtureQuery()`, `callFor()` and existing local executor methods are *references for behaviour*, **not** implementations to reuse where they reach the real executor.
- `src/commerce/tool-definition/` and `@modainteract/moda-interact-shared/commerce`: canonical descriptor, input/result schemas and contracts.
- Existing tests: `tests/preview-service.test.ts`, `tests/selected-shop-preview-tool-execution.test.ts`, `tests/preview-integration.test.ts`.

## Required implementation

1. Add a small, independently testable module under `src/commerce/preview/` (recommended `mock-tool-executor.ts`) with explicit fixture input and `execute({descriptor, arguments, signal, ...})`. Keep fixture selection/data construction distinct from result validation and presentation. No large catch-all class.
2. Validate descriptor identity and supplied arguments using the **published Shared input/result schemas**; continue to enforce the existing preview bundle/snapshot/grant identity checks where relevant. Tool identity in the mock must match the selected frozen revision; no ad hoc name-only matching.
3. Define a deterministic fixture lookup keyed by the frozen tool revision, selected fixture/scenario and intended arguments. Use existing `PreviewFixture`/saved-fixture conventions where possible. No random, timestamp-dependent or external-data-dependent output unless the fixture specifies it explicitly.
4. Return a `CommerceToolResultSchema`-valid `OK` result only for a **declared matching fixture**. For absent/unsupported/malformed fixtures, emit a contract-valid explicit failure such as `UNAVAILABLE` or `INVALID_INPUT`. Never fabricate a successful catalogue, merchant policy or knowledge answer.
5. Preserve `AbortSignal` handling and Shared runner callback signature; an already aborted mock must not return a successful result. Do not introduce preview-specific MCP deadlines, provider-request limits or execution-policy constants.
6. Label fixture-derived results as **SIMULATED** in a way the later Studio UI can display, without adding fields that violate Shared strict result schemas; use separate preview metadata if necessary.
7. Make the adapter injectable and unit-testable without a database, Redis, network service, Shopify installation or running MCP endpoint.

## Acceptance criteria

- [ ] Matching fixture returns a deterministic schema-valid result; identical inputs produce identical data and rendered text.
- [ ] Missing fixture, mismatched revision, invalid arguments, unsupported execution kind and cancellation fail explicitly, with no provider I/O.
- [ ] Concurrent shops and preview conversations cannot read each other's fixture or frozen definition; no arbitrary tool can be selected by model text.
- [ ] Existing Shared result contract and runner interface are unchanged; no MCP SDK dependency in the new mock module.
- [ ] Focused unit tests prove providers/credentials/network are never touched, including error paths.

## Focused verification

Add `tests/studio-mock-tool-executor.test.ts` (or equivalent); run that suite and the existing selected-shop preview execution tests adapted for the new pure boundary. This task **does not switch live Studio wiring yet**.

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
