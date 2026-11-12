---
id: ARCH-069-SHARED-001
architecture_id: ARCH-069
title: Preserve chronological model conversation inputs
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
  - ARCH-069-SHARED-002
created: 2026-11-12
updated: 2026-11-12
---

# Preserve chronological model conversation inputs

## Architecture

ARCH-069 — `docs/architecture/ARCH-069-chronological-commerce-model-inputs.md`; coordinator moda_architect.

## Objective

Correct the Shared OpenRouter model message order while preserving its existing contracts and validation.

## Context

Production's snowboard turn returned an internal-looking indicator. The model serializer independently places current context before prior history. This task addresses only its bounded owning outcome; the exact indicator cause requires evidence and must not be asserted merely from a passing structural test.

## Scope

Repository: `moda-interact-shared`.

- Move current-context message after validated older history and before current-turn tool results.
- Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Out of Scope

Moderation/STOP changes, sentinel blocklists, provider/model switching, schema or queue changes, credential edits, production message replay, unrelated dependency changes and another repository's implementation.

## Requirements

- Move current-context message after validated older history and before current-turn tool results.
- Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Work Items

- [ ] Move current-context message after validated older history and before current-turn tool results.
- [ ] Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- [ ] Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- [ ] Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Interfaces / Contracts

Existing Shared ModelRequest/ModelStep and `@modainteract/moda-interact-shared/commerce/model/node`; no wire schema changes. Background remains host/lifecycle owner. Shared implementation owner: ARCH-069-SHARED-001.

## Dependencies

None

## Enables

- ARCH-069-SHARED-002

## Acceptance Criteria

- [ ] Move current-context message after validated older history and before current-turn tool results.
- [ ] Add deterministic role/order/content regressions with older history ending in an assistant failure/indicator and a fresh product question.
- [ ] Retain malformed-history rejection, tool-result ownership validation, budgets, cancellation and provider error semantics.
- [ ] Prepare version 5.13.2 metadata and a validated package artifact; do not publish.

## Validation

- [ ] Inspect declared package scripts and run focused model adapter regressions.
- [ ] Run the existing full Shared suite, typecheck and build required by the repository.
- [ ] Run packed-export/import smoke validation; record exact artifact hash and version.
- [ ] Where the coordinator supplies a protected failed-context request, record paired old/new no-send probe evidence without committing private payloads; distinguish causality from structural correctness.

## Stop Condition

After the scoped work, acceptance criteria and required validation pass, complete this task's report, set review, publish both mirrored task branches, return to moda_architect and STOP. Do not begin dependent work, merge main or send a production message.

## Implementation Notes

Use launcher-resolved physical parent and implementation task worktrees for the entire attempt. Preserve unrelated changes. All no-send/live diagnostic artifacts must be protected and excluded from Git; no credentials or private customer prompt payloads in reports. Publication task validation is release mechanics only.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Existing request schemas and pinned-release contracts remain unchanged.

### Unresolved Issues

Exact indicator causality and production answer verification remain coordinator-owned evidence gates.

### Architectural Concerns

None beyond the bounded ordering defect.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
