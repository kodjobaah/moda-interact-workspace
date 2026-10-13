---
id: ARCH-038-ADMIN-002
architecture_id: ARCH-038
title: Manage Price Plan LIVE CommerceAgent overrides
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-13
---
# Manage Price Plan LIVE CommerceAgent overrides

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_admin`
- Repository: `moda-interact-admin`

## Objective

Add administrator-only optional LIVE CommerceAgent budget overrides to the existing Merchant Pricing Plan builder.

## Context

ARCH-024 assigns Commerce models on MerchantPricingPlan, not BillingPlan. Plan identity for subscription benefits matches by shopifyPlanHandle.

## Scope

- Add independent optional deadline and output-token override controls in the current Merchant Pricing Plan authoring flow.
- Display the inherited Platform value when each `budget` JSON key is absent, without persisting the computed value as an override.
- Implement audited version-checked plan policy changes and explicit clear-to-inherit actions.
- Preserve current price-plan publication, translations, economics and model association workflow.

## Out of Scope

- Do not create another plan editor, duplicate BillingPlan fields or modify live shop policy.
- Do not expose override mutation to merchant-facing apps.

## Requirements

- Use MerchantPricingPlan.id for persisted override association; selection remains current-subscription handle match in Background.
- Saving one key in a sparse versioned JSONB `budget` must not implicitly copy Platform values or erase the other key. Reject explicit JSON null and unknown schema versions.
- An inactive plan may remain the current subscribed plan; do not silently remove its existing benefits.

## Work Items

- [ ] Integrate form fields into existing Merchant Pricing Plan UI and actions.
- [ ] Add audit/CAS and inheritance validation.
- [ ] Add focused plan-authoring regressions including clears and conflicting edit.

## Interfaces / Contracts

Consumes `CommerceModelPolicy` (`context=LIVE`, `scope=PRICE_PLAN`, sparse `budget`) from DATABASE-001; no separate relation to BillingPlan.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Admin may override one field and inherit the other.
- [ ] Plan publishing/model/translation behaviour remains unchanged.
- [ ] Unauthorised changes and cross-plan writes are rejected.

## Validation

- [ ] Focused plan UI/action tests
- [ ] Relevant typecheck/lint/build scripts
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

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

Pending implementation

### Follow-up

None
