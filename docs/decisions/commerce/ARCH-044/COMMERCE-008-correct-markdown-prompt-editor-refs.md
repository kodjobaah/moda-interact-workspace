---
id: ARCH-044-COMMERCE-008
architecture_id: ARCH-044
title: Fix Markdown prompt editor React ref violations without changing CodeMirror behavior
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 15
attempt: 1
depends_on: []
enables: []
created: '2026-10-18'
updated: 2026-11-01
---

# Fix Markdown prompt editor React ref violations without changing CodeMirror behavior

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Eliminate the two confirmed pre-existing `react-hooks/refs` lint errors in the controlled CodeMirror Markdown editor without changing its input, synchronization or draft semantics.

## Context

Both unchanged Commerce baseline and ARCH-043 task worktree report the same two ESLint errors and 15 unrelated warnings. The errors are in `src/studio/prompt-editor/markdown-prompt-editor.tsx` at render-time writes `valueRef.current = value;` (line 26) and `onChangeRef.current = onChange;` (line 27). This component is shared across prompt editing and is intentionally controlled, so a mechanical ref removal could introduce stale closures or bogus user edits.

## Scope

- Refactor the controlled CodeMirror integration to avoid writing refs during render while retaining latest `value`, latest `onChange`, and stable editor lifecycle.
- Ensure external canonical value replacement updates the document without calling `onChange`, while local edits still invoke current callback exactly once.
- Preserve maxLength, aria label, CodeMirror history, editor identity when appropriate and cleanup on unmount.
- Add focused component regression tests for callback update, external replacement and dirty/canonical synchronization.

## Out of Scope

- No CodeMirror major upgrade, UI redesign, unrelated hook-rule suppressions or blanket lint configuration changes.
- Do not change the fifteen existing warning sites unless they become directly relevant to the bounded correction.

## Requirements

1. `react-hooks/refs` must report no errors for `markdown-prompt-editor.tsx`; avoid suppressing the rule with ESLint comments.
2. Latest callback/value must be honored after rerender without false intermediate user edits.
3. CodeMirror instance is not destroyed and recreated on every keystroke; resource cleanup remains correct.
4. Existing props and accessible editor contract remain unchanged.

## Work Items

- [x] Add tests showing external replacement does not issue user `onChange` and a changed callback is observed after rerender.
- [x] Replace render-time ref writes with a React-compliant synchronization technique compatible with CodeMirror update listeners.
- [x] Exercise editor identity, length limit, dirty state, unmount and canonical refresh.
- [x] Run targeted lint and regression suites; record remaining unrelated warning count.

## Interfaces / Contracts

Local `MarkdownPromptEditor` props (`value`, `onChange`, `maxLength`, `ariaLabel`) and CodeMirror controlled-input contract only; no service API or cross-repository contract.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [x] No `react-hooks/refs` errors; full repository lint has zero errors, assuming no concurrent new errors.
- [x] External value changes do not call `onChange`; user edits call the latest callback once.
- [x] Editor remains stable under ordinary prop refresh and retains accessible text input behavior.
- [x] Existing Feature Configuration and Result Template editor tests pass.

## Validation

- [x] `npx eslint src/studio/prompt-editor/markdown-prompt-editor.tsx` — PASS, exit 0; no diagnostics.
- [x] `npx vitest run tests/feature-configuration-screen.test.tsx tests/result-template-tab.test.tsx tests/code-editor.test.tsx tests/markdown-prompt-editor.test.tsx` — PASS, exit 0; 4 files, 45 tests passed.
- [x] `npm run lint` — PASS, exit 0; 0 errors and 15 warnings at unrelated existing sites.
- [x] `npm run typecheck` — FAILED, exit 2. Schema sync and Next route type generation passed. TypeScript reports the unchanged unrelated error `tests/system-commerce-tool-sync.test.ts(305,72): error TS2345: Argument of type '{}' is not assignable to parameter of type 'ProcessEnv'. Property 'NODE_ENV' is missing in type '{}' but required in type 'ProcessEnv'.` The source line predates this task at implementation start commit `15d505e`.
- [x] `git diff --check` — PASS, exit 0.
- [x] Test prerequisite: `npx prisma generate --schema database/prisma/schema.prisma` — PASS, generated Prisma Client v6.19.3.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

