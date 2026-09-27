---
id: ARCH-023-BACKGROUND-002
architecture_id: ARCH-023
title: Reconcile Commerce shop profile activation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Reconcile Commerce shop profile activation

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Reconcile pending Store Category selections against durable Shopify subscription projection, creating the initial Shop Instructions automatically after activation and later category-change drafts without premature activation.

## Context

Pending category state is persisted before Managed Pricing. Durable `SubscriptionProjectionStatus.ACTIVE` or `TRIALING` is the activation authority; missed browser callbacks must be recoverable through existing billing/background reconciliation.

## Scope

- Consume/request profile reconciliation for one shop and add periodic/billing-cycle repair of eligible pending profiles.
- For first activation, verify active/trialing subscription plus pinned complete 20-locale template snapshot, create Shop prompt/revision/translations, publish/activate it, promote pending category to active and clear pending fields atomically.
- For later category change, create/update the pinned Shop Instructions DRAFT/translations while leaving current active category/prompt unchanged.
- Make all operations idempotent and stale-pending-safe.

## Out of Scope

- Shopify category-selection UI.
- Admin publication of later drafts.
- Changing subscription projection semantics.

## Requirements

- `onboardingCompleted` alone never activates profile state.
- First activation uses the exact template edit version/language previewed before redirect, even if Admin later edits/disables the template.
- Initial prompt/category promotion is transactional.
- Later category selection never self-publishes; Admin publication owns activation.
- Reconciliation tolerates missed enqueue/callback and repeated jobs.

## Work Items

- [ ] Add profile reconciliation service/worker integration.
- [ ] Integrate with existing billing reconciliation trigger/scan.
- [ ] Add first-activation, abandon, missed-callback, later-change and idempotency tests.

## Interfaces / Contracts

Consumes ARCH-023-SHARED-001 profile job and ARCH-023-DATABASE-002 profile/prompt/translation state.

## Dependencies

- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Pending onboarding remains inactive without active/trialing subscription.
- [ ] Active/trialing subscription promotes first category and initial prompt exactly once.
- [ ] Later category produces draft/pending state only.

## Validation

- [ ] Focused reconciliation tests with real database where repository convention requires.
- [ ] Billing reconciliation regression tests.
- [ ] Build/typecheck/lint as declared.
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
