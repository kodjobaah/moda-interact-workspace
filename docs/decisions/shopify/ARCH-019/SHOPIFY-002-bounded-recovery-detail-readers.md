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
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 3
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

- [x] Record representative local EXPLAIN (ANALYZE, BUFFERS) for actual chronological/latest reader queries on a long transcript; demonstrate index cursor traversal without work proportional to the entire transcript. Follow the existing developer-owned execution policy for long rehearsals.

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

Ready for Review — Attempt 3. Scoped correction and authorized PostgreSQL rehearsal passed. No architect acceptance is claimed. Full repository typecheck retains the unchanged baseline syntax blocker.

### Attempt 3 correction checklist

1. **Fixture loading — corrected.** `tests/helpers/recovery-detail-seed.mjs` removes only the exact leading psql `\set ON_ERROR_STOP on` directive, preserving every SQL byte after it. It rejects missing/unknown client directives and propagates pg errors. Three cheap tests use the real database-owned fixture and verify exact SQL preservation and failure propagation. The database fixture is unchanged.
2. **Required PostgreSQL evidence — supplied.** The user explicitly authorized the exact non-UTC command below. All five tests passed on PostgreSQL 15.19. Complete version, command output, tested revision and four JSON EXPLAIN ANALYZE BUFFERS plans are committed in `moda-interact/docs/evidence/ARCH-019-SHOPIFY-002-attempt3-rehearsal.md`. The first passing run omitted console logs; direct stdout output fixed evidence capture and the same authorized rehearsal passed again. No query assertion was weakened.
3. **Prior corrections and baseline — preserved.** Client-local UTC timestamp decoding and ISO Date binding remain unchanged; Europe/London, America/New_York and Asia/Kolkata regression cases pass. Full typecheck still fails with the same seven syntax diagnostics, distinct from TYPECHECK-001's older 48 type errors.

### Files Changed

Attempt 3 modifies the integration suite, focused unit suite and reader documentation; adds the fixture loader and committed rehearsal evidence. Earlier production reader/cursor/DTO modules, UTC helper and focused TypeScript configuration remain intact. No production reader change, database fixture edit, dependency/lockfile edit or unrelated route edit.

### Work Completed

The existing implementation provides tenant-constrained recovery ownership; first/next/previous/latest message windows with tuple cursors, a 51-row query limit and 50-row chronological result; related same-shop/customer recoveries in pages of five; safe enum-based message/content/delivery DTOs; and persisted milestones/decimal values. Guests are not grouped. Missing and foreign IDs are indistinguishable. No provider calls, writes, raw media IDs or arbitrary metadata are exposed. Attempt 3 makes the actual PostgreSQL harness executable and records the required evidence.

### Validation Results

- `npm test -- tests/unit/recovery-detail-readers.test.ts tests/integration/recovery-detail-query-plans.test.ts --no-cache`: 37 unit tests passed; 5 opt-in tests skipped in this fast-check invocation only.
- `./node_modules/.bin/tsc --noEmit -p tests/tsconfig.recovery-detail.json`: passed, including a repeat after the evidence-output change.
- `git diff --check`: passed.
- Authorized command below at **eb343405196047e18c0537da69dd87015b9f6b38**: exit **0**, all **5 passed**, PostgreSQL **15.19**, database submodule **9c6a4d8402a01840e2ea8dc18e89171f00564d29**. Final implementation commit adds evidence only after that tested revision.

```sh
TZ=Europe/London MODA_RECOVERY_DETAIL_POSTGRES=1 npm test -- tests/integration/recovery-detail-query-plans.test.ts --no-cache
```

All four actual message queries use `ConversationMessage_conversationId_createdAt_id_idx`, with exactly 51 actual rows in a single index scan and no Sort or Join. First/next scan forward; previous/latest backward. Shared buffer hits are 4/6/5/7 respectively; no read or temporary blocks. Tenant isolation, round-trip pagination, exact UTC timestamps and related recovery bounds pass. These fixture observations do not establish production latency guarantees.

`npm run typecheck` was rerun in Attempt 3 and exited 2: seven TS1109/TS1434/TS1134/TS1128 syntax diagnostics in `tests/unit/merchant-route-access-policy.test.ts` at lines 201, 219 and 220. That file remains identical to baseline c4fd514. The complete output is in the evidence artifact. Focused validation does not certify full repository typecheck.

Existing installed dependencies remain linked via ignored node_modules; tests used --no-cache. The rehearsal provisions and stops its own disposable PostgreSQL container, with no live/default database credentials.

### Deviations / Unresolved Issues

No pending PostgreSQL validation. The unchanged full-typecheck syntax defect remains for architect disposition; no unrelated repair performed. No source-scope deviation.

