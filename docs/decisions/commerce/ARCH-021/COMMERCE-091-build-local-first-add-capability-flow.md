---
id: ARCH-021-COMMERCE-091
architecture_id: ARCH-021
title: Build the local-first Add Capability flow
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 94
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-088
  - ARCH-021-COMMERCE-090
enables:
  - ARCH-021-COMMERCE-092
created: 2026-09-29
updated: 2026-09-29
---

# Build the local-first Add Capability flow

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide a simple `Capability -> Tool -> Review` Feature-scoped authoring flow that keeps all new-Capability state local until the final Create action atomically assigns one existing Tool.

## Context

A Capability is not a miniature publication workflow. Its behaviour comes from an already-authored Tool and the Feature-level Behaviour prompt shared with sibling Capabilities.

The current flow persists a shell before a Tool is assigned, then requires a second Capability draft/editor. The accepted Tool creation work has already established the desired local-first principle: incomplete authoring belongs to the browser; durable identity is created only at the final save boundary.

This Capability flow is deliberately smaller than Tool creation because Tool Request/Response/Test/Result Template authoring already happened elsewhere.

## Scope

Primary implementation should live under the dedicated Feature domain introduced by COMMERCE-090, for example:

```text
src/studio/features/add-capability/*
src/studio/features/* contracts/state as required
app/features/[id]/* route integration
focused Add Capability UI tests
```

Use the existing Tool read service/library data and COMMERCE-088 `createFeatureCapability` mutation.

## Out of Scope

- Tool creation/editing/testing.
- Feature behaviour editing beyond the COMMERCE-090 surface.
- Release creation/runtime.
- Capability revision/history/publish UI.
- Billing/subscription/plan selection.
- Adding multiple Tools to one Capability.
- Final legacy route/API deletion (COMMERCE-092).

## Requirements

### R1 — exactly three authoring phases

Expose the sequence:

```text
Capability
Tool
Review
```

`Previous` / `Next` controls may guide traversal. Once a phase has sufficient local state to be enabled, direct clicking of that enabled phase must remain allowed; do not impose unnecessary forced sequential navigation.

### R2 — Capability phase owns only identity/display metadata

Collect:

```text
Capability key
Display name
Description
```

The parent Feature is already fixed by route/context and is shown read-only.

Do not collect a prompt, Capability type, binding type, configuration limits or Tool revisions.

### R3 — Tool phase selects one existing usable Tool

Display the existing Tool library in a user-readable selector. Each selectable Tool must currently be enabled and have at least one PUBLISHED revision, matching COMMERCE-088 final server validation.

The user selects a Tool identity only. Do not expose or ask them to choose a Tool revision.

### R4 — all pre-Create state is local/non-durable

Opening the flow, editing Capability fields, changing tabs/phases, selecting/changing the Tool, navigating Back or cancelling must perform zero Capability mutation Server Actions.

The browser may use component state/session state as appropriate for this bounded flow, but must not create orphaned durable Capability records.

### R5 — Review is derived and read-only

Review shows at least:

```text
Feature
the Feature Behaviour prompt relationship (summary, not an editable duplicate)
Capability key/display name/description
selected Tool
```

The Review phase does not own additional editable fields.

### R6 — final Create performs exactly one mutation

`Create capability` calls `createFeatureCapability` once with the complete candidate.

On success, navigate back to the Feature configuration surface and show the newly created Capability/Tool association.

On validation/replay/conflict failure, keep the local candidate available for correction/retry. Do not create a second row silently.

### R7 — no old Capability workflow terminology

The new flow contains no UI/action for:

```text
Create draft
Edit as new draft
Publish Capability
Capability revision
selectionBinding
BASE
RECOVERY_POLICY
maxSearchResults
maxRecommendations
Tool bindings
```

## Work Items

- [x] Add local authoring state for Capability metadata + one Tool identity.
- [x] Build Capability phase.
- [x] Build Tool selection phase from existing usable Tools.
- [x] Build derived read-only Review phase.
- [x] Add Previous/Next and enabled-phase direct navigation semantics.
- [x] Add Cancel/Back with zero persistence.
- [x] Wire final Create to exactly one COMMERCE-088 mutation.
- [x] Refresh/navigate to the parent Feature after success.
- [x] Preserve the local candidate across recoverable final-create failures.
- [x] Add mutation-spy regressions proving no create call before final Create.
- [x] Add final Create success/replay-recovery/conflict/error regressions.

## Interfaces / Contracts

Consumes:

```text
COMMERCE-088 createFeatureCapability
COMMERCE-088 Feature context
existing Tool read contract
```

No new cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-088
- ARCH-021-COMMERCE-090

## Enables

- ARCH-021-COMMERCE-092

