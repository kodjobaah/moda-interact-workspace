---
id: ARCH-023-SYSTEM-TEST-001
architecture_id: ARCH-023
title: Validate Store Category and prompt localisation end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-002
  - ARCH-023-SHARED-004
  - ARCH-023-ADMIN-001
  - ARCH-023-ADMIN-002
  - ARCH-023-ADMIN-003
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHOPIFY-002
  - ARCH-023-BACKGROUND-001
  - ARCH-023-BACKGROUND-002
  - ARCH-023-COMMERCE-001
  - ARCH-023-COMMERCE-003
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Validate Store Category and prompt localisation end to end

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Validate the integrated Store Category onboarding, 20-locale prompt lifecycle and additive Platform/Shop instruction behaviour after all implementation dependencies are architect-accepted and developer manual validation is complete.

## Context

This is a terminal architecture-validation task. It must not gate unfinished implementation work.

## Scope

- Seed/author an enabled category with explicit default template, mappings/fallback and all 20 translations.
- Validate Shopify category preselection, merchant override, pending persistence before Managed Pricing, abandon/return behaviour and ACTIVE/TRIALING activation.
- Validate initial Shop Instructions use the exact pinned template edit-version bundle.
- Validate later category change produces a draft/pending state until Admin publication.
- Validate Platform + Shop Instructions are additive and selected by shop language with English fallback, while customer language only changes reply presentation.

## Out of Scope

- Merchant Knowledge URL/vector ingestion (SYSTEM-TEST-002).
- Rare simultaneous multi-tab onboarding races explicitly excluded from v1.

## Requirements

- Use integrated services/databases/queues rather than repository-local mocks for asserted cross-service outcomes.
- Capture durable evidence identifying shop/profile/prompt/template versions and language choices.

## Work Items

- [ ] Add/extend system scenario fixture and runner.
- [ ] Execute integrated happy/failure/language cases.
- [ ] Record evidence and cleanup.

## Interfaces / Contracts

Terminal validation of ARCH-023 category/prompt path.

## Dependencies

- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004
- ARCH-023-ADMIN-001
- ARCH-023-ADMIN-002
- ARCH-023-ADMIN-003
- ARCH-023-SHOPIFY-001
- ARCH-023-SHOPIFY-002
- ARCH-023-BACKGROUND-001
- ARCH-023-BACKGROUND-002
- ARCH-023-COMMERCE-001
- ARCH-023-COMMERCE-003

## Enables

None

## Acceptance Criteria

- [ ] No prompt/category activates before ACTIVE/TRIALING subscription projection.
- [ ] All-20 translation gate is observable.
- [ ] Pinned template version survives later Admin edit.
- [ ] Platform instructions remain present with Shop instructions.
- [ ] French shop configuration can respond to English customer in English without switching underlying shop prompt locale.

## Validation

- [ ] Integrated system scenario passes against architecture-approved topology.
- [ ] Evidence records exact versions/ids/statuses.
- [ ] Cleanup leaves no cross-test tenant state.
- [ ] `git diff --check` for system-test repository changes.

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
