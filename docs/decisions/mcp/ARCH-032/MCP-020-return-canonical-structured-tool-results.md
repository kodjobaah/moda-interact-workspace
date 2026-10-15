---
id: ARCH-032-MCP-020
architecture_id: ARCH-032
title: Return canonical structured Commerce results from MCP tools/call
task_kind: implementation
domain: mcp
status: complete
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
priority: 18
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-032-MCP-019
enables:
- ARCH-032-BACKGROUND-001
- ARCH-032-COMMERCE-006
- ARCH-032-SYSTEM-TEST-002
created: '2026-10-15'
updated: '2026-10-15'
---

# ARCH-032-MCP-020 — Return canonical structured Commerce results from MCP tools/call

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`. Coordinator: `moda_architect`.

## Objective

Return the validated `CommerceToolResult` through SDK `structuredContent` while preserving existing content, error semantics and tool identity.

## Context

The snapshot MCP `src/mcp/registration.ts` only sends JSON text content; Background and Commerce Live Test read `structuredContent` using published `CommerceToolResultSchema`. This independent MCP provider defect follows manifest registration, not system-test changes.

## Scope

- Add canonical `structuredContent` to MCP tool call responses after validating against published Shared commerce schema.
- Preserve text `content` for legacy consumers and the exact `isError` relation to the result status.
- Cover success, denial, provider errors, schema mismatch and zero-tool negative cases with SDK tests.

## Out of Scope

- No tool alias changes; no Background/Commerce source changes.
- No reinterpretation of errors, broad JSON text fallback or local schema copies.

## Requirements

- MCP protocol must expose valid structured JSON object without leaking raw failures.
- Error handling remains fail-closed and bounded.

## Work Items

- [x] Inspect current SDK response type and runner result shape.
- [x] Add schema-validated structured result envelope.
- [x] Extend SDK and focused unit tests.

## Interfaces / Contracts

- `@modainteract/moda-interact-shared/commerce` `CommerceToolResultSchema` (published).
- `tools/call` returns `structuredContent`, `content`, `isError`.

## Dependencies

- `ARCH-032-MCP-019`

## Enables

Calculated from `depends_on` in the 2026-10-15 reconciliation metadata; dependent work is never automatically claimed.

## Acceptance Criteria

- [x] Success and error results parse as published `CommerceToolResult`.
- [x] Structured and legacy text representations agree; errors never imply success.
- [x] No change to MCP advertised capability-key transport identity.

## Validation

- [x] npm run typecheck
- [x] npm run lint
- [x] focused MCP tools/call SDK tests
- [x] npm test
- [x] npm run build

## Stop Condition

Finish the bounded task, record the evidence in the Completion Report, move to `review`, return to `moda_architect`, and STOP. Repository agents do not close their own tasks. For developer-completion tasks, explicit developer completion remains required after acceptance.

## Implementation Notes

Do not alter MCP-019 resource contract or patch system-test fixtures. Accept MCP-019 first.

## Completion Report

### Status

Complete — Attempt 1 accepted and explicitly completed by the developer.

### Files Changed

`src/mcp/registration.ts` and `tests/unit/mcp/structured-results.test.ts` contain
the structured-result implementation and SDK tests. The same pushed implementation
commit also changes the `database` submodule pointer from the prepared baseline
`5f6c7d473771ca7beac8dd64729f228438d95bc4` to
`12c3bee13cabeb3c8b9cb0ac602d836700702413`; this out-of-scope pointer delta was
explicitly accepted by the developer. No other source files are changed relative
to `origin/main`.

### Work Completed

The MCP `tools/call` handler now validates results with the published
`CommerceToolResultSchema`, returns the validated object in SDK `structuredContent`,
preserves matching JSON text for legacy clients, and sets `isError` from the
validated status. Added SDK tests for success, denial, provider and malformed
result failures, empty capability sets, shared capability identity, and HTTP
transport. The developer explicitly accepted the completion with the database
gitlink deviation disclosed below.

### Launcher Preparation Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-032-MCP-020`, branch `task/ARCH-032-MCP-020`; created for this attempt.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-032-MCP-020`, branch `task/ARCH-032-MCP-020`; created for this attempt.
- Neither shared checkout was switched or mutated for task work; no other task worktree was reused.
- Parent and implementation task branches were already current with `origin/main`; no remote task-branch fast-forward was needed.
- `git submodule sync --recursive` and `git submodule update --init --recursive` passed. Prepared database submodule commit: `5f6c7d473771ca7beac8dd64729f228438d95bc4`.
- Dependency gate passed: `ARCH-032-MCP-019` was complete.
- Attempt 1 claim was durably committed and pushed by the launcher at `177ca6e658cabc891fead63ed5c59f6a64c9c083`.

### Validation Results

- Focused `npx tsx --test tests/unit/mcp/structured-results.test.ts`: 7 passed,
  0 failed.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm test`: 155 passed, 0 failed, 0 skipped.
