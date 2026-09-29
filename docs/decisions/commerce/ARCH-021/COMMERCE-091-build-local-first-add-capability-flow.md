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
status: review
priority: 94
executor: null
claimed_at: null
attempt: 1
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
