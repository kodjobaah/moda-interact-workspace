---
id: ARCH-019-DATABASE-001
architecture_id: ARCH-019
title: Index tenant-scoped recovery browsing and transcript pagination
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-019-SHOPIFY-001
  - ARCH-019-SHOPIFY-002
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Index tenant-scoped recovery browsing and transcript pagination

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Provide indexes aligned with the bounded recovery readers without changing durable business semantics.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

prisma/schema.prisma; one additive migration; focused schema/migration validation; generated schema documentation where required by the repository.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [x] Add CheckoutRecovery B-tree indexes on (shopId, detectedAt, id), (shopId, status, detectedAt, id), and (shopId, customerId, detectedAt, id); ascending definitions may serve matching reverse traversal.
- [x] Add ConversationMessage index on (conversationId, createdAt, id) for deterministic transcript traversal. Retain existing indexes unless equivalence and all consumers are proven; no unrelated index cleanup.
- [x] Inspect the exact accepted schema before editing; do not duplicate equivalent indexes if an intervening accepted migration already added them.
- [x] Document migration application and index-only rollback, lock/build behaviour, and the accepted database commit for downstream nested Gitlink consumption.

## Interfaces / Contracts

Architecture sections Query contract, Data architecture and Rollout. Existing CheckoutRecovery and ConversationMessage ownership remains unchanged.

## Dependencies

None.

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-001
- ARCH-019-SHOPIFY-002
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Migration is additive, preserves all rows/constraints and can be applied to an existing populated schema.
- [x] The migration and Prisma schema describe equivalent index definitions with deterministic query tie-breakers.
- [x] Representative two-tenant, status-filtered, related-customer and transcript queries have recorded EXPLAIN plans on a sufficiently populated local fixture; no fabricated throughput or forced index-selection claims.
- [x] No new entity, provider interaction, billing rule or queue payload is introduced.

## Validation

- [x] Run npm run prisma:validate and git diff --check.
- [x] Add and run a bounded schema-contract check covering the required columns/order and additive migration.
- [x] Developer-owned: apply the migration to an isolated populated PostgreSQL fixture and record exact command, exit code and EXPLAIN (ANALYZE, BUFFERS) evidence. Do not access shared databases without exact authorization.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Complete — Attempt 1. Architect accepted implementation `54c0ec2e092cd9db52d76e5bb46899efa4063965` on 2026-09-20 after code review and the explicitly authorized PostgreSQL 15.19 populated rehearsal (exit 0). Submission-era validation notes below are historical; the final Architect Review supersedes pending-evidence statements.

### Files Changed

- package.json
- prisma/schema.prisma
- docs/ARCH-019-recovery-read-indexes.md
- prisma/migrations/20260920120000_arch019_merchant_recovery_read_indexes/migration.sql
- scripts/fixtures/arch019-recovery-indexes-assert.sql
- scripts/fixtures/arch019-recovery-indexes-plans.sql
- scripts/fixtures/arch019-recovery-indexes-seed.sql
- scripts/rehearse-arch019-recovery-indexes.sh
- scripts/validate-arch019-recovery-indexes.mjs

### Work Completed

- Added the three tenant/date/status/customer recovery indexes and the transcript
  createdAt/id tie-breaker index. Retained every prior index and constraint.
- Added exactly one additive SQL migration, verified against Prisma's offline
  before/after datamodel diff; no data/field/business-state mutation.
- Added a bounded static contract test checking exact full SQL statement grammar,
  field order, schema mapping, names and preservation of prior index contracts.
- Added a developer-owned isolated PostgreSQL rehearsal with two tenants, 20,000
  recoveries and 201,980 synthetic messages, before/after query plans, row-content
  fingerprints, old-index preservation and index-ready/valid checks.
- Documented write-lock implications, deployment ordering, rollback and downstream
  consumption. ERD has no changes because only secondary indexes changed and the
  current generator does not display them.

### Validation Results

Agent-executed (all exit 0):

1. `npm run test:arch019-recovery-indexes` — passed all four additive contracts
   and retained-index checks.
2. `npm run prisma:validate` with a local placeholder DATABASE_URL — schema valid.
   Used the existing canonical database checkout's installed Prisma binary via
   PATH, read-only; no dependency or lockfile installation/change. No database
   connection or migration performed by this command.
3. `bash -n scripts/rehearse-arch019-recovery-indexes.sh` — syntax passed.
4. `git diff --check` and new-file whitespace checks — passed.
5. `prisma migrate diff --from-schema-datamodel /tmp/arch019-before.prisma
   --to-schema-datamodel prisma/schema.prisma --script` — generated exactly the
   same four CREATE INDEX statements as the authored migration. Baseline schema
   came from implementation HEAD before the task edits, not a live database.

Node recovery initially failed from the sibling worktree because the existing
bootstrap searches only its current directory's ancestors. Running the approved
bootstrap from canonical workspace, then returning to this implementation worktree,
resolved it. No bootstrap/environment policy code was changed.

Developer validation required, from the implementation worktree at `54c0ec2e092cd9db52d76e5bb46899efa4063965`:

```bash
bash scripts/rehearse-arch019-recovery-indexes.sh
```

Expected: exit 0; printed evidence directory containing full.log with commit/image/
PostgreSQL version, successful populated migration, unchanged row fingerprints and
prior indexes, four valid new indexes, and before/after EXPLAIN (ANALYZE, BUFFERS)
for both tenants, status/ongoing, related-customer and transcript cursor queries.
Planner choices are observed, never forced. Supply full.log and exit code for
architect review. This command was NOT run by the agent because task Validation
explicitly assigns it to the developer. No query performance has been measured.

### Deviations

