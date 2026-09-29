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

Changes Requested

### Review Notes

Attempt 2 resolves all three Attempt-1 findings: post-submit local edits are no longer overwritten merely because the admitted save completes; stale-CAS remains gated through further edits until explicit refresh; and Feature routes now pass an explicit unavailable release model so an omitted shell read is not rendered as `No active release`. The focused regressions cover those three corrections.

Two corrections remain inside C090's Behaviour-save/navigation scope:

**A2-R1 — do not advance CAS to a newer canonical version while preserving local text based on an older version.** After a successful mutation, `FeatureDetail.save()` first adopts the mutation result's `editVersion`, which is safe. It then always adopts `refreshed.value.editVersion`, even when `promptRevision` proves newer local edits exist and the refreshed prompt is deliberately *not* adopted. If another actor updates the Feature between this client's successful mutation and its refresh, the refresh can return a later canonical version. The current code then pairs local text derived from the older version with that later `editVersion`; the next Save can therefore pass CAS and overwrite the concurrent canonical change without surfacing a stale conflict. Never pair preserved local text with a canonical version it was not based on. A minimal acceptable correction is to keep the successful mutation's returned `editVersion` while newer local edits exist; if the post-save refresh reveals a different version, either retain the older expected version so the next Save naturally CAS-conflicts, or explicitly enter the stale/conflict gate while preserving the local text. Add a regression: mutation commits version 5 -> user edits while the save is unresolved -> refresh returns version 6 with different canonical prompt -> the UI preserves the user's text but must not permit a retry using `expectedEditVersion: 6` without an explicit reconciliation/rebase path.

**A2-R2 — an admitted pending save must not be discardable navigation state.** Attempt 2 adds `pending` to `blocked`, but the blocker still passes `locked` rather than `locked || pending`. During an unresolved save, Studio therefore presents the ordinary `Discard unsaved changes` path. Choosing it can navigate away while the already-admitted mutation continues and may commit, so the UI cannot truthfully describe that action as discarding the operation. Treat an unresolved admitted save as locked/unconfirmed navigation state (or provide equivalent non-discardable semantics). Add a focused regression with an unresolved save promise: navigation away must show the pending-operation/locked path and must not expose `Discard unsaved changes`; once the operation is resolved and ordinary unsaved edits remain, normal dirty-discard semantics may resume.

The repository-wide 271 TypeScript diagnostics and the neighboring generic `StudioWorkspace` failures remain recorded but are not C090 rejection reasons because they are outside the inspected C090 changed-file set.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-shell.tsx`
- `components/studio-composer-context.tsx`
- `src/studio/features/feature-configuration-screen.tsx`
- `src/studio/features/contracts.ts`
- `src/studio/features/services.ts`
- `src/studio/features/persistence.ts`
- `tests/feature-configuration-page.test.tsx`
- `tests/feature-configuration-screen.test.tsx`
- `tests/studio-shell.test.tsx`
- prior Attempt-1 C090 archive for a bounded Attempt-2 diff comparison
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-088-implement-direct-feature-capability-authoring.md`

### Validation Reviewed

- Attempt-2 focused packet reported: 11/11 tests across `feature-configuration-page`, `feature-configuration-screen` and `studio-shell`.
- Targeted ESLint reported clean.
- Changed-file diagnostics reported clean.
- `git diff --check` reported clean.
- Repository typecheck remains red with 271 diagnostics across 27 files outside the C090 changed-file set.
- The current and prior supplied C090 archives were compared directly; the Attempt-2 runtime delta is bounded to the review corrections in `feature-configuration-screen.tsx` and `production-studio-page.tsx`, with the corresponding focused test updates.
- The supplied archive does not contain Git metadata or installed `node_modules`, so pushed commit/remote cleanliness and the submitted Vitest/ESLint commands could not be independently rerun from this review artifact; those items were reviewed from the durable Completion Report and source/test evidence.

### Architecture Conformance

Partially conformant. Attempt 2 satisfactorily closes A1-R1, A1-R2 and A1-R3. R1, R2, R4, R5 and the dedicated ownership direction of R6 remain conformant. R3 is still not fully acceptable because the post-save refresh can advance CAS past the version on which preserved local text is based, creating a silent concurrent-overwrite path. The new pending-navigation blocker also needs non-discardable semantics while an admitted save is unresolved.

### Follow-up

Return **ARCH-021-COMMERCE-090** to `ready` for Attempt 3 with A2-R1 and A2-R2 above as the complete correction contract. Preserve `attempt: 2`; the next authorized claim increments it exactly once. `ARCH-021-COMMERCE-091` remains Pending and must not start until C090 is architect-accepted Complete.
