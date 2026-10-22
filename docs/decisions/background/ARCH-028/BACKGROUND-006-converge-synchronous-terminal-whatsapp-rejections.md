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
status: in_progress
priority: 72
executor: developer
claimed_at: 2026-10-22T19:40:40Z
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

The developer explicitly invoked `/moda_developer_create ARCH-028-BACKGROUND-006`, taking execution and completion authority from the prior agent-owned definition. The task scope, dependencies, acceptance criteria and validation expectations are unchanged; `assigned_agent: moda_background` remains the logical repository owner. The next canonical launcher preparation will claim Attempt 1 after this ownership amendment is published.

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
- [x] Final `pnpm exec tsc6 --noEmit && git diff --check` succeeded, confirmed by developer terminal output on 2026-10-22. Earlier Prisma generation and changed-path ESLint passed before the final correction; not rerun in the supplied final output.
- [ ] Latest full Background suite: 2,420 passed, 5 failed (2,425 total). Neither earlier BG006-specific failure remains. Five failures in other suites still require independent baseline/ownership verification; do not mark the suite passing.
- [ ] Declared `pnpm run build`: previously stopped at `tsc: command not found` after Prisma generation. Direct `tsc6` succeeded; declared build is not verified as passing.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep provider error parsing bounded to the numeric/string code needed by policy. Do not make WhatsAppService own billing/recovery policy.

Keep the synchronous provider-rejection adapter thin and reuse the asynchronous terminal-failure policy owners. Do not duplicate compensation, hard-limit or reachability policy in the WhatsApp provider client/service.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-22T19:40:40Z. Attempt 1 review history is preserved below.

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

- Earlier focused `pnpm exec vitest run` matrix: **69/69 passed** across nine suites.
- Corrections rerun: **39/39 passed** across two suites — `recovery-outreach-follow-up-processor.service.test.ts` (28/28) and `outbound-admission-reservation.service.test.ts` (11/11). This supersedes the prior two task-related isolated failures.
- Latest full `pnpm test`: **2,420/2,425 passed**, with five remaining failures, in `checkout-refresh.test.ts`, `inbound-whatsapp-abuse-admission.service.test.ts` (two), `observability-startup.test.ts`, and `recovery-agent-context.service.test.ts`. None of those five test files was changed by BG006; their root cause/baseline classification still needs independent validation. The suite is NOT reported as passing.
- Final developer terminal output: `pnpm exec tsc6 --noEmit && git diff --check && echo "ARCH-028-BACKGROUND-006 TYPECHECK PASSED"` succeeded.
- Earlier Prisma generation, changed-path ESLint and direct TypeScript compilation passed; no unverified claim is made that they were rerun after the final type-only correction.
- Standard `pnpm run build` previously failed because the declared script calls unavailable `tsc` (`sh: tsc: command not found`). Direct `tsc6` succeeded, but the declared script has **not** been verified as passing.
- Git evidence: pushed implementation commit `0bb1a62cd9d787114764946fbd5209c33025a2d5` on `origin/task/ARCH-028-BACKGROUND-006`; user-provided `git status` confirms that implementation worktree is clean and tracking the remote branch. GitHub compare against `main` confirms 23 implementation/test paths changed.

### Deviations

- Developer Changes Requested review returned formal Attempt 1 to `ready`. The correction commits were pushed without a separately evidenced canonical Attempt 2 claim. This workflow gap must be reconciled by `/moda_developer_create ARCH-028-BACKGROUND-006` before submitting a newly reviewed attempt; no claim timestamp or attempt increment is invented here.
- Five full-suite failures outside the 23 changed BG006 paths and the declared-build `tsc` alias problem remain validation exceptions; these are not represented as passes.

### Assumptions

- Repository ownership remains `moda_background`; developer execution/completion modes are unchanged.
- The currently pushed implementation revision is commit `0bb1a62cd9d787114764946fbd5209c33025a2d5` (superseding earlier snapshot `2aa1153ed97413c88e495808ba2786df46ef3a32`) on `origin/task/ARCH-028-BACKGROUND-006`. This was directly verified using the GitHub commit/branch comparison.
- The prior parent worktree was reported clean and synchronized at the Changes Requested self-review. The required physical start-of-Attempt-2 launcher packet has not been supplied.

### Unresolved Issues

- The two previous BG006 correction items are implemented and covered by passing focused tests; no known task-local test failure remains from those findings.
- Five failures persist in the full Background suite; their baseline/cross-task cause has not been independently resolved. Do not mark full-suite validation complete without a justified baseline finding or a passing rerun.
- The declared `pnpm run build` is still unverified due to the missing `tsc` command. Direct `tsc6` typecheck passed; repository build-script behavior must be resolved or explicitly accepted as a documented validation limitation.
- No new formal Attempt 2 claim exists in the canonical task. Developer review/acceptance must follow the actual claim workflow; the task is not Complete and does not yet unblock BG008.
- Launcher-resolved physical worktree and synchronization evidence for the new attempt must be attached to the Completion Report when available.

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
- This note preserves the historical Attempt 1 Changes Requested decision. It is **not** an Accepted developer self-review, a canonical Attempt 2 claim, or a task completion decision.

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
