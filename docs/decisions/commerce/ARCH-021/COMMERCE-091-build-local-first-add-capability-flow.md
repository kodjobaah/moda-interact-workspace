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
status: in_progress
priority: 94
executor: copilot
claimed_at: 2026-09-29T16:50:42Z
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

- [x] Focused Add Capability, Feature configuration and Studio shell tests: 5 files, 19 tests passed.
- [x] Explicit zero-mutation-before-final-Create regression.
- [x] Final-create success, committed-operation reconciliation (without duplicate mutation), conflict/correction and unavailable/error regression coverage.
- [x] Targeted ESLint passed for all four changed files.
- [x] Changed-file diagnostics report no errors. `npm run typecheck` was also run and reports 271 TypeScript errors in 27 other files; none of the four task files appear in its diagnostics.
- [x] `git diff --check` passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin legacy deletion.

## Implementation Notes

Prefer a small dedicated state machine/model over reusing Tool authoring state structures that carry irrelevant Request/Response/Test concepts.

## Completion Report

### Status

Ready for architect review (Attempt 1).

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

### Validation Results

- `npm exec -- vitest run tests/add-capability-screen.test.tsx tests/add-capability-route.test.tsx tests/feature-configuration-screen.test.tsx tests/feature-configuration-page.test.tsx tests/studio-shell.test.tsx`: 5 files, 19 tests passed.
- `npm exec -- eslint 'app/features/[id]/capabilities/new/page.tsx' src/studio/features/add-capability/add-capability-screen.tsx tests/add-capability-screen.test.tsx tests/add-capability-route.test.tsx`: passed.
- Changed-file diagnostics: no errors in the four task files.
- `npm run typecheck`: failed with 271 errors in 27 files elsewhere in the Commerce repository; no diagnostic references any task file. These unrelated diagnostics were not changed as part of this task.
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

Start-of-attempt synchronization:
- parent remote task branch fast-forwarded: not needed; parent task branch was already at `origin/task/ARCH-021-COMMERCE-091`
- parent `origin/main` incorporated: no; the existing parent task branch does not contain current `origin/main`
- implementation remote task branch fast-forwarded: not needed; no remote implementation task branch existed
- implementation `origin/main` incorporated: already current at implementation branch creation

Review submission:
- implementation commit: `bdf7fd3` (`task(ARCH-021-COMMERCE-091): add local-first capability flow`)
- implementation commit pushed to `origin/task/ARCH-021-COMMERCE-091`: yes
- parent task report is committed and pushed on `task/ARCH-021-COMMERCE-091` as this review submission.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is accepted in substance for the local-first persistence boundary, Tool eligibility filtering, derived read-only Review surface, exactly-one final `createFeatureCapability` mutation and unknown-outcome reconciliation.

Attempt 2 is narrowly bounded to **navigation-frontier correctness plus workflow synchronization evidence**. Do not redesign the Capability flow and do not begin COMMERCE-092.

#### A. Replace live-predicate phase locking with a monotonic unlock frontier

The current `AddCapabilityFlow` derives phase access directly from the current candidate:

```ts
const enabled =
  item === 'Capability' ||
  (item === 'Tool' && validCapability) ||
  (item === 'Review' && canReview);
```

and `goTo()` re-checks the same live predicates.

That violates R1 / the Acceptance Criterion that a phase remains directly clickable after it has been enabled. A later edit to an upstream field currently re-locks Tool/Review.

Implement one session-local monotonic access frontier for this **new Capability authoring session only**.

Use these exact phase identifiers and order:

```ts
type Phase = 'Capability' | 'Tool' | 'Review';

const phases: Phase[] = [
  'Capability',
  'Tool',
  'Review',
];
```

Add one local state value with initial value `Capability`:

```ts
const [enabledThrough, setEnabledThrough] =
  useState<Phase>('Capability');
```

The exact helper semantics must be equivalent to:

```ts
function phaseIndex(candidate: Phase): number {
  return phases.indexOf(candidate);
}

function isPhaseEnabled(candidate: Phase): boolean {
  return phaseIndex(candidate) <= phaseIndex(enabledThrough);
}

function unlockThrough(candidate: Phase): void {
  if (phaseIndex(candidate) > phaseIndex(enabledThrough)) {
    setEnabledThrough(candidate);
  }
}
```

