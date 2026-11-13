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
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T15:48:57Z
attempt: 1
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

- [x] Verify task-owned backup provenance and fresh-main overlap classification.
- [x] Incorporate only the missing bounded behavior and necessary regression tests.
- [x] Complete required validation, mirrored publication and truthful report; return review and stop.

## Interfaces / Contracts

Existing architecture-owned contracts and current published dependencies remain authoritative. No new Shared release is required. Original local files are evidence, not a replacement mainline. Root verified all15 Git bundles, staged/unstaged binary patches and nonignored untracked archives at external moda-local-reconciliation-backup-20261113T145749Z before any reconciliation writes; preserve that backup and primary originals. Never publish credential exports, operator scratch scripts, transcripts or generated artifacts as product source.

## Dependencies

ARCH-038-DATABASE-001, ARCH-017-DATABASE-002

## Enables

ARCH-038-ADMIN-004

## Acceptance Criteria

- [x] Scoped missing functionality is incorporated with newer main behavior preserved.
- [x] Relevant trust/lifecycle/audit/immutability boundaries and explicit negative behavior remain enforced.
- [x] Required checks and exact source/backup/worktree/synchronization evidence recorded; no live mutation or unrelated publication.

## Validation

- [x] Actual disposable PostgreSQL fresh+upgrade complete migration chain,1/64 acceptance and0/65/fraction/unknown rejection, legacy/default/override preservation and relevant concurrency/CAS/audit checks; canonical checksum/static validation, Prisma validate/generate and relevant declared lint/tests. No live DDL.
- [x] Diff/privacy hygiene and task-owned file whitelist; original backup/primary changes remain intact.

## Stop Condition

After scoped work and required validation, publish matching task branches, set review and return to moda_architect. Do not self-accept, merge main, deploy, execute hosted writes or start another task.

## Implementation Notes

You are not alone; do not revert or absorb others' edits. Use normal launcher preparation and dedicated matching parent/implementation task worktrees. No old task worktree reuse or shared checkout mutation. Root owns final integration and operational rollout. Return genuine new cross-repository/schema/contract gaps before widening scope.

## Completion Report

### Status

Ready for Review — ARCH-038-DATABASE-003, attempt 1, executor codex.

### Files Changed

Implementation commit `85c051a` on mirrored `task/ARCH-038-DATABASE-003`:
- `prisma/migrations/20261111090000_arch038_initial_outreach_tool_call_budget/migration.sql`.
- `scripts/test-arch038-model-policy-postgres.mjs`.
- `scripts/validate-arch038-model-policy-schema.mjs`.

### Work Completed

- Selectively incorporated the budget SQL and directly related PostgreSQL harness delta from the verified external `moda-local-reconciliation-backup-20261113T145749Z/moda-interact-database` archive/unstaged patch. Original archived SQL checksum was `3be33e9e482addfe38683a7407394faf5059e726ec56f77e625b06fcd987d539`. Primary originals, backup, scratch scripts/transcripts and other repositories were preserved.
- Root-authorized read-only ledger evidence initially confirmed this new migration absent from BOTH test and production. Root repeated the check during this attempt: each hosted ledger has 79 finished migrations, zero unfinished/pending/checksum mismatches against accepted `86db55833c804327f32a9208977cf54ae93cf4a1`; new budget migration remains absent. No hosted DDL, seed, ledger repair or other write was performed by this task.
- Because SQL is not deployed, removed its redundant identical second function definition and wrapped function replacement plus bounded trigger disable/backfill/enable in explicit BEGIN/COMMIT. New SHA-256: `f903e539b7db712b98202f72bd5fc3240c98d7e23ba7e2fed38e074736417b2f`.
- Preserved schemaVersion1, positive safe integers, required Platform deadline/token keys, legacy two-field compatibility, nonempty sparse overrides, unknown-key rejection and approved initialOutreachToolCalls range1–64. Only missing LIVE Platform keys backfill16 with version/timestamp increment; Preview, overrides, existing explicit values and attribution remain intact. No Shared release or Prisma model/ERD change.
- All 79 previously canonical migration.sql files are byte-for-byte unchanged against accepted source baseline above, including historical retirement SHA `6afd411b773669387f6289243537ea999df07a1f8c553163862a1f21de06cde2`. SHA-256 over sorted `path + " " + file_sha256 + "\n"` for those 79: `2db76d8613b20afb65f3b24794b8cc14d48d01251b0357fcd3974c2c1907daa1`. Complete chain now80 migrations.
- Replaced the obsolete target-last assumption with complete-chain membership plus newer-source retention. Upgrade applies all79 existing sources, including later ARCH075, before applying pending earlier-named target LAST.
- Prepared launcher evidence: exact primary `moda-interact-workspace`; parent `moda-interact-workspace-task-ARCH-038-DATABASE-003` reused; implementation `moda-interact-workspace.worktrees/ARCH-038-DATABASE-003` created. Both mirrored task branches synchronized their own remote task state (not-needed), current main already incorporated. Parent baseline `018d6fb28190c2734ee0769f3a489c642103f9e0`; implementation baseline above; recursive submodule sync/update ready (no nested entries). Durable attempt1 claim `8a1f046a92ffc2d3426a951bad45bd9ef6a2e291` pushed. No shared/default checkout or main changes.

