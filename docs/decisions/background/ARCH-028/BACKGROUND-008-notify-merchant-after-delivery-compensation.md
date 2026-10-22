---
id: ARCH-028-BACKGROUND-008
architecture_id: ARCH-028
title: Notify merchant after terminal delivery compensation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 80
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-028-BACKGROUND-006
enables:
  - ARCH-028-BACKGROUND-009
created: 2026-10-07
updated: 2026-10-22
---

# Notify merchant after terminal delivery compensation

## Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-028-BACKGROUND-008`, taking execution and completion authority from the agent-owned definition. The task scope, dependencies, acceptance criteria and validation expectations are unchanged; `assigned_agent: moda_background` remains the logical repository owner. The dependency `ARCH-028-BACKGROUND-006` is complete. The takeover preserved the ready, attempt-0 state; canonical preparation then claimed Attempt 1 as `developer` and pushed parent claim `0fa0e428d1047af2510851b9409f411866ace642`.

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Create one deduplicated merchant SYSTEM support message for a corrected, recovery-linked terminal delivery failure only after financial correction and every *applicable* reachability update have durably succeeded.

## Context

Merchant notification must never claim a credit was restored before accounting correction is true. Existing `MerchantSupportThread` / `MerchantSupportMessage.sourceKey` provides the notification mechanism and deduplication identity.

Under the currently agreed `131026` policy, reachability suppression is applicable and must succeed first. A separately approved general-`FAILED` credit correction must not pretend a different Meta failure means recipient-unreachable; a bounded reachability `not-applicable` result must allow accurate post-correction notification without writing suppression.

## Scope

- Define deterministic source key from the recovery/usage/message identity.
- Create/reuse merchant support thread and SYSTEM message after successful correction and the applicable `131026` suppression (or an explicit `not-applicable` reachability outcome for a separately approved broader correction).
- Use platform-owned bounded wording.
- Wording must reflect actual result: spendable restoration, held/historical correction, or RESERVED release; never say spendable credit was restored for `HISTORICAL_ONLY`/`HELD_FOR_REFUND`.
- Notification retries are idempotent.
- Translation/rendering failure must not roll back completed compensation/suppression.

## Out of Scope

- New notification table/subsystem.
- Provider monetary refunds.
- Purchased compensation itself (BACKGROUND-009 integrates with this capability after its correction succeeds).

## Requirements

- [x] Notification is last in terminal convergence ordering.
- [x] Deterministic sourceKey prevents duplicates on provider-status/job retry.
- [x] Merchant text does not expose provider payload/error details or phone number.
- [x] No notification is created for deferred/failed compensation.
- [x] Distinguish required `131026` suppression from an explicitly non-applicable reachability action; a missing/failed required suppression never enables an early notice.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Add deterministic source-key helper/policy message builder.
- [x] Add generic async/sync notification integration after correction/suppression success.
- [x] Add disposition-sensitive wording/tests.
- [x] Add retry/dedup/translation-failure tests.
- [x] Test correction-success + suppression-required, correction-success + reachability-not-applicable, and suppression-failed retry; verify no false reachability claims.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes existing Merchant Support persistence plus BACKGROUND compensation/reachability bounded outcomes.

## Dependencies

- `ARCH-028-BACKGROUND-006`

## Enables

- `ARCH-028-BACKGROUND-009`

## Acceptance Criteria

- [x] Merchant never receives a false "credit restored" claim.
- [x] Duplicate provider/job retries create at most one SYSTEM message.
- [x] Completed financial correction is never rolled back because notification failed.
- [x] Sync and async terminal paths use the same notification owner.
- [x] The notification cannot imply recipient unreachability where no `131026` suppression was applied.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused merchant-support integration/unit tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep merchant wording platform-owned and bounded. Provider code may drive internal classification but should not be surfaced as raw provider diagnostics to the merchant.

Keep merchant-notification composition/deduplication separate from compensation and reachability policy. The notification owner should consume an already-resolved terminal outcome rather than recalculate financial state.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Review — developer Attempt 1. Implementation commit `e692fde` is pushed to `origin/task/ARCH-028-BACKGROUND-008`. The task remains `review`, not `complete`; explicit developer completion is pending.

### Files Changed

Implementation repository `moda-interact-background` (11 task-owned files committed in `e692fde`):

- `src/services/recovery-delivery-merchant-notification.service.ts`
- `src/services/recovery-delivery-notification-content.ts`
- `src/services/recovery-delivery-support-message.service.ts`
- `src/services/synchronous-recipient-failure.service.ts`
- `src/services/whatsapp-provider-status.service.ts`
- `tests/integration/arch028-delivery-merchant-notification.integration.test.ts`
- `tests/unit/services/recovery-delivery-merchant-notification.service.test.ts`
- `tests/unit/services/recovery-delivery-notification-content.test.ts`
- `tests/unit/services/recovery-delivery-support-message.service.test.ts`
- `tests/unit/services/synchronous-recipient-failure.service.test.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`