## Acceptance Criteria

- [x] The visible sequence is exactly Capability -> Tool -> Review.
- [x] The author never selects a Capability type/binding, Tool revision, search limit or recommendation limit.
- [x] Only enabled Tools with at least one PUBLISHED revision are selectable.
- [x] No durable Capability exists before the final Create mutation succeeds.
- [x] Cancel/Back before Create causes zero Capability mutation calls.
- [x] Review is derived and read-only.
- [x] Final Create performs one `createFeatureCapability` call with the full candidate.
- [x] Success returns to the Feature and shows the new Capability with its assigned Tool.
- [x] Recoverable failures preserve the local candidate without duplicate rows.
- [x] Enabled phases remain directly clickable; the UI does not unnecessarily lock previously enabled navigation.

## Validation

- [x] Focused Add Capability, Feature configuration and Studio shell tests: 5 files, 20 tests passed on Attempt 2.
- [x] Explicit zero-mutation-before-final-Create regression.
- [x] Final-create success, committed-operation reconciliation (without duplicate mutation), conflict/correction and unavailable/error regression coverage.
- [x] Targeted ESLint passed for all four changed files on Attempt 2.
- [x] Changed-file diagnostics report no errors on Attempt 2. Attempt 1's `npm run typecheck` reported 271 TypeScript errors in 27 other files; none of the four task files appeared in its diagnostics.
- [x] `git diff --check` passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin legacy deletion.

## Implementation Notes

Prefer a small dedicated state machine/model over reusing Tool authoring state structures that carry irrelevant Request/Response/Test concepts.

## Completion Report

### Status

Ready for architect review (Attempt 2).

### Attempt 1 History (preserved)

- Implementation commit: `bdf7fd3` (`task(ARCH-021-COMMERCE-091): add local-first capability flow`); parent report submission commit: `4823d720`.
- Attempt 1 validation: 5 focused test files / 19 tests passed; targeted ESLint, changed-file diagnostics and `git diff --check` passed. Repository-wide typecheck reported 271 errors in 27 unrelated files.
- Architect Review requested changes only for live-predicate phase locking and missing `origin/main` incorporation evidence in the initial report. No local-first, mutation-safety or Tool eligibility correction was requested.

### Files Changed

- `app/features/[id]/capabilities/new/page.tsx`
- `src/studio/features/add-capability/add-capability-screen.tsx`
- `tests/add-capability-route.test.tsx`
- `tests/add-capability-screen.test.tsx`

### Work Completed

- Added an authenticated, force-dynamic Feature-scoped route that loads the Feature and filters the Tool library to enabled Tools with at least one PUBLISHED revision; only Tool identity/display data reaches the client.
- Added the local-only Capability -> Tool -> Review flow. Review derives the shared Feature behaviour-prompt relationship and all candidate details; one final action submits one `createFeatureCapability` call.
- Preserved the candidate after validation/conflict/unavailable outcomes. Pending or unknown outcomes lock edits/navigation and prevent duplicate submissions; committed outcomes reconcile to the Feature without retrying the mutation.
- Added route and UI tests for Tool filtering, zero pre-create mutation, exactly-one create, cancellation, committed-operation reconciliation, conflict correction, and candidate retention after errors.
- Attempt 2 added a monotonic `enabledThrough` phase frontier. Previously unlocked phases stay navigable while upstream candidate fields change; current candidate readiness independently gates Create.
- Review remains visible if the previously selected Tool is no longer eligible, displays that no eligible Tool is selected, and disables Create until current inputs are valid again.
- Added a regression covering first-unlock readiness, persistent direct navigation, Previous/Next after invalidation, unavailable selected Tool data, disabled/enabled Create readiness and zero mutations from all navigation actions.

### Validation Results

- `npm exec -- vitest run tests/add-capability-screen.test.tsx tests/add-capability-route.test.tsx tests/feature-configuration-screen.test.tsx tests/feature-configuration-page.test.tsx tests/studio-shell.test.tsx`: 5 files, 20 tests passed on Attempt 2.
- `npm exec -- eslint 'app/features/[id]/capabilities/new/page.tsx' src/studio/features/add-capability/add-capability-screen.tsx tests/add-capability-screen.test.tsx tests/add-capability-route.test.tsx`: passed.
- Changed-file diagnostics: no errors in the four task files on Attempt 2.
- Attempt 1 `npm run typecheck`: 271 errors in 27 files elsewhere in the Commerce repository; no diagnostic referenced a task file. No repository-wide typecheck was rerun for Attempt 2 because the review explicitly scoped its validation to the focused packet, targeted ESLint, changed-file diagnostics and diff check.
- `git diff --check`: passed.

### Deviations

