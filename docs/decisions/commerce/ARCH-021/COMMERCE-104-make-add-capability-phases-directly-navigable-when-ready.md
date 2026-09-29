---
id: ARCH-021-COMMERCE-104
architecture_id: ARCH-021
title: Make Add Capability phases directly navigable when ready
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-091
enables:
  - ARCH-021-SYSTEM-TEST-003
created: 2026-09-29
updated: 2026-09-29
---

# Make Add Capability phases directly navigable when ready

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Correct the existing `Capability -> Tool -> Review` Add Capability flow so a phase button becomes directly clickable as soon as the **current local candidate satisfies that phase's first-entry prerequisite**, while preserving COMMERCE-091's monotonic unlock frontier, local-first/no-persistence authoring model, current-candidate Create gating and unknown-outcome navigation lock.

## Context

COMMERCE-091 established the local-first three-phase Add Capability flow and a session-local monotonic `enabledThrough` frontier. Its accepted implementation deliberately separates navigation access from current mutation readiness after a phase has been unlocked.

Manual validation exposed one remaining first-entry defect in that model.

The current implementation in:

```text
src/studio/features/add-capability/add-capability-screen.tsx
```

uses:

```ts
function isPhaseEnabled(candidate: Phase): boolean {
  return phaseIndex(candidate) <= phaseIndex(enabledThrough);
}
```

and phase buttons use:

```tsx
disabled={!isPhaseEnabled(item) || pending || outcomeUnknown}
```

`goTo()` is capable of first-unlocking `Tool` when `validCapability` is true and first-unlocking `Review` when `canReview` is true, but a disabled phase button cannot call `goTo()` in the first place. Therefore the author must press `Next` to unlock a phase even when the visible phase button already has enough current local state to be usable.

Observed example:

```text
Capability key valid
Display name valid
Description valid
        |
        v
validCapability = true
        |
        v
Tool button remains disabled
        |
        v
only Next can unlock Tool
```

This task corrects only that first-entry navigation admission gap. It does not reopen the accepted persistence, Tool eligibility, final Create, reconciliation or Feature/Capability data model.

## Scope

The implementation scope is deliberately narrow.

Primary source file:

```text
src/studio/features/add-capability/add-capability-screen.tsx
```

Primary regression file:

```text
tests/add-capability-screen.test.tsx
```

`tests/add-capability-route.test.tsx` may be executed as validation but should not require source changes.

Do not modify server actions, contracts, database code, routes, Tool eligibility queries, Feature configuration data loading or styles for this task. If the required behaviour cannot be implemented within the two primary files above, stop and return the concrete blocker to `moda_architect` rather than broadening scope.

## Out of Scope

- Changing the three-phase order.
- Adding/removing Capability fields.
- Changing which Tools are eligible/selectable.
- Creating a Tool from the Add Capability flow.
- Changing Feature Behaviour editing.
- Changing `createFeatureCapability` or reconciliation contracts.
- Persisting any candidate state before final Create.
- Reintroducing Capability revisions, bindings, limits or legacy Capability terminology.
- Converting the step navigation to a new design system or changing CSS/layout.
- Changing Tool-authoring navigation owned by COMMERCE-095/103.
- Changing single-flight Tool-authoring behaviour owned by COMMERCE-102.

## Requirements

### R1 — canonical phase order is unchanged

The only phases remain, in this exact order:

```text
Capability
Tool
Review
```

Keep the existing `Phase` union and `phases` order unless an equivalent typed representation is required by the same file.

### R2 — separate historical unlock from current first-entry readiness

The implementation MUST distinguish these two concepts instead of treating `enabledThrough` as the only enabled-state predicate.

Use semantics equivalent to:

```ts
phaseUnlocked(candidate) =
  phaseIndex(candidate) <= phaseIndex(enabledThrough)

phaseReadyForFirstEntry('Capability') = true
phaseReadyForFirstEntry('Tool')       = validCapability
phaseReadyForFirstEntry('Review')     = canReview

phaseAvailable(candidate) =
  phaseUnlocked(candidate) || phaseReadyForFirstEntry(candidate)
```

The exact helper names may differ, but the truth table below is authoritative.

| Phase | Never unlocked + current candidate not ready | Never unlocked + current candidate ready | Previously unlocked + current candidate later invalid |
|---|---|---|---|
| Capability | Available | Available | Available |
| Tool | Unavailable | Available when `validCapability === true` | Available |
| Review | Unavailable | Available when `canReview === true` | Available |

`pending` and `outcomeUnknown` are independent global navigation locks and still disable phase navigation regardless of this table.

### R3 — direct phase click must perform first unlock

When the author clicks a phase button:

```text
if pending || outcomeUnknown
    -> do nothing

else if destination is already unlocked
    -> set active phase to destination

else if destination is currently ready for first entry
    -> monotonically unlock through destination
    -> set active phase to destination

else
    -> do nothing
```

