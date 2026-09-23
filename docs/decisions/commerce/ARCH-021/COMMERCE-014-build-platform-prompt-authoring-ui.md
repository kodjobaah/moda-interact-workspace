---
id: ARCH-021-COMMERCE-014
architecture_id: ARCH-021
title: Build platform CommerceAgent prompt authoring UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 74
executor: copilot
claimed_at: 2026-09-23T19:50:21Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-011
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Build platform CommerceAgent prompt authoring UI

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add application-wide CommerceAgent prompt lineage, draft, immutable revision history and active-pointer authoring to the Agent Configuration Studio surface.

## Context

The configurable platform behavioural prompt has a distinct lifecycle from reusable prompt templates. COMMERCE-009 owns the platform/shop prompt service and COMMERCE-008 supplies selectable published template revisions for copy-on-use. COMMERCE-011 establishes the Agent Configuration shell. This task implements only the platform prompt authoring UI; selected-shop prompt authoring remains COMMERCE-012.

## Scope

- Extend Agent Configuration with the application-wide/platform prompt section.
- Show the singleton platform prompt lineage, revision history and current environment active revision.
- Create a DRAFT revision from:
  - empty content;
  - current lineage content;
  - one exact currently-selectable published template revision.
- Edit/save DRAFT content with CAS and accepted replay/conflict/unknown-outcome handling.
- Publish non-blank DRAFT content into an immutable published revision.
- Activate a published platform revision using the environment-scoped pointer operation.
- Show `sourceTemplateRevisionId` provenance when a draft/revision originated from a template, without implying live linkage.
- Display immutable revision id/hash/status/published metadata needed for later preview validation.
- Apply dirty/navigation guards to unsaved prompt edits.
- ADMIN remains read-only; SUPER_ADMIN gets mutation controls outside development bypass.

## Out of Scope

- Prompt-template category/template management UI; owned by ARCH-021-COMMERCE-013.
- Shop prompt/model override UI; owned by ARCH-021-COMMERCE-012.
- Model catalogue/default UI; owned by ARCH-021-COMMERCE-011.
- Feature prompt removal.
- Live provider/model/tool execution.
- Grant/manifest/Background changes.
- Merchant access.

## Requirements

- Production composition must use COMMERCE-009 prompt operations and COMMERCE-008 selectable-template reads, never fixture ports.
- Platform prompt state/editor/mutation orchestration remains under `src/studio/agent-configuration/`, not `StudioWorkspace`.
- Empty DRAFT prompt content is valid. Publish must preserve the user's exact persisted text and surface the service validation error when it is blank/whitespace-only.
- `Use template` copies the exact selected published template revision into a prompt DRAFT; it is not a dynamic link.
- Published revisions are presented as immutable; editing requires a new DRAFT.
- Model selection must not be changed by any prompt operation.
- Mutation UI must preserve accepted durable replay/conflict/unknown-outcome semantics.

### Deterministic file boundary

Primary locations:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
app/agent-configuration/page.tsx
tests/agent-configuration-platform-prompt-ui.test.tsx
```

Small helper components may be added only under `src/studio/agent-configuration/`. `StudioWorkspace` requires no new prompt editor state.

## Work Items

- [ ] Add platform lineage/history/active-pointer presentation.
- [ ] Add create-empty/create-from-current/create-from-template DRAFT actions.
- [ ] Add DRAFT editing/saving with dirty/CAS handling.
- [ ] Add immutable publish action and validation presentation.
- [ ] Add platform active-pointer mutation UI.
- [ ] Add provenance and stable revision/hash presentation.
- [ ] Add focused lifecycle/auth/replay UI tests.

## Interfaces / Contracts

Consumes:

- prompt-template selectable-revision port from ARCH-021-COMMERCE-008;
- prompt lifecycle/configuration port from ARCH-021-COMMERCE-009;
- Agent Configuration shell/module from ARCH-021-COMMERCE-011.

Produces the application-wide platform CommerceAgent prompt authoring surface. It does not own selected-shop prompt authoring.

## Dependencies

- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-011

## Enables

None.

## Acceptance Criteria

- [ ] Platform admins can inspect platform prompt history and active revision.
- [ ] A platform prompt DRAFT may start empty, from current lineage content or from one exact selectable published template revision.
- [ ] Empty DRAFT content may be saved; blank/whitespace-only publication is rejected and shown without silent text normalisation.
- [ ] Published revisions are immutable and their stable id/hash/status is visible.
- [ ] Activating a platform prompt targets only a published platform revision and does not change model state.
- [ ] Template provenance is visible as historical provenance only; no live template linkage is represented.
- [ ] ADMIN is read-only and no secret/session token is rendered.
- [ ] Platform prompt state/actions do not accumulate in `StudioWorkspace`.
- [ ] No live model/provider execution occurs.

## Validation

- [ ] focused platform-prompt route/component tests
- [ ] blank-draft/publish-validation tests
- [ ] template-copy/provenance UI tests
- [ ] pointer CAS/replay/conflict/unknown-outcome UI tests
- [ ] authorization/development-bypass UI tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin another Phase 2 task.

## Implementation Notes

Do not concatenate platform and shop prompts and do not remove the legacy capability prompt field here. Runtime consumption changes belong to later ARCH-021 phases.

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