- `npm run build`: passed.
- `git diff --check`: passed.
- Implementation task branch is pushed at `c5b4aa5`; it is in sync with
  `origin/task/ARCH-032-MCP-020`.
- The commit advances the database submodule pointer from prepared commit
  `5f6c7d4` to `12c3bee`. The developer explicitly accepted this deviation; the
  database repository itself was not modified.
- The cross-service black-box system test was not run.

### Deviations

The database gitlink advance described above remains in the implementation
branch and was explicitly accepted by the developer as part of this completion.
It is not represented as a Database source change or as a Database repository
modification.

### Assumptions

None beyond the inspected 2026-10-15 snapshot.

### Unresolved Issues

The accepted database pointer deviation remains visible in the implementation
branch. The editor focus on the API `catalogue_not_current` implementation was
not part of MCP-020 and no API repository change was made. Cross-service
validation remains for the separately gated system-test task.

### Architectural Concerns

No Database or API source ownership was exercised. The developer accepted the
Database submodule pointer advance as a bounded deviation for this task.

## Architect Review

### Review Status

Accepted — developer supplied `Architect Review Accepted` with the explicit
completion action on 2026-10-15.

### Review Notes

The developer accepts the implemented structured result contract, recorded
validation evidence, and documented database gitlink deviation. This records the
developer-supplied disposition; it does not assert an independent review event
or any cross-service system-test result.

### Reviewed Files

MCP implementation commit `c5b4aa5` and this task's Completion Report on parent
branch `task/ARCH-032-MCP-020`.

### Validation Reviewed

Focused structured-results SDK tests (7/7), `npm run typecheck`, `npm run lint`,
`npm test` (155/155), `npm run build`, and `git diff --check` passed. The
cross-service system-test task was not run.

### Architecture Conformance

Accepted for the bounded MCP result contract. The documented database pointer
advance is explicitly accepted; no Database source change or cross-service test
success is claimed.

### Follow-up

Continue with the separately governed Background and Commerce tasks. The
system-test task remains manual-gated and must not be claimed until its remaining
dependencies are complete.

## 2026-10-15 — Architect dependency reconciliation

**Separate correction:** do not claim this task until every listed dependency has an accepted Complete decision. It is not permission to alter any sibling repository. Earlier `depends_on`: `ARCH-032-MCP-019`. Earlier `enables`: None.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-019`. Active `enables`: `ARCH-032-BACKGROUND-001`, `ARCH-032-COMMERCE-006`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## Developer Self-Review - Changes Requested

### Review Outcome

The structured-result implementation and its validation pass, but Attempt 1 is
not review-ready because commit `c5b4aa5` includes an unrelated `database`
submodule pointer update. The task owns MCP service code and tests only; it does
not authorize advancing the Database submodule.

### Required Corrections

- Remove the unrelated database gitlink delta from the MCP-020 task branch by
  restoring it to the MCP-020 prepared baseline commit
  `5f6c7d473771ca7beac8dd64729f228438d95bc4`. Do not edit or commit the Database
  repository itself.
- Keep the `src/mcp/registration.ts` structured-result behavior and
	`tests/unit/mcp/structured-results.test.ts` coverage intact.
- Rerun `git diff --check`, `npm run typecheck`, `npm run lint`, the focused
	structured-results SDK test, `npm test`, and `npm run build` after the
	correction; confirm the final task diff contains only MCP-owned files.

### Attempt State

Returned to `ready`; `executor` and `claimed_at` are cleared. Attempt remains 1.
The next developer claim increments it once. The implementation commit remains
published and was not rewritten or reverted during this reconciliation.

## Developer Completion Decision — 2026-10-15

The developer explicitly requested `complete` with `Architect Review Accepted`.
This later decision supersedes the earlier changes-requested self-review for
task disposition. Attempt 1 is complete; `executor` and `claimed_at` are cleared.
The database gitlink discrepancy remains disclosed and accepted, and the
cross-service black-box system test remains unrun. No main-branch merge is
implied.
