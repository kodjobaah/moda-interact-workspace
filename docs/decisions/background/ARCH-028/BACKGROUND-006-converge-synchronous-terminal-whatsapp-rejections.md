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

- [ ] Sync 131026 and async FAILED/131026 converge to the same policy outcome.
- [ ] Raw Meta error text/body is not persisted/logged.
- [ ] Other synchronous rejections are not silently classified as recipient-undeliverable.
- [ ] Pre-dispatch validation/configuration/moderation failures are non-billable; synchronous definitive rejection is distinguished from admitted/unknown provider outcomes without a second Meta send.
- [ ] RESERVED recovery source is released idempotently.
- [ ] Outbound hard-limit UsageEvent is removed consistently with async terminal failure.
- [ ] Reachability suppression occurs only after correction succeeds.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Add bounded providerCode extraction/error type tests for text/template sends.
- [ ] Wire synchronous terminal classifier to message evidence.
- [ ] Reuse compensation/hard-limit/reachability owners.
- [ ] Add duplicate, non-terminal and ambiguous failure tests.
- [ ] Add pre-permit versus post-permit failure and recovery HUMAN follow-up boundary regression checks (without assuming a pending ARCH-040 task is already complete).
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Repository-local `WhatsAppServiceError.providerCode?: string` only; no new cross-service contract.

## Dependencies

- `ARCH-028-BACKGROUND-011`

## Enables

- `ARCH-028-BACKGROUND-008`

## Acceptance Criteria

- [ ] Sync `131026` results match async terminal policy except there is no later provider message-status requirement.
- [ ] Non-131026/network/configuration failures preserve existing safe semantics.
- [ ] No double release/hard-limit correction/suppression occurs on retries.
- [ ] `providerCode` classification is bounded and exact; ordinary HUMAN_TEXT cannot acquire a recovery-credit adjustment through shared provider error handling.
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused WhatsApp service, outbound admission and recovery send tests; full Background tests/build; `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Keep provider error parsing bounded to the numeric/string code needed by policy. Do not make WhatsAppService own billing/recovery policy.

Keep the synchronous provider-rejection adapter thin and reuse the asynchronous terminal-failure policy owners. Do not duplicate compensation, hard-limit or reachability policy in the WhatsApp provider client/service.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Implementation complete — Attempt 1 claimed by developer at 2026-10-22T17:30:08Z. Awaiting architect review.

### Files Changed

- `moda-interact-background/src/services/whatsapp.service.ts`
- `moda-interact-background/src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `moda-interact-background/tests/unit/services/whatsapp.service.test.ts`
- `moda-interact-background/tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`

### Work Completed

- Added bounded numeric/string Meta provider-code extraction to `WhatsAppServiceError` for text and template rejection responses; raw provider bodies remain discarded.
- Persisted synchronous definitive failure evidence on the outbound message, preserving non-definitive/ambiguous behavior.
- Routed exact synchronous `131026` failures through the existing message-based recovery compensation and reachability-correction owners, preserving idempotent convergence and ordinary HUMAN_TEXT boundaries.
- Added provider parsing, unbounded-code, and synchronous convergence regression tests.

### Validation Results

- `pnpm exec vitest run tests/unit/services/whatsapp.service.test.ts tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts` — 34/34 passed.
- `pnpm exec tsc6 --noEmit` — passed.
- `pnpm exec eslint src/services/whatsapp.service.ts src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts tests/unit/services/whatsapp.service.test.ts tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts` — passed.
- `git diff --check` — passed.
- Production files reviewed: `whatsapp.service.ts` 239 lines; `outbound-message-delivery.service.ts` 345 lines. The latter pre-existed above 300 lines and received only focused integration/composition changes; no new production file was added.
- `pnpm test` — 2,393/2,398 tests passed; five unrelated existing failures remain in shared-runtime version, platform-configuration-dependent ordering, and B011 source-shape fixtures.

### Deviations

- The repository `pnpm run build` script stopped after Prisma generation because it invokes unavailable `tsc`; equivalent direct `pnpm exec tsc6 --noEmit` passed.

### Assumptions

None.

### Unresolved Issues

- Full Background test/build remains for architect or validation follow-up.

### Architectural Concerns

None.

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