No behavioural scope deviation. Migration was authored without `migrate dev`
against the developer database, since database-backed application/rehearsal is
developer-owned in this task; its SQL was instead verified against offline Prisma
diff. Populated local validation is still required before acceptance.

### Assumptions

Standard ascending B-tree equality prefixes support reverse date/id traversal.
Multi-status filters may choose a different plan. Docker/PostgreSQL rehearsal
results and actual deployment lock-time tolerance must be evaluated by the
developer/architect; no production capacity or lock-duration claim is made.

### Unresolved Issues

None blocking database acceptance. Transcript query-shape evidence is assigned to SHOPIFY-002; no further database index is indicated by this fixture.

### Architectural Concerns

Ordinary CREATE INDEX blocks table writes while building; the deployment window
must be acceptable. If it is not, request an explicit concurrent-build amendment.
No additional implementation task is assumed. No other repository was modified.

### Git / VCS

Task branch: `task/ARCH-019-DATABASE-001` in both repositories.

Physical worktree isolation (launcher packet):
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-DATABASE-001` (reused).
- Implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-DATABASE-001` (created).
- Shared/default checkouts switched/mutated for this task: no.
- Another task worktree reused: no.

Start-of-attempt synchronization (launcher packet):
- Parent remote task branch fast-forward: not-needed; origin/main: already-current.
- Implementation remote task branch fast-forward: not-needed; origin/main: already-current.
- Implementation baseline: `3518f504a3ba1d600d603905a93371f385952cab`.
- Recursive submodule sync/update/status: passed; no submodules present.

Claim:
- Executor: codex; Attempt 1; claimed_at: 2026-09-20T11:16:05Z.
- Parent claim commit: `59dca9a95acbd1c7f3b9bb67379aa0d9cc5dff5e`; pushed: yes.
- Latest pre-implementation Architect Review was Pending; no Changes Requested.

Implementation:
- Repository: moda-interact-database.
- Commit: `54c0ec2e092cd9db52d76e5bb46899efa4063965`; remote: origin/task/ARCH-019-DATABASE-001; pushed and remote SHA verified: yes.
- Candidate downstream database revision: `54c0ec2e092cd9db52d76e5bb46899efa4063965`, only after architect acceptance.

Parent report:
- File: `docs/decisions/database/ARCH-019/DATABASE-001-index-merchant-recovery-read-paths.md`.
- Report commit: the commit containing this Completion Report; exact SHA returned
  with submission evidence (cannot embed a commit's own hash in itself).
- Publication: commit/push on origin/task/ARCH-019-DATABASE-001 required for submission.
- Parent implementation Gitlink staged: no.
- Implementation/main merges, workspace/main merges and direct main pushes: none.

## Architect Review

### Review Status

Accepted — 2026-09-20, Attempt 1. Task Complete under completion_mode: automatic.

### Review Notes

Accepted implementation `54c0ec2e092cd9db52d76e5bb46899efa4063965`, unchanged since source review. Reviewed all nine implementation files, submission `fdf51c7a750b1f9ac51dc63ed0dbaabc68f6ea79`, ARCH-019 contracts and the successful populated rehearsal. All database acceptance criteria are satisfied. No blocking implementation defect or workflow non-conformance remains.

### Reviewed Files

Prisma schema and migration, package script, static validator, rehearsal shell, three SQL fixtures, rollout documentation, task report and architecture. Dedicated worktree and clean implementation HEAD verified; prepared launcher isolation/synchronization evidence retained in the Completion Report.

### Validation Reviewed

- Focused static contract test, shell syntax and committed-diff whitespace checks passed; submitted Prisma validation and exact offline schema-diff evidence reviewed.
- User-authorized command `python3 /tmp/rehearse-arch019-existing.py`, exit 0, tested this exact implementation using PostgreSQL 15.19 in local_postgres. Runner, log and analysis are preserved in [rehearsal evidence](evidence/2026-09-20-postgresql15/README.md).
- Prior migrations applied to a new temporary database; target migration applied transactionally to 20,000 recoveries and 201,980 messages. Row fingerprints and prior indexes preserved; all four new indexes valid, ready and nonunique. Temporary database cleanup succeeded.
- Reviewed default-planner before/after EXPLAIN (ANALYZE, BUFFERS) for two tenants, completed/ongoing status, related recoveries and chronological/latest transcripts. Recovery pages use the intended new indexes without the former sorts.
- Explicitly accepted test-environment variation: existing PostgreSQL 15.19 with temporary-database isolation instead of a new PostgreSQL 16 container. Committed SQL fixtures/migration unchanged. No PostgreSQL 16 or production performance claim.

### Architecture Conformance

Four additive indexes match required equality prefixes and deterministic ordering. Existing fields, constraints, tenant/lifecycle semantics and business contracts are unchanged. Write-lock implications, deployment-before-app order and index-preserving rollback documented. No deployment or merge performed. The synthetic rehearsal proves fixture compatibility, not production lock duration or capacity.

### Follow-up

SHOPIFY-001 and SHOPIFY-002 are Ready with accepted dependency metadata reconciled into their canonical parent worktrees. All other tasks remain Pending. Actual source consumption still requires developer integration or explicit accepted-commit consumption under the existing handoff contract; no launch or claim is implied.

SHOPIFY-002 must address the measured joined-transcript plan: top-N sorts consume 760/1,000 messages and one ownership lookup repeats 760 times. Resolve owned recovery/conversation once and paginate by an equality-bound conversation ID plus createdAt/id cursor, or demonstrate an equivalently bounded tenant-safe plan. Preserve fixed query count and server-side ownership checks; verify actual reader plans. This is application query work in its existing scope, not a missing database acceptance criterion.

The developer explicitly delegated commit/push of acceptance and shared-frontier updates on 2026-09-20. These records are published on the matching parent task branches. No main/gitlink or implementation history changed.
