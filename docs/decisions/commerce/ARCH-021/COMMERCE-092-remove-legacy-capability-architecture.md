---
id: ARCH-021-COMMERCE-092
architecture_id: ARCH-021
title: Remove the legacy Capability revision architecture
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 96
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-089
  - ARCH-021-COMMERCE-091
  - ARCH-021-BACKGROUND-002
enables:
  - ARCH-021-SYSTEM-TEST-003
created: 2026-09-29
updated: 2026-09-29
---

# Remove the legacy Capability revision architecture

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Delete the obsolete Capability draft/revision/binding UI, lifecycle, contracts, persistence adapters and fixtures after every supported authoring/runtime consumer has moved to the direct Feature/Capability/Tool model.

## Context

COMMERCE-088/089/090/091 and BACKGROUND-002 establish the replacement path. Temporary legacy code may have remained only to keep intermediate branches buildable while the backend and UI migrated independently.

This task is the subtractive completion gate. It must leave materially less Capability code, not a permanent compatibility layer around an obsolete domain model.

## Scope

Delete/reconcile obsolete Commerce files and symbols across:

```text
app/capabilities/page.tsx
app/capabilities/[id]/page.tsx
components/studio-workspace.tsx legacy Capability branches
src/studio/contracts.ts legacy CapabilityRevision/ToolBinding contracts
src/studio/server-actions.ts / server-services.ts legacy Capability actions
src/studio/testing/in-memory-studio-services.ts legacy Capability revision simulator
src/commerce/publication/ports.ts legacy CapabilityDraft/Revision/binding types
src/commerce/publication/lifecycle.ts obsolete Capability create-draft/update-draft/publish code
src/commerce/publication/validation.ts obsolete binding/config validation
src/commerce/publication/read-models.ts legacy revision views
src/commerce/integration/backend/publication-storage.ts obsolete capability-revision read/write handling
obsolete tests/fixtures/C20 setup that only support the removed model
navigation entries for standalone Capability authoring where no longer required
```

Retain release/runtime paths implemented by COMMERCE-089 and Feature authoring from COMMERCE-088/090/091.

## Out of Scope

- New functionality.
- Tool authoring cleanup unrelated to Capability architecture.
- Billing/subscription policy changes.
- Shared or Background changes already owned by their tasks.
- Broad Studio redesign unrelated to deleting obsolete Capability paths.

## Requirements

### R1 — remove standalone Capability authoring routes/surface

The primary authoring model is Feature-centric. Remove the standalone Capability list/editor routes and navigation when they exist only to support Capability revisions.

A deep/internal route may remain only if the new Feature-owned UX genuinely requires it; it must not expose the old editor/lifecycle.

### R2 — delete old lifecycle operations

Remove Capability operations/types whose semantics no longer exist:

```text
create Capability shell before Tool assignment
createDraft
updateDraft
publishRevision
clone Capability revision
Capability revision CAS/editor state
multi-Tool toolBindings[]
per-Capability promptTemplate/configuration
```

Do not retain deprecated wrappers or no-op methods.

### R3 — delete removed domain terminology from supported Commerce source

Supported Commerce source must contain no active Capability-domain use of:

```text
selectionBinding
BASE
RECOVERY_POLICY
CapabilityRevision
maxSearchResults
maxRecommendations
```

Generic runtime safety constants may exist under different generic names only where they are genuinely execution-safety concerns, not Capability configuration.

Historical architecture/task documents are not part of this source-code grep invariant.

### R4 — remove whole-publication Capability persistence machinery no longer needed

If the broad publication state/read-all/write-all adapter remains only for legacy Capability mutation after Tool/release migration, delete that Capability-specific handling.

Do not remove still-used release activation/rollback or Tool publication behavior merely for stylistic consistency.

### R5 — replace obsolete fixtures rather than translating them

Remove fixtures that manufacture `conversation_core` BASE Capabilities, Capability revisions, promptName identities or multi-binding configurations. Rewrite only the minimum deterministic fixtures required by supported Feature Capability/release/runtime tests.

### R6 — no unreachable compatibility branches

There must be one supported Feature Capability authoring path and one supported release/runtime path. Tests must prove old Capability routes/actions are absent or unreachable as designed.

## Work Items

- [ ] Remove standalone legacy Capability routes/navigation/editor.
- [ ] Remove CapabilityRevision/CapabilityDraft/ToolBinding Studio contracts.
- [ ] Remove legacy Capability draft/update/publish Server Actions/services.
- [ ] Remove obsolete publication lifecycle/validation/read-model code.
- [ ] Remove obsolete publication-storage capability-revision handling.
- [ ] Remove Capability `selectionBinding`/BASE/RECOVERY_POLICY branches from Commerce source.
- [ ] Remove Capability-level `maxSearchResults` / `maxRecommendations` plumbing; retain only generically named implementation safety bounds where required.
- [ ] Replace C20/in-memory/test fixtures that only model the old architecture.
- [ ] Delete unreachable compatibility adapters introduced solely for staged migration.
- [ ] Add source-level regression assertions/grep-style checks where useful to prevent legacy symbol reintroduction.

## Interfaces / Contracts

Consumes the accepted replacement paths from:

```text
ARCH-021-COMMERCE-088
ARCH-021-COMMERCE-089
ARCH-021-COMMERCE-090
ARCH-021-COMMERCE-091
ARCH-021-BACKGROUND-002
```

Produces no new runtime contract.

## Dependencies

- ARCH-021-COMMERCE-089
- ARCH-021-COMMERCE-091
- ARCH-021-BACKGROUND-002

## Enables

- ARCH-021-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] There is no supported standalone Capability revision editor/list workflow.
- [ ] `createDraft`, `updateDraft`, Capability `publishRevision` and Capability clone flow are removed.
- [ ] Commerce source no longer models `CapabilityRevision`/`CapabilityDraft`/multi-Tool bindings.
- [ ] Commerce source no longer branches on Capability `selectionBinding`, BASE or RECOVERY_POLICY.
- [ ] Capability-level `maxSearchResults` / `maxRecommendations` are absent; any remaining generic safety bounds are clearly execution-owned and not author-configurable.
- [ ] No current fixture requires `conversation_core` as a BASE Capability.
- [ ] The new Feature authoring and release/runtime focused suites remain green after deletion.
- [ ] No temporary migration compatibility adapter remains reachable.

## Validation

- [ ] focused Feature/Capability UI suites from COMMERCE-090/091
- [ ] focused publication/backend suites from COMMERCE-089
- [ ] affected Studio integration/C20 suites after fixture replacement
- [ ] targeted repository source search proving removed Capability-domain symbols are absent from supported source paths
- [ ] targeted ESLint
- [ ] changed-file TypeScript diagnostics / repository typecheck evidence per baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin SYSTEM-TEST-003.

## Implementation Notes

Deletion is the purpose of this task. Do not preserve old code "just in case" during this pre-production breaking rollout.

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
