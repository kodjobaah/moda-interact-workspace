---
id: ARCH-019-SHOPIFY-002
architecture_id: ARCH-019
title: Implement tenant-scoped recovery detail and transcript readers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: codex
claimed_at: 2026-09-20T12:08:03Z
attempt: 1
depends_on:
  - ARCH-019-DATABASE-001
enables:
  - ARCH-019-SHOPIFY-004
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Implement tenant-scoped recovery detail and transcript readers

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Read one owned recovery and bounded conversation context without exposing unrelated or cross-shop data.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

New app/services/recoveries detail/transcript/related-read modules and local DTOs; focused tests; accepted database dependency synchronization as needed.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [x] Apply the accepted DATABASE-001 plan finding: resolve the owned recovery/conversation once, then paginate messages using equality-bound conversationId and createdAt/id keys (or prove an equivalent bounded plan). Avoid the fixture's join-driven sort over 760/1,000 messages and repeated ownership lookup; retain tenant authorization and fixed query count.

- [x] Load recovery by authenticated shopId plus recoveryId, then constrain every transcript/related read through that owned recovery.
- [x] Provide first/next/previous/latest transcript windows of 50 messages with chronological display and (createdAt,id) tie-breaking.
- [x] Map all sender/status/content enum values honestly, including AUTOMATION, HUMAN, AUDIO and unavailable/rejected/failed transcription; expose only safe merchant-facing content and recorded delivery evidence.
- [x] Read related recoveries for the same shop/customer in pages of five, excluding the current recovery; do not group guest/null customer records.
- [x] Project recorded recovery timestamps and allowlisted milestone reasons, not arbitrary statusHistory metadata, provider IDs or internal diagnostics.

## Interfaces / Contracts

Parent architecture Detail contract. Reuse existing persisted schema and merchant-local date formatting; do not reconstruct absent runtime events.

## Dependencies

- ARCH-019-DATABASE-001

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-004
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Missing and foreign recovery identifiers produce indistinguishable unavailable results after authentication.
- [x] Forged cursors, conversation IDs or customer IDs cannot cross tenant boundaries; no unbounded nested relation include exists.
- [x] First/latest and adjacent message windows have stable ordering for tied timestamps; newest messages do not make previously visited windows duplicate older records.
- [x] Inbound message statuses are not misrepresented as outbound delivery receipts; unknown sender and missing metadata are not invented.
- [x] No provider media URLs, raw media IDs, credentials, internal prompts or arbitrary metadata leak into response DTOs.
- [x] A recovery without a conversation, a guest recovery and a long/multilingual transcript have valid bounded responses.

## Validation

- [ ] Record representative local EXPLAIN (ANALYZE, BUFFERS) for actual chronological/latest reader queries on a long transcript; demonstrate index cursor traversal without work proportional to the entire transcript. Follow the existing developer-owned execution policy for long rehearsals.

- [x] Run npm test -- tests/unit/recovery-detail-readers.test.ts (create this focused suite).
- [x] Run npm run typecheck and git diff --check.
- [x] Use local fixtures for two-shop access, tied timestamps, all sender/content states and >100-message windows; do not call Meta or Shopify.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Ready for Review — Attempt 1. Implementation and fast checks finished. Actual PostgreSQL query-plan validation remains developer-owned/pending; no acceptance is claimed.

### Files Changed

- app/services/recoveries/detail-cursor.server.ts
- app/services/recoveries/detail-message.ts
- app/services/recoveries/recovery-detail.server.ts
- tests/unit/recovery-detail-readers.test.ts
- tests/integration/recovery-detail-query-plans.test.ts
- tests/tsconfig.recovery-detail.json
- docs/ARCH-019-recovery-detail-readers.md

### Work Completed

- Independent tenant-constrained ownership lookup in detail, transcript and related-recovery readers; missing/foreign returns null.
- Direct equality-bound conversation query with tuple date/id keyset comparisons, first/next/previous/latest windows, 51-row limit and 50-row chronological result. At most three queries regardless of row count; indexed edge probes provide navigation.
- Related recoveries use the owned customer's ID, authenticated shop and current-recovery exclusion; five rows plus lookahead. Guests have no grouping.
- Strict bounded resource-bound cursors retain deleted-boundary coordinates; parameterized SQL and safe explicit projections.
- Prisma enum-based sender/direction/content/delivery mapping, unknown fallbacks, successful audio transcription only, persisted milestones, exact decimal strings. No provider/media IDs, arbitrary metadata, history reasons, raw errors, writes or provider calls.
- Added opt-in disposable PostgreSQL tests using the actual SQL builder and committed fixtures. Checks tenant isolation, real traversal and first/next/previous/latest plans without sort/join/full-transcript scanning.

