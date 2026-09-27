---
id: ARCH-023-ADMIN-003
architecture_id: ARCH-023
title: Author Platform and Shop Instructions in Admin
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-002
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-COMMERCE-003
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Author Platform and Shop Instructions in Admin

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Make Admin the authoritative product UI for Platform Instructions and shop-scoped Shop Instructions, including draft/revision publication gated by complete 20-locale translations.

## Context

ARCH-021 currently exposes platform/shop prompt authoring in Commerce Studio. ARCH-023 moves business/platform prompt ownership to Admin while retaining the existing Commerce persistence/lifecycle semantics and leaving capability prompts in Studio.

## Scope

- Platform Instructions list/edit draft/publish workflow.
- Shop selection and Shop Instructions list/edit draft/publish workflow.
- Translation dispatch/status for exact prompt revision/edit version.
- Read-only provenance when a Shop prompt was seeded from a category template.
- CAS/stale-write guards and existing platform-admin authorization/audit semantics.

## Out of Scope

- Capability prompt authoring.
- Removing Commerce Studio UI (owned by ARCH-023-COMMERCE-003).
- Translation provider implementation.
- Changing model-selection UI.

## Requirements

- Platform and Shop Instructions are independently persisted; Shop publication never replaces/deletes Platform Instructions.
- Publication/activation is rejected until all 20 current-version translations are available.
- Existing published prompt remains active while a new draft/translation set is incomplete.
- Later category-generated shop drafts require explicit Admin publication.
- Admin uses one authoritative backend persistence/lifecycle, not a duplicate prompt store.

## Work Items

- [ ] Expose Admin server actions/services using existing Commerce prompt tables/lifecycle invariants.
- [ ] Build Platform Instructions and selected-Shop Instructions screens.
- [ ] Add translation readiness, CAS and provenance UI/tests.

## Interfaces / Contracts

Consumes ARCH-023-DATABASE-002 and Shared translation/locale contracts; produces translation jobs for ARCH-023-BACKGROUND-001.

## Dependencies

- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-COMMERCE-003
- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Platform and Shop prompt drafts can be authored independently.
- [ ] 20/20 translation gate is enforced server-side.
- [ ] Publishing a Shop prompt does not alter the Platform prompt.
- [ ] Category-template provenance remains visible and immutable for the seeded revision.

## Validation

- [ ] Focused unit/security/UI tests.
- [ ] CAS/stale-write regressions.
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
