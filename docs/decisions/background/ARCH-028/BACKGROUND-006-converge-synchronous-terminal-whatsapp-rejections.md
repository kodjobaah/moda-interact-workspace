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
status: review
priority: 72
executor: developer
claimed_at: 2026-10-22T17:30:08Z
attempt: 1
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
- [x] Non-131026/network/configuration failures preserve existing safe semantics.
- [x] No double release/hard-limit correction/suppression occurs on retries.
- [x] `providerCode` classification is bounded and exact; ordinary HUMAN_TEXT cannot acquire a recovery-credit adjustment through shared provider error handling.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

- [x] Focused WhatsApp, outbound admission, recovery send and synchronous rejection tests: 64/64 passed across eight suites (before the small nullability follow-up).
- [x] Follow-up tests for the null-attempt correction and adjacent admission/delivery behaviour: 31/31 passed across three suites; this run overlaps the eight-suite run and is not 31 additional distinct tests.
- [x] `pnpm exec tsc6 --noEmit` and `git diff --check`: successful combined command confirmed by the developer (`ARCH-028-BACKGROUND-006 VALIDATION PASSED`).
- [x] `pnpm run prisma:generate` and direct `pnpm exec tsc6`: Prisma generated and no compilation errors shown in the follow-up log.
- [ ] Full Background test suite: prior Attempt 1 run reported 2,393/2,398 passing with five failures; not re-run after the revised implementation.
- [ ] Declared `pnpm run build`: Prisma generation succeeded but the script stopped at `tsc: command not found`. Direct `tsc6` compilation succeeded; standard script remains unresolved.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep provider error parsing bounded to the numeric/string code needed by policy. Do not make WhatsAppService own billing/recovery policy.

Keep the synchronous provider-rejection adapter thin and reuse the asynchronous terminal-failure policy owners. Do not duplicate compensation, hard-limit or reachability policy in the WhatsApp provider client/service.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Review — developer-owned **formal Attempt 1**, with the second implementation revision and subsequent nullability fix applied and locally validated on 2026-10-22. The existing `executor: developer`, `claimed_at` and `attempt: 1` are preserved because there is no evidence of a separate canonical Attempt 2 claim. Review is requested; this does not constitute architect acceptance or developer completion.

### Files Changed

Implementation files in `moda-interact-background/` (the Attempt 2 correction plus the earlier provider-code work, 20 distinct paths):

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
- `tests/unit/services/outbound-whatsapp-admission/failed-outreach-admission.test.ts`
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
- Reviewed modularity: `whatsapp-provider-rejection.ts` (20 lines), `synchronous-recipient-failure.service.ts` (32), `synchronous-recipient-failure-evidence.service.ts` (93), `outbound-provider-failure.service.ts` (45), and `failed-outreach-admission.ts` (30). `outbound-message-delivery.service.ts` is 286 lines (down from 345). Existing larger dispatcher (419 lines) receives only thin integration; no new catch-all module was introduced.

### Validation Results

- Eight-suite `pnpm exec vitest run` covering WhatsApp provider, synchronous recipient failure/evidence, provider failure, failed outreach, outbound delivery/reservations and merchant recovery follow-up: **64/64 passed** (2026-10-22 local terminal log).
- Three-suite follow-up covering failed outreach admission, outbound admission reservation and outbound message delivery after the nullable-attempt fix: **31/31 passed** (overlapping subset of the earlier suites, not additive).
- `pnpm exec tsc6 --noEmit && git diff --check && echo "ARCH-028-BACKGROUND-006 VALIDATION PASSED"`: **passed**, confirmed by developer terminal output.
- `pnpm run prisma:generate` and `pnpm exec tsc6`: Prisma Client generation succeeded, direct TypeScript compilation returned without errors in the supplied log.
- First revision's focused `pnpm exec eslint` run for the original four files passed. A complete lint run for every revised file has not been evidenced.
- Earlier broader `pnpm test` run: **2,393/2,398 passed** with five failures reported in the previous Completion Report; no evidence yet demonstrates that these are confirmed baseline failures or that the full suite has passed after this correction.
- Standard `pnpm run build` did **not** pass: the declared script calls `tsc`, which was unavailable (`sh: tsc: command not found`) in the tested dependency environment. The equivalent direct `tsc6` compilation passed; no claim is made that the declared build script passed.

### Deviations

- The task underwent a second implementation revision plus a small follow-up typecheck fix within the existing formally claimed developer Attempt 1. No unverified increment to `attempt` or new launcher claim has been invented.
- Repository-declared build and full-suite validation remain incomplete as described above; direct compiler success is recorded separately, not substituted for a passing declared build.

### Assumptions

- The previously claimed developer worktree remains the execution context; formal `attempt: 1`, ownership and completion authority are unchanged.
- All implementation path listings describe the files in the submitted worktree snapshot and incremental correction patch, not a verified pushed implementation-branch diff.

### Unresolved Issues

- Confirm whether the declared `pnpm run build` dependency/toolchain failure is a documented baseline condition or requires a separate owner correction.
- Reconcile the five failures in the earlier full Background suite against the current baseline; the broad suite was not rerun after the latest corrections.
- Supply/check implementation commit SHA, successful push, dedicated parent/implementation worktree isolation and launcher start-of-attempt synchronization evidence before acceptance. These are not established by the submitted terminal logs or archive.

### Architectural Concerns

- No new cross-repository runtime contract or database schema change introduced by this task. The correction deliberately reuses existing compensation and reachability owners. The pre-existing 419-line human dispatcher remains a maintainability hotspot but has only thin task integration; the modularity review found no blocking new module-boundary issue.

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