Do not store one boolean per phase. Do not derive access from `validCapability` / `canReview` after a phase has already been unlocked.

#### B. Exact first-unlock rules

First-time forward unlock remains validation/readiness-gated:

```text
Capability -> Tool
    first unlock requires validCapability === true

Tool -> Review
    first unlock requires canReview === true
```

On successful first-time forward traversal:

```text
Capability -> Tool
    unlockThrough('Tool')
    setPhase('Tool')

Tool -> Review
    unlockThrough('Review')
    setPhase('Review')
```

Once a destination is already enabled, navigation to it MUST NOT re-check its predecessor readiness.

Therefore this is required:

```text
Tool was previously unlocked
user returns to Capability
user makes Capability invalid
Tool remains enabled/clickable
direct Tool click succeeds
```

and:

```text
Review was previously unlocked
user returns upstream
user makes Capability invalid or clears/replaces the Tool
Review remains enabled/clickable
direct Review click succeeds
```

Navigation access and candidate readiness are separate concerns.

#### C. Exact direct-tab navigation contract

For the phase-tab buttons:

```text
disabled = !isPhaseEnabled(item) || pending || outcomeUnknown
```

Do not use current `validCapability` or `canReview` to disable a phase that is already within `enabledThrough`.

The active phase remains represented by `aria-current="step"` exactly as today.

A direct click on an enabled phase changes only the active phase. It must not:

- run validation;
- call `createFeatureCapability`;
- generate a new operation id merely because navigation occurred;
- alter the selected Tool;
- alter candidate fields;
- lower `enabledThrough`.

#### D. Exact Previous / Next semantics

`Previous` never performs validation and never lowers `enabledThrough`.

Exact Previous destinations:

```text
Tool   -> Capability
Review -> Tool
```

For `Next`:

```text
Capability -> Tool
Tool       -> Review
```

If the destination has never been unlocked, use the first-unlock predicate from section B.

If the destination is already enabled, `Next` navigates there even if the current predecessor has since become invalid/stale.

Do not add forced sequential traversal after a phase has been unlocked.

#### E. Review may remain accessible while Create becomes invalid

After Review has been unlocked, upstream edits may make the current candidate invalid. Review must remain accessible because access is controlled by `enabledThrough`.

Create readiness remains controlled by the **current** candidate.

Change the final button gate from the current equivalent of:

```tsx
disabled={pending || outcomeUnknown}
```

to:

```tsx
disabled={!canReview || pending || outcomeUnknown}
```

The existing `create()` guard:

```ts
if (!canReview || submitting.current || pending || outcomeUnknown) return;
```

must remain.

This means:

```text
Review unlocked earlier
    +
current Capability metadata invalid
or current selected Tool absent
    ->
Review remains clickable
Create capability is disabled
zero create mutation occurs
```

When the current candidate becomes valid again, Create may re-enable without requiring Tool/Review to be unlocked again.

#### F. Preserve pending / unknown-outcome locking

Do not weaken the accepted mutation-safety behavior.

While `pending || outcomeUnknown`:

- keep navigation locked as currently implemented;
- keep candidate edits protected as currently implemented;
- do not unlock or traverse phases merely because the monotonic frontier exists;
- do not issue a duplicate create mutation.

The monotonic frontier applies to normal authoring navigation only; it does not override the existing admitted/uncertain-operation lock.

#### G. Preserve all local-first persistence invariants

Attempt 2 must not change these accepted C091 behaviors:

- opening/editing/traversing/cancelling performs zero Capability mutation;
- only the final Create action calls `createFeatureCapability`;
- exactly one existing Tool identity is submitted;
- no Tool revision is selected in the UI;
- recoverable create failures preserve the local candidate;
- an unknown outcome is reconciled instead of blindly replaying the mutation;
- successful create returns to the Feature configuration surface;
- old Capability revision/binding/type/limit terminology stays absent.

Do not add a database, Shared, Background or release/runtime change.

#### H. Required executable regressions

Extend `tests/add-capability-screen.test.tsx` with deterministic regressions proving all of the following:

