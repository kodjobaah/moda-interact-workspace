---
id: ARCH-031-DATABASE-002
architecture_id: ARCH-031
title: Add Merchant Pricing publication lifecycle
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-031-DATABASE-001
  - ARCH-031-BACKGROUND-001
enables:
  - ARCH-031-ADMIN-003
  - ARCH-031-BACKGROUND-002
created: 2026-10-11
updated: 2026-10-11
---

# Add Merchant Pricing publication lifecycle

## Architecture

Architecture ID: `ARCH-031`

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`

Coordinator: `moda_architect`

## Objective

Persist an inactive English-only Merchant Pricing publication draft while automatic translation is running, while preserving exact 20-locale completeness before the plan can become READY/active.

## Context

Implementation showed that translation must begin only after the administrator explicitly saves a complete valid draft. The original no-persisted-draft design therefore required a bounded database lifecycle extension.

This task is recorded retrospectively during final reconciliation because the implementation exists in the 2026-10-11 snapshot but its durable task file was not materialised at implementation time.

## Scope

- add `MerchantPricingPlanPublicationStatus` with `TRANSLATING`, `TRANSLATION_FAILED`, `READY`;
- add `currentTranslationRunId` linkage and publication indexes/constraints;
- require active plans to be READY;
- require non-READY plans to remain linked to their translation run;
- permit exactly English source translations while non-READY;
- preserve exact canonical 20-locale validation when READY;
- provide focused schema/migration validators and PostgreSQL fresh/upgrade rehearsal coverage.

## Out of Scope

- Admin builder behaviour;
- provider execution;
- Background publication logic;
- system-test implementation.

## Requirements

The linked run handle must match the plan handle. Non-READY plans remain inactive and English-only. READY plans/highlights retain the exact ARCH-014 canonical locale completeness invariant.

## Work Items

- [x] Add publication status enum and plan fields.
- [x] Add active/READY and non-READY/run integrity constraints.
- [x] Adapt plan/highlight validation functions for publication state.
- [x] Add schema/migration validators and PostgreSQL rehearsal script.

## Interfaces / Contracts

Database-owned persisted lifecycle consumed by Admin and Background. No new published Shared contract.

## Dependencies

- `ARCH-031-DATABASE-001`
- `ARCH-031-BACKGROUND-001`

## Enables

- `ARCH-031-ADMIN-003`
- `ARCH-031-BACKGROUND-002`

## Acceptance Criteria

- [x] A TRANSLATING/TRANSLATION_FAILED plan cannot be active.
- [x] A non-READY plan is linked to a matching translation run and stores English-only translation source.
- [x] A READY plan/highlight requires the exact canonical 20-locale set.
- [x] Existing development plans default to READY; no production backfill/compatibility mechanism is required.

## Validation

- [x] Static ARCH-031 publication lifecycle validator.
- [x] Developer-side PostgreSQL fresh/upgrade rehearsal accepted during implementation.
- [x] `git diff --check` accepted during implementation.

## Stop Condition

Retrospectively satisfied; implementation is complete and architect-accepted.

## Implementation Notes

Migration: `prisma/migrations/20261010170000_arch031_merchant_pricing_publication_lifecycle/migration.sql`.

## Completion Report

### Status

Ready for Review — retrospectively materialised from accepted integrated implementation.

### Files Changed

`prisma/schema.prisma`, publication lifecycle migration and focused validation/rehearsal scripts.

### Work Completed

Publication lifecycle implemented as scoped.

### Validation Results

`npm run test:arch031-merchant-pricing-publication-lifecycle` passed during 2026-10-11 snapshot review. Developer-side PostgreSQL rehearsal evidence was accepted during implementation.

### Deviations

Task record was materialised retrospectively during final reconciliation.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

The migration and Prisma schema match the reconciled persisted-draft lifecycle and preserve the activation/completeness boundary.

### Reviewed Files

`prisma/schema.prisma`; `prisma/migrations/20261010170000_arch031_merchant_pricing_publication_lifecycle/migration.sql`; focused ARCH-031 validator/rehearsal scripts.

### Validation Reviewed

Static publication lifecycle validator PASS in snapshot review; accepted developer-side PostgreSQL evidence.

### Architecture Conformance

Conforms.

### Follow-up

ARCH-031-SYSTEM-TEST-001 remains terminal validation.
