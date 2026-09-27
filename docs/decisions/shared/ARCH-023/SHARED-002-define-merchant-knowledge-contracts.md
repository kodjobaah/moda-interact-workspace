---
id: ARCH-023-SHARED-002
architecture_id: ARCH-023
title: Define Merchant Knowledge contracts and content units
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-023-SHARED-004
created: 2026-09-27
updated: 2026-09-27
---

# Define Merchant Knowledge contracts and content units

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Define canonical Merchant Knowledge purpose, plan-configuration, process/reconcile queue contracts and the deterministic language-neutral content-unit metric.

## Context

Plan configuration is opaque JSON at the database layer. Shopify, Background and Commerce must agree on one validated Merchant Knowledge configuration and one content-unit calculation.

## Scope

- Define allow-listed Merchant Knowledge Purpose values.
- Define `MerchantKnowledgeFeatureConfigurationV1` with `schemaVersion`, `maxKnowledgeEntries`, and `maxContentUnitsPerLocaleSource` plus bounded positive limits.
- Define process and reconcile job schemas plus deterministic job-id helpers.
- Implement `countMerchantKnowledgeContentUnits` using NFC, whitespace normalization, Unicode code-point counting and `ceil(codePoints / 4)`.
- Expose constants/helpers through a runtime-safe Shared entrypoint.

## Out of Scope

- Embedding model/provider selection.
- URL fetching or HTML extraction.
- Database/vector implementation.

## Requirements

- Content-unit calculation must count Unicode code points, never UTF-16 code units or LLM tokens.
- Configuration validation fails closed for missing/unknown schema versions or invalid bounds.
- Queue payloads carry durable ids/generation/revision identity, not extracted content or vectors.
- Knowledge Purpose is metadata only and grants no tool authority.

## Work Items

- [ ] Implement schemas/types/constants/helpers.
- [ ] Add multilingual content-unit fixtures including combining characters/emoji/CJK/whitespace normalization.
- [ ] Add queue contract/idempotency tests and export validation.

## Interfaces / Contracts

Producer: Shopify. Consumer: Background. Commerce consumes purpose/config helpers. Published package gate: ARCH-023-SHARED-004.

## Dependencies

None

## Enables

- ARCH-023-SHARED-004

## Acceptance Criteria

- [ ] Equivalent NFC-normalized text produces identical units.
- [ ] CJK/emoji cases are deterministic.
- [ ] Unknown configuration fields/versions reject.
- [ ] Process/reconcile ids are deterministic and revision-sensitive.

## Validation

- [ ] Focused tests including multilingual fixtures.
- [ ] Package build/export validation.
- [ ] Typecheck/lint as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Use the 1500-unit value only as an example/default planning value where a caller explicitly needs one; do not encode Free/Starter commercial constants.

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
