---
id: ARCH-038-DATABASE-003
architecture_id: ARCH-038
title: Persist the initial outreach tool-call policy
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-017-DATABASE-002
enables:
  - ARCH-038-ADMIN-004
created: 2026-11-13
updated: 2026-11-13
---

# Persist the initial outreach tool-call policy

## Architecture

ARCH-038; docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md; coordinator moda_architect.

## Objective

Persist the initial outreach tool-call policy without losing current main behavior or the verified local backup.

## Context

Prerequisite integration verified by root: ARCH017DATABASE002 accepted source merged as Database main `86db55833c804327f32a9208977cf54ae93cf4a1` (PR76); accepted parent PR1015 merged `adba9b8efbf85f6c47b26cffeb68670465c8469b`. Both dependency task files are Complete; this task is Ready without an execution claim.

Background main already consumes initialOutreachToolCalls with default16 and max64, but canonical Database still rejects that key and Admin has unpublished editing support. Backed-up local SQL adds the existing JSON budget field and LIVE Platform default; no new schema model or Shared contract is needed.

## Scope

The backed-up untracked 20261111090000_arch038_initial_outreach_tool_call_budget migration and directly related actual PostgreSQL policy harness/static validation only.

## Out of Scope

Order Support retirement/history, application UI/runtime edits, provider/credential changes, Shared release, live migrations/settings, counter resets and main integration.

## Requirements

- Preserve the existing budget schemaVersion1, positive safe integer validation, required Platform deadlineMs/outputTokens, sparse plan/shop overrides and1–64 tool-call bound. Existing legacy missing-field reads retain historical16; do not invent a different Preview policy owner.
- Verify root-owned read-only test/production migration ledger evidence before changing migration bytes. If already deployed, canonicalize the exact SHA256 3be33e9e482addfe38683a7407394faf5059e726ec56f77e625b06fcd987d539 with its original name and bytes; do not tidy duplicate function definitions in an applied migration. If not deployed, report that fact and still preserve authorized backed-up semantics; never fabricate ledger rows or run live DDL.
- Root-owned read-only ledger check confirmed the new budget migration absent from BOTH environments on2026-11-13. Its duplicated function definition may therefore be simplified before first publication, preserving behavior and recording the new checksum. Historical order_support migration bytes remain immutable under ARCH017DATABASE002.
- Wrap the complete new migration in explicit BEGIN/COMMIT so a backfill failure cannot leave its guard trigger disabled.
- Migration changes only the intended JSON validator/default state, preserving existing values, audit/ownership constraints and newer ARCH075 migrations. Temporary trigger disabling must be bounded within the migration transaction and restored before commit; genuine failure must roll back safely. Never leave an unaudited broad writer path open.
- Hosted upgrade applies this earlier-named pending migration AFTER newer ARCH075 migrations already recorded. Prove upgrade by applying ALL existing canonical migrations except the new budget target (including later timestamps), seed legacy rows, then apply the new target LAST. Fresh applies the full sorted chain.
- Correct the PG harness's obsolete assumption that this target must be the final migration. Prove the target is included in the complete ordered canonical chain and fresh/upgrade behavior with later migrations retained; don't discard newer sources. No seed retirement or legacy order_support migration in this task.
- Port selectively from the verified external backup onto current main. Preserve primary originals and all newer main functionality; no wholesale old-tree replacement. Source integration and actual hosted migration rollout are separate root-owned gates; Admin writers remain gated until schema rollout is verified.

## Work Items

- [ ] Verify task-owned backup provenance and fresh-main overlap classification.
- [ ] Incorporate only the missing bounded behavior and necessary regression tests.
- [ ] Complete required validation, mirrored publication and truthful report; return review and stop.

## Interfaces / Contracts

Existing architecture-owned contracts and current published dependencies remain authoritative. No new Shared release is required. Original local files are evidence, not a replacement mainline. Root verified all15 Git bundles, staged/unstaged binary patches and nonignored untracked archives at external moda-local-reconciliation-backup-20261113T145749Z before any reconciliation writes; preserve that backup and primary originals. Never publish credential exports, operator scratch scripts, transcripts or generated artifacts as product source.

## Dependencies

ARCH-038-DATABASE-001, ARCH-017-DATABASE-002

## Enables

ARCH-038-ADMIN-004

## Acceptance Criteria

- [ ] Scoped missing functionality is incorporated with newer main behavior preserved.
- [ ] Relevant trust/lifecycle/audit/immutability boundaries and explicit negative behavior remain enforced.
- [ ] Required checks and exact source/backup/worktree/synchronization evidence recorded; no live mutation or unrelated publication.

## Validation

- [ ] Actual disposable PostgreSQL fresh+upgrade complete migration chain,1/64 acceptance and0/65/fraction/unknown rejection, legacy/default/override preservation and relevant concurrency/CAS/audit checks; canonical checksum/static validation, Prisma validate/generate and relevant declared lint/tests. No live DDL.
- [ ] Diff/privacy hygiene and task-owned file whitelist; original backup/primary changes remain intact.

## Stop Condition

After scoped work and required validation, publish matching task branches, set review and return to moda_architect. Do not self-accept, merge main, deploy, execute hosted writes or start another task.

## Implementation Notes

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
