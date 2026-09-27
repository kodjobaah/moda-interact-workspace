---
id: ARCH-023-COMMERCE-001
architecture_id: ARCH-023
title: Compose localised Platform and Shop Instructions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-002
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-COMMERCE-003
  - ARCH-023-SYSTEM-TEST-001
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Compose localised Platform and Shop Instructions

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Change effective Commerce prompt resolution from Shop-overrides-Platform to additive localised Platform + optional Shop Instructions while preserving independent model override semantics and immutable runner precedence.

## Context

ARCH-021 currently resolves one effective prompt. ARCH-023 requires the immutable kernel first, then store-language Platform Instructions, then store-language Shop Instructions, then capability prompts. Customer conversation language controls reply language only.

## Scope

- Resolve shop configuration language from `ShopSettings.defaultLanguageTag` through the Shared supported-locale helper with English fallback.
- Load active Platform prompt translation and optional active Shop prompt translation for that shop language.
- Compose both as trusted host instructions in deterministic order.
- Preserve `shop model override ?? platform model` behaviour unchanged.
- Fail closed for missing/incomplete active translation state rather than switching to customer language.
- Update Studio/runtime effective-configuration read models/tests as required without retaining Shop-prompt replacement semantics.

## Out of Scope

- Admin authoring UI.
- Capability prompt changes.
- Merchant Knowledge vector lookup.

## Requirements

- Platform Instructions are always retained when a Shop prompt exists.
- Shop/customer language are not conflated.
- English fallback applies only when shop language is absent/unsupported or localized configuration policy explicitly permits it.
- Immutable Shared kernel remains ahead of all configurable prompts.

## Work Items

- [ ] Refactor effective configuration/prompt resolution.
- [ ] Wire composed instructions into production/preview runner calls.
- [ ] Add platform-only, platform+shop, locale/fallback and customer-language-independence tests.

## Interfaces / Contracts

Consumes ARCH-023-DATABASE-002 and published Shared locale/runner contracts.

## Dependencies

- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-COMMERCE-003
- ARCH-023-SYSTEM-TEST-001
- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Shop prompt no longer replaces Platform prompt.
- [ ] Changing customer language does not select a different Platform/Shop translation.
- [ ] Model override behaviour is unchanged.

## Validation

- [ ] Focused effective-config/runtime/preview tests.
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
