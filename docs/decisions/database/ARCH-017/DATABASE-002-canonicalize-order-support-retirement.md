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
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T15:09:56Z
attempt: 1
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

- [x] Verify task-owned backup provenance and fresh-main overlap classification.
- [x] Incorporate only the missing bounded behavior and necessary regression tests.
- [x] Complete required validation, mirrored publication and truthful report; return review and stop.

## Interfaces / Contracts

Existing architecture-owned contracts and current published dependencies remain authoritative. No new Shared release is required. Original local files are evidence, not a replacement mainline. Root verified all15 Git bundles, staged/unstaged binary patches and nonignored untracked archives at external moda-local-reconciliation-backup-20261113T145749Z before any reconciliation writes; preserve that backup and primary originals. Never publish credential exports, operator scratch scripts, transcripts or generated artifacts as product source.

## Dependencies

ARCH-017-DATABASE-001

## Enables

None

## Acceptance Criteria

- [x] Scoped missing functionality is incorporated with newer main behavior preserved.
- [x] Relevant trust/lifecycle/audit/immutability boundaries and explicit negative behavior remain enforced.
- [x] Required checks and exact source/backup/worktree/synchronization evidence recorded; no live mutation or unrelated publication.

## Validation

- [x] Canonical migration SHA256/history validation, disposable PostgreSQL fresh+upgrade retirement/rollback checks, current seed/static validators and relevant declared schema/Prisma/lint/tests. No live DDL or seed.
- [x] Diff/privacy hygiene and task-owned file whitelist; original backup/primary changes remain intact.

## Stop Condition

After scoped work and required validation, publish matching task branches, set review and return to moda_architect. Do not self-accept, merge main, deploy, execute hosted writes or start another task.

## Implementation Notes

You are not alone; do not revert or absorb others' edits. Use normal launcher preparation and dedicated matching parent/implementation task worktrees. No old task worktree reuse or shared checkout mutation. Root owns final integration and operational rollout. Return genuine new cross-repository/schema/contract gaps before widening scope.

## Completion Report

### Status

Ready for Review — ARCH-017-DATABASE-002, attempt 1, executor codex.

### Files Changed

Implementation commit `0e50734` on mirrored `task/ARCH-017-DATABASE-002`:
- `prisma/migrations/20261106023000_remove_order_support/migration.sql`: exact already-applied historical SQL.
- `prisma/seed.mjs`: remove four current seed references to the retired feature.
- `scripts/validate-arch017-billing-materialisation-schema.mjs`: current-seed parity, historical checksum guard, whitespace-independent relation assertion.
- `scripts/test-arch017-order-support-retirement-postgres.mjs`: disposable complete-chain fresh, upgrade and refusal/rollback integration checks.
- `package.json`: three declared retirement PostgreSQL validation modes.

### Work Completed

- Used the verified external backup `moda-local-reconciliation-backup-20261113T145749Z` (database unstaged patch and untracked archive). Preserved the primary checkout, independent budget changes, operator scratch script/transcript and full backup. No unrelated source was imported.
- Root-authorized read-only test and production `_prisma_migrations` checks both confirmed the historical migration finished, not rolled back, with SHA-256 `6afd411b773669387f6289243537ea999df07a1f8c553163862a1f21de06cde2`. Credentials were read only into process memory/environment and never printed. No hosted writes, ledger repairs, migrate resolve, DDL or seed commands were executed.
- Canonicalized exactly those historical bytes. All 78 prior canonical migration SQL files remain byte-for-byte equal to source baseline `6f42b71112efe7ac63654d55f41cd74ca569b1ae`; total is now 79. SHA-256 over sorted `path + " " + file_sha256 + "\n"` entries for the 78 unchanged files: `2be5360262d82eb09082d595fe5db99ffaa07b0d44c685f4f82f3e40cf3edfaa`.
- Historical feature creation assertions remain; only current seed stops recreating Order Support. Prices, subscriptions, other features, releases/audits and existing immutable-configuration guards are preserved. No model/schema or ERD change is required.
- Prepared launcher evidence: canonical primary workspace `moda-interact-workspace`; dedicated parent `moda-interact-workspace-task-ARCH-017-DATABASE-002` and implementation `moda-interact-workspace.worktrees/ARCH-017-DATABASE-002`; matching task branch. Parent baseline `d799a5fa3a939aeb3e6fcfa0bb4f7707ef72ce27`, implementation baseline above; parent reused/implementation created, each own remote task synchronization not needed and main already current; recursive submodule initialization ready (none in implementation). Durable claim `1124c959a3f93d0fbed2dcfa2e9651301ca87923` was pushed. No shared/default checkout switching or main integration.

### Validation Results

Passed with workspace bootstrap Node 24.19.0 / npm 11.17.0:
- `npm ci`; `npm run prisma:validate`; `npm run prisma:generate` (Prisma client 6.19.3).
- `npm run test:arch017-billing-materialisation`; `npm run test:arch017-ai-conversations-required`.
- `npm run test:arch017-order-support-retirement:postgres:fresh`: **79 migrations, 18 assertions**; actual development seed executed twice, retired rows absent and unrelated fixtures preserved.
- `npm run test:arch017-order-support-retirement:postgres:upgrade`: **all 78 existing migrations first, then historical retirement; 20 assertions**; unused retired feature and three link types removed, unrelated plans/prices/subscription/config/history preserved, actual seed twice does not resurrect feature.
- `npm run test:arch017-order-support-retirement:postgres:rollback`: **78 migrations, 10 assertions**; historical audit FK `23503` and current immutable configuration guard `23514` both refuse deletion and roll back every preceding delete, preserving feature/link/config/release/audit and unrelated rows. Later ARCH075 tables remain present in all modes.
- All PostgreSQL writes used unique invocation-owned disposable pgvector/PostgreSQL 17 containers, loopback-only seed URLs and explicit database-name checks; containers removed on completion.
- `npm run lint` (zero warnings); `git diff --check`; task-owned file whitelist and exact migration history/checksum comparison.

### Deviations

The first positive-upgrade fixture incorrectly included an active feature configuration: the unchanged ARCH021 no-delete guard correctly refused it. Corrected the positive fixture to the task's unused feature and added explicit negative configuration coverage. The first negative assertion assumed generic `P0001`; actual canonical guard explicitly reports check-violation `23514`, so only the expectation was corrected. Both corrected checks pass; applied SQL and guard were never altered.

The existing static validator assumed a precise Prisma alignment spacing for the merchant-plan feature relation and failed against current main formatting. Replaced only that spacing assumption with a whitespace-independent relation regex, retaining the semantic relation assertion.

### Assumptions

Root owns accepted branch integration and operational rollout. This task canonicalizes already-applied history; it does not independently prove live application behavior or authorize new hosted changes.

### Unresolved Issues

None within scope. Initial-outreach budget migration and test remain preserved for the separately sequenced ARCH-038-DATABASE-003 task.

### Architectural Concerns

Historical retirement intentionally refuses referenced/currently configured features. Preserve that behavior; do not disable guards or purge history to force retirement.

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
