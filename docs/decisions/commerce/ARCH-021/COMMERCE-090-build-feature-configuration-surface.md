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
status: complete
priority: 93
executor: null
claimed_at: null
attempt: 3
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

Attempt 3 corrections are ready for Architect Review. Claim metadata is cleared.

### Files Changed

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/features/feature-configuration-screen.tsx`
- `tests/feature-configuration-page.test.tsx`
- `tests/feature-configuration-screen.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/studio-shell.test.tsx`

### Work Completed

- Added a dedicated Feature list/detail surface using only `listFeatureAuthoring`, `getFeatureAuthoring`, and `updateFeatureBehaviour`; Feature routes bypass generic shop-selection, shell publication, and legacy Feature reads.
- Rendered Admin-owned Feature identity read-only, one shared Behaviour prompt, and human-readable Capability-to-Tool associations without revision/billing concepts.
- Added empty-prompt CAS save, explicit refresh after stale CAS, preserved local text on conflicts, and refresh-before-retry for unknown mutation outcomes.
- Attempt 2 A1-R1: captured the prompt edit revision at save admission; successful mutation/read results update canonical `editVersion` but replace/clear prompt state only if no newer edit occurred. Pending saves also hold the navigation blocker, and status distinguishes submitted text from newer unsaved edits.
- Attempt 2 A1-R2: kept stale-CAS gating through further local edits and added a regression proving saving resumes only after explicit refresh, using the refreshed CAS version.
- Attempt 2 A1-R3: Feature list and detail routes now pass an explicit unavailable release model to `StudioShell`; focused route assertions verify this without calling `getShell`, and shell coverage verifies this renders “Release status unavailable,” not “No active release.”
- Attempt 3 A2-R1: only adopt the post-save refresh's `editVersion` when no newer local prompt edit occurred. Otherwise retain the successful mutation's CAS version, so a concurrent server update causes the next save to return stale-CAS rather than silently overwriting it. Added a regression for mutation version 5, a concurrent refresh at version 6, and retained local text.
- Attempt 3 A2-R2: classify an unresolved save as locked navigation state. Added a regression proving the pending dialog has no discard action and ordinary dirty-discard navigation returns after the save completes.
- Added Add capability navigation to the COMMERCE-091 route without invoking a creation action.
- Removed Feature detail ownership and the obsolete Feature title from `StudioWorkspace`.
- Attempt 1 implementation commit `7f7b075` (`feat(commerce): add Feature configuration surface`) and Attempt 2 correction commit `515c234` (`fix(commerce): address Feature surface review findings`) are pushed to `task/ARCH-021-COMMERCE-090`.

### Validation Results

- `npm exec -- vitest run tests/feature-configuration-page.test.tsx tests/feature-configuration-screen.test.tsx`: passed, 2 files / 8 tests.
- Attempt 2 `npm exec -- vitest run tests/feature-configuration-page.test.tsx tests/feature-configuration-screen.test.tsx tests/studio-shell.test.tsx`: passed, 3 files / 11 tests, including A1-R1 in-flight edit retention, A1-R2 stale gate/refresh, and A1-R3 unavailable shell status.
- Attempt 3 `npm exec -- vitest run tests/feature-configuration-page.test.tsx tests/feature-configuration-screen.test.tsx tests/studio-shell.test.tsx`: passed, 3 files / 13 tests, including both A2 regressions.
- Targeted ESLint on all six changed files: passed with no warnings or errors.
- Attempt 2 targeted ESLint on the route, Feature screen, shell, and regression test files: passed with no warnings or errors.
- Attempt 3 targeted ESLint on both changed files: passed with no warnings or errors.
- Pylance diagnostics on all six changed files: no errors found.
- Attempt 2 Pylance diagnostics on all seven changed files: no errors found.
- Attempt 3 Pylance diagnostics on both changed files: no errors found.
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

### Attempt 2 Changes-Requested Reconciliation

- A1-R1 is addressed in `src/studio/features/feature-configuration-screen.tsx`; the regression is in `tests/feature-configuration-screen.test.tsx` (“preserves edits made while an admitted save is unresolved”). An edit made after save admission remains visible and dirty; subsequent save uses the successful mutation's `editVersion`.
- A1-R2 is addressed in `src/studio/features/feature-configuration-screen.tsx`; the regression in `tests/feature-configuration-screen.test.tsx` (“keeps stale CAS gated through further edits until explicit refresh”) verifies local text retention, continued save blocking and successful retry only after canonical refresh.
- A1-R3 is addressed in `components/production-studio-page.tsx`; route-model assertions in `tests/feature-configuration-page.test.tsx` and actual shell rendering coverage in `tests/studio-shell.test.tsx` verify Feature authoring does not imply “No active release” and does not add `getShell` or shop-selection reads.

Attempt 2 launcher evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Reused exact parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-090` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-090`, both on `task/ARCH-021-COMMERCE-090`; neither shared checkout nor another task worktree was used.
- Parent `origin/main` was incorporated (`yes`); implementation `origin/main` was already current. Remote task branch fast-forward was `not-needed` for both.
- Recursive submodule sync and initialization passed; `database` is initialized at `e9fb60221f1532205650154dfff2aadb6270b14c`, status `ready`.
- The launcher claim is `a8d8873c4e5168a9c6538c00cb4263b11d1ace7a`. Attempt 2 implementation commit `515c234e8d9c3d8707e47d77e126394592583dee` is pushed to the mirrored task branch. No task branch was merged to `main`.
- Task status is `review`, `executor: null`, and `claimed_at: null`. The Architect Review section above is unchanged.

### Attempt 3 Changes-Requested Reconciliation

- A2-R1 is addressed in `src/studio/features/feature-configuration-screen.tsx`; the regression in `tests/feature-configuration-screen.test.tsx` covers a mutation at editVersion 5 followed by a concurrent refresh at editVersion 6 while newer local text is retained. The retry submits expectedEditVersion 5 and receives stale-CAS, preserving the local prompt.
- A2-R2 is addressed in `src/studio/features/feature-configuration-screen.tsx`; the navigation blocker treats pending saves as locked. The focused regression verifies an unresolved operation cannot be discarded and ordinary dirty-discard behavior resumes after completion.
- Attempt 3 launcher claim commit: `95385be8498798c3ae7cf579ef13e1064b40520a`, pushed on the parent `task/ARCH-021-COMMERCE-090` branch. The launcher reused the canonical parent and implementation worktrees, synchronized both task branches, and verified the recursive `database` submodule at `e9fb60221f1532205650154dfff2aadb6270b14c`.
- Implementation correction commit `1ccf345` is pushed on `origin/task/ARCH-021-COMMERCE-090`. No task branch was merged into `main`, and no database gitlink was staged.
- Parent status is `review`; `executor` and `claimed_at` are cleared. The existing Architect Review text remains unchanged.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 closes both remaining Attempt-2 findings and C090 is accepted.

**A2-R1 is resolved.** `FeatureDetail.save()` now adopts the successful mutation's `editVersion` immediately, but it only replaces the local prompt and advances again to the post-save refresh `editVersion` when `promptRevision` still matches the admitted revision. When newer local text exists, the local text remains paired with the mutation-returned CAS version rather than an unrelated later canonical version. The focused regression covers mutation version 5, a concurrent refresh at version 6 and a subsequent retry that still submits `expectedEditVersion: 5`, forcing stale-CAS rather than silently overwriting the concurrent change.

**A2-R2 is resolved.** The navigation blocker now classifies `pending` as locked (`locked || pending`). An admitted unresolved save therefore exposes only the pending-operation path and no discard action. The focused regression also proves that after the save resolves, ordinary dirty navigation returns to the normal discard-confirmation path.

The Attempt-3 implementation delta is limited to `feature-configuration-screen.tsx` and its focused regression tests. No unrelated runtime behavior was added. The recorded repository-wide TypeScript diagnostics remain outside the C090 changed-file set and are not a rejection reason for this task.

### Reviewed Files

- `src/studio/features/feature-configuration-screen.tsx`
- `tests/feature-configuration-screen.test.tsx`
- `components/studio-composer-context.tsx` for navigation-blocker semantics
- `components/production-studio-page.tsx`
- `tests/feature-configuration-page.test.tsx`
- `tests/studio-shell.test.tsx`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-088-implement-direct-feature-capability-authoring.md`
- Attempt-2 and Attempt-3 supplied C090 archives for bounded diff comparison

