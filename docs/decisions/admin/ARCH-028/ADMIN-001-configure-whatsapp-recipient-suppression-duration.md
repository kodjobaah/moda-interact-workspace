---
id: ARCH-028-ADMIN-001
architecture_id: ARCH-028
title: Configure WhatsApp recipient suppression duration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-DATABASE-001
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-07
updated: 2026-10-07
---

# Configure WhatsApp recipient suppression duration

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Expose the ARCH-028 platform-level WhatsApp recipient suppression duration through the existing SUPER_ADMIN Platform Billing Policy controls, defaulting to seven days and preserving existing policy audit/version semantics.

## Context

DATABASE-001 adds `PlatformBillingPolicy.whatsappRecipientSuppressionDays @default(7)`. The Admin application already reads/mutates/audits the singleton Platform Billing Policy through SUPER_ADMIN controls.

## Scope

- Read/render the current suppression-day value on `/system-controls/platform-policy` using existing UI conventions.
- Accept a required positive integer day count; default/read value is `7` from persistence.
- Persist through the existing platform-policy mutation/upsert transaction.
- Include the field in before/after billing audit snapshots and policy version increment automatically through the existing path.
- Add/update Admin translations/tests/types/read models required by the existing form.

## Out of Scope

- Per-Shop suppression override.
- Reachability runtime logic.
- Provider-code classification.
- Database schema/migration.

## Requirements

- [ ] Existing SUPER_ADMIN authorization remains unchanged.
- [ ] Value must be positive; zero/negative/invalid input is rejected with bounded UI error.
- [ ] Saving another policy field must not silently reset suppression days.
- [ ] No duplicate policy store/config mechanism is introduced.

## Work Items

- [ ] Extend policy validation/input types/action/read model.
- [ ] Add form field/help text/translations.
- [ ] Add focused validation/action/component tests.

## Interfaces / Contracts

Consumes `PlatformBillingPolicy.whatsappRecipientSuppressionDays` from DATABASE-001.

## Dependencies

- `ARCH-028-DATABASE-001`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Existing persisted value displays correctly.
- [ ] Seven-day default is visible when policy is initialized normally.
- [ ] SUPER_ADMIN can change value and audited policy mutation increments version.
- [ ] Invalid non-positive values are rejected.

## Validation

Use repository-declared focused unit/component/action tests, lint/typecheck/build as available, and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

This is a platform policy, not a merchant setting. Do not add a ShopBillingPolicyOverride field in ARCH-028.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
