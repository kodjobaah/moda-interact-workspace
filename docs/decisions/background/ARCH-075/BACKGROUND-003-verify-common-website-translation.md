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
status: review
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

- [x] Confirm the exact owning producer/consumer boundary and reproduce relevant regression.
- [x] Implement only the bounded parity correction or consumer test coverage.
- [x] Complete validation, mirrored report and stop.

## Interfaces / Contracts

Published Shared 5.13.9 canonical shop.websiteUrl semantic binding; existing Admin translation source snapshot and Background protected-marker transport. Preserve existing versions and hashes; no new contract is authorized.

## Dependencies

ARCH-075-BACKGROUND-002, ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Canonical common website binding survives actual translation snapshot/codec path with exact identity.
- [x] Negative marker/hash/unknown semantic boundaries remain strict; legacy supported inputs unchanged.
- [x] Canonical physical isolation, synchronization and exact validation evidence reported with no live writes.

## Validation

- [x] Meaningful focused positive/negative regression through actual owning boundary; Admin must demonstrate red before correction.
- [x] Focused actual codec/worker tests and scoped lint/typecheck; exact-head repository CI where configured. No unnecessary dependency, database, broad build or runtime changes for test-only coverage.
- [x] Diff/privacy hygiene and no live provider/database mutation.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet owns startup/claim. Existing accepted tasks must not be rewritten. Root owns merges and live verification.

## Completion Report

### Status

Ready for Review. Implementation and required validation complete. Source5831a9ad32b8185dadf6d79ecf5f3081b7d9cbb4 is committed/pushed on task/ARCH-075-BACKGROUND-003; [implementation PR214](https://github.com/kodjobaah/moda-interact-background/pull/214). Both exact-head CI runs passed; awaiting moda_architect review. No architect acceptance or live action claimed.

### Files Changed

- `tests/unit/services/template-translation/segment-codec.test.ts` only: three focused common recovery marker regressions using the actual worker repository snapshot guard and codec. No runtime, dependency, schema, generated client or provider changes.

### Work Completed

- Confirmed Background already accepts the canonical website semantic hint: its protected occurrence variable field is a bounded string, not Admin's semantic allowlist. Actual submit/ingest reuse repository.assertRunSnapshot and the same codec. No speculative runtime correction was made.
- Synthetic common header name/website and checkout conditional pass the real worker snapshot validator, encode each occurrence to a distinct sentinel, preserve semantic hints, accept legitimate translated/reordered text and restore exact original markers in source-key order. Snapshot and source hash remain unchanged.
- Missing website occurrence and moving it into the checkout segment are rejected even when other markers/segment keys or global website count remain intact. Existing malformed/hash/version/membership/duplicate/invented/leaked-token negatives and legacy inputs remain passing.
- The positive regression also checks stale definition hash rejection and proves that snapshot validation makes no database call. Default client construction is isolated in the unit test; parser/repository behavior is real.
- Admin's producer red/green correction belongs to ARCH-075-ADMIN-003. Root reported the actual common translation producer rejection and separately coordinates that source correction; this task verifies Background consumer compatibility and does not claim to fix Admin.

### Validation Results

- `vitest run tests/unit/services/template-translation/segment-codec.test.ts`:17/17 passed,407ms (includes the three new regressions).
- `vitest run tests/unit/services/template-translation`:20/20 passed across3files,527ms.
- Scoped `eslint tests/unit/services/template-translation/segment-codec.test.ts`:passed.
- Existing repository TypeScript `tsc --noEmit`:passed.
- `git diff --check`:passed; only the assigned test file changed. No live database, Redis, translation provider or credential access.
- Exact-head [push CI43372104763](https://github.com/kodjobaah/moda-interact-background/actions/runs/43372104763) passed1m45s and [PR CI43372111807](https://github.com/kodjobaah/moda-interact-background/actions/runs/43372111807) passed1m56s. Full final unit suite382/382files and4157/4157tests passed. No broad local build/database run was necessary or performed for this test-only scope.

Launcher isolation evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-003`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-003`; both branches task/ARCH-075-BACKGROUND-003. Prepared basecaf19da784afbc467f4cc23944527639773e24b1. Both remote task fast-forwards not needed; both origin/main already current; recursive submodule sync/update/init passed at Databasea9b6ab852a8245dfd14447808aac288a23b113d0. Prepared claimd7299416e0576eeea520ed941990e0d2f8e1ffbd already pushed; no duplicate preparation/claim. No shared/other-task checkout used for implementation; parent gitlink untouched.

### Deviations

None. Current unrestricted runtime permitted direct edits/publication in the exact canonical prepared worktree; root supplied lockfile installation. Node recovery used only the primary workspace bootstrap with its canonical MODA_WORKSPACE_ROOT; no manual version selection/install.

### Assumptions

The Background segment transport treats semantic variable names as bounded hints, not authorization to render variable values. Strict authoring semantic approval remains with the owning Admin/Shared boundaries; this test does not introduce a competing allowlist.

### Unresolved Issues

No implementation or required-validation issues remain; this mirrored task report submits the source for review. No runtime consumer defect or cross-repository contract gap was found.

### Architectural Concerns

No change to existing hashes, versions, protected occurrence identities, provider requests, retry policy or common frame authority. Admin003 and live translation/activation/system verification remain with their assigned owners/root. No live writes, sends, activation or main merge performed.

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
