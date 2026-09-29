---
id: ARCH-021-COMMERCE-110
architecture_id: ARCH-021
title: Render Add Capability phases as semantic tabs
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 76
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-104
enables:
  - ARCH-021-SYSTEM-TEST-003
created: 2026-09-30
updated: 2026-09-30
---

# Render Add Capability phases as semantic tabs

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the current numbered vertical `Capability / Tool / Review` phase selector on **Add capability** with a real three-tab authoring presentation while preserving every accepted COMMERCE-091/104 navigation, readiness, local-first persistence and final-Create rule.

This task changes presentation/semantics only. It must not redesign the Add Capability state machine.

## Context

Manual validation after COMMERCE-104 shows that Add Capability still renders its phase selector as:

```tsx
<nav aria-label="Capability setup">
  <ol className="tab-list">
    ...
  </ol>
</nav>
```

The current Commerce stylesheet contains no `.tab-list` presentation for this surface, so the browser renders an ordinary numbered vertical list:

```text
1. Capability
2. Tool
3. Review
```

COMMERCE-104 intentionally corrected only phase admission/unlocking. It did not create a tab presentation.

The accepted navigation authority must remain unchanged:

```text
before first entry:
  Tool   available when validCapability
  Review available when canReview

after first unlock:
  Tool/Review remain directly navigable

pending / outcomeUnknown:
  navigation remains locked

Create capability:
  remains gated by current canReview
```

## Scope

Only:

```text
src/studio/features/add-capability/add-capability-screen.tsx
app/styles.css
tests/add-capability-screen.test.tsx
```

`tests/add-capability-route.test.tsx` may be run for validation but should not require modification.

## Out of Scope

- Changing the phase order or labels.
- Changing `enabledThrough`.
- Changing `validCapability`, `canReview`, Tool eligibility or first-entry readiness.
- Changing pending/unknown-outcome navigation locking.
- Changing Previous/Next semantics.
- Changing Create/reconciliation actions or operation identity.
- Persisting phase state.
- Changing Feature Behaviour authoring.
- Changing Tool-authoring `ToolAuthoringTabs`.
- Creating a generic/shared wizard/tab abstraction.
- Adding a design-system dependency.
- Broad Studio restyling.

## Requirements

### R1 — retain the exact three-phase source of truth

Keep the existing `Phase` union and `phases` array as the only source of order:

```text
Capability
Tool
Review
```

Do not create another phase-order array.

### R2 — replace ordered-list markup with one semantic tablist

Remove the Add Capability `<ol>` / `<li>` phase markup.

Render exactly:

```tsx
<nav
  className="capability-authoring-tabs"
  role="tablist"
  aria-label="Capability setup"
>
  ...
</nav>
```

Inside it, render exactly one native `<button type="button">` per existing phase.

Every phase button MUST have:

```text
role="tab"
visible label = Capability | Tool | Review
aria-selected = phase === active phase
aria-disabled = same boolean as disabled
disabled = !isPhaseAvailable(item) || pending || outcomeUnknown
className = "active" only for the active phase
onClick = goTo(item)
```

Do not render `<ol>`, `<ul>`, `<li>`, numeric prefixes or step numbers.

### R3 — deterministic tab/panel relationships

Use these exact IDs:

```text
Capability tab   capability-phase-tab
Capability panel capability-phase-panel

Tool tab         tool-phase-tab
Tool panel       tool-phase-panel

Review tab       review-phase-tab
Review panel     review-phase-panel
```

Each tab gets:

```text
aria-controls="<matching panel id>"
```

The currently rendered phase `<section>` gets:

```text
role="tabpanel"
id="<matching panel id>"
aria-labelledby="<matching tab id>"
```

Only the active panel remains mounted, matching current behaviour.

### R4 — preserve COMMERCE-104 navigation authority exactly

Do not introduce a second tab-specific availability function.

Tab disabled state MUST be:

```ts
!isPhaseAvailable(item) || pending || outcomeUnknown
```

Do not change the meaning of:

```text
phaseIndex
isPhaseUnlocked
isPhaseReadyForFirstEntry
isPhaseAvailable
unlockThrough
goTo
```

The following must remain true:

```text
fresh:
  Capability available
  Tool unavailable until validCapability
  Review unavailable until canReview

before first entry:
  readiness can be revoked

after first entry:
  historical unlock keeps the phase available

pending/outcomeUnknown:
  phase navigation is locked
```

### R5 — direct tabs and Previous/Next share the same `goTo`

A tab click MUST call the existing `goTo(destination)`.

Previous and Next remain in their current location and use the same navigation path.

Do not implement independent tab transition logic.

### R6 — exact bounded styling

Add this dedicated block to `app/styles.css`:

```css
.capability-authoring-tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 22px 0 26px;
}

.capability-authoring-tabs button {
  min-width: 0;
  width: 100%;
  background: #f8faf7;
  color: #315b4d;
  border: 1px solid #d6dfd7;
  text-align: left;
}

.capability-authoring-tabs button.active {
  background: #18372f;
  border-color: #18372f;
  color: #fff;
}

.capability-authoring-tabs button:disabled {
  cursor: not-allowed;
}
```

Add this responsive rule:

```css
@media (max-width: 760px) {
  .capability-authoring-tabs {
    grid-template-columns: 1fr;
  }
}
```