Do **not** require the currently active phase to be the immediate predecessor as an additional first-unlock condition.

Concrete required scenario:

```text
1. enter valid Capability metadata
2. click Tool directly (without pressing Capability Next)
3. select an eligible Tool
4. return to Capability using Previous or Capability button
5. click Review directly (without pressing Tool Next)
```

Step 2 and step 5 must both succeed when their live readiness predicate is true.

### R4 — unlock remains monotonic for the browser authoring session

Once `Tool` has been unlocked, later invalid Capability metadata must not lock `Tool` again.

Once `Review` has been unlocked, later invalid Capability metadata or loss of current Tool eligibility must not lock `Review` again.

`enabledThrough` must therefore remain monotonic. `Previous`, direct backward navigation and candidate edits must never lower it.

This requirement preserves the accepted COMMERCE-091 correction semantics.

### R5 — before first unlock, readiness remains live

A phase that is merely **ready** but has not yet been unlocked may become unavailable again if the author invalidates the current candidate before entering it.

Required examples:

```text
valid Capability -> Tool available
invalidate Display name before entering Tool -> Tool unavailable
revalidate Display name -> Tool available again
```

and, before Review has ever been entered:

```text
valid Capability + eligible selected Tool -> Review available
remove/currently lose selected Tool readiness -> Review unavailable
```

After first unlock, R4 takes precedence and the phase remains navigable.

### R6 — Previous/Next use the same availability model

Keep the existing footer navigation.

`Next` from `Capability` targets only `Tool`.

`Next` from `Tool` targets only `Review`.

For each `Next` button:

```text
disabled = destination is not phaseAvailable
           OR pending
           OR outcomeUnknown
```

Clicking `Next` must use the same navigation/unlock path as direct phase clicking; do not maintain a second first-unlock implementation with different rules.

`Previous` from `Tool` targets `Capability`.

`Previous` from `Review` targets `Tool`.

`Previous` is disabled only by the existing pending/unknown lock and never reduces the unlock frontier.

### R7 — phase navigation remains side-effect free

The following actions must perform zero Capability mutation/reconciliation calls:

```text
direct Capability/Tool/Review phase click
Previous
Next
```

Specifically, navigation must not call:

```text
createFeatureCapability
reconcileFeatureOperation
```

It must not create durable Capability state, change the selected Tool implicitly, validate through a server action, or navigate away from the current Add Capability route.

Local `phase` / `enabledThrough` state changes are expected and are not persistence.

### R8 — final Create admission remains current-candidate authoritative

Do not weaken or replace the existing final Create rule:

```ts
canReview = validCapability && selectedTool !== undefined
```

`Create capability` must remain disabled when `canReview` is false even if `Review` is historically unlocked and visible.

The existing `create()` guard against:

```text
!canReview
submitting.current
pending
outcomeUnknown
```

must remain effective.

### R9 — pending/unknown-outcome safety is unchanged

During a pending create/reconcile operation or an unknown create outcome:

- phase buttons remain locked according to the existing safety boundary;
- Previous/Next remain locked;
- protected candidate editing behaviour remains unchanged;
- reconciliation continues to use the original operation identity;
- this task must not introduce a way to bypass the navigation blocker.

### R10 — existing Tool eligibility is unchanged

Do not change how `eligibleTools` or `selectedTool` are derived.

Only the Tool identities already supplied by the existing server path remain selectable. This task must not broaden Tool eligibility or synthesize/fallback a selected Tool.

## Work Items

- [ ] Split historical unlock and current first-entry readiness into explicit predicates in `add-capability-screen.tsx`.
- [ ] Make each phase button available from `historically unlocked OR currently ready for first entry`, then apply the existing pending/unknown global lock.
- [ ] Update `goTo()` so a direct click on a currently ready first-entry destination monotonically advances `enabledThrough` and opens that phase.
- [ ] Remove predecessor-phase-only checks from first-entry admission; readiness + historical frontier are the complete normal navigation contract.
- [ ] Make both `Next` buttons use the same destination-availability/navigation path as phase buttons.
- [ ] Preserve `Previous` behaviour without reducing `enabledThrough`.
- [ ] Preserve current `canReview` Create gating and unknown-outcome safety.
- [ ] Replace/extend the focused Add Capability navigation regression with the deterministic matrix in Validation below.
- [ ] Prove all navigation actions perform zero create/reconciliation mutations.

## Interfaces / Contracts

Consumes existing COMMERCE-091 browser-local state only:

```text
Phase
phase
enabledThrough
validCapability
canReview
selectedTool
pending
outcomeUnknown
```

Consumes existing mutation boundaries unchanged:

```text
createFeatureCapability
reconcileFeatureOperation
```

No new API, Server Action, database, shared-package or cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-091

## Enables

