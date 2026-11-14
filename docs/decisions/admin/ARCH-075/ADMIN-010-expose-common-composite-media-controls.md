---
id: ARCH-075-ADMIN-010
architecture_id: ARCH-075
title: Expose common composite media bindings and dimensions
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T11:47:43Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-009
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Expose common composite media bindings and dimensions

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Expose truthful common-template media bindings with discoverable saved logo/product dimensions and matching schematic preview.

## Context

ADMIN009 is Complete and already provides compositeProfile geometry. Existing logoWidth/Height and productWidth/Height controls are hidden under a profile checkbox. response.productImage is an AI-only optional BEFORE_BODY binding; SHARED composite runtime independently uses the verified selected product. Do not expose a selectable SHARED field the worker ignores.

## Scope

Admin template editor controls, binding explanation and preview; focused UI/persistence regression tests.

## Out of Scope

Shared releases, Background semantics, new variables/URLs/media sources, provider registration, live edits, activation, database/schema changes, independent configuration policy.

## Requirements

Show fixed trusted shop-logo and optional verified selected-product bindings for SHARED common composites; identify image absence/no-product behavior honestly. Reuse existing compositeProfile numeric dimensions and validation, grouped clearly as Logo size and Product image size. Make required profile discoverable rather than hidden behind an unchecked optional-looking control. Preserve existing AI productImage binding behavior. Do not save SHARED productImage or imply arbitrary binding choices. Preview uses same saved/unsaved geometry, product/no-product variants and caption position; label schematic accurately. Preserve canonical source/profile hashing, explicit clone/review workflow, locale equality, bounds, and historical audit display. No infrastructure or telemetry changes.

## Work Items

- [ ] Inspect current editor/binding/preview seams.
- [ ] Expose fixed SHARED media bindings and grouped dimensions.
- [ ] Update matching preview and focused regressions.
- [ ] Record exact isolation/source/check evidence.

## Interfaces / Contracts

Published Shared6.0.0 compositeProfile and existing AI ConversationProductImageBinding remain unchanged. SHARED presentation uses existing runtime-selected verified product, not an invented response variable.

## Dependencies

ARCH-075-ADMIN-009 Complete and integrated.

## Enables

None

## Acceptance Criteria

- [ ] SHARED editor visibly explains actual logo/verified-product binding without unsupported selectable fields.
- [ ] Logo/product width and height are explicit, discoverable and persist through existing clone/save/read.
- [ ] Preview reflects edited dimensions and no-product case; AI binding behavior unchanged.
- [ ] Invalid dimensions/profile and immutable existing revisions remain protected.

## Validation

- [ ] Focused editor/preview/profile persistence tests and relevant authoring tests.
- [ ] Types, scoped lint, production build and exact remote check.
- [ ] Inspect package scripts; no unaffected PG/full-suite repeats unless relevant failure requires them.
- [ ] Diff/privacy and browser-safe dependency graph checks appropriate to changed imports.

## Stop Condition

After work/checks publish source and mirrored report, set review and STOP. Root owns all merges/live operations.

## Implementation Notes

Normal moda-task launcher must create dedicated sibling worktrees; task authoring created only parent worktree. You are not alone; preserve others. Prefer existing controls and preview over new editor/framework. Return any genuine unsupported runtime binding requirement before implementing contract changes.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

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

Pending actual implementation

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root integration after acceptance
