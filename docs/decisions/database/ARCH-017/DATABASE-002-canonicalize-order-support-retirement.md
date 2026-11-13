---
id: ARCH-017-DATABASE-002
architecture_id: ARCH-017
title: Canonicalize the retired Order Support feature
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
  - ARCH-017-DATABASE-001
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Canonicalize the retired Order Support feature

## Architecture

ARCH-017; docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md; coordinator moda_architect.

## Objective

Canonicalize the retired Order Support feature without losing current main behavior or the verified local backup.

## Context

The untracked 20261106023000_remove_order_support migration SHA2566afd411b773669387f6289243537ea999df07a1f8c553163862a1f21de06cde2 matches the previously verified finished test/production ledger exception. Current canonical history lacks that file, while local seed removes four order_support rows. Root requests preservation and incorporation of genuine functionality, not ledger rewriting.

## Scope

Canonicalize the exact historical remove_order_support migration plus current seed/static-validation parity for the already retired unused feature.

## Out of Scope

Initial-outreach budget change, application feature behavior, deleting historical releases/audits, live DDL/seed/settings, provider/credential changes and main integration.

## Requirements

- Reconfirm root-owned read-only exact ledger/checksum evidence, then add the historical migration with the exact original name/bytes/checksum. Never rewrite the applied SQL, create a replacement migration, use migrate resolve or alter hosted ledger/state. Preserve all newer canonical migrations.
- The historical SQL retires only order_support links/catalogue state, not prices, subscriptions, other feature definitions or durable audit/release history. Its existing FK/reference refusal and transaction rollback must remain intact; no CASCADE or historical record purge.
- Fresh seed must stop recreating the retired feature and plan links. Intentionally update current ARCH017 static seed assertions that require order_support while retaining historical migration assertions and all mandatory/current feature invariants.
- Prove fresh complete-chain seed behavior and upgrade from pre-retirement state, including unrelated feature/plan/price/subscription preservation and historical-reference failure rollback. Do not run live destructive migration or seeds.
- Port only task-owned backed-up files; preserve the original primary checkout and independent initial-outreach budget migration/test changes for ARCH038DATABASE003. Coordinate shared implementation repository integration through root without reusing another task worktree.

## Work Items

- [ ] Verify task-owned backup provenance and fresh-main overlap classification.
- [ ] Incorporate only the missing bounded behavior and necessary regression tests.
- [ ] Complete required validation, mirrored publication and truthful report; return review and stop.

## Interfaces / Contracts

Existing architecture-owned contracts and current published dependencies remain authoritative. No new Shared release is required. Original local files are evidence, not a replacement mainline. Root verified all15 Git bundles, staged/unstaged binary patches and nonignored untracked archives at external moda-local-reconciliation-backup-20261113T145749Z before any reconciliation writes; preserve that backup and primary originals. Never publish credential exports, operator scratch scripts, transcripts or generated artifacts as product source.

## Dependencies

ARCH-017-DATABASE-001

## Enables

None

## Acceptance Criteria

- [ ] Scoped missing functionality is incorporated with newer main behavior preserved.
- [ ] Relevant trust/lifecycle/audit/immutability boundaries and explicit negative behavior remain enforced.
- [ ] Required checks and exact source/backup/worktree/synchronization evidence recorded; no live mutation or unrelated publication.

## Validation

- [ ] Canonical migration SHA256/history validation, disposable PostgreSQL fresh+upgrade retirement/rollback checks, current seed/static validators and relevant declared schema/Prisma/lint/tests. No live DDL or seed.
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
