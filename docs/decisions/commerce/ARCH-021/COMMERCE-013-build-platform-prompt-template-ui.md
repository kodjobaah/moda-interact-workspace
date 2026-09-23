---
id: ARCH-021-COMMERCE-013
architecture_id: ARCH-021
title: Build platform prompt-template library UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 72
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-011
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Build platform prompt-template library UI

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add the platform-managed category-organised prompt-template library to the Agent Configuration Studio surface using the accepted COMMERCE-008 service.

## Context

Prompt templates are application-wide authoring starting points, not active runtime prompts. They have their own category/template/revision lifecycle and can be implemented/reviewed independently of model management and platform prompt activation. COMMERCE-011 establishes the Agent Configuration route/module shell; this task adds only the template-library capability.

## Scope

- Extend the Agent Configuration module with a platform prompt-template library section.
- List/filter/group templates and revisions by category/classification.
- Create categories with stable authored slug and mutable display metadata.
- Update category display metadata without presenting stable slug/identity as renameable.
- Enable/disable categories.
- Create multiple template identities within one category.
- Update template display metadata and enable/disable templates.
- Create/edit DRAFT template revisions, including an empty initial draft.
- Publish a non-blank template revision.
- Display immutable published revision identity/hash and historical disabled category/template state where returned by COMMERCE-008.
- Apply dirty/navigation guards to unsaved template edits.
- ADMIN remains read-only; SUPER_ADMIN gets mutation controls outside development bypass.

## Out of Scope

- Platform prompt lineage/draft/history/active pointer; owned by ARCH-021-COMMERCE-014.
- Shop prompt/model overrides; owned by ARCH-021-COMMERCE-012.
- Platform model catalogue/default controls; owned by ARCH-021-COMMERCE-011.
- Live provider/model/tool execution.
- Grant/manifest/Background changes.
- Merchant-owned template libraries.

## Requirements

- Production composition must use COMMERCE-008 server actions/ports, never fixture ports.
- Category/template editor state and mutation orchestration remain under `src/studio/agent-configuration/` and must not move into `StudioWorkspace`.
- Category slug is shown as stable identity after creation; UI edit operations change display metadata only.
- Empty DRAFT content is valid, but the publish action must surface the COMMERCE-008 validation error for blank/whitespace-only content rather than silently altering the text.
- Disabled category/template history remains inspectable while new-authoring selection is unavailable according to COMMERCE-008.
- Mutation UI must preserve accepted replay/conflict/unknown-outcome semantics.

### Deterministic file boundary

Primary locations:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/prompt-template-library.tsx
app/agent-configuration/page.tsx
tests/agent-configuration-template-ui.test.tsx
```

Small helper components may be added only under `src/studio/agent-configuration/`. `StudioWorkspace` requires no new domain state for this task.

## Work Items

- [ ] Add category list/create/display-metadata-update/enable/disable UI.
- [ ] Add category-grouped/filterable template discovery.
- [ ] Add template identity metadata/enablement controls.
- [ ] Add template DRAFT editor/history/publish flow.
- [ ] Add dirty/navigation and replay/conflict/unknown-outcome handling.
- [ ] Add focused read-only/admin/auth/lifecycle UI tests.

## Interfaces / Contracts

Consumes:

- prompt-template service from ARCH-021-COMMERCE-008;
- Agent Configuration shell/module from ARCH-021-COMMERCE-011.

Produces the platform prompt-template library UI used by administrators for reusable copy-on-use authoring assets. It does not own prompt copy/activation.

## Dependencies

- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-011

## Enables

None.

## Acceptance Criteria

- [ ] Platform admins can manage data-driven template categories without mutating stable category slug/identity.
- [ ] Multiple templates can be browsed/authored within one category.
- [ ] Empty DRAFT template content can be saved; blank/whitespace-only publication is rejected and shown to the user.
- [ ] Published revision identity/hash/history is displayed without implying published content is editable.
- [ ] Disabled category/template history remains visible while new selection is unavailable.
- [ ] ADMIN is read-only and no secret/session token is rendered.
- [ ] Template-library state/actions do not accumulate in `StudioWorkspace`.
- [ ] No active prompt mutation or live model/provider execution occurs.

## Validation

- [ ] focused template-library route/component tests
- [ ] category/template lifecycle UI tests
- [ ] empty-draft/publish-validation UI regression
- [ ] authorization/development-bypass UI tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin another Phase 2 task.

## Implementation Notes

A template remains an authoring asset. Do not add UI wording or state that suggests an active platform/shop prompt stays dynamically linked to the template.

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