Do not alter `.tool-editor-tabs`.

Do not override the repository-global disabled opacity.

### R7 — preserve page/control placement

Keep:

```text
Feature configuration heading / feature context / Cancel
Capability setup tabs
active phase panel
phase footer controls
status/alert
```

Do not move Cancel into the tablist.

Do not move Previous/Next/Create into the tablist.

### R8 — navigation remains zero-write

Tab clicks, Previous and Next MUST invoke zero:

```text
createFeatureCapability
reconcileFeatureOperation
```

The only durable create boundary remains `Create capability`.

### R9 — preserve candidate/session-local state

Tab traversal must not reset:

```text
key
displayName
description
toolId
enabledThrough
operationId
message
```

### R10 — keep the correction local

Do not introduce `GenericTabs`, `WizardTabs`, `StudioTabs` or a shared tab state machine.

Do not change Tool-authoring tab contracts.

## Work Items

- [ ] Remove the Add Capability ordered-list/list-item phase markup.
- [ ] Render one `Capability setup` semantic tablist from the existing `phases`.
- [ ] Add exact tab IDs, `role="tab"`, `aria-selected`, `aria-disabled` and `aria-controls`.
- [ ] Add exact matching tabpanel IDs, `role="tabpanel"` and `aria-labelledby`.
- [ ] Preserve the exact C104 availability expression and `goTo` path.
- [ ] Add the exact `.capability-authoring-tabs` styles and responsive rule.
- [ ] Preserve Previous/Next/Create placement and behaviour.
- [ ] Add focused semantic-tab regressions.
- [ ] Preserve the existing C104 readiness/unlock regression behaviour.
- [ ] Prove tab/footer navigation causes zero create/reconciliation calls.
- [ ] Run focused tests, targeted ESLint, `npm run typecheck` and `git diff --check`.
- [ ] Complete the Completion Report and STOP.

## Interfaces / Contracts

Consumes only:

```text
COMMERCE-091 local-first Add Capability flow
COMMERCE-104 navigation/readiness authority
createFeatureCapability
reconcileFeatureOperation
```

No server/database/Shared/Background/Gateway contract changes.

## Dependencies

- ARCH-021-COMMERCE-104

## Enables

- ARCH-021-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Exactly three phase tabs render: Capability, Tool, Review.
- [ ] No ordered/unordered list or browser list numbering remains in the phase selector.
- [ ] The selector has `role="tablist"` with accessible name exactly `Capability setup`.
- [ ] Each phase button has `role="tab"`.
- [ ] Exactly one tab has `aria-selected="true"`.
- [ ] Every tab points to the exact matching panel ID with `aria-controls`.
- [ ] The active panel has `role="tabpanel"` and matching `aria-labelledby`.
- [ ] Initial Tool/Review availability still follows C104 readiness.
- [ ] Live first-entry readiness still makes Tool/Review directly clickable before Next.
- [ ] First direct tab entry still advances the monotonic unlock frontier.
- [ ] Later invalidation does not re-lock a historically unlocked phase.
- [ ] Pending/unknown outcome still locks phase navigation.
- [ ] `Create capability` remains independently gated by current `canReview`.
- [ ] Direct tab clicks, Previous and Next invoke zero Capability mutation/reconciliation calls.
- [ ] Candidate values and selected Tool survive tab traversal.
- [ ] Desktop/tablet presentation uses three equal columns.
- [ ] At/below 760px the tab layout becomes one column.
- [ ] Existing Tool-authoring tabs are unchanged.

## Validation

Run from the launcher-prepared Commerce implementation worktree:

```text
npm exec -- vitest run \
  tests/add-capability-screen.test.tsx \
  tests/add-capability-route.test.tsx \
  --reporter=dot
```

If repository policy requires the installed local Vitest binary, record the exact equivalent command instead of changing dependency manifests.

Required `tests/add-capability-screen.test.tsx` regressions:

1. `getByRole('tablist', { name: 'Capability setup' })` exists.
2. Exactly three tabs exist in order: Capability, Tool, Review.
3. No `list`/`listitem` phase semantics or numeric prefixes remain.
4. Initial selected/disabled states match C104.
5. Valid Capability metadata enables Tool; direct Tool tab entry selects it, renders `tool-phase-panel`, and performs zero mutation/reconciliation.
6. Eligible Tool selection enables Review; direct Review tab entry selects it, renders `review-phase-panel`, and performs zero mutation/reconciliation.
7. C104 readiness revocation before first entry and monotonic access after first entry remain correct.
8. Current invalidation disables Create even when Review remains unlocked.
9. Previous/Next update selected tab/panel and remain zero-write.
10. Candidate values and selected Tool survive tab traversal.

Also run:

```text
targeted ESLint:
  src/studio/features/add-capability/add-capability-screen.tsx
  tests/add-capability-screen.test.tsx

npm run typecheck
git diff --check
```

Inspect:

```text
git diff -- app/styles.css
```

and confirm only the bounded C110 tab styles/responsive rule were added.

## Stop Condition

After implementation and validation:

1. set C110 to `review`;
2. complete the Completion Report with exact launcher/worktree/synchronization/submodule evidence and validation commands/results;
3. STOP.

Do not begin SYSTEM-TEST-003 or another follow-on task.

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