### Validation Results

Passed:
- `npm test -- tests/unit/recovery-detail-readers.test.ts --no-cache`: 31 passed.
- `npm test -- tests/unit/recovery-detail-readers.test.ts tests/integration/recovery-detail-query-plans.test.ts --no-cache`: 31 passed; 5 PostgreSQL tests skipped because opt-in was not set. Skips are not runtime evidence.
- `npx tsc --noEmit -p tests/tsconfig.recovery-detail.json`: passed; changed TS source and tests checked under strict repository settings, legacy imported JS excluded.
- `git diff --cached --check`: passed.

Required full check executed: `npm run typecheck` exits 2 on seven pre-existing syntax diagnostics in tests/unit/merchant-route-access-policy.test.ts at lines 201, 219, 220. Confirmed unchanged in baseline HEAD c4fd514. This is a different condition from documented TYPECHECK-001's 48 type errors; no claim that the full check passed or that the old baseline exactly matches. That file was not modified. Focused changed-file typecheck passes.

Existing installed reference dependencies were linked read-only via ignored node_modules; tests used --no-cache. No dependency/lockfile or generated Prisma schema edits. Bootstrap succeeded from canonical workspace; invoking it from the sibling worktree cannot locate the workspace and was corrected by using canonical cwd.

Developer validation required from this implementation worktree at a2c23d19a930bfb9e2402dbfb6b4fad454776b1f:

```sh
MODA_RECOVERY_DETAIL_POSTGRES=1 npm test -- tests/integration/recovery-detail-query-plans.test.ts --no-cache
```

Supply tested commit, full output and exit code. Expected: all five tests pass, version and JSON EXPLAIN ANALYZE BUFFERS printed, message scans bounded to 51 rows with the accepted index and no sort/join. Suite uses a disposable PostgreSQL 15 container and does not consume live/default database credentials. This task has not been authorized to run the long rehearsal; the prior DATABASE-001 authorization applied to that specific run.

### Deviations

Full repository typecheck is blocked by an unchanged syntax defect, with focused type evidence supplied. Required live query plans remain pending under the task's developer-owned validation policy. No source-scope deviation.

### Assumptions

Future route loaders enforce authentication/lifecycle RECOVERY_HISTORY before passing resolved internal shopId. This task provides internal readers, not route wiring. UI maps stable enum codes to localized labels and renders text safely; no raw HTML/Markdown rendering is introduced here. Reads are live rather than cross-request snapshots.

### Unresolved Issues

Developer-owned PostgreSQL evidence pending. Existing repository test syntax defect blocks full typecheck. Both are explicitly reported for architect disposition.

### Architectural Concerns

DATABASE-001 join/sort concern addressed by direct conversation equality and tuple cursor SQL; actual-plan suite remains to be run. No new database index or shared contract required. No SHOPIFY-001 modules modified; reader implementations are separate for concurrent work.

### Git / VCS

Mirrored branch: task/ARCH-019-SHOPIFY-002.
Canonical primary workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-SHOPIFY-002 (reused).
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-SHOPIFY-002 (created).
Shared/default checkouts switched/mutated for implementation: no. Another task worktree reused: no.

Prepared launcher evidence: parent remote fast-forward not-needed; origin/main incorporated yes (a4b83a560a5dccc7fff05a75ba3bd776be52802d). Implementation remote fast-forward not-needed; origin/main already-current (c4fd514b54a34bac8ee4770dd6c9b0fe7a4059e5). Recursive submodule sync/update passed, status ready; database initialized at 9c6a4d8402a01840e2ea8dc18e89171f00564d29, which already includes the merged accepted ARCH-019 indexes. No gitlink update needed.

Attempt 1 claimed by codex at 2026-09-20T12:08:03Z; durable pushed parent claim 73044dae7af872eec90226db8acc2f9b6e5761c2. Existing Architect Review was Pending, with no rework requested. No startup re-claim performed.

Implementation commit: a2c23d19a930bfb9e2402dbfb6b4fad454776b1f; pushed origin/task/ARCH-019-SHOPIFY-002 and remote SHA verified. Parent report is published in the commit containing this report (SHA supplied in final submission). No parent gitlink staged, main merge/push, or downstream launch. Architect Review below preserved unchanged.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Awaiting implementation review.

### Follow-up

Reconcile task/index/frontier after accepted implementation; terminal system test remains manually invoked.