- Added a locked navigation state while a create is pending or its outcome is unknown, retaining the original candidate/operation ID until reconciliation. Confirmed success explicitly bypasses that blocker to return to the Feature.

### Assumptions

- Returning through the existing Studio router to the force-dynamic Feature page reloads its server-provided Capability/Tool association after the mutation.

### Unresolved Issues

- The repository-wide typecheck remains red on 271 diagnostics across 27 files outside this task's changed files; ownership and resolution are outside COMMERCE-091.

### Architectural Concerns

None

### Git / VCS

Task branch: `task/ARCH-021-COMMERCE-091`

Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-091`
- parent branch: `task/ARCH-021-COMMERCE-091`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-091`
- implementation branch: `task/ARCH-021-COMMERCE-091`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Attempt 1 start-of-attempt synchronization (historical; preserved):
- parent remote task branch fast-forwarded: not needed; parent task branch was already at `origin/task/ARCH-021-COMMERCE-091`
- parent `origin/main` incorporated: no; the existing parent task branch does not contain current `origin/main`
- implementation remote task branch fast-forwarded: not needed; no remote implementation task branch existed
- implementation `origin/main` incorporated: already current at implementation branch creation

Attempt 1 review submission (historical; preserved):
- implementation commit: `bdf7fd3` (`task(ARCH-021-COMMERCE-091): add local-first capability flow`)
- implementation commit pushed to `origin/task/ARCH-021-COMMERCE-091`: yes
- parent report commit: `4823d720`; pushed to `origin/task/ARCH-021-COMMERCE-091`.

Attempt 2 launcher synchronization evidence:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-091`
- parent branch: `task/ARCH-021-COMMERCE-091`
- parent remote task-branch fast-forward: `not-needed`
- parent `origin/main` incorporated: `yes`
- parent synchronized HEAD: `d8f2f8b91b5ddc81b4b1ee79df7d18ef399ec214`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-091`
- implementation branch: `task/ARCH-021-COMMERCE-091`
- implementation remote task-branch fast-forward: `not-needed`
- implementation `origin/main` incorporated: `yes`
- implementation synchronized HEAD: `95e5a162dd26fec6cc3473b36da6b523761a501a`
- recursive submodule preparation: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; status `ready`; `database` initialized at `e9fb60221f1532205650154dfff2aadb6270b14c`.

Attempt 2 review submission:
- implementation commit: `4c49548` (`task(ARCH-021-COMMERCE-091): preserve unlocked authoring phases`), pushed to `origin/task/ARCH-021-COMMERCE-091`.
- parent report submission commit: `906ddc03` (`task(ARCH-021-COMMERCE-091): resubmit attempt 2 for review`), pushed to `origin/task/ARCH-021-COMMERCE-091`; this VCS-evidence line is its follow-up report amendment.

### Attempt 2 Architect Review Dispositions

- A — Implemented in `src/studio/features/add-capability/add-capability-screen.tsx`: added the session-local monotonic `enabledThrough` frontier and phase-index helpers. Verified by the focused navigation-frontier test and changed-file diagnostics.
- B — Implemented in `src/studio/features/add-capability/add-capability-screen.tsx`: first Tool/Review unlocks still require current metadata/Tool readiness; already unlocked destinations bypass predecessor readiness. Verified by the focused navigation-frontier test.
- C — Implemented in `src/studio/features/add-capability/add-capability-screen.tsx`: phase-tab disabled state is exactly the frontier plus pending/unknown locks; direct navigation changes only phase. Verified by the focused navigation-frontier test's enabled-state and zero-mutation assertions.
- D — Implemented in `src/studio/features/add-capability/add-capability-screen.tsx`: Previous returns to the immediately preceding phase without reducing the frontier; Next uses readiness only for first unlock. Verified by the focused navigation-frontier test.
- E — Implemented in `src/studio/features/add-capability/add-capability-screen.tsx`: Review remains renderable after unlock if the selected Tool becomes unavailable, while Create uses current `canReview` and the existing create guard. Verified by the focused regression's unavailable-Tool rerender and Create disabled/re-enabled assertions.
- F — Implemented/preserved in `src/studio/features/add-capability/add-capability-screen.tsx`: pending/unknown blocker, protected candidate fields and duplicate-submission guard remain; existing unknown-outcome reconciliation regression passes in the five-suite packet.
- G — Preserved in `src/studio/features/add-capability/add-capability-screen.tsx` and `tests/add-capability-screen.test.tsx`: one final mutation, local-only pre-create state, candidate retention, Tool identity-only selection and reconciliation remain intact. Verified by the five-suite 20-test packet.
- H — Implemented in `tests/add-capability-screen.test.tsx`: deterministic regression covers initial lock state, both first unlocks, invalidation, direct phase navigation, Previous/Next, stale Tool eligibility, Create gating, zero navigation mutations and continued reconciliation-lock coverage. Five focused suites passed, 20 tests total.
- I — Implemented through the canonical launcher before claim; no manual synchronization bypass. Launcher packet records both dedicated paths/branches, both `origin/main` incorporation results as `yes`, synchronized HEADs and recursive submodule readiness/commit above. No additional synchronization edits were required.