- ARCH-021-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Initial render has `Capability` enabled and `Tool` / `Review` unavailable.
- [ ] Entering valid Capability metadata makes `Tool` directly clickable **before** pressing `Next`.
- [ ] Invalidating Capability metadata before the first Tool entry makes Tool unavailable again; revalidating makes it available again.
- [ ] Directly clicking a ready Tool phase enters Tool and permanently advances the local unlock frontier through Tool.
- [ ] Selecting an eligible Tool while Capability metadata is valid makes `Review` directly clickable **before** pressing Tool `Next`.
- [ ] A ready-but-never-entered Review follows current `canReview`; once Review is entered/unlocked it stays directly navigable after later candidate invalidation.
- [ ] A Tool/Review phase that was previously unlocked stays clickable after upstream edits or selected-Tool eligibility loss.
- [ ] `Create capability` stays disabled whenever the **current** `canReview` is false, even on an unlocked Review phase.
- [ ] Direct phase clicks, Previous and Next cause zero `createFeatureCapability` and zero `reconcileFeatureOperation` calls.
- [ ] Previous never lowers the unlock frontier.
- [ ] Next and direct phase clicking share the same first-entry eligibility semantics; neither path can unlock a destination the other would reject for the same candidate state.
- [ ] Pending and unknown-outcome locks remain effective.
- [ ] Existing Tool eligibility and final exactly-one-create/reconciliation behaviour remain unchanged.

## Validation

Run from `moda-interact-commerce/` after using the task-prepared Node environment.

### A — focused behavioural regression

```bash
npx vitest run \
  tests/add-capability-screen.test.tsx \
  tests/add-capability-route.test.tsx
```

The screen regression MUST explicitly prove, in this order:

```text
1. Capability enabled; Tool/Review disabled initially.
2. Make Capability valid without clicking Next.
3. Assert Tool is enabled.
4. Invalidate Capability before first Tool entry; assert Tool is disabled again.
5. Revalidate Capability; click Tool tab directly; assert Tool phase renders.
6. Assert zero create/reconcile calls.
7. Select eligible Tool; assert Review is enabled without clicking Next.
8. Return to Capability without entering Review through Next.
9. Click Review tab directly; assert Review renders.
10. Invalidate Capability after Tool/Review have been unlocked.
11. Assert Tool and Review remain enabled/navigable.
12. Assert Create capability is disabled for the invalid current candidate.
13. Revalidate current candidate; assert Create capability re-enables.
14. Exercise Previous/Next and assert the frontier never regresses.
15. Assert every navigation-only action still caused zero create/reconcile calls.
```

Retain the existing success, conflict/correction, unavailable/error and unknown-outcome reconciliation regressions.

### B — targeted lint

```bash
npx eslint \
  src/studio/features/add-capability/add-capability-screen.tsx \
  tests/add-capability-screen.test.tsx
```

### C — project typecheck

```bash
npm run typecheck
```

Any failure in a changed C104 file is task-owned and must be corrected. If a documented baseline condition outside C104 is encountered, record the baseline ID rather than broadening scope.

### D — patch hygiene

```bash
git diff --check
```

All four validation items are required before review. Do not substitute a build for any listed check and do not add unrelated repository-wide cleanup.

## Stop Condition

After the two-file implementation/test correction satisfies every Work Item, Acceptance Criterion and Validation item, update the Completion Report, set the task to `review`, return control to `moda_architect` and STOP.

Do not start SYSTEM-TEST-003, C102, C103 or any other follow-on task.

## Implementation Notes

The smallest conforming implementation should keep the existing local state machine and make the navigation predicates explicit.

A deterministic shape equivalent to the following is preferred:

```ts
function isPhaseUnlocked(candidate: Phase): boolean {
  return phaseIndex(candidate) <= phaseIndex(enabledThrough);
}

function isPhaseReadyForFirstEntry(candidate: Phase): boolean {
  switch (candidate) {
    case 'Capability':
      return true;
    case 'Tool':
      return validCapability;
    case 'Review':
      return canReview;
  }
}

function isPhaseAvailable(candidate: Phase): boolean {
  return isPhaseUnlocked(candidate) || isPhaseReadyForFirstEntry(candidate);
}

function goTo(candidate: Phase): void {
  if (pending || outcomeUnknown || !isPhaseAvailable(candidate)) return;
  if (!isPhaseUnlocked(candidate)) unlockThrough(candidate);
  setPhase(candidate);
}
```

Equivalent code is acceptable only if it satisfies the exact truth table and tests above.

Then use `isPhaseAvailable(destination)` consistently for:

```text
phase-button disabled state
Capability -> Tool Next disabled state
Tool -> Review Next disabled state
```

Do not add a second independent condition such as `phase === 'Capability'` or `phase === 'Tool'` for first unlock. The destination's readiness plus the monotonic frontier are authoritative.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
