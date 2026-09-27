---
id: ARCH-023-SHOPIFY-002
architecture_id: ARCH-023
title: Support post-onboarding Store Category changes
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-SHOPIFY-001
  - ARCH-023-DATABASE-002
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Support post-onboarding Store Category changes

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Let an onboarded merchant choose a different Store Category later without replacing the currently active category or published Shop Instructions.

## Context

A later category choice creates pending profile state and a candidate Shop Instructions draft; Admin publication is the activation boundary.

## Scope

- Add merchant settings surface showing active category and available ready categories.
- Persist a new pinned pending category/default-template edit version/language selection.
- Request profile reconciliation/draft creation best effort using the Shared contract.
- Show pending-category state while current active category remains effective.

## Out of Scope

- Admin publication UI.
- Automatic activation of later category changes.
- Concurrent multi-tab conflict special handling beyond normal persisted edit/version semantics.

## Requirements

- Changing category after onboarding never changes active category immediately.
- Existing published Shop Instructions continue to resolve until Admin publishes the pending category-generated draft.
- Repeated same pending selection is idempotent.

## Work Items

- [ ] Add category settings UI/action.
- [ ] Wire best-effort reconcile request.
- [ ] Add active-vs-pending and repeat-selection tests.

## Interfaces / Contracts

Produces pending `CommerceShopProfile` state consumed by ARCH-023-BACKGROUND-002 and subsequently published through ARCH-023-ADMIN-003.

## Dependencies

- ARCH-023-SHOPIFY-001
- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Active category remains unchanged after merchant submits a new category.
- [ ] Pending selection is visible/restorable.
- [ ] No direct prompt publication occurs in Shopify app.

## Validation

- [ ] Focused settings/service tests.
- [ ] Authorization/tenant-isolation tests.
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
