---
id: ARCH-070-SHARED-004
architecture_id: ARCH-070
title: Publish accepted canonical selection semantics
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-070-SHARED-003
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Publish accepted canonical selection semantics

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Publish accepted canonical selection semantics within existing verified and bounded execution contracts.

## Context

Provider-free reproductions prove schema-valid missing-version/nonempty-list can skip runner repair but host drops the list; truthy null/null shipping without disposition similarly skips repair but host discards it. Fresh production version6 exact raw final shape is unavailable, so historical exact cause is not claimed. Existing accepted null-URL/footer/terminal fixes remain valid.

## Scope

Only exact accepted immutable5.13.4 artifact publication, canonical metadata/download verification and receipt.

## Out of Scope

Unrelated refactors, provider/model changes, fabricated selections or automatic product choice, new queue retry loop, broader schema/infra/credential/consent changes, live customer sends or resetting processed input.

## Requirements

After prerequisite architect acceptance and developer merge, sole-publish exact accepted5.13.4 artifact once to canonical public npm. No implementation changes, tests/lint/types/build reruns or consumer work. Metadata and actual downloaded bytes must match accepted hashes; no duplicate publish during propagation.

## Work Items

- [ ] Verify accepted exact artifact and prerequisite merge.
- [ ] Publish once and verify actual canonical downloadable bytes.
- [ ] Report release evidence and stop.

## Interfaces / Contracts

Shared owns canonical semantic normalization and repair eligibility; public package @modainteract/moda-interact-shared/commerce. Background consumes published helper and retains tenant/provider/evidence policy. Existing schemas, normal answer contract and budgets remain compatible.

## Dependencies

ARCH-070-SHARED-003. Publication additionally requires developer merge of accepted implementation.

## Enables

Next publication/consumer task in ARCH-070, then developer production verification.

## Acceptance Criteria

- [ ] Requirements hold, including unchanged security and bounded failure behavior.
- [ ] Canonical reusable mechanics are not duplicated across Shared/Background.
- [ ] No private prose, prompts or secret payloads added to diagnostics.
- [ ] Prepared mirrored worktree, start-sync and recursive submodule evidence recorded.

## Validation

- [ ] Accepted prerequisite/version/artifact hashes, successful canonical publish receipt, exact registry metadata plus actual downloaded bytes, no unauthorized source changes.
- [ ] Exact changed-file scope and diff/secret hygiene.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

Historical exact raw final shape remains unconfirmed; deterministic contract gaps are reproduced.

### Unresolved Issues

None beyond owned correction.

### Architectural Concerns

Return cross-owner gaps before modifying outside scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
