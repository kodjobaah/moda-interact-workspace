---
id: ARCH-021-COMMERCE-111
architecture_id: ARCH-021
title: Clarify Tool library publication state and Capability eligibility
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 77
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-09-30
updated: 2026-09-30
---

# Clarify Tool library publication state and Capability eligibility

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the **Reusable tools / Global tool library** truthful about each Tool's lifecycle state so an administrator can immediately understand why a Tool does or does not appear in Add Capability.

Keep the existing Add Capability eligibility rule unchanged:

```text
Tool enabled
AND
at least one PUBLISHED Tool revision
```

The Tool library must show the facts needed to evaluate that rule instead of showing only a total revision count.

## Context

The current Tool library renders every `ToolSummary` and describes the section as:

```text
Reusable published versions
```

but each row currently shows only:

```text
<tool name> · <N> revisions
```

`ToolSummary` already contains:

```text
enabled
revisions[].status = DRAFT | PUBLISHED
```

The Add Capability route independently filters the same summaries with:

```ts
tool.enabled
&& tool.revisions.some(
  (revision) => revision.status === 'PUBLISHED'
)
```

A Tool with one DRAFT revision therefore appears in the Global tool library as `1 revisions` but correctly does not appear in Add Capability. The current library presentation makes those two screens look contradictory even when the backend state is consistent.

This task changes presentation only. Add Capability remains the authoritative Capability-selection gate.

## Scope

Primary implementation:

```text
src/studio/tools/tool-library.tsx
tests/tool-library.test.tsx
```

Validation-only existing coverage:

```text
tests/add-capability-route.test.tsx
```

No Server Action, service, persistence or schema change is required.

## Out of Scope

- Filtering the Global tool library down to published/eligible Tools.
- Changing `listTools()`.
- Changing `ToolSummary`.
- Changing Add Capability's `eligibleTools(...)` predicate.
- Publishing or enabling a Tool from the library.
- Changing Tool history/edit screens.
- Deleting rehearsal/test Tools from persistence.
- Database cleanup or test isolation; COMMERCE-112 owns that concern.
- Creating another Tool lifecycle state.
- Changing Tool publication semantics.
- Updating `docs/decisions/commerce/ARCH-021/_index.md` during implementation. Architect review will reconcile the index after acceptance.

## Requirements

### R1 — keep the Global tool library complete

Continue to render every Tool returned through the existing `tools: ToolSummary[]` prop.

Do not filter out:

```text
disabled Tools
zero-revision Tools
DRAFT-only Tools
published Tools
```

Preserve the existing order supplied by `listTools()`.

### R2 — replace the misleading section explanation

Change the explanatory copy under `Global tool library` to exactly:

```text
All Tools are shown. Add Capability can select only enabled Tools with at least one published revision.
```

Keep these controls/labels unchanged:

```text
Global tool library
Inspect a merchant's tool list
Create Tool
Open history
```

### R3 — derive revision counts only from the existing ToolSummary

For every Tool row derive:

```ts
const publishedCount =
  tool.revisions.filter(
    (revision) => revision.status === 'PUBLISHED'
  ).length;

const draftCount =
  tool.revisions.filter(
    (revision) => revision.status === 'DRAFT'
  ).length;

const totalCount = tool.revisions.length;
```

Do not perform another Server Action or Tool-detail read per row.

Do not infer publication state from `readyToPublish`, `revisionNumber`, definition shape or total count.

### R4 — render exact row lifecycle metadata

Every Tool row must continue to show:

```text
displayName
name
Open history
```

and must add one lifecycle metadata line with this exact logical content:

```text
<Enabled|Disabled> · <publishedCount> published · <draftCount> draft · <totalCount> total
```

Examples:

```text
Enabled · 1 published · 0 draft · 1 total
Enabled · 0 published · 1 draft · 1 total
Disabled · 2 published · 1 draft · 3 total
Enabled · 0 published · 0 draft · 0 total
```

Do not hide zero counts.

### R5 — show exact Add Capability eligibility result and reason

Compute only:

```ts
const capabilityEligible =
  tool.enabled && publishedCount > 0;
```

Render exactly one eligibility line per Tool.

If eligible:

```text
Available to Add Capability
```

If enabled but no published revision:

```text
Not available to Add Capability: no published revision
```

If disabled but at least one published revision:

```text
Not available to Add Capability: Tool disabled
```

If disabled and there is no published revision:

```text
Not available to Add Capability: Tool disabled; no published revision
```

Do not use total revision count as an eligibility signal.

### R6 — Add Capability remains authoritative and unchanged

Do not change:

