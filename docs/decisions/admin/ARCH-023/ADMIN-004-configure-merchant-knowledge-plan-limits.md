---
id: ARCH-023-ADMIN-004
architecture_id: ARCH-023
title: Configure Merchant Knowledge plan limits
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Configure Merchant Knowledge plan limits

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Extend Admin pricing-plan feature configuration so platform admins can set and materialise validated Merchant Knowledge entry/content-unit limits without hard-coded plan names.

## Context

Merchant Knowledge limits live on the feature mapping. The database stores generic JSON; Shared owns the `MerchantKnowledgeFeatureConfigurationV1` schema.

## Scope

- Expose Merchant Knowledge configuration when the `merchant_knowledge` Feature is attached to a merchant pricing plan.
- Edit/validate `maxKnowledgeEntries` and `maxContentUnitsPerLocaleSource`.
- Materialise exact validated configuration into `BillingPlanFeature.configuration` using existing plan materialisation rules.
- Display validation errors and preserved values during plan editing.

## Out of Scope

- Creating the Commerce capability.
- Merchant knowledge URLs/content.
- Changing other feature configuration semantics.

## Requirements

- No Free/Starter branch logic.
- Unknown/invalid configuration is rejected before catalogue/materialised writes.
- Existing plan materialisation transaction/consistency behaviour is preserved.
- Other features may retain `{}` or their own future schemas without Merchant Knowledge-specific columns.

## Work Items

- [ ] Extend plan feature editor/server validation.
- [ ] Wire Shared schema into catalogue/materialisation path.
- [ ] Add plan edit/materialisation tests.

## Interfaces / Contracts

Consumes ARCH-023-DATABASE-001 and `MerchantKnowledgeFeatureConfigurationV1` from the published Shared package.

## Dependencies

- ARCH-023-DATABASE-001
- ARCH-023-SHARED-004

## Enables

- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Validated limits persist on catalogue mapping and materialise identically.
- [ ] Invalid/missing v1 fields fail closed for Merchant Knowledge.
- [ ] No unrelated feature mapping is rewritten.

## Validation

- [ ] Focused pricing/materialisation unit/security tests.
- [ ] Repository lint/typecheck/build as declared.
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
