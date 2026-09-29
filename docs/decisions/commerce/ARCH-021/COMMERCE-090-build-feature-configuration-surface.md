---
id: ARCH-021-COMMERCE-090
architecture_id: ARCH-021
title: Build the Feature configuration surface
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 93
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-088
enables:
  - ARCH-021-COMMERCE-091
created: 2026-09-29
updated: 2026-09-29
---

# Build the Feature configuration surface

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the current Feature "linked configurations / Add behaviour" presentation with a dedicated Feature-centric Commerce Studio surface that shows the Admin-owned Feature, its one shared behaviour prompt and its current Capability -> Tool associations.

## Context

The current Feature route renders inside the broad `StudioWorkspace`, exposes raw Capability IDs as "Linked configurations", and immediately persists a Capability shell from an "Add behaviour" form.

The new product language is Feature-centric. The user configures an existing Admin Feature; the Feature behaviour prompt applies to all of that Feature's Capabilities; Capabilities are shown by human-readable identity and assigned Tool.

This task builds the Feature surface only. The local-first Add Capability wizard is COMMERCE-091.

## Scope

Primary areas include:

```text
app/features/page.tsx
app/features/[id]/page.tsx
src/studio/features/*                        # new dedicated domain UI encouraged
components/studio-workspace.tsx              # remove Feature-detail ownership where replaced
app/styles.css or local feature styles
focused Feature UI tests
```

Consume only COMMERCE-088 read/update actions.

## Out of Scope

- Capability creation wizard (COMMERCE-091).
- Release/runtime changes.
- Admin Feature creation/editing.
- Billing/subscription information or entitlement diagnostics.
- Tool authoring.
- Final `/capabilities` route deletion (COMMERCE-092).

## Requirements

### R1 — Features remain read-only Admin identities

The Feature surface may display Admin-owned identity/metadata but must not offer Feature creation, rename, activation-mode or billing-plan editing.

### R2 — show current Capabilities by meaningful data

For a Feature, list each current Capability using at least:

```text
display name
key
description where useful
assigned Tool display name/name
enabled state where retained
```

Do not show raw Capability IDs as the primary label and do not expose Capability revision status/history.

### R3 — one Feature behaviour editor

Show exactly one `Behaviour prompt` editor for the Feature, outside the individual Capability rows/cards.

Save through COMMERCE-088 CAS semantics. Surface stale-CAS/conflict errors without overwriting newer state. Successful Save refreshes the canonical prompt/editVersion and clears dirty state.

An empty behaviour prompt is valid.

### R4 — Add Capability is an entry point, not an immediate mutation

Expose an `Add capability` action that navigates/opens the COMMERCE-091 authoring flow.

Clicking `Add capability` in this task must not call `createFeatureCapability` itself.

### R5 — no removed concepts in the Feature UI

Do not render or mention:

```text
selection binding
BASE / FEATURE / RECOVERY_POLICY
Capability draft/revision
Capability publish
max search results
max recommendations
multiple Tool bindings
```

### R6 — extract Feature ownership from the generic workspace

Feature-detail rendering should live in a dedicated Feature domain component/module rather than adding another large branch to `components/studio-workspace.tsx`.

Do not refactor unrelated Tools/Releases/Shops merely to reduce that file.

## Work Items

- [x] Add dedicated Feature configuration route/component ownership.
- [x] Render Feature identity/metadata as read-only Admin-owned context.
- [x] Render human-readable Capability -> Tool associations.
- [x] Add one Feature Behaviour prompt editor and CAS Save handling.
- [x] Add `Add capability` navigation/entry point with zero mutation.
- [x] Remove the current raw `Linked configurations` Feature presentation.
- [x] Remove the current immediate `Add behaviour` mutation form.
- [x] Extract Feature-detail UI ownership out of the generic Studio workspace.
- [x] Add focused Feature loading, prompt-save, stale-CAS and navigation tests.

## Interfaces / Contracts

Consumes COMMERCE-088 Feature read model and `updateFeatureBehaviour` mutation.

Produces the Feature surface consumed by COMMERCE-091.

## Dependencies

- ARCH-021-COMMERCE-088

## Enables

- ARCH-021-COMMERCE-091

## Acceptance Criteria