### Validation Reviewed

- Attempt-3 focused packet reported: 13/13 tests across `feature-configuration-page`, `feature-configuration-screen` and `studio-shell`.
- The new A2-R1 regression explicitly verifies the retained mutation CAS version across a concurrent post-save refresh.
- The new A2-R2 regression explicitly verifies non-discardable navigation while the save is unresolved and restoration of ordinary dirty-discard semantics after completion.
- Targeted ESLint reported clean for the Attempt-3 changed files.
- Changed-file diagnostics reported clean.
- `git diff --check` reported clean.
- Repository typecheck remains red with 271 diagnostics across 27 files outside the C090 changed-file set.
- The supplied archive does not contain Git metadata or installed `node_modules`, so pushed-ref cleanliness and the submitted Vitest/ESLint commands could not be independently rerun from the review artifact; source/test evidence and the durable Completion Report were inspected directly.

### Architecture Conformance

Conformant. C090 now satisfies R1-R6 and the full Behaviour-save contract. Feature identity remains read-only, Capability-to-Tool associations are human-readable, exactly one shared Behaviour prompt is CAS-safe, Add Capability remains navigation-only, removed concepts are absent from the Feature UX, and Feature-detail ownership is kept outside the generic workspace. The two concurrency/navigation defects identified during review are closed without broadening scope.

### Follow-up

`ARCH-021-COMMERCE-090` is **Complete / Accepted, Attempt 3**. Because `ARCH-021-COMMERCE-088` and C090 are both Complete, `ARCH-021-COMMERCE-091` is now **Ready**. C091 may be claimed through the normal `/moda-task` preparation path. `ARCH-021-COMMERCE-092` remains dependency-gated and must not start early.
