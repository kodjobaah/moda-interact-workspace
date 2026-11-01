---
id: ARCH-044-COMMERCE-005
architecture_id: ARCH-044
title: Restore Studio Workspace authoring behavior and regression tests
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-18'
updated: '2026-10-18'
---

# Restore Studio Workspace authoring behavior and regression tests

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Resolve all six failing Studio Workspace authoring tests against the current modular Studio editor, preserving genuine error, dirty state and CAS semantics.

## Context

Baseline `tests/studio-workspace.test.tsx` has **6/13 failing tests**, notably `Unable to find a label with the text of: Immutable MCP name` and `Unable to find an accessible button named Save draft`. The component and authoring navigation have evolved across `components/studio-workspace` and `src/studio/tools/authoring` while older tests still target obsolete editor labels/routes. Missing elements alone do not establish whether the implementation is defective or the tests are outdated.

## Scope

- Inspect `components/studio-workspace.tsx`, `components/studio-workspace/use-studio-workspace-controller.ts`, `components/studio-workspace/studio-page-content.tsx`, `src/studio/tools/tool-editor.tsx` and current persisted Tool editor children.
- Map old `Immutable MCP name` and `Save draft` fixtures to current accessible labels, modular routes and role gates; do not add misleading old UI just to satisfy selectors.
- Preserve actionable error classes, navigation to exact new Tool IDs, malformed local JSON buffering, editor state reset on changed record, edits made during pending save and stale CAS conflict retention.
- Fix true UI bugs found by current-behavior tests; otherwise modernise obsolete fixtures/selectors and document each decision.

## Out of Scope

- No redesign of unrelated Tool/Preview screens; no new identities/permissions or backend action contract.
- No weakening of dirty navigation, role gating, CAS conflict handling or unknown-outcome protection.

## Requirements

1. The current modular authoring UI is the source of actual reachable behavior, with accessible roles/labels used by tests.
2. Unexpected action rejections surface bounded typed failure classes without sensitive detail.
3. Draft creation and save update only the intended Tool record, preserving exact returned identity and optimistic concurrency.
4. Late responses and stale CAS results cannot replace newer edits or navigate to an incorrect record.

## Work Items

- [ ] Map the six failing test names to current routes, labels and authoring controller entrypoints.
- [ ] Replace obsolete selector/setup assumptions with current accessible UI behaviors.
- [ ] Validate erroneous-action, create-and-navigate, invalid JSON, record switch, late save and CAS conflict tests.
- [ ] Correct only genuine production behavior issues with focused tests.
- [ ] Preserve all seven previously passing Studio Workspace tests.

## Interfaces / Contracts

Existing `StudioResult` typed failure class, current Tool IDs/revisions, server-action/mutation operation IDs, CAS edit versions, and modular `StudioWorkspace` controller. No new runtime contract.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [ ] All 13 Studio Workspace tests pass including the six named failures.
- [ ] Present accessible controls and routes reflect the current UI; no obsolete labels added merely for tests.
- [ ] Late save and stale CAS safety semantics remain correct and directly asserted.
- [ ] Nearby controller, navigation lifecycle and Tool editor regression suites pass.

## Validation

- [ ] `npx vitest run tests/studio-workspace.test.tsx tests/studio-workspace-controller.test.tsx tests/studio-navigation-lifecycle.test.tsx`.
- [ ] `npx vitest run tests/tool-authoring-screen.test.tsx tests/persisted-tool-authoring-controller.test.tsx` when relevant.
- [ ] `npm run typecheck`, changed-file lint, `git diff --check`.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

Don't infer a regression solely from `getByLabelText("Immutable MCP name")` or `getByRole("button", {name:"Save draft"})`. Verify current editability/route and whether the actor is authorised to mutate before changing the component.

### Exact unchanged-baseline failures (6)

- `exposes the failure class when a named Studio action rejects unexpectedly`
- `authors a reusable tool without publishing and navigates to its returned ID`
- `retains incremental invalid JSON and saves only the complete canonical tool definition`
- `resets editor state when a mounted detail changes to another record`
- `keeps newer edits dirty when an earlier save completes`
- `retains editor input after stale CAS`

## Completion Report

### Status

Not Started

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run. Record each exact command, environment, exit code, test totals and any known-baseline differences. Baseline failures may not be silently treated as task successes.

### Worktree / Synchronisation Evidence

Not yet materialised. Record launcher-resolved canonical workspace root, dedicated parent and implementation worktrees, initial branch/commit identities and recursive submodule state when execution begins.

### Deviations

None yet.

### Assumptions

Task definition based on the 2026-10-18 source snapshot and supplied baseline/task logs; re-inspect current implementation when executing.

### Unresolved Issues

None beyond the explicitly described diagnostics to investigate.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation evidence.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

Not assessed.

### Follow-up

None yet.