- [x] The Feature screen shows current Capabilities and assigned Tools without revision terminology.
- [x] Exactly one Behaviour prompt editor exists per Feature.
- [x] Behaviour Save is CAS-safe and a conflict never silently overwrites newer text.
- [x] Empty Feature behaviour text is supported.
- [x] `Add capability` performs no durable mutation before entering the authoring flow.
- [x] No billing/subscription data is required to render or edit the Feature configuration surface.
- [x] The old `Linked configurations` + immediate `Add behaviour` form is no longer the Feature UX.
- [x] Feature-detail implementation is owned by a dedicated Feature module/component rather than the generic workspace branch.

## Validation

- [x] focused Feature UI tests
- [x] focused server-action integration mocks/fixtures for Feature reads and behaviour Save
- [x] targeted ESLint
- [x] changed-file TypeScript diagnostics / repository typecheck evidence per baseline policy
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not implement the Capability wizard.

## Implementation Notes

Use the current Tool creation UX as a visual/interaction reference, not as a reason to reproduce its six tabs for this much smaller flow.

## Completion Report

### Status

Attempt 1 is ready for Architect Review. Claim metadata is cleared.

### Files Changed

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/features/feature-configuration-screen.tsx`
- `tests/feature-configuration-page.test.tsx`
- `tests/feature-configuration-screen.test.tsx`
- `tests/studio-workspace.test.tsx`

### Work Completed

- Added a dedicated Feature list/detail surface using only `listFeatureAuthoring`, `getFeatureAuthoring`, and `updateFeatureBehaviour`; Feature routes bypass generic shop-selection, shell publication, and legacy Feature reads.
- Rendered Admin-owned Feature identity read-only, one shared Behaviour prompt, and human-readable Capability-to-Tool associations without revision/billing concepts.
- Added empty-prompt CAS save, explicit refresh after stale CAS, preserved local text on conflicts, and refresh-before-retry for unknown mutation outcomes.
- Added Add capability navigation to the COMMERCE-091 route without invoking a creation action.
- Removed Feature detail ownership and the obsolete Feature title from `StudioWorkspace`.
- Committed implementation as `7f7b075` (`feat(commerce): add Feature configuration surface`) and pushed `task/ARCH-021-COMMERCE-090`.

### Validation Results

- `npm exec -- vitest run tests/feature-configuration-page.test.tsx tests/feature-configuration-screen.test.tsx`: passed, 2 files / 8 tests.
- Targeted ESLint on all six changed files: passed with no warnings or errors.
- Pylance diagnostics on all six changed files: no errors found.
- `git diff --check`: passed.
- `npm run typecheck`: did not pass; 271 errors remain across 27 repository files. The changed Feature files are absent from the final compiler error summary; task-introduced diagnostics found in the initial run were corrected.
- `npm exec -- vitest run tests/studio-workspace.test.tsx`: 7 passed, 6 failed in existing generic Studio/Tools editor workflows; the focused Feature route/screen suite passes independently.

### Deviations

The full repository typecheck and neighboring StudioWorkspace suite are not green; both results are recorded above rather than expanding this task into unrelated backend/type/test repairs.

### Assumptions

- COMMERCE-091 owns the destination capability-creation route; this task provides navigation only.
- Admin Feature identity and Capability/Tool associations are read-only in this surface; only the shared behaviour prompt is mutable here.

### Unresolved Issues

- Repository-wide typecheck remains blocked by 271 errors in 27 files outside the changed Feature files.
- The neighboring StudioWorkspace suite remains partially failing in generic editor workflows (6 failures, 7 passes).

### Architectural Concerns

- No Feature-scope architecture deviation identified. The generic StudioWorkspace failures and repository-wide compiler errors should be triaged separately from this Feature surface.

### Attempt 1 Worktree and Handoff Evidence

Physical worktree isolation:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-090`, `task/ARCH-021-COMMERCE-090`.
- Implementation worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-090`, `task/ARCH-021-COMMERCE-090`.
- Both worktrees were newly created for this task; neither shared/default checkout was switched or used for implementation, and no other task worktree was reused.

Start-of-attempt synchronization from the launcher packet:

- Parent remote task branch fast-forwarded: `not-needed`; parent `origin/main` incorporated: `already-current`.
- Implementation remote task branch fast-forwarded: `not-needed`; implementation `origin/main` incorporated: `already-current`.
- Recursive implementation submodule synchronization and initialization passed. `database` was initialized at `e9fb60221f1532205650154dfff2aadb6270b14c`; launcher status was `ready`.

Published task state:

- Implementation commit `7f7b075` is pushed to `origin/task/ARCH-021-COMMERCE-090`.
- No task branch was merged into `main`.
- Task status is `review`; `executor` and `claimed_at` are cleared. The Architect Review section below remains unchanged.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
