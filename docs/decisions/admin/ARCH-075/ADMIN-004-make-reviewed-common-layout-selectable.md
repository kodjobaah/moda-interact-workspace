---
id: ARCH-075-ADMIN-004
architecture_id: ARCH-075
title: Make reviewed common layouts selectable from editor workflow
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-ADMIN-003
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Make reviewed common layouts selectable from editor workflow

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Make reviewed common layouts selectable from editor workflow.

## Context

Actual immutable common wrapper has all 20 reviewed projections but definition remains TRANSLATION_QUEUED; selector/eligibility allow only SAVED/PUBLISHED. Separately, editor blank footer becomes one empty text node, while canonical Shared common reference requires a zero-node static footer. Do not rewrite existing saved snapshots or bypass canonical validation.

## Scope

New wrapper draft/editor empty optional-footer AST conversion; wrapper staging selector/eligibility lifecycle parity; actual draft/save/translation/review/selector/activation regressions. Existing compiler output, immutable records and canonical Shared5.13.9 remain unchanged.

## Out of Scope

Live definition edits, translation/provider requests, activation, production replay/reset, source merges, new schemas/packages, broad translation refactors or permission workarounds.

## Requirements

For NEW editable drafts, exactly empty optional static footer becomes [], preserving nonempty and whitespace-only authored bytes. Fix actual editor conversion/default, not old compiler semantics or saved-row normalization. Existing invalid source requires a legitimate new cloned/saved identity and translations/review. Align staging definition statuses with existing Meta source eligibility: SAVED, TRANSLATION_QUEUED, TRANSLATING, PARTIALLY_FAILED, READY_FOR_REVIEW, PUBLISHED. All 20 canonical immutable locale/reviewer/author/hash/protected-token checks remain mandatory; retired/malformed/incomplete sources refuse. Status labels alone never establish readiness. Existing coordinated CAS is the only publication/activation path; final runtime still requires PUBLISHED and active pointer. No DB status workaround, Shared release or Background change. Preserve old snapshots/compiler/hash bytes and provide strict end-to-end actual function/UI draft conversion proof.

## Work Items

- [ ] Reproduce both actual editor/lifecycle blockers before correction.
- [ ] Correct only new draft empty-footer and reviewed staging eligibility boundaries.
- [ ] Prove end-to-end actual owning workflow and strict negative/legacy compatibility; submit report and stop.

## Interfaces / Contracts

Existing Admin authoring AST, immutable compiler/snapshot hashes, wrapper eligibility and coordinated activation. Published Shared5.13.9 common-reference parser unchanged. No new cross-service contract.

## Dependencies

ARCH-075-ADMIN-003; ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] New common wrapper editor workflow yields canonical empty static footer without altering old projections.
- [ ] Fully reviewed staged wrapper is selectable and can publish through existing coordinated CAS; incomplete/retired/hash-invalid sources remain refused.
- [ ] Actual draft→save→translation/review→selector→activation regression and canonical isolation evidence complete; no live mutation.

## Validation

- [ ] Meaningful red/green for blank editor footer and reviewed TRANSLATION_QUEUED definition; actual save/review/selector/coordinator flow with real PostgreSQL where persistence matters.
- [ ] Unknown/retired/incomplete/tampered negatives, old saved compiler/hash compatibility and authored whitespace preservation.
- [ ] Declared relevant units/types/lint/build/security and exact-head repository check evidence; no live writes.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet owns startup/claim. Existing accepted tasks must not be rewritten. Root owns merges and live verification.


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

None beyond approved immutable contracts.

### Unresolved Issues

None currently.

### Architectural Concerns

Return actual cross-owner gaps before widening scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
