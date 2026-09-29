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
status: ready
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

Changes Requested

### Review Notes

Attempt 1 is not accepted. The dedicated Feature surface is directionally conformant: Feature identity is read-only, Capability -> Tool associations are human-readable, the old immediate Capability mutation UI is removed, one shared Behaviour prompt is exposed, and `Add capability` performs navigation only. The focused route split also correctly avoids reintroducing billing/subscription eligibility into Feature authoring.

Three corrections remain inside C090 scope:

**A1-R1 — preserve edits made after a save has been admitted.** `FeatureDetail.save()` unconditionally applies the returned/refreshed canonical prompt and clears dirty state after a successful mutation. The textarea remains editable while `pending`, so text entered after the request starts can be silently overwritten when the earlier save resolves. Preserve the established Studio save invariant: either prevent editing for the complete admitted save interval or track a content/admission revision and only replace/clear local state when no newer edit exists. Add a focused regression that edits the Behaviour prompt while the save promise is unresolved and proves the newer text is not silently lost.

**A1-R2 — stale CAS must remain gated until explicit refresh.** After a `STALE_CAS`, the UI correctly sets `conflict`, but the textarea `onChange` immediately calls `setConflict(false)`. A single subsequent edit therefore re-enables `Save behaviour` with the same stale `editVersion`, contradicting the displayed instruction and the Completion Report's claimed explicit-refresh contract. Editing may retain the user's local text, but it must not clear the stale-CAS gate. Add a regression: stale CAS -> edit again -> Save remains unavailable and Refresh remains required; after refresh, a new edit may save against the refreshed editVersion.

**A1-R3 — do not report an unverified release state from the extracted Feature route.** `ProductionStudioPage` intentionally skips `getShell()` for Features, but then renders `StudioShell` with `shell === undefined`; `StudioShell` maps that to `No active release`. That is a false assertion whenever an active release exists. Keep Feature authoring independent of billing/shop selection and do not reintroduce a publication aggregate read merely for this task, but pass/render an explicit unavailable/not-loaded release state (or otherwise suppress the release claim) so the shell never turns an omitted read into `No active release`. Add a focused route/shell regression for this state.

The recorded repository-wide TypeScript diagnostics and the six neighboring generic `StudioWorkspace` failures are not, by themselves, C090 rejection reasons because the inspected C090 diff does not modify those generic editor behaviours. They should remain recorded, and the correction attempt must still show no changed-file diagnostics plus the focused Feature packet, targeted ESLint and `git diff --check`.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `components/studio-shell.tsx` (interaction with the new Feature route)
- `components/studio-composer-context.tsx` (navigation-blocker semantics)
- `src/studio/features/feature-configuration-screen.tsx`
- `src/studio/features/contracts.ts`
- `src/studio/features/services.ts`
- `src/studio/features/reconciliation-server-actions.ts`
- `tests/feature-configuration-page.test.tsx`
- `tests/feature-configuration-screen.test.tsx`
- `tests/studio-workspace.test.tsx`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-088-implement-direct-feature-capability-authoring.md`

### Validation Reviewed

- Focused Feature packet reported: 8/8 tests across two files.
- Targeted ESLint reported clean for the six changed files.
- Changed-file diagnostics reported clean.
- `git diff --check` reported clean.
- Repository typecheck remains red with 271 diagnostics outside the C090 changed-file set.
- Neighboring `StudioWorkspace` suite reported 7 passed / 6 failed in generic editor workflows; the inspected C090 diff removes legacy Feature ownership but does not alter those generic workflows.
- The supplied archive does not preserve Git metadata, so pushed commit/remote-cleanliness claims were reviewed from the durable Completion Report rather than independently rerun from the archive.

### Architecture Conformance

Partially conformant. R1, R2, R4, R5 and the dedicated ownership direction of R6 are implemented. R3 is not yet acceptable because the save state machine can lose post-submit edits and the stale-CAS gate is not durable until refresh. The route extraction also introduces a false shell release-status presentation that must be corrected without adding billing/subscription coupling.

### Follow-up

Return **ARCH-021-COMMERCE-090** to `ready` for Attempt 2 with the three corrections above. Preserve `attempt: 1`; the next authorized claim increments it. `ARCH-021-COMMERCE-091` remains Pending and must not start until C090 is architect-accepted Complete.
