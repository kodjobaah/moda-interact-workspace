---
id: ARCH-075-BACKGROUND-003
architecture_id: ARCH-075
title: Verify common website translation marker roundtrip
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: codex
claimed_at: 2026-11-13T05:22:21Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-002
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Verify common website translation marker roundtrip

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Verify common website translation marker roundtrip.

## Context

A saved common wrapper is valid under authoring/compiler but Admin translation segment validation rejects its canonical shop.websiteUrl protected variable before a run can start. Accepted source/activation tasks remain unchanged. This correction preserves translation transport integrity rather than adding another frame authority.

## Scope

Verify actual template-translation segment codec and worker snapshot handling accept protected shop.websiteUrl and preserve it exactly through translation/reconstruction. Current codec has no website-specific rejecting allowlist; prefer meaningful consumer regression tests only. Change runtime only for a reproduced matching defect, return any other gap first.

## Out of Scope

Live definition edits, translation/provider requests, activation, production replay/reset, source merges, new schemas/packages, broad translation refactors or permission workarounds.

## Requirements

Preserve canonical common source hashes, exact protected marker identity/count and semantic variables. Reject unknown variables at existing strict boundaries, missing/duplicate/unregistered markers, changed hashes and malformed snapshots. No normalization/dropping protected tokens or silent retry. Use synthetic fixtures representing the actual common header name/website and checkout conditional, not private production content. Do not duplicate a generic cross-service parser; report a genuine Shared gap rather than publishing opportunistically.

## Work Items

- [ ] Confirm the exact owning producer/consumer boundary and reproduce relevant regression.
- [ ] Implement only the bounded parity correction or consumer test coverage.
- [ ] Complete validation, mirrored report and stop.

## Interfaces / Contracts

Published Shared 5.13.9 canonical shop.websiteUrl semantic binding; existing Admin translation source snapshot and Background protected-marker transport. Preserve existing versions and hashes; no new contract is authorized.

## Dependencies

ARCH-075-BACKGROUND-002, ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Canonical common website binding survives actual translation snapshot/codec path with exact identity.
- [ ] Negative marker/hash/unknown semantic boundaries remain strict; legacy supported inputs unchanged.
- [ ] Canonical physical isolation, synchronization and exact validation evidence reported with no live writes.

## Validation

- [ ] Meaningful focused positive/negative regression through actual owning boundary; Admin must demonstrate red before correction.
- [ ] Focused actual codec/worker tests and scoped lint/typecheck; exact-head repository CI where configured. No unnecessary dependency, database, broad build or runtime changes for test-only coverage.
- [ ] Diff/privacy hygiene and no live provider/database mutation.

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

None beyond the existing canonical contracts.

### Unresolved Issues

None currently.

### Architectural Concerns

Return actual cross-repository gaps before widening scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source and report review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
