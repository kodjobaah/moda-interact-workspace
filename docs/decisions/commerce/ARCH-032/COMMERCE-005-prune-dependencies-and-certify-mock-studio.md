---
id: ARCH-032-COMMERCE-005
architecture_id: ARCH-032
title: Prune retired MCP dependencies and certify mock-only Commerce Studio
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-COMMERCE-004
enables: []
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-COMMERCE-005 — Prune retired MCP dependencies and certify mock-only Commerce Studio

**Authoritative phase:** mock-first removal of embedded Commerce MCP. Supersedes earlier remote-client/snapshot task plan. Breaking changes to the obsolete embedded integration are explicitly allowed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Objective

Deliver the final **Commerce MCP extraction certificate** for this development phase: no embedded MCP runtime, no Commerce MCP client and no provider-backed tool execution. Studio authoring, publication and Shared-powered test conversations remain functional with visibly simulated tools. Breaking deletions are intentional.

## Required implementation

1. Inspect `moda-interact-commerce/package.json`, lockfiles, `scripts/`, `tests/fixtures/`, Next route tree and runtime config. Remove `@modelcontextprotocol/sdk` **if no other legitimate consumers remain**; similarly remove `@shopify/dev-mcp` or other runtime dependencies/scripts **only if** their use is entirely retired. Do not remove `graphql`, Shared, Zod or compiler dependencies required for authoring/validation.
2. Remove unused `COMMERCE_MCP_URL`, `/api/mcp` diagnostics, local external MCP harness scripts and imported runtime configuration **only in Commerce**. Do not change Background `COMMERCE_MCP_URL` or standalone MCP deployment settings.
3. Add a repeatable boundary check (test or CI lint rule) that fails if `app/api/mcp/`, Commerce `src/commerce/mcp/`, MCP SDK imports, `createMcpService`, `backend.execution.execute`, or a private MCP client is reintroduced. Permit authoring labels like `MCP name` and canonical shared contract identifiers.
4. Run full Commerce typecheck, lint, complete unit/integration test suite and production build. Investigate test failures caused by obsolete imports; remove legacy runtime tests when irrelevant and replace coverage of retained user-facing behaviour with mock tests. Record unrelated environmental blockers separately.
5. Run authenticated browser/API smoke: create/edit/publish tool, feature composition, start selected-shop test conversation, model selects a fixture-backed tool, visible SIMULATED trace, missing-fixture error, single-tool draft fixture test, External HTTP response sample, policy-operation test either simulated or clearly disabled.
6. Prove no outbound tool provider request from Studio mocks with rejecting/fake network/credential ports. Confirm Background, standalone MCP, Shared runner and platform policy code have no changes in the implementation diff.
7. Produce a precise removal inventory and remaining-authoring-dependency inventory. Describe deferred **future** remote Studio testing as a new architectural decision, not an active acceptance condition here.

## Acceptance criteria / definition of done

- [ ] Commerce has neither MCP server/route nor MCP client/SDK runtime.
- [ ] No local provider-backed tool execution reachable from Studio; mocks use Shared result contracts and never silently succeed without fixtures.
- [ ] All retained Studio authoring, validation, publication, model orchestration, selected-shop conversation and fixture-test UX work; simulated status visible.
- [ ] `npm run typecheck`, `npm run lint`, `npm test`, `npm run build` pass or each pre-existing environmental blocker is explicitly evidenced; no undocumented regressions.
- [ ] Static boundary, route absence, cancellation, cross-shop and missing-fixture regressions pass.
- [ ] No compatibility shim or intermediate remote preview integration remains; no database migration/Shared package publication needed for this phase.

## Evidence artifact

Produce a final task Completion Report with files deleted, feature smoke matrix, exact commands/results and remaining unrelated failures. No Render/Background endpoint cutover is authorised by this task.

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
