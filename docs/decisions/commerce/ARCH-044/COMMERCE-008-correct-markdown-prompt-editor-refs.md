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
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-18'
updated: '2026-10-18'
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

- [ ] Add tests showing external replacement does not issue user `onChange` and a changed callback is observed after rerender.
- [ ] Replace render-time ref writes with a React-compliant synchronization technique compatible with CodeMirror update listeners.
- [ ] Exercise editor identity, length limit, dirty state, unmount and canonical refresh.
- [ ] Run targeted lint and regression suites; record remaining unrelated warning count.

## Interfaces / Contracts

Local `MarkdownPromptEditor` props (`value`, `onChange`, `maxLength`, `ariaLabel`) and CodeMirror controlled-input contract only; no service API or cross-repository contract.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [ ] No `react-hooks/refs` errors; full repository lint has zero errors, assuming no concurrent new errors.
- [ ] External value changes do not call `onChange`; user edits call the latest callback once.
- [ ] Editor remains stable under ordinary prop refresh and retains accessible text input behavior.
- [ ] Existing Feature Configuration and Result Template editor tests pass.

## Validation

- [ ] `npx eslint src/studio/prompt-editor/markdown-prompt-editor.tsx`.
- [ ] `npx vitest run tests/feature-configuration-screen.test.tsx tests/result-template-tab.test.tsx tests/code-editor.test.tsx` plus new direct editor tests.
- [ ] `npm run lint`, `npm run typecheck`, `git diff --check`.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

The source has two render-time ref assignments at lines 26–27 and effect-driven CodeMirror setup/synchronization at lines 29–68. A fix must preserve deliberate separation between local editor transactions and external canonical refresh.

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
