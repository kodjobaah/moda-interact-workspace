---
id: ARCH-028-BACKGROUND-006
architecture_id: ARCH-028
title: Converge synchronous terminal WhatsApp rejections
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 72
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-028-BACKGROUND-011
enables:
  - ARCH-028-BACKGROUND-008
created: 2026-10-07
updated: 2026-10-22
---

# Converge synchronous terminal WhatsApp rejections

## Architecture

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-028-BACKGROUND-006`, taking execution and completion authority from the prior agent-owned definition. The task scope, dependencies, acceptance criteria and validation expectations are unchanged; `assigned_agent: moda_background` remains the logical repository owner. Attempt 1 was claimed and returned with changes requested. Attempt 2 was claimed through the canonical launcher on 2026-10-22T19:40:40Z.

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Preserve bounded Meta provider codes from synchronous HTTP rejection and make exact code `131026` follow the same compensation, hard-limit and Shop-scoped suppression policy as asynchronous terminal failure.

## Context

`WhatsAppService` currently discards the provider error body/code and throws only `provider-rejected`. Recovery billing failure handling cannot therefore distinguish terminal recipient rejection from other synchronous provider failures.

The newer Background send fence persists final dispatch admission before HTTP, and ARCH-040 introduces a distinct recovery-linked merchant template path. A synchronous definitive `131026` response, a pre-permit/configuration denial and an uncertain response are not interchangeable. BACKGROUND-013 is the separate owner for *admitted but uncertain* credit settlement; this task must not implement that policy.

## Scope

- Extend `WhatsAppServiceError` with optional bounded `providerCode` extracted from Meta error response without retaining raw detail/body.
- For synchronous exact `131026`, persist message `FAILED` + failure evidence and use the same local terminal-recipient classifier.
- Invoke the same idempotent compensation/release/hard-limit owner used by asynchronous processing.
- After successful correction invoke the same reachability suppression owner.
- Preserve existing ambiguous/non-terminal provider-failure handling for other codes/network uncertainty.
- Keep pre-provider denials and a definitive response rejection distinct from an already-admitted unknown outcome; never auto-resend an irreversible provider admission. Inspect both automated recovery-template and merchant recovery-follow-up integration points, without adding recovery-credit accounting to ordinary HUMAN_TEXT. If a human path depends on unfinished ARCH-040 fencing, record the interface gap for BACKGROUND-013 rather than expanding this task.
- Keep duplicate/idempotent admission semantics.

## Out of Scope

- New provider-code classification beyond `131026`.
- Merchant notification (BACKGROUND-008).
- Purchased COMMITTED compensation (BACKGROUND-009).
- Crash-repair or presumed-success accounting at the durable final dispatch fence (BACKGROUND-013).

## Requirements

- [x] Sync 131026 and async FAILED/131026 converge to the same policy outcome.
- [x] Raw Meta error text/body is not persisted/logged.
- [x] Other synchronous rejections are not silently classified as recipient-undeliverable.
- [x] Pre-dispatch validation/configuration/moderation failures are non-billable; synchronous definitive rejection is distinguished from admitted/unknown provider outcomes without a second Meta send.
- [x] RESERVED recovery source is released idempotently.
- [x] Outbound hard-limit UsageEvent is removed consistently with async terminal failure.
- [x] Reachability suppression occurs only after correction succeeds.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Add bounded providerCode extraction/error type tests for text/template sends.
- [x] Wire synchronous terminal classifier to message evidence.
- [x] Reuse compensation/hard-limit/reachability owners.
- [x] Add duplicate, non-terminal and ambiguous failure tests.
- [x] Add pre-permit versus post-permit failure and recovery HUMAN follow-up boundary regression checks (without assuming a pending ARCH-040 task is already complete).
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Repository-local `WhatsAppServiceError.providerCode?: string` only; no new cross-service contract.

## Dependencies

- `ARCH-028-BACKGROUND-011`

## Enables

- `ARCH-028-BACKGROUND-008`

## Acceptance Criteria

- [x] Sync `131026` results match async terminal policy except there is no later provider message-status requirement.
- [x] Non-131026/network/configuration failures preserve existing safe semantics (exact persisted 131026 duplicate checks and existing pre-provider/uncertain-path tests).
- [x] No double release/hard-limit correction/suppression occurs on retries.
- [x] `providerCode` classification is bounded and exact; ordinary HUMAN_TEXT cannot acquire a recovery-credit adjustment through shared provider error handling.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

- [x] Earlier focused matrix: 69/69 passed across nine suites.
- [x] Correction-focused suites: 39/39 passed (follow-up processor 28/28; admission reservation 11/11), including exact/missing/non-131026 duplicate cases and corrected admission fixture.
- [x] Attempt 2 correction suites: 39/39 passed (follow-up processor 28/28; admission reservation 11/11), including exact/missing/non-131026 duplicate cases and the corrected admission fixture.
- [x] `pnpm exec tsc6 --noEmit`, changed-path ESLint, and `git diff --check origin/main...HEAD` passed on the current implementation branch.
- [ ] Current full Background suite: 2,420 passed and 5 failed (2,425 total). The failures are in four unchanged files: inbound abuse-admission source-shape tests (2), checkout refresh platform-configuration fixture, recovery-agent-context summary expectation, and shared-runtime version assertion. No BG006-specific failure was reported; suite is not represented as passing.
- [ ] Current declared `pnpm run build` generated Prisma Client but failed at `tsc: command not found`. Direct `tsc6 --noEmit` passed; declared build remains unresolved.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep provider error parsing bounded to the numeric/string code needed by policy. Do not make WhatsAppService own billing/recovery policy.

Keep the synchronous provider-rejection adapter thin and reuse the asynchronous terminal-failure policy owners. Do not duplicate compensation, hard-limit or reachability policy in the WhatsApp provider client/service.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Complete — explicit developer completion recorded for accepted Attempt 2. The claim was committed and pushed at `65ee1f18e33cbb4b71ce04a396f3f34b3983fcdf`; implementation is published at `0bb1a62cd9d787114764946fbd5209c33025a2d5`. Full-suite and declared-build limitations remain documented below.

### Files Changed

Implementation files in `moda-interact-background/` (23 changed paths between `main` and pushed `task/ARCH-028-BACKGROUND-006`, verified against GitHub):

- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`
- `src/services/outbound-whatsapp-admission.service.ts`
- `src/services/outbound-whatsapp-admission/failed-outreach-admission.ts`
- `src/services/outbound-whatsapp-admission/outbound-admission-reservation.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-provider-failure.service.ts`
- `src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `src/services/recovery-conversation/human-send-reconciliation.service.ts`
- `src/services/synchronous-recipient-failure-evidence.service.ts`
- `src/services/synchronous-recipient-failure.service.ts`
- `src/services/whatsapp-provider-rejection.ts`
- `src/services/whatsapp.service.ts`
- `tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/failed-outreach-admission.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-admission-reservation.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-admission.test-support.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`
- `tests/unit/services/outbound-whatsapp-admission/outbound-provider-failure.service.test.ts`
- `tests/unit/services/recovery-conversation/human-synchronous-rejection.test.ts`
- `tests/unit/services/synchronous-recipient-failure-evidence.service.test.ts`
- `tests/unit/services/synchronous-recipient-failure.service.test.ts`
- `tests/unit/services/whatsapp.service.test.ts`

### Work Completed

- Kept bounded Meta provider-code extraction in `WhatsAppServiceError`, including text/template synchronous rejections; no raw provider response body or text is retained for policy/logging.
- Introduced a small provider-rejection classifier and provider-failure adapter; exact `131026` is separated from unrelated definitive errors, pre-provider denials and uncertain outcomes.
- Extracted durable synchronous rejection evidence and existing recovery-attempt/message linkage so the correction resolver still has its immutable source before any hard-limit UsageEvent removal.
- Reused the existing correction/release/hard-limit and Shop-scoped recipient reachability owners; suppression only follows accepted correction.
- Integrated the same rejection convergence into automated recovery outreach and recovery-linked merchant follow-up. Ordinary `HUMAN_TEXT` remains outside recovery-credit correction/reachability policy.
- Preserved a durable failed-outreach/admission replay fence to prevent a second irreversible provider send after compensated failure.
- Added focused tests for provider-code bounds, correction evidence ordering, lost/duplicate attempt handling, failure classification, idempotent replay, merchant follow-up, and `HUMAN_TEXT` isolation. Resolved TS18047 for a nullable recovery attempt and added its regression test.
- Corrected historical FAILED duplicate classification: return `recipient-undeliverable` only when the persisted provider code is exactly `131026`, including both initial-message and existing-follow-up lookup paths; other and missing codes retain generic failure semantics.
- Extended the outbound admission transaction test fixture with `recoveryOutreachAttempt.findUnique` and added historical lookup/duplicate replay regressions.
- Aligned the failed-outreach helper's explicit TypeScript return type with its selected `providerFailureCode` field; final `tsc6 --noEmit` passed.
- Reviewed modularity: `whatsapp-provider-rejection.ts` (20 lines), `synchronous-recipient-failure.service.ts` (32), `synchronous-recipient-failure-evidence.service.ts` (93), `outbound-provider-failure.service.ts` (45), and `failed-outreach-admission.ts` (approximately 31 lines). `outbound-message-delivery.service.ts` is 286 lines (down from 345). Existing larger dispatcher (419 lines) receives only thin integration; no new catch-all module was introduced.

### Validation Results

- Focused correction tests rerun for Attempt 2: **39/39 passed** across the two suites covering the prior review findings.
- `pnpm exec tsc6 --noEmit`: **passed**.
- ESLint over all 23 changed implementation/test paths: **passed**.
- `git diff --check origin/main...HEAD`: **passed**; implementation worktree is clean and tracks the remote task branch at `0bb1a62cd9d787114764946fbd5209c33025a2d5`.
- Current full `pnpm test`: **2,420/2,425 passed**. The five failures are in four unchanged files: two B011 inbound abuse-admission source-shape checks, checkout-refresh's unavailable platform-configuration fixture, recovery-agent-context's summary expectation, and an observability assertion expecting Shared `2.4.1` while the package is `2.5.0`. No changed file is among those failures; causes/baseline are not independently established, so full-suite validation remains incomplete.
- Current `pnpm run build`: Prisma generation passed, then script failed with `sh: tsc: command not found`. The direct `tsc6` check passed; the declared build is not reported as passing.
- Canonical Attempt 2 launcher packet: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-006`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-006`; both reused on `task/ARCH-028-BACKGROUND-006`. Dependency gate passed (`ARCH-028-BACKGROUND-011` complete); parent `origin/main` was merged (`origin_main_incorporated: yes`), implementation was already current, recursive database submodule sync/init/status passed at `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`, and claim commit `65ee1f18` was pushed.

### Deviations

- Attempt 1's Changes Requested decision and correction history are retained below. Attempt 2 is formally claimed and submitted for review; its launcher evidence is recorded above.
- Five full-suite failures in unchanged files and the declared-build `tsc` alias problem remain validation exceptions; they are not represented as passes or as proven baseline failures.

### Assumptions

- Repository ownership remains `moda_background`; developer execution/completion modes are unchanged.
- The currently pushed implementation revision is commit `0bb1a62cd9d787114764946fbd5209c33025a2d5` (superseding earlier snapshot `2aa1153ed97413c88e495808ba2786df46ef3a32`) on `origin/task/ARCH-028-BACKGROUND-006`. This was directly verified using the GitHub commit/branch comparison.
- The Attempt 2 preparation packet is the source of truth for synchronization and physical worktree evidence; both worktrees are currently clean and remote-synchronized.

### Unresolved Issues

- The two previous BG006 correction items are implemented and covered by passing focused tests; no known task-local test failure remains from those findings.
- The full suite still has five failures outside the changed paths; their baseline/cross-task cause is not confirmed.
- The declared build remains blocked by the missing `tsc` executable although direct `tsc6` passes.
- Completion mode is developer; passing this review leaves explicit developer completion pending and does not complete/unblock BG008.

### Architectural Concerns

- No new cross-repository runtime contract or database schema change introduced by this task. The correction deliberately reuses existing compensation and reachability owners. The pre-existing 419-line human dispatcher remains a maintainability hotspot but has only thin task integration; the modularity review found no blocking new module-boundary issue.

## Developer Self-Review - Changes Requested

### Review Status

Changes Requested — Attempt 1 returned to `ready`; no new attempt was claimed during review reconciliation.

### Findings

- [ ] In `RecoveryOutreachFollowUpProcessorService`, a durable FAILED duplicate is classified as `recipient-undeliverable` without verifying exact provider code `131026`. Require the persisted exact code; other or missing codes must retain generic duplicate/failure semantics. Add tests for exact and non-exact codes.
- [ ] The outbound-admission test harness does not provide `recoveryOutreachAttempt.findUnique`, which the new failed-outreach lookup requires. Extend the transaction fixture and rerun the regression test.

### Validation

- Focused matrix: 69/69 passed across nine suites; `tsc6`, changed-path ESLint, Prisma generation, and diff checks passed.
- Full suite: 2,391/2,398 passed. Both task-related failures reproduced in isolation (29/31); five other failures are unrelated. The declared build script still fails because `tsc` is unavailable, while direct `tsc6` passes.
- Implementation commit `2aa1153ed97413c88e495808ba2786df46ef3a32` is pushed to `origin/task/ARCH-028-BACKGROUND-006`.

### Next Action

Correct both findings in a newly claimed developer attempt, then rerun the focused and full validation. Preserve `attempt: 1` in this review update; the next launcher claim owns the attempt increment.

### Subsequent Correction Evidence (not a new review decision)

- Both Changes Requested implementation findings were corrected in pushed Background commit `0bb1a62cd9d787114764946fbd5209c33025a2d5`.
- Exact durable Meta-code gating now uses persisted `providerFailureCode` and requires `131026`; tests cover non-131026 and missing-code variants.
- Admission transaction fixtures now expose `recoveryOutreachAttempt.findUnique`, and the historical failed-outreach lookup is covered.
- Corrected focused suites passed 39/39, the latest full suite had 2,420 passes and five other failures, and final `tsc6 --noEmit` plus `git diff --check` passed.
- At the time this note was appended, it preserved the historical Attempt 1 Changes Requested decision and was not itself an Accepted review, Attempt 2 claim, or completion decision. Attempt 2 was later claimed in parent commit `65ee1f18`.

## Developer Self-Review Passed/Accepted

### Review Decision

Attempt 2 passes developer self-review. The task is submitted as `status: review`, with `executor: null`, `claimed_at: null`, and `attempt: 2` unchanged. Because `completion_mode: developer`, explicit developer completion remains pending.

### Findings Reconciled

- The prior duplicate-classification defect is fixed: only a persisted exact provider code `131026` yields `recipient-undeliverable`; absent and other codes preserve generic duplicate/failure behavior.
- The outbound-admission transaction fixture includes `recoveryOutreachAttempt.findUnique`; the historical lookup path is covered.
- Both findings' focused suites pass on the reviewed implementation snapshot. No changed-path failure remains.

### Validation Reviewed

- Focused correction suites: **39/39 passed**.
- `pnpm exec tsc6 --noEmit`: **passed**.
- ESLint across the 23 changed implementation/test paths: **passed**.
- `git diff --check origin/main...HEAD`: **passed**.
- Full `pnpm test`: **2,420/2,425 passed**, with five failures in unchanged files. Their causes/baseline are not independently established; the suite is not called passing.
- Declared `pnpm run build`: Prisma generation succeeded, then failed because `tsc` is unavailable. Direct `tsc6` passed; the declared build is not called passing.
- Implementation commit `0bb1a62cd9d787114764946fbd5209c33025a2d5` is pushed. The Attempt 2 claim is pushed as parent commit `65ee1f18e33cbb4b71ce04a396f3f34b3983fcdf`; canonical launcher evidence and worktree synchronization are recorded above.

### Completion Authority

Developer completion is not inferred from this passing review. The developer may complete explicitly with `/moda_developer_update ARCH-028-BACKGROUND-006 complete`.

## Developer Completion Decision

The developer explicitly invoked `/moda_developer_update ARCH-028-BACKGROUND-006 complete` after the durable Attempt 2 `Developer Self-Review Passed/Accepted` record. All Work Items and Acceptance Criteria are checked; task-owned implementation changes are committed and pushed on the implementation task branch. The known five full-suite failures and missing `tsc` executable remain validation limitations documented above; neither is represented as a passing result. Completion is recorded without merging either task branch into `main`.

Transition: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 2` (unchanged).

Dependency frontier reconciled on 2026-10-22: `ARCH-028-BACKGROUND-008` has only this task as a dependency and was unclaimed in `pending`, so it is promoted to `ready`. No other task explicitly depends on this task.

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