### Assumptions / Architectural Concerns

Future route loaders enforce authentication/lifecycle RECOVERY_HISTORY before supplying internal shopId, localize enum labels and render text safely. Reads are live rather than cross-request snapshots. The actual fixture plans now verify the direct conversation equality/tuple pagination response to DATABASE-001's join/sort finding. No new schema/shared contract is required. Downstream tasks are not launched or promoted.

### Git / VCS

Mirrored branch: `task/ARCH-019-SHOPIFY-002`.
Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-SHOPIFY-002` (reused).
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-SHOPIFY-002` (reused).
Shared/default checkouts switched/mutated for implementation: no. Another task worktree reused: no.

Prepared Attempt 3: both remote task fast-forwards not-needed; parent origin/main already-current; implementation origin/main incorporated. Parent baseline `1a6e78b3c5f56af09890d9c2d76640a9cfa8f3eb`; implementation synchronized baseline `30c69f842e71407055aa5a02f0ecd0ded21179f0`. Recursive submodule sync/update passed, status ready; database at `9c6a4d8402a01840e2ea8dc18e89171f00564d29` unchanged.

Claim: codex, 2026-09-20T12:56:40Z, Attempt 3; parent claim `434c5eec731fbc8a413a5b4bcbd8b67b990dbf78` pushed by launcher. Latest Changes Requested read completely. No repeated preparation or claim.

Implementation commits: fixture correction `39a30e4ed2d860b3da461a4f2f58d0c539b8e043`; tested evidence-output correction `eb343405196047e18c0537da69dd87015b9f6b38`; final evidence commit **1a60f1e17a27b9b927bb9a8b0bfff4c032a85e16**, pushed to origin/task/ARCH-019-SHOPIFY-002. Separate correction PR: https://github.com/kodjobaah/moda-interact/pull/40, because prior PR #38 was already merged by the developer.

Parent report: published in the commit containing this report (SHA provided in final submission), same remote task branch; existing report PR https://github.com/kodjobaah/moda-interact-workspace/pull/159. Only this task file staged. No parent gitlink staged, main merge/push or downstream promotion. Architect Review below is preserved unchanged.

## Architect Review

### Review Status

Accepted — 2026-09-20, Attempt 3. Complete under `completion_mode: automatic`.

### Review Notes

Accepted implementation `1a60f1e17a27b9b927bb9a8b0bfff4c032a85e16`, report `b0d2e628efaa3f57e94856624caa78f38da629ae`. Verified PR #40 and report PR #159 heads and open states. All previous correction items are satisfied; no blocking implementation defect or workflow non-conformance remains.

The app-owned seed helper removes only the exact leading psql ON_ERROR_STOP directive, preserves all remaining SQL, rejects unsupported directives and propagates database failures. Regression tests use the real unmodified database-owned fixture. UTC decoding/bindings and non-UTC regressions remain intact; no query-plan assertions were weakened. Production detail/cursor/message DTO modules are unchanged from the prior source review.

### Reviewed Files

Attempt 3 helper, unit/integration diffs, reader documentation and complete rehearsal evidence; prior reviewed production reader/DTO/cursor and UTC adapter verified unchanged. Reviewed task corrections, architecture, accepted DATABASE-001 dependency and current SHOPIFY-003 acceptance for downstream readiness.

### Validation Reviewed

- Architect rerun: `npm test -- tests/unit/recovery-detail-readers.test.ts --no-cache` — **37 passed**, exit 0. Focused TypeScript and committed-diff whitespace checks passed.
- Accepted the supplied explicitly authorized rehearsal evidence at `moda-interact/docs/evidence/ARCH-019-SHOPIFY-002-attempt3-rehearsal.md`: `TZ=Europe/London MODA_RECOVERY_DETAIL_POSTGRES=1 npm test -- tests/integration/recovery-detail-query-plans.test.ts --no-cache`, exit **0**, **5 passed**, PostgreSQL **15.19**, tested commit `eb343405196047e18c0537da69dd87015b9f6b38`. Final `1a60f1e` differs only by the added evidence document. No redundant infrastructure rerun.
- Parsed all four recorded JSON EXPLAIN plans. First/next use forward and previous/latest backward `ConversationMessage_conversationId_createdAt_id_idx` scans, each **51 Actual Rows, 1 Actual Loop, 0 index rechecks**, no Sort/Join. Shared hits are **4/6/5/7**, with zero read/temp blocks. Actual-reader behavior tests also cover ownership denial, exact UTC timestamps, adjacent/round-trip/latest windows and bounded related recoveries. Fixture plans establish the required bounded traversal, not production throughput or latency guarantees.
- Full typecheck evidence retains seven syntax diagnostics in the unchanged access-policy test on this branch. That branch-specific condition is not the newer baseline after SHOPIFY-003's accepted test repair; neither is a clean full typecheck. No unrelated repair required.
- Canonical worktrees, Attempt 3 claim/synchronization history, clean implementation and recursive database `9c6a4d8` agree with submission. Database fixture and production reader sources remain unchanged by Attempt 3.

