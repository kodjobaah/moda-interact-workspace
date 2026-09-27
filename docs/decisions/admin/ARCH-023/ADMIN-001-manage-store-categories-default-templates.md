---
id: ARCH-023-ADMIN-001
architecture_id: ARCH-023
title: Manage Store Categories and default templates
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-002
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-ADMIN-002
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Manage Store Categories and default templates

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Add the Admin management surface for Store Categories, Shopify taxonomy mappings and each category's explicit default Commerce prompt template.

## Context

The database category/template concepts already exist but Admin has no management UI. ARCH-023 makes Store Category a merchant onboarding input, so platform admins need one authoritative catalogue surface.

## Scope

- Create/list/edit/enable-disable Store Categories.
- Designate exactly one platform fallback category.
- Manage Shopify taxonomy mappings.
- Create/list/edit/enable-disable templates within a category and choose that category's explicit default template.
- Show source language/edit version and translation-readiness state without implementing translation execution in this task.
- Use existing platform-admin authorization/audit conventions.

## Out of Scope

- Translation worker implementation.
- Platform/shop instruction authoring.
- Shopify merchant onboarding UI.

## Requirements

- Cannot make an enabled category merchant-selectable without an enabled default template whose 20 translations are current/available.
- Default template must belong to the category.
- Fallback/category/taxonomy invariants are enforced server-side, not only in UI.
- Admin actions use existing audit/security patterns and never write another repository.

## Work Items

- [ ] Add server actions/services for category/template/mapping lifecycle.
- [ ] Add Admin navigation and management screens.
- [ ] Add focused authorization/validation/UI tests.

## Interfaces / Contracts

Consumes ARCH-023-DATABASE-002 and published ARCH-023 Shared locale/config contracts.

## Dependencies

- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-ADMIN-002
- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Admin can create a category, map taxonomy ids, create templates, set one default and designate fallback subject to server validation.
- [ ] Unauthorized users cannot mutate catalogue state.
- [ ] Unavailable translations prevent merchant-selectable readiness.

## Validation

- [ ] Focused unit/security/UI tests.
- [ ] Repository lint/typecheck/build as declared for changed areas.
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