Unrelated untracked `pnpm-lock.yaml`, `pnpm-workspace.yaml` and `typescript` artifacts remain untouched and excluded. No schema or submodule pointer changed.

### Work Completed

Implemented a deterministic SHA-256 source key from Shop, recovery and immutable message identity. The focused content builder emits bounded platform-owned wording for released, already-released, restored-spendable, historical-only and held-for-refund dispositions, and mentions temporary recipient pause only when suppression actually occurred.

Added a notification coordinator that checks failed outbound recovery-message lineage and Shop consistency, skips incomplete/deferred compensation, and requires the correct reachability outcome. Added a separate merchant-support writer that creates the SYSTEM message in its own transaction, confirms duplicates by source key, and propagates unrelated persistence errors for retry.

Both synchronous persisted rejection and asynchronous provider FAILED status now invoke the same notification owner after compensation and reachability. Unit/integration coverage exercises ordering, retry, deduplication, suppression-required/not-applicable, skipped/deferred outcomes, bounded copy and support persistence.

### Validation Results

- Focused Vitest suites (three new notification suites plus the two touched sync/provider-status suites): **PASS 60/60**.
- Disposable PostgreSQL integration via `npm exec -- node scripts/test-integration.mjs tests/integration/arch028-delivery-merchant-notification.integration.test.ts`: **PASS 1/1**.
- ESLint across all 11 task-owned changed paths: **PASS**.
- `npm run build`: **PASS** (Prisma Client generation and TypeScript compilation).
- Full `npm test`: **2,442 passed, 5 failed of 2,447**. Failures occur in four unchanged files: two inbound-abuse source-shape assertions, checkout-refresh platform-configuration fixture, recovery-agent-context ordering/summary expectation, and observability shared-version assertion. These are not presented as passing, and their baseline cause is not independently established in this review.
- `git diff --check`: **PASS**. The three new production modules are 76, 68 and 39 lines.
- Launcher evidence: dependency `ARCH-028-BACKGROUND-006` passed as complete; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-008` reused, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-008` created and synchronized from current `origin/main`; recursive `database` submodule initialized at `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`. Claim commit `0fa0e428d1047af2510851b9409f411866ace642`; implementation commit `e692fde` pushed to the task branch.

### Deviations

No scope deviation. Five full-suite failures in unchanged files remain documented as a validation limitation. Unrelated untracked toolchain artifacts were excluded from the implementation commit.

### Assumptions

Support notification persistence is independent from the already-committed compensation and reachability operations. Static platform-owned English copy is stored with the support system code/version for downstream support rendering; provider diagnostics and recipient phone data are not used in copy.

### Unresolved Issues

Full Background suite still reports five failures in unchanged files, with baseline causes not independently established. No task-focused unit, integration, lint or build failure remains. Explicit developer completion is pending this accepted review.

### Architectural Concerns

Notification, content policy and support persistence are separate focused modules. Existing compensation and reachability owners remain authoritative; no schema migration or cross-service queue contract was added.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.

## Developer Self-Review Passed/Accepted

### Review Decision

Attempt 1 passes developer self-review. The task is submitted as `status: review`, with `executor: null`, `claimed_at: null`, and `attempt: 1` unchanged. Because `completion_mode: developer`, explicit developer completion remains pending.

### Findings Reconciled

- Both synchronous and asynchronous terminal failure paths call the shared notification owner only after compensation and applicable reachability handling.
- Deterministic Shop/recovery/message source identity prevents duplicate SYSTEM notices across retries; only confirmed source-key collisions count as duplicates.
- Copy reflects correction disposition and does not imply spendable restoration or recipient suppression when those outcomes did not occur.
- Deferred/incomplete correction is skipped; notification persistence errors propagate for retry without sharing the completed correction transaction.
- New production modules are within the source-size constraint, and focused boundaries keep notification policy separate from support persistence, compensation and reachability.

### Validation Reviewed

- Focused unit tests: **60/60 passed**; disposable PostgreSQL integration: **1/1 passed**.
- Changed-path ESLint, `npm run build` and `git diff --check`: **passed**.
- Full Background suite: **2,442 passed, 5 failed** in unchanged files; root cause/baseline is not independently proven, and the suite is not represented as passing.
- Implementation commit `e692fde` is pushed to `origin/task/ARCH-028-BACKGROUND-008`. Parent claim commit `0fa0e428d1047af2510851b9409f411866ace642` is pushed; canonical worktree and recursive-submodule evidence is recorded in the Completion Report.

### Completion Authority

This accepted review does not itself complete the task. Explicit developer completion remains pending and requires `/moda_developer_update ARCH-028-BACKGROUND-008 complete`.