### Architecture Conformance

Owned-recovery resolution precedes direct conversation-bound tuple pagination, replacing the earlier join/sort query shape. Read-only behavior, tenant scoping, safe DTO projection, honest message states and fixed query counts conform. Prior developer merge #38 is historical integration before acceptance; this acceptance covers the final corrected task, with correction PR #40 still requiring developer integration. No main merge/push, deployment or automatic revert performed.

### Follow-up

SHOPIFY-002 Complete at Attempt 3, executor/claim cleared; prior reviews retained below. SHOPIFY-004 becomes Ready at Attempt 0 because SHOPIFY-002 and SHOPIFY-003 are both accepted/Complete. Accepted dependency records and shared state are reconciled into its canonical parent worktree before publication. SHOPIFY-005/006 and SYSTEM-TEST-001 remain Pending. Readiness does not claim or launch execution; integrate accepted implementation dependencies or explicitly authorize accepted-commit consumption before execution. Publish review/frontier updates on the matching parent task branches under the developer's delegated authorization.

### Historical Architect Review — Attempt 2 and earlier


#### Review Status

Changes Requested — 2026-09-20, Attempt 2. Not accepted. Same task returned to Ready, claim cleared, attempt preserved at 2.

#### Review Notes

Reviewed implementation `85656328b8607236af017e36383a3b300b2e3a8a` and report `7835d3bba8b358d7a014c85e48e986f5c623b04b`. The prior timezone defect is corrected: client-local OID 1114 decoding and ISO Date bindings retain UTC fields; all three non-UTC subprocess regressions pass without weakening plan assertions. A separate fixture-loading defect prevents the required PostgreSQL rehearsal from reaching its assertions.

#### Required Corrections

1. **P2 — Load the psql fixture through a compatible execution path.** At `tests/integration/recovery-detail-query-plans.test.ts:26`, `client.query` receives the complete `database/scripts/fixtures/arch019-recovery-indexes-seed.sql`. Its first line is `\set ON_ERROR_STOP on`, a psql client directive, not server SQL. The pg driver forwards it unchanged, so PostgreSQL rejects setup with a syntax error before any of the five tests run. Correct the app-owned harness: execute through psql with failure propagation, or explicitly remove the known directive and send SQL only, retaining fail-fast driver errors. Do not edit the database-owned fixture merely to work around this. Add a cheap regression using the actual fixture to prove the supported loading path; preserve all seed SQL and existing plan assertions.
2. **Required evidence — Run the corrected five-test rehearsal under the non-UTC command and established execution policy.** Supply tested commit, exit code, PostgreSQL version, and full first/next/previous/latest EXPLAIN ANALYZE BUFFERS output. All five tests must pass with non-empty bounded index traversal and no sort/join. The authorization question raised during this review concerned the current command; no run was started after source inspection identified this setup defect. Pending or skipped validation cannot establish acceptance.
3. **Preserve the verified corrections and baseline limits.** Keep UTC read/write handling and non-UTC tests. Full typecheck remains blocked by the unchanged baseline syntax errors; focused passing checks do not certify the repository.

#### Reviewed Files

All eight task files: three production reader/DTO/cursor modules, focused tests, PostgreSQL suite, UTC helper, focused TypeScript configuration and reader documentation. Also inspected the exact database seed, schema relationships/indexes, parent architecture, task history and both PR states.

#### Validation Reviewed

Architect reran `npm test -- tests/unit/recovery-detail-readers.test.ts --no-cache`: 34 passed. Focused `tsc --noEmit -p tests/tsconfig.recovery-detail.json` and committed-diff whitespace check passed. The baseline syntax-error file remains identical to `c4fd514`; the same seven errors were independently established during the adjacent reader review. No Docker or PostgreSQL plan rehearsal launched in this review. The fixture incompatibility is established by the exact file contents and direct `client.query` call; no claim of executed integration failure is made.

#### Architecture Conformance

Production source remains read-only and follows owned-recovery lookup, direct conversation equality, tuple pagination, safe DTO projections and fixed query counts. The timezone correction is accepted as a correction, but the task is not accepted while actual-plan evidence is absent and its harness cannot load the fixture. SHOPIFY-004 and SYSTEM-TEST-001 remain gated.

#### Merge / Integration State

