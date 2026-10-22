---
id: ARCH-028-BACKGROUND-011
architecture_id: ARCH-028
title: Converge WhatsApp recipient reachability after correction and success
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: automatic
status: in_progress
priority: 65
executor: developer
claimed_at: 2026-10-22T17:12:23Z
attempt: 2
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-BACKGROUND-010
enables:
  - ARCH-028-BACKGROUND-006
created: 2026-10-08
updated: 2026-10-22
---
# Converge WhatsApp recipient reachability after correction and success

## Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-028-BACKGROUND-011`, taking execution authority from the prior agent-owned definition while preserving automatic completion. `assigned_agent: moda_background` remains the logical repository owner; task scope, dependencies, acceptance criteria and validation expectations are unchanged. The canonical launcher will prepare the implementation worktree and claim Attempt 1 after this amendment is published.

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Upsert finite recipient suppression only after successful terminal delivery-failure release/compensation and clear it only on authoritative positive Shop-scoped evidence, preserving idempotency and chronological convergence.

## Context

BACKGROUND-004 reports durable generic correction (or a bounded deferred committed-purchased result). BACKGROUND-010 owns reads/admission. DATABASE-001 owns reachability state. BACKGROUND-005 captures the actual recipient at each attempt. This task owns reachability writes and positive clearing, not billing or pre-admission policy.

Compensation and recipient reachability are separate predicates. Only exact `131026` is approved for suppression. Even if a future task broadens credit correction to other authoritative `FAILED` messages, those messages must produce an explicit `not-applicable` reachability result, not a fabricated suppression event.

## Scope

- For terminal `131026` evidence associated to an exact message/attempt/recovery/Shop, upsert `(shopId, attempt.recipient)` failure metadata only once release/compensation has durably succeeded.
- Use `PlatformBillingPolicy.whatsappRecipientSuppressionDays` (default seven) and the provider failure time; preserve bounded code and CAS/version/concurrent monotonicity, avoiding stale failures overriding newer positive evidence.
- On a `DELIVERED` or `READ` message, clear suppression only for the exact Shop and attempt recipient; retain historical evidence for audit.
- On an inbound WhatsApp event, clear suppression only after existing routing establishes one concrete Shop/customer/conversation owner; never clear two Shops from a contextless phone number.
- Return stable bounded writer/clearing outcomes for BACKGROUND-006 and BACKGROUND-008; idempotent retries after corrected status are safe.
- Explicitly skip non-`131026` FAILED evidence and return a bounded `not-applicable` outcome to the notification orchestration; do not make unrelated delivery-failure compensation depend on a suppression write.

## Out of Scope

- Admission gating/resume (BACKGROUND-010).
- Provider status classification and generic compensation accounting (BACKGROUND-002/004).
- Committed purchased compensation strategy (BACKGROUND-009).
- Synchronous HTTP rejection integration (BACKGROUND-006).
- Merchant notification (BACKGROUND-008).

## Requirements

- [x] The writer never suppresses on a deferred/failed COMMITTED purchased result before BACKGROUND-009 correction.
- [x] The Shop is resolved from durable message/attempt/recovery lineage, not phone matching.
- [x] Positive evidence cannot be reversed by an older failure replay; stronger positive evidence clears an earlier suppression.
- [x] Default suppression length is seven days; policy changes affect new failure evidence without retroactive inference.
- [x] Logs contain identifiers/outcomes, not raw provider bodies or full phone numbers.
- [x] Failure-code classification cannot mark a recipient unreachable for an unrelated Meta/provider error; successful correction and reachability success are reported as distinct facts.
- [x] New production source files target <=200 lines and never exceed 300; do not build a catch-all service.

## Work Items

- [x] Add focused idempotent reachability writer after accepted release/compensation result.
- [x] Read configured duration and calculate finite suppression from failureAt.
- [x] Clear suppression on exact delivered/read message and safely Shop-routed inbound evidence.
- [x] Test concurrency, version races, replay, late positive status and two-Shop same-phone isolation.
- [x] Test a non-`131026` FAILED event has no suppression side effect, including after a compensated event in any separately approved later policy.
- [x] Expose bounded outcomes to synchronous parity/notification owners.

## Interfaces / Contracts

Consumes DATABASE-001 reachability/policy, immutable attempt recipient from BACKGROUND-005 and bounded correction outcomes from BACKGROUND-004/009. Provides finite suppression and positive-clear operations for the existing provider-status and inbound-message workflows; no new cross-service payload is introduced.

