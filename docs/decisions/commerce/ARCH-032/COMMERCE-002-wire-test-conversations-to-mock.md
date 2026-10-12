---
id: ARCH-032-COMMERCE-002
architecture_id: ARCH-032
title: Wire Studio selected-shop Test Conversations to mock tool execution
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
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

# ARCH-032-COMMERCE-002 — Wire Studio selected-shop Test Conversations to mock tool execution

**Authoritative phase:** mock-first removal of embedded Commerce MCP. Supersedes earlier remote-client/snapshot task plan. Breaking changes to the obsolete embedded integration are explicitly allowed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Objective

Replace the Commerce-local provider callback for **selected-shop Test Conversations** with the deterministic mock from COMMERCE-001. Keep the real Shared `runCommerceTurn()` model/tool-call workflow, selected-shop authorisation and Studio orchestration unchanged. No MCP client or HTTP transport.

## Exact existing path

- `src/commerce/preview/service.ts`: `PreviewService.execute()` invokes `runCommerceTurn()` and injects `conversationToolExecutor.execute(...)` (currently around the run callback).
- `src/commerce/integration/preview/adapters.ts`: `createSelectedShopPreviewToolExecutor()` currently calls `backend.execution.execute(call)` after creating a local `AuthorizedToolCall` with a 10s deadline / 12 requests.
- `src/commerce/integration/studio/services.ts` (and other wiring found by `rg`): constructs `PreviewService`/conversation executor.
- `src/commerce/preview/redis-store.ts`: session history, snapshots and run state. Routes under `app/api/studio/preview/conversations/` remain.

## Required implementation

1. Rewire **only** the injected Shared tool `execute` callback to COMMERCE-001's mock. Remove the selected-shop preview dependency on `backend.execution.execute`, `AuthorizedToolCall` and the old Commerce MCP authorisation/runtime.
2. Continue to validate authenticated principal, selected shop, selected feature composition, exact frozen tool revision/descriptor and conversation grant. No cross-shop fixture access. Retain current `PreviewBundle`/`PreviewConversationSnapshot` and Redis conversation/run state; do not introduce remote snapshot persistence.
3. Preserve Shared model invocation, prompt/instruction composition, run reservation, polling, cancellation and persisted history. Model-chosen arguments still flow to the mocked callback through `runCommerceTurn()`.
4. Provide an explicit fixture/scenario selection for Test Conversations (or a visibly identified existing registered fixture). Extend the Studio start-conversation input/preview snapshot if needed so the fixture choice is frozen with the conversation. Never silently choose arbitrary production data or return fabricated provider responses.
5. Make the simulated nature **prominent** in the Test Conversation screen and run/tool trace. Preserve current API shape where practical, but breaking changes to retired local execution fields/routes are allowed; do not add backwards-compatibility aliases.
6. If a selected tool lacks an explicit fixture, surface a failed simulated tool result and visibly identify fixture unavailability, not a fake answer or a fallback to the provider.
7. Do not move runner code into Commerce or MCP. Do not make *any* provider calls from the Test Conversation tool callback. Model calls are separate and remain real unless existing model-test mocks already apply.

## Acceptance criteria

- [ ] A model-requested tool goes through `runCommerceTurn()` -> mock callback, not `backend.execution.execute()`; assert in tests that the old executor is not called.
- [ ] A selected feature with declared fixtures produces simulated trace/result, while a missing fixture produces explicit error.
- [ ] Studio runs still transition RUNNING -> COMPLETED/FAILED/CANCELLED, with history and run polling preserved.
- [ ] Selected-shop authorisation and frozen descriptor/revision checks still reject mismatched or cross-shop calls.
- [ ] No MCP client, private endpoint setting or network provider execution introduced.

## Focused verification

Add/update `tests/selected-shop-preview-tool-execution.test.ts`, `tests/preview-service.test.ts`, `tests/preview-routes.test.ts`, `tests/preview-page.test.tsx` and `tests/preview-integration.test.ts`; cover model-selected tool calls, no fixture, cancellation, run polling and simulated labels. Mock provider and model ports separately.

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