GitHub confirms implementation PR #38 was merged by the developer at `2026-09-20T12:41:19Z`, merge commit `49526b503b82d1abe39642f44f3b9f3caacba5ee`. The merged task files exactly match reviewed Attempt 2; report PR #159 remains open. Record this as integration before architect acceptance, not agent workflow misconduct or implicit acceptance. These modules have no route consumers in the merged change. This test-harness finding does not itself require reverting production reader code. Correct the same task and submit the later implementation correction for separate developer integration; an already-merged PR cannot integrate later commits. Do not rewrite main or revert automatically.

#### Follow-up

Reclaim `/moda-task ARCH-019-SHOPIFY-002` for Attempt 3 on the same canonical branch/worktrees, following normal main synchronization. Fix only the harness, supply focused and required PostgreSQL evidence, and return to review. SHOPIFY-001 remains Complete and SHOPIFY-003 remains In Progress at Attempt 1; preserve its active claim. No dependent promotion, implementation mutation, merge or deployment is performed by this review. Publish this parent review under the developer-delegated review-publication workflow.

#### Historical Architect Review — Attempt 1


##### Review Status

Changes Requested — 2026-09-20, Attempt 1. Not accepted. Same task returned to Ready; claim cleared, attempt preserved.

##### Review Notes

Reviewed implementation a2c23d19a930bfb9e2402dbfb6b4fad454776b1f and report 8a5aa031c640207cc939221db4818b5337bcd73c. Tenant-constrained ownership, explicit projections, parameterized tuple pagination and fixed query counts conform in source inspection. Required PostgreSQL evidence is absent, and its proposed harness has a reproducible timezone defect. No production data/code change is demanded by this finding; test source correction is required.

##### Required Corrections

1. **P2 — Match production timestamp semantics in the PostgreSQL harness.** tests/integration/recovery-detail-query-plans.test.ts uses pg default TIMESTAMP WITHOUT TIME ZONE decoding and Date parameter serialization. These use the host time zone, unlike the intended UTC Prisma behavior. Under TZ=Europe/London, timestamp `2026-09-01 00:02:05` decodes to `2026-08-31T23:02:05.000Z`, and Date `2026-09-01T00:02:05.000Z` serializes to `2026-09-01T01:02:05.000+01:00`. The builder casts to timestamp, yielding 01:02:05, beyond the fixture's final message at 00:04:10; the next-plan test can therefore return zero rows. Fix both input and output semantics, preferably exercising the production Prisma client, or use a demonstrably UTC-equivalent adapter. Add a cheap regression under a non-UTC host time zone that proves exact persisted timestamps and correct boundary parameters. Do not fix by weakening/removing the plan assertions or only testing under the default UTC environment.
2. **Required evidence — Execute the corrected opt-in PostgreSQL validation under the existing developer-owned policy.** Supply command, tested commit, exit code, version and complete EXPLAIN output for first/next/previous/latest. Confirm non-empty bounded index traversal without full-transcript sorts/joins and actual tenant/page behavior. Skipped tests are not evidence. If still awaiting developer execution at submission, leave validation pending and return to Review, not Complete.
3. **Report validation limits accurately.** Preserve the pre-existing full-typecheck syntax blocker and focused typecheck evidence. Do not equate the observed seven syntax errors with TYPECHECK-001's older 48 type errors. No unrelated repair is required by this review.

##### Reviewed Files

All seven changed implementation files, ARCH-019 detail/query contracts, task acceptance criteria and completion report. Implementation worktree clean at reviewed SHA; prepared physical isolation/synchronization evidence recorded.

##### Validation Reviewed

Submitted 31 passing focused tests, passing focused strict TypeScript check and whitespace checks inspected. Full typecheck blocked by unchanged syntax errors. PostgreSQL suite unrun (five skipped).

Reviewer reproduced driver behavior without database access using installed pg and pg/lib/utils.js with TZ=Europe/London: getTypeParser(1114)("2026-09-01 00:02:05").toISOString() -> "2026-08-31T23:02:05.000Z"; prepareValue(new Date("2026-09-01T00:02:05.000Z")) -> "2026-09-01T01:02:05.000+01:00". No long/live rehearsal launched.

##### Architecture Conformance

Read-only service scope and tenant boundaries appear aligned. Missing/foreign records return null; unknown message states and inbound delivery are handled without invented receipts. Production query-plan conformance remains unproven until corrected validation passes. No schema or cross-service change requested.

##### Follow-up

Reclaim the same task through `/moda-task ARCH-019-SHOPIFY-002` for Attempt 2, correct the test harness, rerun focused checks and publish both branches. SHOPIFY-004 and SYSTEM-TEST-001 remain gated; no dependent promotion. Implementation PR #38 and report PR #159 stay open for correction. Review metadata publication is delegated by the developer; no merge or main update.
