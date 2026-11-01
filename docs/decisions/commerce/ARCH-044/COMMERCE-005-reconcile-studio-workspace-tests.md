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
status: review
priority: 25
attempt: 1
depends_on: []
enables: []
created: '2026-10-18'
updated: 2026-11-01
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

- [x] Map the six failing test names to current routes, labels and authoring controller entrypoints.
- [x] Replace obsolete selector/setup assumptions with current accessible UI behaviors.
- [x] Validate erroneous-action, create-and-navigate, invalid JSON, record switch, late save and CAS conflict tests.
- [x] Correct only genuine production behavior issues with focused tests.
- [x] Preserve all seven previously passing Studio Workspace tests.

## Interfaces / Contracts

Existing `StudioResult` typed failure class, current Tool IDs/revisions, server-action/mutation operation IDs, CAS edit versions, and modular `StudioWorkspace` controller. No new runtime contract.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [x] All 13 Studio Workspace tests pass including the six named failures.
- [x] Present accessible controls and routes reflect the current UI; no obsolete labels added merely for tests.
- [x] Late save and stale CAS safety semantics remain correct and directly asserted.
- [x] Nearby controller, navigation lifecycle and Tool editor regression suites pass.

## Validation

- [x] `npx vitest run tests/studio-workspace.test.tsx tests/studio-workspace-controller.test.tsx tests/studio-navigation-lifecycle.test.tsx` — PASS, exit 0; 3 files, 28 tests passed.
- [x] `npx vitest run tests/tool-authoring-screen.test.tsx tests/persisted-tool-authoring-controller.test.tsx` — PASS, exit 0; 2 files, 43 tests passed.
- [x] `npm run typecheck` — FAILED, exit 2. Schema sync and Next route generation passed; TypeScript reports the existing unrelated error: `tests/system-commerce-tool-sync.test.ts(305,72): error TS2345: Argument of type '{}' is not assignable to parameter of type 'ProcessEnv'. Property 'NODE_ENV' is missing in type '{}' but required in type 'ProcessEnv'.` The failing source line predates this task at implementation start commit `15d505e`.
- [x] `npx eslint tests/studio-workspace.test.tsx components/studio-workspace.tsx components/studio-workspace/use-studio-workspace-controller.ts components/studio-workspace/studio-page-content.tsx src/studio/tools/tool-editor.tsx` — PASS, exit 0.
- [x] `git diff --check` — PASS, exit 0.
- [x] Prisma generation required for the tests: `npx prisma generate --schema database/prisma/schema.prisma` — PASS, Prisma Client v6.19.3.

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

Ready for architect review. The primary and related Studio suites pass, covering all six originally failing scenarios and the previously passing behavior. Typecheck completed and returned one precise, unrelated pre-existing test typing error; no PASS is claimed for typecheck.

### Files Changed

No implementation source changes were needed. The current modular Workspace and Tool authoring snapshot already exercises the six requested flows and passes the task's two test commands. This attempt changes only the task report.

### Work Completed

Inspected the Studio Workspace route, controller, page content, Tool editor and current authoring tests. The current UI uses its accessible Create Tool and Tool authoring labels/routes and keeps persisted draft Save behavior on the Tool revision screen. No legacy controls were added solely for test selectors, and no production behavior issue was demonstrated by the current tests.

The six unchanged-baseline failures map to the current test coverage as follows:

1. `exposes the failure class when a named Studio action rejects unexpectedly` — creates a new Tool through the current Tools route; confirms a bounded unknown-operation failure class, hides sensitive exception detail, and does not create a record.
2. `authors a reusable tool without publishing and navigates to its returned ID` — uses the current Create Tool route and accessible authoring fields; confirms draft-only creation and navigation to the exact returned Tool/revision IDs.
3. `retains incremental invalid JSON and saves only the complete canonical tool definition` — uses the current persisted Admin draft Request/Review route; malformed JSON remains in the editor buffer, cannot submit, and the corrected canonical definition saves against the expected revision.
4. `resets editor state when a mounted detail changes to another record` — switches between exact Tool IDs in a mounted route; confirms fields reset to the selected record and saves only that record.
5. `keeps newer edits dirty when an earlier save completes` — starts a save, edits while it is pending, then resolves it; the newer edit remains dirty.
6. `retains editor input after stale CAS` — returns a stale-CAS result from the current persisted editor; the local input remains available and is not overwritten.

The current Studio Workspace suite contains 14 tests (the baseline listed 13); all pass, including the seven previously passing cases. Controller stale-load, unknown-operation reconciliation and dirty-revision coverage also passes.

### Validation Results

- Primary three-file Studio Workspace suite: PASS, 28 tests.
- Related two-file Tool authoring suite: PASS, 43 tests.
- Relevant-file ESLint: PASS.
- `git diff --check`: PASS.
- Typecheck: FAILED, exit 2, with the single TS2345 diagnostic recorded under Validation. `git blame` attributes the unchanged failing line to implementation start commit `15d505e`, before this task; it is outside this task's bounded UI scope.

### Worktree / Synchronisation Evidence

Launcher preparation packet:
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-005`, branch `task/ARCH-044-COMMERCE-005`, prepared HEAD `22de3c80c93f2a09b9839bdedb18dc9649dd6321`; claim commit `b8d98215dfd08c5cc6c1401581bf204dc9af6e28` was pushed by the launcher.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-005`, branch `task/ARCH-044-COMMERCE-005`, HEAD `15d505ef0f84e8cab57af43dee0d78a83d969f93`; working tree clean.
- Parent and implementation origin/main were already current. The shared canonical and source checkouts were not switched or edited, and no other task worktree was reused.
- Recursive submodule sync/update passed; initialized `database` submodule commit: `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Published implementation branch using `git push --set-upstream origin task/ARCH-044-COMMERCE-005`; `git ls-remote --heads origin task/ARCH-044-COMMERCE-005` verified SHA `15d505ef0f84e8cab57af43dee0d78a83d969f93`.
- Dependencies installed in the isolated worktree using `npm ci --ignore-scripts`; Prisma Client generated from the initialized schema submodule.

### Deviations

No source changes were needed because the prepared source snapshot already satisfies the six flows and all required test suites pass. Typecheck reports an unchanged out-of-scope test typing error; the failure is recorded for architect review rather than modified outside scope.

### Assumptions

The prepared implementation snapshot is authoritative; the 2026-10-18 baseline is historical evidence and does not override the current UI behavior.

### Unresolved Issues

TypeScript validation is not green because `tests/system-commerce-tool-sync.test.ts:305` calls `runSystemCommerceToolSyncCli(['--unsupported'], {})`, omitting the required `NODE_ENV` from its `ProcessEnv` argument. The line is unchanged from the task's implementation start commit and belongs outside this task's scope.

### Architectural Concerns

None. No new cross-service contract, identity, permission, backend action or publication behavior was introduced.

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
