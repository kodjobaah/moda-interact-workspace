---
id: ARCH-021-COMMERCE-020
architecture_id: ARCH-021
title: Extract Tool authoring domain from StudioWorkspace
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-005
  - ARCH-021-COMMERCE-006
enables:
  - ARCH-021-COMMERCE-021
  - ARCH-021-COMMERCE-022
created: 2026-09-23
updated: 2026-09-24
---

# Extract Tool authoring domain from StudioWorkspace

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Move the existing Tools library/editor orchestration out of `components/studio-workspace.tsx` into a dedicated Tool-authoring domain module without changing accepted Phase 1/ARCH-020 behavior, so Phase 3 editors do not add more domain state to the 2,600-line workspace shell.

## Context

ARCH-021 established incremental, domain-driven Studio decomposition. Phase 2 extracted Agent Configuration. Phase 3 now touches Tool authoring and therefore owns the equivalent bounded extraction.

## Scope

Create/use exactly:

```text
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-library.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/types.ts              # only shared local props/types if needed
components/studio-workspace.tsx
tests/tool-authoring-screen.test.tsx
```

Existing specialized editor modules such as `src/studio/external-http/editor.tsx` and `src/studio/code-response/code-editor.tsx` remain specialized modules and are composed by the extracted Tool domain; do not mechanically move them just for naming consistency.

## Out of Scope

- Changing saved definitions.
- Adding request JavaScript/Admin GraphQL fields.
- Live testing.
- Refactoring Feature/Explore/Capabilities/Releases/Shops surfaces.
- Changing Studio navigation contracts.

## Requirements

- Extract the current `ToolLibrary` and `ToolEditor` domain state/handlers from `StudioWorkspace`.
- `StudioWorkspace` retains only surface selection/navigation and passes the existing `services`, selected-shop context, external HTTP port and code-panel composition into `ToolAuthoringScreen`.
- Preserve dirty guards, locked/pending behavior, U06/U14 navigation, connection revision selection, revision history and current tests.
- Do not introduce a new state store/context library.
- The extraction commit must be behavior-neutral; snapshots/queries should show identical existing labels/actions before Phase 3 editor tasks alter them.

## Work Items

- [ ] Extract Tool library/editor components and local types.
- [ ] Reduce `StudioWorkspace` to orchestration for the Tools surface.
- [ ] Preserve existing ports/guards/navigation.
- [ ] Add focused behavior-equivalence tests.

## Interfaces / Contracts

Consumes accepted COMMERCE-005/006 production Tool composition and COMMERCE-016 contract baseline.

Produces the UI boundary extended by COMMERCE-021/022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-005
- ARCH-021-COMMERCE-006

## Enables

- ARCH-021-COMMERCE-021
- ARCH-021-COMMERCE-022

## Acceptance Criteria

- [ ] Tool-specific state/action code is no longer owned by StudioWorkspace.
- [ ] Existing Tool authoring behavior is unchanged.
- [ ] Unrelated Studio surfaces are not refactored.

## Validation

- [ ] focused `tests/tool-authoring-screen.test.tsx`
- [ ] existing `tests/studio-workspace.test.tsx`
- [ ] `npm run test:arch020-external-tools-ui`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not add Phase 3 authoring fields in this task.

## Implementation Notes

This is the Phase 3 continuation of the incremental Studio decomposition rule, not a wholesale workspace rewrite.

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
