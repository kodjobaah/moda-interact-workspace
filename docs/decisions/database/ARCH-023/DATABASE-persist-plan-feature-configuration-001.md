---
id: ARCH-023-DATABASE-001
architecture_id: ARCH-023
title: Persist generic plan-feature configuration
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-023-ADMIN-004
  - ARCH-023-SHOPIFY-003
  - ARCH-023-BACKGROUND-003
  - ARCH-023-COMMERCE-002
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Persist generic plan-feature configuration

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Add durable generic JSON configuration to merchant pricing-plan feature mappings and their materialised billing-plan feature mappings without introducing Merchant Knowledge-specific billing columns.

## Context

ARCH-023 needs plan-owned Merchant Knowledge limits, but plan names must not be hard-coded. The existing `MerchantPricingPlanFeature` and `BillingPlanFeature` rows already represent catalogue and materialised feature membership, so the configuration must travel with those mappings.

## Scope

- Add `configuration JSONB` with a safe empty-object default to both plan-feature mapping models.
- Add one migration preserving all existing rows and uniqueness/foreign-key semantics.
- Extend schema/migration fixtures so materialisation can prove exact JSON preservation.

## Out of Scope

- Merchant Knowledge entry/source tables.
- Admin UI or Shared runtime validation of feature-specific configuration.
- Changing existing Feature activation or preference semantics.

## Requirements

- Existing mappings migrate to `{}` without data loss.
- The database treats configuration as generic opaque JSON; feature-specific schema validation belongs to Shared/application code.
- Catalogue-to-billing materialisation can copy configuration byte-for-byte/equivalently without adding a second configuration store.
- No plan-name-specific columns or Free/Starter constants are introduced.

## Work Items

- [ ] Update Prisma schema and migration.
- [ ] Add fresh-schema and upgrade-preservation fixtures.
- [ ] Add/extend database validation for plan-feature configuration round-trip.

## Interfaces / Contracts

Produces `MerchantPricingPlanFeature.configuration` and `BillingPlanFeature.configuration` for consumers. `ARCH-023-SHARED-002` owns the Merchant Knowledge v1 runtime schema.

## Dependencies

None

## Enables

- ARCH-023-ADMIN-004
- ARCH-023-SHOPIFY-003
- ARCH-023-BACKGROUND-003
- ARCH-023-COMMERCE-002
- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Existing feature mappings survive migration with `{}` configuration.
- [ ] Non-empty JSON configuration round-trips through Prisma/database.
- [ ] Uniqueness and delete behaviour of plan-feature mappings remain unchanged.

## Validation

- [ ] `prisma validate` for the repository schema.
- [ ] Fresh migration validation.
- [ ] Upgrade migration validation with pre-existing plan-feature rows.
- [ ] Focused schema/fixture tests and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Do not add database constraints that attempt to understand individual feature configuration shapes.

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
