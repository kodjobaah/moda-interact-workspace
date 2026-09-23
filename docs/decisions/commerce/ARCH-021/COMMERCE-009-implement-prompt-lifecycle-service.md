---
id: ARCH-021-COMMERCE-009
architecture_id: ARCH-021
title: Implement platform and shop prompt lifecycle service
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
  - ARCH-021-DATABASE-001
  - ARCH-021-COMMERCE-008
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-021-COMMERCE-010
  - ARCH-021-COMMERCE-011
created: 2026-09-23
updated: 2026-09-23
---

# Implement platform and shop prompt lifecycle service

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide the authenticated Commerce lifecycle for platform/shop behavioural prompt drafts, immutable published revisions and independent environment-scoped active pointers.

## Context

ARCH-021 requires exactly one configurable behavioural prompt at runtime. Platform admins author one platform prompt lineage and optionally one shop-specific lineage per shop. Prompt templates are copy-on-use starting points, not runtime inheritance.

Phase 2 only authors and selects prompts; existing ARCH-020 per-capability prompts remain intact until the later runtime migration.

## Scope

- Read/create the singleton platform prompt lineage and per-shop prompt lineage.
- Create/update prompt drafts with CAS/edit-version semantics.
- Allow a new draft to start blank/from current lineage content or by copying one exact published template revision.
- Record `sourceTemplateRevisionId` provenance without dynamic linkage.
- Publish immutable prompt revisions.
- Read/set the current environment's platform active prompt pointer.
- Read/set/clear the current environment's shop prompt override pointer.
- Enforce that active pointers target published revisions.
- Enforce platform pointer -> platform lineage and shop pointer -> the exact selected shop's lineage.
- Derive environment server-side and validate shop identity server-side.
- Write durable audit events for privileged mutations.
- Expose typed server actions/ports for Studio.

## Out of Scope

- Removing capability-level prompt fields.
- Manifest/grant/runner changes.
- Executing a model with the prompt.
- Merchant authorization.
- Shop-owned reusable templates.

## Requirements

- ADMIN is read-only; mutations require SUPER_ADMIN outside development bypass.
- Development bypass uses the canonical effective development actor.
- Only one platform lineage and at most one lineage per shop may exist; service handles concurrent create races using database constraints/idempotency.
- Published revisions cannot be mutated.
- Copy-from-template copies exact content into the new prompt draft and records provenance; subsequent template changes have no effect.
- Clearing a shop prompt override means inheritance and must not alter shop model selection.
- Pointer mutations use CAS/editVersion and distinguish replay/conflict/unknown outcomes consistently with existing Studio commands.

## Work Items

- [ ] Implement platform/shop prompt lineage read/create operations.
- [ ] Implement draft create/update operations with CAS.
- [ ] Implement copy-from-published-template draft creation.
- [ ] Implement immutable publish operation.
- [ ] Implement platform active pointer set/read.
- [ ] Implement shop override set/read/clear.
- [ ] Enforce prompt scope and published-state invariants.
- [ ] Add audit events and typed server actions/ports.
- [ ] Add concurrency, scope, template-copy, CAS/replay and auth tests.

## Interfaces / Contracts

Consumes:

- ARCH-021-DATABASE-001 prompt lineages/revisions and environment-scoped active pointers.
- ARCH-021-COMMERCE-008 exact template-revision reads for copy-on-use.

Produces a Commerce-local prompt configuration port for effective resolution and Studio UI.

## Dependencies

- ARCH-021-DATABASE-001
- ARCH-021-COMMERCE-008
- ARCH-020-COMMERCE-002

## Enables

- ARCH-021-COMMERCE-010
- ARCH-021-COMMERCE-011

## Acceptance Criteria

- [ ] Platform and shop prompt lineages obey singleton/per-shop ownership.
- [ ] Draft edits are CAS protected and published revisions are immutable.
- [ ] A prompt draft created from a template is an independent copy with immutable provenance.
- [ ] Platform active prompt can only target a published platform revision.
- [ ] Shop override can only target a published revision belonging to that exact shop.
- [ ] Clearing the shop prompt override returns prompt inheritance without changing model state.
- [ ] Existing capability prompt/runtime behaviour is not modified in Phase 2.
- [ ] No model/provider call occurs.

## Validation

- [ ] focused prompt lifecycle tests
- [ ] template-copy/provenance tests
- [ ] CAS/concurrency tests with disposable PostgreSQL where required
- [ ] focused authorization/development-bypass tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Do not concatenate platform and shop configurable prompts. Shop override selection replaces the platform configurable prompt for that shop.

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