## Dependencies

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-BACKGROUND-010`

## Enables

- `ARCH-028-BACKGROUND-006`

## Acceptance Criteria

- [x] Corrected terminal recipient failure creates finite Shop/recipient suppression exactly once.
- [x] Deferred/uncompensated purchased source creates no false suppression or notification-ready outcome.
- [x] Non-`131026` failure does not update reachability; a generic correction disposition never implicitly means recipient-undeliverable.
- [x] Duplicate or stale provider failure cannot override later positive evidence.
- [x] Delivered/read or unambiguous inbound clears only the owning Shop/recipient.
- [x] All touched modules respect focused responsibility/300-line production ceiling.

## Validation

Focused unit/PostgreSQL race/idempotency tests, provider-status replay, positive/inbound routing multi-Shop tests; repository-declared Background tests/build and `git diff --check`.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Keep separate modules for durable suppression writes and positive evidence clearing, with a thin integration point. Preserve the existing message/status transaction; do not call a provider or Redis inside the compensation transaction. Existing purchased correction is wired later by BACKGROUND-009.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-22T17:12:23Z. Attempt 1 review history is preserved below.

### Files Changed

Production (`moda-interact-background`):

- `src/services/recipient-reachability-failure.service.ts` (new)
- `src/services/recipient-reachability-positive.service.ts` (new)
- `src/services/recipient-reachability-store.ts` (new)
- `src/services/whatsapp-inbound-processing.service.ts` (new)
- `src/services/whatsapp-provider-status-lifecycle.ts` (new)
- `src/services/whatsapp-provider-status.service.ts`
- `src/workers/whatsapp.worker.ts`

Tests (`moda-interact-background`):

- `tests/integration/arch028-recipient-reachability.integration.test.ts` (new)
- `tests/integration/commerce/voice-workflow.test.ts`
- `tests/unit/services/recipient-reachability-failure.service.test.ts` (new)
- `tests/unit/services/recipient-reachability-positive.service.test.ts` (new)
- `tests/unit/services/recipient-reachability-store.test.ts` (new)
- `tests/unit/services/whatsapp-provider-status.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`

### Work Completed

- Added bounded `not-applicable` / `deferred` / `suppressed` / `unchanged` reachability outcomes; only an exact terminal `131026` with successfully corrected delivery usage reaches the suppression writer. Purchased compensation still pending is deferred.
- Uses durable outbound message, recovery, Shop and immutable attempt-recipient lineage; no phone-based Shop inference. Other provider failure codes cannot create reachability suppression.
- Added Shop-and-recipient-keyed PostgreSQL upsert logic with configured suppression days (seven-day default), event timestamps, version increments and monotonic handling of duplicated, stale and competing evidence.
- Records positive evidence from exact `DELIVERED`/`READ` provider status or a persisted inbound message with a single resolved Shop/conversation. Later positive evidence clears suppression; older failure replay cannot reverse it.
- Wired writes after the existing compensation/settlement and routed-inbound persistence boundaries. Extracted focused inbound and provider-status helpers rather than expanding existing worker files; all seven changed/new production modules are 300 lines or fewer.
- Added focused unit coverage and a PostgreSQL integration scenario for replay, races, timestamp order, and cross-Shop isolation. Added the related voice-workflow test mock for the new reachability collaborator.

### Validation Results

Local terminal evidence: `typescript(20261022-163824)`, recorded on 2026-10-22 (17:36–17:38 UK time).

- `git branch --show-current` — **PASS**, `task/ARCH-028-BACKGROUND-011`.
- `git apply --check --whitespace=error-all ~/Downloads/ARCH-028-BACKGROUND-011-attempt1-implementation.patch` — **PASS**; application and `git diff --check` returned no errors.
- `npm ci` — completed; warnings: **14 vulnerabilities (7 moderate, 7 high)** and five install scripts requiring approval. No dependency upgrade is included in this task.
- `npm run prisma:generate` — **PASS**, Prisma Client `6.19.3` generated.
- `npx vitest run tests/unit/services/recipient-reachability-store.test.ts tests/unit/services/recipient-reachability-failure.service.test.ts tests/unit/services/recipient-reachability-positive.service.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts tests/unit/workers/whatsapp.worker.test.ts` — **PASS**, 5 files / **70 tests**.
- `npm run build` (`npm run prisma:generate && tsc`) — **PASS**.
- `npm run test:integration -- tests/integration/arch028-recipient-reachability.integration.test.ts` — **PASS**, 1 PostgreSQL integration test, including duplicate, stale, competing, newer, and independent-Shop evidence.
- **Total focused tests: 71/71 passed.** A broader repository test suite was not shown in the supplied log.
- Source review of the Attempt 1 implementation patch: seven changed/new production modules, each <=300 lines; no DB schema or published Shared contract changes.

### Deviations

No intentional scope expansion. Extraction of the existing inbound processing and provider-status lifecycle helpers was needed to keep responsibilities focused and changed production modules below the 300-line ceiling. The voice-workflow test mock was updated for the extracted collaborator.

### Assumptions

- `ARCH-028-BACKGROUND-004` supplies durable correction outcomes. `ARCH-028-BACKGROUND-009` retains the separate committed-purchased credit compensation implementation.
- The reachability writer uses the existing DATABASE-001 tables/policy and BACKGROUND-005 immutable attempt recipient; no new inter-service payload or database migration is introduced.

### Unresolved Issues

- **Git/worktree provenance remains to be attached for acceptance.** The terminal confirms the implementation branch and a dedicated implementation execution path, `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-011`. It does **not** show an implementation commit SHA or successful push, the launcher-resolved parent-worktree/implementation-worktree preparation packet, start-of-attempt synchronization, or recursive submodule evidence. Verify and record these before architect acceptance; do not infer them from passing tests.
- The 14 `npm ci` audit findings and skipped install-script warnings are outside this task's scope; no impact on the executed tests/build was reported.

### Architectural Concerns

No new architecture changes proposed. `moda_architect` must independently review implementation boundaries, provenance, and tests before acceptance.

## Architect Review

### Review Status

Developer Self-Review — Changes Requested, Attempt 1.

### Review Notes

The reported focused validation passes, but the implementation is not durably published. The implementation worktree contains the reported source and test files as uncommitted modifications/untracked files, including an untracked `typescript` entry, while branch `task/ARCH-028-BACKGROUND-011` is at `f9659c1`, matching `origin/main` and containing no task implementation commit. The parent report's review commit does not substitute for an implementation commit.

### Reviewed Files

- Reported production and test files listed in the Completion Report were present in the dedicated implementation worktree, but remain uncommitted and therefore are not accepted as published implementation.

### Validation Reviewed

- Supplied focused evidence: 71/71 tests passed, build passed, and the report states all changed production files are within the 300-line ceiling.
- Publication check: failed; implementation branch has no task commit and is not ahead of `origin/main`.
- Worktree cleanliness: failed; task-owned changes are uncommitted and an untracked `typescript` entry is present.

### Architecture Conformance

The reported scope and validation appear aligned with the task, but architectural acceptance is blocked until the exact reviewed implementation is committed and pushed from the isolated implementation worktree.

### Follow-up

Return to developer execution for Attempt 1 publication reconciliation. Preserve the existing implementation worktree changes; commit only the task-owned implementation and test files after inspecting the untracked `typescript` entry, push `task/ARCH-028-BACKGROUND-011`, update the Completion Report with exact SHAs and synchronization evidence, then resubmit for review. Do not create Attempt 2 in this review.

### Developer Self-Review - Changes Requested — Attempt 1

- Inspect the untracked `typescript` entry and confirm whether it is task-owned generated/setup content; do not silently discard it or unrelated user work.
- Commit and push the reported BACKGROUND-011 implementation and tests on `task/ARCH-028-BACKGROUND-011` from the dedicated implementation worktree. The branch must contain the implementation commit and match its remote task ref.
- Reconcile the Completion Report with the actual implementation SHA, remote publication state, parent/implementation worktree paths, start-of-attempt synchronization evidence, and recursive submodule state.
- Rerun the focused tests/build/diff checks if publication changes the implementation, then resubmit the parent task as `review` with `executor: null` and `claimed_at: null`. Do not increment the attempt during this review.

## Dependency Frontier Reconciliation

On 2026-10-22, `ARCH-028-BACKGROUND-004` was explicitly completed by the developer at Attempt 1. `ARCH-028-BACKGROUND-010` also resolves `complete`; these are BG011's complete declared dependency set. BG011 is therefore promoted from `pending` to `ready` at Attempt 0. `executor` and `claimed_at` remain null. This is dependency readiness only: no implementation worktree was created and no attempt was claimed.
