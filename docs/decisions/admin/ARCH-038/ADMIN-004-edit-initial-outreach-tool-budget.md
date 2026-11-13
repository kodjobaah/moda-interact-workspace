---
id: ARCH-038-ADMIN-004
architecture_id: ARCH-038
title: Edit the initial outreach tool-call policy
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-13T16:06:38Z
attempt: 1
depends_on:
  - ARCH-038-DATABASE-003
  - ARCH-038-ADMIN-003
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Edit the initial outreach tool-call policy

## Architecture

ARCH-038; docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md; coordinator moda_architect.

## Objective

Edit the initial outreach tool-call policy without losing current main behavior or the verified local backup.

## Context

Dependency integration verified: Database source PR77 main `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`, accepted parent PR1016 `5bb98c073fd6c167a89da56f7a899c9dd457af18`. Root verified TEST then PROD hosted rollout on2026-11-13 (16:03:51Z/16:04:20Z):80 finished migrations, zero unfinished/checksum mismatches,10 policy rows/five missing LIVE defaults16, other fields preserved, guard enabled O. The hosted pre-merge schema gate is satisfied; owning Admin validation/review remains mandatory.

Read-only comparison shows12 production files plus9 budget tests missing from current main. Background already resolves/enforces this field. Two other local template-impact edits are already incorporated in current main and must not be reapplied or used to overwrite newer tests.

## Scope

Recover the missing backed-up initialOutreachToolCalls policy controls across existing Platform/Price Plan/Merchant editors and new-plan wizard, with their directly related tests.

## Out of Scope

Template impact changes already in main, database/migration implementation, Background/Commerce source, Shared publication, live policy edits and main integration.

## Requirements

- Reuse existing platform/plan/shop JSON policy, schemaVersion1, authorization, trusted scope/environment, audit reason, CAS/editVersion and per-field inheritance; bounded initialOutreachToolCalls is a positive safe integer1–64, legacy read fallback16. Do not introduce another setting or Shared release.
- Platform writes must not silently reset a saved value when an old cached two-field form omits the new field. Require explicit valid value on the new full Platform form, or preserve the trusted current persisted value under the same CAS; never default a missing writer value to16. Legacy persisted two-field READ compatibility remains16. Add the missing-form regression.
- Third-field-only Platform changes must count as real edits and audit atomically. Plan/shop sparse overrides can inherit/clear independently, label effective source correctly and preserve untouched other budgets. New-plan wizard validates/serializes the optional override with reason in its existing atomic save.
- Preserve current main's template-impact/greeting/providerguard/frozenhash/stalestatus tests; local old whole-file test versions are not authoritative. Port only the missing budget delta from the verified backup.
- Do not raise runtime deadlines, change ordinary conversation turns or merchant billing, mutate live policies, or enable writers before accepted Database003 and root-verified hosted schema rollout. Existing Studio initial-outreach runtime policy semantics remain unchanged.

## Work Items

- [ ] Verify task-owned backup provenance and fresh-main overlap classification.
- [ ] Incorporate only the missing bounded behavior and necessary regression tests.
- [ ] Complete required validation, mirrored publication and truthful report; return review and stop.

## Interfaces / Contracts

Existing architecture-owned contracts and current published dependencies remain authoritative. No new Shared release is required. Original local files are evidence, not a replacement mainline. Root verified all15 Git bundles, staged/unstaged binary patches and nonignored untracked archives at external moda-local-reconciliation-backup-20261113T145749Z before any reconciliation writes; preserve that backup and primary originals. Never publish credential exports, operator scratch scripts, transcripts or generated artifacts as product source.

## Dependencies

ARCH-038-DATABASE-003, ARCH-038-ADMIN-003

## Enables

None

## Acceptance Criteria

- [ ] Scoped missing functionality is incorporated with newer main behavior preserved.
- [ ] Relevant trust/lifecycle/audit/immutability boundaries and explicit negative behavior remain enforced.
- [ ] Required checks and exact source/backup/worktree/synchronization evidence recorded; no live mutation or unrelated publication.

## Validation

- [ ] Focused boundary/malformed/missing/stale-form tests; platform third-field-only audit/CAS/no-op checks; sparse inheritance/clear/current-plan switching; wizard validation/atomic save; relevant existing policy/page/drawer/authorization tests, actual declared typecheck/lint/build and exact-head CI. No live writes.
- [ ] Diff/privacy hygiene and task-owned file whitelist; original backup/primary changes remain intact.

## Stop Condition

After scoped work and required validation, publish matching task branches, set review and return to moda_architect. Do not self-accept, merge main, deploy, execute hosted writes or start another task.

## Implementation Notes

Root verified the current Admin Blueprint build/start has no migration hook. Updating the nested Database gitlink or building Admin does NOT apply the SQL guard. Root must apply only the accepted tested new migration to TEST then PROD, verify complete ledger/checksum/no-other-pending evidence, and only then merge Admin004 to main (which can auto-deploy new writers). Historical6afd migration is already finished in both environments and must not be replayed. Task executor performs no hosted DDL; record this concrete pre-merge gate in the Completion Report.

You are not alone; do not revert or absorb others' edits. Use normal launcher preparation and dedicated matching parent/implementation task worktrees. No old task worktree reuse or shared checkout mutation. Root owns final integration and operational rollout. Return genuine new cross-repository/schema/contract gaps before widening scope.

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

Local backup is preserved; root owns live-state evidence and integration.

### Unresolved Issues

None beyond explicit task requirements.

### Architectural Concerns

Return any newly discovered gap to moda_architect.

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

Pending implementation review

### Follow-up

No architecture completion or production capability claim follows from local source incorporation alone.