### Validation Results

Passed using workspace bootstrap Node24.19.0 / npm11.17.0:
- `npm ci`; `node --check scripts/test-arch038-model-policy-postgres.mjs`.
- `npm run test:arch038-model-policy-schema`: historical schema/ownership/audit invariants and new SQL transaction, exactly one function definition, bound/default/missing-only selector, trigger restoration ordering/checksum.
- `npm run lint` (zero warnings); `npm run prisma:validate`; `npm run prisma:generate` (client6.19.3); `git diff --check` and task-owned whitelist/checksum comparison.
- `npm run test:arch038-model-policy:postgres:fresh`: PASS with full80 sorted migration chain; later ARCH075 tables retained, five LIVE defaults/independent Preview defaults, legacy and sparse validation, bounds1/64 accepted and0/65/negative/fraction/string/null/unsafe values rejected; unknown keys/schema versions/owner/FK/admin/uniqueness restrictions retained. Explicit value7 and every policy field/version survive repeated missing-only backfill unchanged.
- `npm run test:arch038-model-policy:postgres:upgrade`: PASS with all79 prior migrations first, valid populated Shop/Plan/Billing/Subscription plus sparse legacy policy fixtures, then target LAST. Custom LIVE deadline71000/token913 preserved and default16 added; Preview42000/512/version2 and all other row fields/ownership/overrides remain exact. All protected business rows survive.
- Upgrade injects a deliberate failing backfill trigger: transaction rolls back full validator function text and all policy rows, restores guard enabled state, and rejects a subsequent unauthorised/unversioned write. Fixture-only trigger is then removed; normal migration succeeds. No production guard is weakened.
- Both modes prove per-field inheritance, stale CAS refusal, atomic policy/audit rollback and two actual simultaneous PostgreSQL sessions competing for version2: exactly one wins, one observes zero updates, final version3 and exactly one additional audit row. Deleting override preserves both immutable audit rows.
- Every PostgreSQL write used a uniquely named invocation-owned pgvector/PostgreSQL17 container with network disabled; both containers cleaned up. No paid/provider calls or hosted writes.

### Deviations

Only authorized prepublication SQL normalization (duplicate function removal and explicit transaction) plus required harness correction for newer migration chronology. A static lint check initially found unnecessary quote escapes in newly added assertions; corrected before the successful lint/Prisma/PostgreSQL validation sequence. No functional PostgreSQL failures occurred.

### Assumptions

Existing Background consumer already supports range1–64/default16. Legacy Platform writers may still save two fields; missing-field consumer fallback remains16. Admin004 is separately gated and must not deploy before root verifies actual hosted schema rollout.

### Unresolved Issues

Root must integrate accepted source and perform/verify TEST then PROD migrate-deploy before enabling new Admin writers. This task performs no hosted migration and claims no deployed capability.

### Architectural Concerns

The explicit transaction retains a bounded migration-only trigger bypass under PostgreSQL table lock; failure restores data, validator and original enabled guard. No enduring broad unaudited writer path is introduced. No new contract or schema dependency discovered.

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