```text
1. Initial state:
   Capability enabled
   Tool disabled
   Review disabled

2. Enter valid Capability metadata.
   Use Next or the newly enabled Tool tab to unlock Tool.

3. Return to Capability.
   Clear Display name (or otherwise make validCapability false).
   Tool remains enabled and directly clickable.

4. While Capability is invalid and Tool is already unlocked:
   clicking Tool succeeds;
   no createFeatureCapability call occurs.

5. Restore valid Capability metadata.
   Select the eligible Tool.
   Unlock Review.

6. Return to Capability.
   Make Capability invalid again.
   Tool and Review both remain enabled and directly clickable.

7. Navigate directly to Review while the current candidate is invalid.
   Review renders.
   `Create capability` is disabled.
   `createFeatureCapability` has not been called.

8. Restore the Capability to a valid current state.
   Review remains unlocked.
   `Create capability` becomes enabled without any re-unlock step.

9. From Review use Previous to Tool, then Previous to Capability.
   `enabledThrough` remains Review-equivalent;
   Tool and Review are still directly clickable.

10. Once Review is unlocked, clearing/changing Tool selection or otherwise
    making `canReview` false does not re-lock Review; it only disables Create.

11. Phase clicks, Previous, Next, unlock operations and upstream invalidation
    perform zero Capability mutation Server Actions.

12. Existing pending / unknown-outcome navigation locking and reconciliation
    regressions continue to pass.
```

If implementation structure makes test 10 impossible because Tool selection currently cannot be cleared from the UI, prove the equivalent by making another `canReview` dependency false without changing the accepted product surface. Do not add a new "clear Tool" feature solely for the test.

#### I. Start-of-attempt synchronization correction

Attempt 1's Completion Report records:

```text
parent origin/main incorporated: no
```

That is workflow non-conformance under the mandatory task-worktree isolation/startup policy.

Before Attempt 2 implementation begins, the canonical launcher/preparation path MUST synchronize the dedicated C091 parent and implementation worktrees according to current `origin/main`.

The Attempt 2 Completion Report must record launcher-resolved evidence for both worktrees, including:

```text
parent worktree path
parent branch
parent remote task-branch fast-forward result
parent origin/main incorporated: yes | already-current
parent synchronized HEAD

implementation worktree path
implementation branch
implementation remote task-branch fast-forward result
implementation origin/main incorporated: yes | already-current
implementation synchronized HEAD

recursive submodule preparation evidence
```

Do not manually bypass the launcher by executing Attempt 2 from a stale/shared checkout.

If preparation cannot incorporate current `origin/main`, stop before claim and return the synchronization conflict to `moda_architect`.

Preserve all Attempt 1 history. Do not rewrite or remove the Attempt 1 Completion Report.

### Reviewed Files

- `docs/decisions/commerce/ARCH-021/COMMERCE-091-build-local-first-add-capability-flow.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- `docs/decisions/commerce/ARCH-021/_index.md`
- `moda-interact-commerce/src/studio/features/add-capability/add-capability-screen.tsx`
- `moda-interact-commerce/tests/add-capability-screen.test.tsx`
- `moda-interact-commerce/app/features/[id]/capabilities/new/page.tsx`
- `moda-interact-commerce/tests/add-capability-route.test.tsx`

### Validation Reviewed

Attempt 1 evidence reviewed:

- focused Add Capability / Feature configuration / Studio shell packet: 5 files, 19 tests passed;
- targeted ESLint passed for the four C091 changed files;
- changed-file diagnostics are clean;
- repository-wide `npm run typecheck` remains red on 271 diagnostics in 27 files outside the four C091 task files;
- `git diff --check` passed.

The repository-wide unrelated diagnostics do not by themselves block this bounded correction. Attempt 2 must rerun the C091-focused packet plus the new navigation-frontier regressions, targeted ESLint, changed-file diagnostics and `git diff --check`.

### Architecture Conformance

Changes Requested.

The local-first persistence boundary, Tool eligibility, Review derivation, exactly-one final create mutation and uncertain-outcome reconciliation conform. The current phase-access implementation does not conform because it re-locks previously enabled phases using live `validCapability` / `canReview` predicates. The parent start-of-attempt synchronization evidence also does not conform.

### Follow-up

Return the SAME `ARCH-021-COMMERCE-091` task through `/moda-task` for Attempt 2 after this parent review update is committed/pushed.

Task state for rework:

```text
status: ready
executor: null
claimed_at: null
attempt: 1
```

The next authorized launcher claim increments to Attempt 2.

COMMERCE-092 remains dependency-gated and MUST NOT start until C091 is architect-accepted Complete.