The source has two render-time ref assignments at lines 26–27 and effect-driven CodeMirror setup/synchronization at lines 29–68. A fix must preserve deliberate separation between local editor transactions and external canonical refresh.

## Completion Report

### Status

Ready for architect review. The Markdown editor and surrounding regression suites pass, targeted and full lint report no errors, and the required typecheck completed with one unrelated pre-existing type error. No PASS is claimed for typecheck.

### Files Changed

No implementation source changes were needed. At implementation start commit `15d505ef0f84e8cab57af43dee0d78a83d969f93`, the component already synchronized latest props in an effect rather than writing refs during render, and the direct Markdown editor regression suite was present. The current code and tests satisfy the scoped behavior. This attempt changes only this task report.

### Work Completed

Inspected the controlled CodeMirror component and its direct regression tests. Confirmed latest callback and canonical value synchronization occur in an effect; external replacements are suppressed from user `onChange`; editor construction remains stable for ordinary value/callback rerenders; transaction filtering preserves maxLength for user edits without rejecting canonical replacements; CodeMirror history, accessibility and unmount cleanup are covered.

The direct editor tests cover:
- callback replacement after rerender and exact single invocation;
- external canonical replacement, including empty content, without an `onChange` echo;
- dirty draft versus canonical acknowledgement;
- maxLength for local edits and over-limit canonical replacement;
- editor identity, history, accessible textbox and cleanup.

The feature-configuration, Result Template and Code editor suites also pass. No CodeMirror behavior, editor props, rule suppressions or unrelated warning sites were changed.

### Validation Results

- Direct and surrounding regression command: PASS, 45 tests across four files.
- Targeted Markdown editor ESLint: PASS.
- Full repository `npm run lint`: PASS, 0 errors and 15 warnings; the warning sites are unrelated to this task.
- `git diff --check`: PASS.
- `npm run typecheck`: FAILED, exit 2, with one TS2345 at `tests/system-commerce-tool-sync.test.ts:305`; the failing line is unchanged from the implementation start commit and outside task scope.

### Worktree / Synchronisation Evidence

Launcher preparation packet:
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-008`, branch `task/ARCH-044-COMMERCE-008`, prepared HEAD `d581c6efc270f42ef254727b6da3d7a14eaa9191`; claim commit `7d412a2755f818c4095062b23afa1b2d691ca756` was committed and pushed by the launcher.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-008`, branch `task/ARCH-044-COMMERCE-008`, HEAD `15d505ef0f84e8cab57af43dee0d78a83d969f93`; source worktree clean.
- Parent and implementation origin/main were already current; shared canonical/source checkouts and other task worktrees were not switched or edited.
- Recursive submodule sync/update passed. The initialized `database` submodule was at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Published the implementation branch using `git push --set-upstream origin task/ARCH-044-COMMERCE-008`; `git ls-remote --heads origin task/ARCH-044-COMMERCE-008` verified remote SHA `15d505ef0f84e8cab57af43dee0d78a83d969f93`.
- Installed lockfile dependencies in the isolated worktree with `npm ci --ignore-scripts`; generated Prisma Client from the initialized schema submodule.

### Deviations

No source changes were necessary because the prepared source already satisfies the task and the regression suite demonstrates the required semantics. Typecheck was run to completion; its unrelated error is recorded rather than fixed outside scope.

### Assumptions

The prepared implementation snapshot is authoritative; the 2026-10-18 baseline is historical and does not override the current component implementation and direct test coverage.

### Unresolved Issues

The repository-wide typecheck remains red on the unchanged `tests/system-commerce-tool-sync.test.ts:305` call, where an empty environment object omits required `NODE_ENV`. This is outside the Markdown editor task scope.

### Architectural Concerns

None. No service APIs, CodeMirror version, UI contract or cross-repository behavior changed.

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
