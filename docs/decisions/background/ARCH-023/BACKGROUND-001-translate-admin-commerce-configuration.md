---
id: ARCH-023-BACKGROUND-001
architecture_id: ARCH-023
title: Translate Admin Commerce configuration
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Translate Admin Commerce configuration

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Extend the existing approved translation provider/reconciliation runtime to translate Store Categories, templates and Platform/Shop Instruction revisions into all 20 supported locales by exact source version.

## Context

ARCH-023 reuses the current OpenAI-backed translation provider and reconciliation mechanics; it must not create a second provider stack.

## Scope

- Consume `CommerceConfigurationTranslationJob`.
- Load exact durable source target/version and create immutable locale translation rows.
- Translate all 20 supported locales, including preserving/copying the source-language form as the corresponding locale result when appropriate.
- Update current-version translation readiness only after 20/20 success.
- Integrate missing/stale work into existing reconciliation patterns and provider retry classification.

## Out of Scope

- Admin UI.
- Merchant webpage translation.
- Capability prompt translation.
- New provider credentials/model selection.

## Requirements

- Translation output is bound to exact source edit version/revision.
- A newer source edit cannot be marked ready by older provider results.
- Partial success remains unavailable; retries are idempotent per target/version/locale.
- Existing merchant communications translation workflow remains behaviourally intact.

## Work Items

- [ ] Add target adapters into translation assembly/result/reconciliation flow without duplicating provider client.
- [ ] Add immutable translation persistence/readiness updates.
- [ ] Add 20-locale, stale-version, partial/failure/retry tests.

## Interfaces / Contracts

Consumes ARCH-023-SHARED-001 contracts; writes ARCH-023-DATABASE-002 translation rows.

## Dependencies

- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] 20/20 exact-version results set readiness.
- [ ] 19/20 or stale results do not.
- [ ] Existing translation workloads still pass regression tests.

## Validation

- [ ] Focused translation/reconciliation tests.
- [ ] Existing translation provider regression suite.
- [ ] Build/typecheck/lint as declared.
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
