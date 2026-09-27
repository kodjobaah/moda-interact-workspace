---
id: ARCH-023-ADMIN-002
architecture_id: ARCH-023
title: Manage Store Category and template translations
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-ADMIN-001
  - ARCH-023-DATABASE-002
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Manage Store Category and template translations

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Expose translation dispatch, progress, retry and immutable 20-locale readiness for Store Category and category-template source versions in Admin.

## Context

All 20 translations for the exact current source version must succeed before a category/template is available to merchant onboarding. Background owns provider execution; Admin owns authoring and operational presentation.

## Scope

- Dispatch translation for a category/template source edit version using the Shared contract.
- Display per-locale status for all 20 supported locales.
- Allow retry/re-dispatch of failed/missing current-version translations without mutating historical translations.
- Show stale-vs-current translation sets after source edits.

## Out of Scope

- Translation provider calls.
- Platform/shop prompt authoring.
- Changing the supported locale list.

## Requirements

- Admin never marks translation ready client-side; readiness comes from durable current-version translation state.
- All 20 locales are required; 19/20 remains unavailable.
- Historical version translations remain visible/read-only where useful for audit/provenance.
- Queue publication failure follows best-effort/reconciliation semantics and is visible without falsely marking success.

## Work Items

- [ ] Add translation actions/queue producer integration.
- [ ] Build translation status/retry UI.
- [ ] Add current/stale version and 20/20 gating tests.

## Interfaces / Contracts

Produces `CommerceConfigurationTranslationJob` consumed by ARCH-023-BACKGROUND-001.

## Dependencies

- ARCH-023-ADMIN-001
- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] 20/20 current translations yields Ready; any missing/failed locale does not.
- [ ] Editing source content makes prior translation set stale for availability.
- [ ] Retry targets exact source version and locale set.

## Validation

- [ ] Focused unit/security/UI tests.
- [ ] Queue payload contract tests.
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
