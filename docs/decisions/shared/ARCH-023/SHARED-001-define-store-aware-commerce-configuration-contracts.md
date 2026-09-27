---
id: ARCH-023-SHARED-001
architecture_id: ARCH-023
title: Define store-aware Commerce configuration contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
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
  - ARCH-023-SHARED-004
created: 2026-09-27
updated: 2026-09-27
---

# Define store-aware Commerce configuration contracts

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Define the versioned cross-service contracts and deterministic locale helpers for Store Category translation and Commerce shop-profile reconciliation.

## Context

Admin produces translation work, Shopify persists pending category selections, and Background reconciles translated configuration/profile activation. Those service boundaries need one canonical runtime-safe contract owner.

## Scope

- Define versioned Commerce configuration translation job schema/identifiers for category, template, platform-prompt and shop-prompt targets.
- Define versioned Commerce shop-profile reconciliation job schema/identifier.
- Expose deterministic supported-shop-language resolution using the existing 20-locale internationalisation definitions with English fallback.
- Define bounded target identity/version fields so translation work always names an exact source edit version/revision.

## Out of Scope

- Merchant Knowledge ingestion contracts.
- Translation provider implementation.
- Database tables or prompt publication logic.

## Requirements

- Contracts are strict, versioned and runtime validated.
- No queue payload contains full prompt text; workers load authoritative source text from PostgreSQL by durable identity/version.
- Locale resolution never uses customer conversation language.
- Unsupported/missing shop locale resolves to English.
- Deterministic job IDs deduplicate the same durable target/version while allowing a newer version to enqueue independently.

## Work Items

- [ ] Add schemas/types/constants/helpers in an appropriate Shared entrypoint.
- [ ] Add positive/negative contract tests and deterministic-ID tests.
- [ ] Export the new entrypoint through package build configuration.

## Interfaces / Contracts

Producers: Admin and Shopify/billing paths. Consumer: Background. Published package gate: ARCH-023-SHARED-004.

## Dependencies

None

## Enables

- ARCH-023-SHARED-004

## Acceptance Criteria

- [ ] Malformed/extra-field payloads reject.
- [ ] Same target/version yields same job ID; changed version yields a different ID.
- [ ] All 20 supported locales plus English fallback behave deterministically.

## Validation

- [ ] Focused unit tests.
- [ ] Shared build/export validation.
- [ ] Typecheck/lint as declared by the repository.
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
