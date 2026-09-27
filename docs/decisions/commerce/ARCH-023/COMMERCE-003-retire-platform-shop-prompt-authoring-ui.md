---
id: ARCH-023-COMMERCE-003
architecture_id: ARCH-023
title: Retire Platform and Shop prompt authoring from Studio
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-ADMIN-003
  - ARCH-023-COMMERCE-001
enables:
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Retire Platform and Shop prompt authoring from Studio

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Remove Commerce Studio as an authoring surface for Platform/Shop Instructions after the Admin authoring path is available, while retaining capability prompts, model configuration and read-only effective context where useful.

## Context

ARCH-023 assigns business/platform/shop instructions to Admin and executable capability prompts/tools to Commerce Studio. Two competing editors must not remain authoritative.

## Scope

- Remove/disable Platform prompt and selected-Shop prompt mutation UI/actions from Studio routes.
- Retain model configuration as currently owned unless explicitly unrelated to prompt authoring.
- Retain category/template information only where needed read-only for provenance/navigation, with Admin as management surface.
- Preserve capability prompt authoring and all Tool/Release workflows.

## Out of Scope

- Deleting prompt persistence/API used by Admin/runtime.
- Capability prompt changes.
- Admin UI implementation.

## Requirements

- No Studio path can mutate Platform or Shop Instructions after this task.
- Capability prompt authoring remains fully functional.
- Existing runtime resolver uses Admin-managed prompt state through C1.

## Work Items

- [ ] Remove mutation controls/actions and reconcile navigation/copy.
- [ ] Add negative mutation-route tests and capability-authoring regressions.

## Interfaces / Contracts

Depends on ARCH-023-ADMIN-003 being available and ARCH-023-COMMERCE-001 runtime composition.

## Dependencies

- ARCH-023-ADMIN-003
- ARCH-023-COMMERCE-001

## Enables

- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Platform/Shop prompt edits are impossible from Studio UI/actions.
- [ ] Capability prompt/tool/release authoring regressions remain green.

## Validation

- [ ] Focused Studio route/action tests.
- [ ] Capability authoring regression suite relevant to changed navigation/actions.
- [ ] Lint/typecheck/build as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

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

Pending.

### Follow-up

None