## Architect Review

### Review Status

Accepted

### Review Notes

COMMERCE-091 Attempt 2 is **Accepted / Complete**.

Attempt 2 satisfies the exact correction contract from the previous Architect Review without reopening the accepted local-first Capability design.

The reviewed implementation now has one session-local monotonic `enabledThrough` frontier over:

```text
Capability -> Tool -> Review
```

and keeps navigation access separate from current candidate readiness:

- `Capability -> Tool` requires current `validCapability` only for the first unlock;
- `Tool -> Review` requires current `canReview` only for the first unlock;
- once Tool or Review has been unlocked, later upstream edits do not re-lock it;
- direct phase clicks use the unlock frontier rather than live `validCapability` / `canReview` predicates;
- Previous never lowers the frontier;
- Next reuses an already-unlocked destination without re-checking predecessor readiness;
- pending / unknown-outcome state continues to lock navigation independently of the normal authoring frontier.

The final Create boundary is also corrected independently from navigation access. Review may remain visible after an upstream edit or when the previously selected Tool is no longer present in the eligible Tool set, while:

```tsx
disabled={!canReview || pending || outcomeUnknown}
```

keeps `Create capability` unavailable until the **current** candidate is valid again. The existing `create()` guard remains in place, so an accessible stale Review cannot issue a Capability mutation.

The focused Attempt 2 regression proves the required lifecycle: initial lock state, both first unlocks, upstream invalidation after unlock, direct phase navigation, Previous/Next traversal, selected-Tool eligibility loss/recovery, Create disable/re-enable behaviour and zero Capability mutations caused by navigation. Existing exactly-one-create and unknown-outcome reconciliation coverage continues to pass.

The Attempt 1 start-of-attempt synchronization non-conformance is corrected. The Completion Report records canonical launcher preparation for both dedicated task worktrees with `origin/main incorporated: yes`, synchronized HEADs and recursive submodule preparation evidence. Attempt 1 history remains preserved.

The original C091 architectural invariants remain intact:

- Capability authoring is browser-local until the final Create boundary;
- only enabled Tools with at least one PUBLISHED revision are selectable;
- the author selects one Tool identity, not a Tool revision;
- Review is derived/read-only;
- final Create performs one `createFeatureCapability` mutation;
- recoverable/uncertain outcomes preserve the candidate and avoid blind duplicate mutation;
- no legacy Capability revision/binding/type/limit authoring is reintroduced.

### Reviewed Files

- `docs/decisions/commerce/ARCH-021/COMMERCE-091-build-local-first-add-capability-flow.md`
- `src/studio/features/add-capability/add-capability-screen.tsx`
- `tests/add-capability-screen.test.tsx`
- `app/features/[id]/capabilities/new/page.tsx`
- `tests/add-capability-route.test.tsx`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- `docs/decisions/commerce/ARCH-021/_index.md`

### Validation Reviewed

Attempt 2 submitted evidence:

- focused Add Capability / Feature configuration / Studio shell packet: **5 suites, 20 tests passed**;
- targeted ESLint: passed;
- changed-file diagnostics: clean;
- `git diff --check`: passed;
- Attempt 1 repository-wide `npm run typecheck` remains documented at 271 diagnostics across 27 files outside C091's four changed implementation/test files.

The Attempt 2 implementation and focused regression source were inspected directly from the submitted review snapshot. The supplied review archive does not include installed dependencies, so the focused commands were not independently rerun in this review environment. Nothing in the inspected C091 changes introduces a task-owned diagnostic or requires reopening the unrelated repository-wide typecheck baseline.

### Architecture Conformance

Accepted.

C091 conforms to the Phase 5 Feature/Capability authoring model and to the Attempt 2 navigation-frontier correction contract. Navigation accessibility is monotonic after first unlock, persistence remains final-Create-only, and current candidate readiness remains authoritative for mutation admission.

### Follow-up

Set `ARCH-021-COMMERCE-091` to **Complete**.

C091's dependency edge into COMMERCE-092 is now satisfied. COMMERCE-092 remains **Pending** until its other declared dependencies (`COMMERCE-089` and `BACKGROUND-002`) are also architect-accepted Complete.

Do not start COMMERCE-092 solely because C091 is complete.
