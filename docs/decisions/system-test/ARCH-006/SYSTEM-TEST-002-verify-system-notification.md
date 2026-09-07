---
id: ARCH-006-SYSTEM-TEST-002
architecture_id: ARCH-006
title: Verify subscription-ended SYSTEM notification idempotency and translation
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 92
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-006-SHOPIFY-002
  - ARCH-006-SHOPIFY-003
  - ARCH-006-GATEWAY-001
enables: []
created: 2026-09-05
updated: 2026-09-06
---

# ARCH-006-SYSTEM-TEST-002: Verify subscription-ended SYSTEM notification idempotency and translation

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Verify the authoritative billing transition produces exactly one versioned SYSTEM support message with correct English/no-translation or non-English translated visibility.

## Context

This is separate from generic inbox tests because it exercises billing transition provenance/idempotency.

## Scope

Integrated subscription transition fixture through support-message outcome.

## Out of Scope

- Other future system notification codes.
- Translation infrastructure recovery matrix.

## Requirements

Verify genuine ACTIVE/TRIALING -> no-active-provider-subscription transition creates `SUBSCRIPTION_ENDED` v1 once; repeated inactive sync creates no duplicate; later distinct lifecycle can produce a new sourceKey/message; billing transition succeeds even when translation queue/provider is unavailable; English target is immediately AVAILABLE with no translation, non-English is not visible until exact translation AVAILABLE.

## Work Items

- [ ] Build/use authoritative billing transition fixture.
- [ ] Verify first transition, repeated sync and later-lifecycle source-key behavior.
- [ ] Verify English and non-English target branches.
- [ ] Verify queue/provider failure cannot roll back billing state.
- [ ] Record evidence.

## Interfaces / Contracts

Uses deployed Shopify/background/DB behavior under system-test conventions.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

None

## Acceptance Criteria

- [ ] One message per genuine source transition.
- [ ] No duplicate on repeated inactive sync.
- [ ] Billing state is independent of messaging failure.
- [ ] Translation/visibility branches match architecture.
- [ ] SYSTEM origin/provenance cannot be produced from UI paths.

## Validation

Run relevant system-test commands and record results/evidence.

## Implementation Notes

No future notification codes should be added merely to expand this test.

## Completion Report

### Status

Not started.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

None yet.

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