```text
app/features/[id]/capabilities/new/page.tsx
```

or its current predicate:

```ts
tool.enabled
&& tool.revisions.some(
  (revision) => revision.status === 'PUBLISHED'
)
```

The Tool library's displayed eligibility must agree with that predicate but does not replace it.

### R7 — no lifecycle mutation from the library

Rendering the new metadata must perform zero:

```text
create/update Tool
create/update/publish Tool revision
setToolEnabled
Capability mutation
provider call
```

The task is read/presentation-only.

### R8 — empty library behaviour remains bounded

If `tools` is empty, retain the existing page structure and Create Tool action.

Do not invent seed/sample Tools.

## Work Items

- [ ] Replace the misleading Global tool library explanatory copy.
- [ ] Derive published, draft and total counts from `ToolSummary.revisions`.
- [ ] Display Enabled/Disabled state for every row.
- [ ] Display published/draft/total counts including zeroes.
- [ ] Display the exact Add Capability eligibility copy/reason.
- [ ] Keep every Tool in the library regardless of eligibility.
- [ ] Preserve `Open history`, merchant inspection and Create Tool actions.
- [ ] Add focused ToolLibrary regressions in a dedicated test file.
- [ ] Run the existing Add Capability route eligibility regression unchanged.
- [ ] Run targeted ESLint, project typecheck and `git diff --check`.
- [ ] Complete the Completion Report and STOP.

## Interfaces / Contracts

Consumes the existing:

```ts
ToolSummary = {
  enabled: boolean;
  revisions: Array<{
    status: 'DRAFT' | 'PUBLISHED';
    ...
  }>;
  ...
}
```

No public/backend interface changes.

## Dependencies

None.

This task is independent of COMMERCE-110 and COMMERCE-112.

## Enables

None.

## Acceptance Criteria

- [ ] The Global tool library still renders all Tools returned by `listTools()`.
- [ ] The explanatory copy explicitly states the Add Capability eligibility rule.
- [ ] Every Tool row shows Enabled or Disabled.
- [ ] Every Tool row shows exact published, draft and total revision counts.
- [ ] Zero-revision and DRAFT-only Tools are distinguishable from published Tools.
- [ ] Enabled + at least one PUBLISHED revision renders `Available to Add Capability`.
- [ ] Enabled + zero PUBLISHED revisions renders the exact no-published-revision reason.
- [ ] Disabled + PUBLISHED revision renders the exact disabled reason.
- [ ] Disabled + zero PUBLISHED revisions renders both reasons.
- [ ] A Tool with one DRAFT revision is never presented as published/Capability-eligible.
- [ ] `Open history`, merchant inspection and Create Tool actions remain available.
- [ ] Add Capability's existing server-side eligibility filter is unchanged.
- [ ] No Tool/Capability/provider mutation occurs while rendering the library.
- [ ] Project typecheck and focused tests pass.

## Validation

Add:

```text
tests/tool-library.test.tsx
```

with at least these executable cases:

1. enabled + one PUBLISHED revision:
   - `Enabled · 1 published · 0 draft · 1 total`
   - `Available to Add Capability`.

2. enabled + one DRAFT revision:
   - `Enabled · 0 published · 1 draft · 1 total`
   - `Not available to Add Capability: no published revision`.

3. disabled + PUBLISHED revision:
   - Disabled lifecycle line;
   - `Not available to Add Capability: Tool disabled`.

4. disabled + no PUBLISHED revision:
   - exact combined reason.

5. zero revisions:
   - Tool remains visible;
   - all three counts are zero.

6. no filtering:
   - eligible and ineligible Tool display names all appear in one render.

7. navigation/actions:
   - `Open history` targets `/tools/<toolId>`;
   - merchant inspection remains present;
   - `Create Tool` invokes the supplied callback.

Run:

```text
npm exec -- vitest run \
  tests/tool-library.test.tsx \
  tests/add-capability-route.test.tsx \
  --reporter=dot

npm exec -- eslint \
  src/studio/tools/tool-library.tsx \
  tests/tool-library.test.tsx

npm run typecheck
git diff --check
```

If the prepared repository uses installed local binaries instead of `npm exec`, record the exact equivalent command without changing dependency manifests merely for validation.

## Stop Condition

After implementation and validation:

1. set C111 to `review`;
2. complete the Completion Report with exact launcher/worktree/synchronization/submodule evidence and validation commands/results;
3. STOP.

Do **not** update:

```text
docs/decisions/commerce/ARCH-021/_index.md
```

during implementation. The Architect review/acceptance step owns the index reconciliation.

Do not begin COMMERCE-112 or another follow-on task.

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
