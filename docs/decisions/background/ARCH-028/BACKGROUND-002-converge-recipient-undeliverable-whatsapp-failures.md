---
id: ARCH-028-BACKGROUND-002
architecture_id: ARCH-028
title: Converge recipient-undeliverable WhatsApp delivery failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-028-BACKGROUND-001
  - ARCH-028-MESSAGING-001
enables:
  - ARCH-028-BACKGROUND-004
created: 2026-10-03
updated: 2026-10-12
---

# Converge recipient-undeliverable WhatsApp delivery failures

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Classify exact bounded Meta code `131026` as the ARCH-028 terminal recipient-delivery condition, converge linked recovery/follow-up state safely, and make later compensation eligibility independent of `RecoveryOutreachAttempt.status`.

## Context

A delayed provider failure can arrive after the follow-up processor has already moved the initial attempt to `NO_RESPONSE`. Provider delivery authority therefore belongs to `ConversationMessage`, not the attempt response-lifecycle enum.

## Scope

- Add one pure classifier: `131026 -> RECIPIENT_UNDELIVERABLE`, other/absent -> unclassified.
- Resolve the exact linked `RecoveryOutreachAttempt` through `outboundMessageId`; never correlate by phone/customer/timestamp.
- If the exact attempt is still `WAITING_FOR_RESPONSE`, guardedly move it to `FAILED` with `WHATSAPP_RECIPIENT_UNDELIVERABLE` inside the existing provider-status transaction.
- If attempt is already `NO_RESPONSE`, `ENGAGED`, `CANCELLED`, `CAPACITY_BLOCKED` or `FAILED`, do not overwrite its response lifecycle merely to make compensation possible.
- Make due follow-up processing consult authoritative failed-message evidence before `markNoResponseIfWaiting`, billing or provider work.

## Out of Scope

- Usage release/compensation.
- Recipient suppression.
- Hard-limit correction.
- Synchronous HTTP rejection.
- Missing phone.
- Merchant notification.

## Requirements

- [x] Exact `131026` is the only terminal-recipient code in ARCH-028 v1.
- [x] A provider FAILED message linked to a recovery can be financially compensatable regardless of attempt status.
- [x] `WAITING_FOR_RESPONSE -> FAILED` remains a useful convergence transition but is not a financial eligibility precondition.
- [x] `NO_RESPONSE` race cannot permanently block later compensation.
- [x] DELIVERED/READ wins before compensation and prevents terminal classification from acting.
- [x] A due follow-up whose initial message is durably FAILED/131026 performs no policy/billing/provider send.
- [x] No permanent `hasWhatsApp` assertion is created.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Add pure provider-code classifier/tests.
- [x] Resolve linked attempt/recovery from message relation.
- [x] Guard WAITING -> FAILED convergence in the provider-status transaction.
- [x] Preserve other attempt lifecycle states without using them as compensation gates.
- [x] Add failed-message follow-up suppression before no-response/billing/provider work.
- [x] Add NO_RESPONSE race and duplicate/out-of-order tests.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes v3 `failure.providerCode`; introduces repository-local classification `RECIPIENT_UNDELIVERABLE` and stable attempt failure code `WHATSAPP_RECIPIENT_UNDELIVERABLE` when WAITING can be converged.

## Dependencies

- `ARCH-028-BACKGROUND-001`
- `ARCH-028-MESSAGING-001`

## Enables

- `ARCH-028-BACKGROUND-004`

## Acceptance Criteria

- [x] `131026` classifies terminal-recipient; other/absent codes do not.
- [x] Linked WAITING attempt can become FAILED idempotently.
- [x] Existing NO_RESPONSE/ENGAGED/etc. state is not overwritten solely for compensation.
- [x] Later compensation can use FAILED/131026 message + exact reservation lineage even when attempt is not FAILED.
- [x] Due follow-up no-ops before billing/provider work when authoritative initial delivery failed.
- [x] Positive delivery/read and unrelated failures retain existing behaviour.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Run focused classifier/provider-status/follow-up tests, repository unit/full test/build gates and `git diff --check` as declared by the current repository.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not redesign `RecoveryOutreachStatus` to carry two independent dimensions. Message delivery and attempt response lifecycle stay separate; later compensation reads both durable associations without requiring an artificial state rewrite.

Keep terminal-recipient classification and recovery/attempt convergence as focused units. Do not bury the provider-code classifier or NO_RESPONSE race policy inside the follow-up processor or provider-status consumer.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Architect review (Attempt 1, 2026-10-12). Implementation commit: `3a48d4eb974bcde1835050d0cd8fdcb8b67b98d4`.

### Files Changed
Added `src/domain/whatsapp-recipient-failure.ts` and `tests/unit/domain/whatsapp-recipient-failure.test.ts`. Updated `src/services/whatsapp-provider-status.service.ts`, `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, and their focused tests.

### Work Completed
Added a pure exact-match classifier: only `131026` maps to `RECIPIENT_UNDELIVERABLE`; all other, absent, or non-exact codes remain unclassified.

The existing serializable provider-status transaction now loads the exact linked `recoveryOutreachAttempt` relation from the `ConversationMessage`. For accepted FAILED/131026 evidence, it compare-and-sets only a `WAITING_FOR_RESPONSE` attempt to `FAILED`, recording `WHATSAPP_RECIPIENT_UNDELIVERABLE` and the failure time. Other attempt lifecycle states are not rewritten; the durable failed message, provider code, and exact attempt/recovery link remain available independently of attempt status. Later DELIVERED/READ evidence remains authoritative at the message layer.

Due follow-up processing now checks the initial attempt's exact `outboundMessageId` before no-response claiming. A durably FAILED message with exact provider code 131026 is suppressed before policy resolution, further attempt creation, billing, template selection, or provider send. Unrelated codes and positive delivery states retain the existing path. No compensation execution, schema/migration, reachability, hard-limit, or merchant-notification behavior was added; compensation remains outside this task's scope.

### Validation Results
PASS: focused classifier/provider-status/follow-up suite, 52 tests across 3 files.

PASS: `npm run build` (Prisma Client generation and TypeScript compilation), `npm run prisma:validate`, changed-file diagnostics (no errors), and `git diff --check`.

NOT PASS: `npm run test:unit` and `npm test` each reported 2,084 passed and 6 failed across 204 files. The same six failures are confined to untouched `tests/unit/services/checkout-refresh.test.ts`; its fixture lacks `pendingRecoveryCandidateService.withCheckoutLock`, so execution fails before the checkout-refresh assertions. No test in the changed provider-status/follow-up paths failed. Both full repository gates were run and the failures are reported for Architect review.

### Deviations
The fresh implementation worktree initially had no Prisma Client. A `pnpm exec` invocation attempted dependency setup and hit pnpm's ignored-build-script gate; Prisma Client was generated using the repository-declared Prisma CLI, after which focused tests and the build passed. The generated untracked pnpm YAML files were removed; no dependency manifest or lockfile change remains.

### Assumptions
ARCH-028-BACKGROUND-004 owns compensation execution. BACKGROUND-002 preserves durable FAILED/131026 message evidence and exact attempt/recovery lineage without using the mutable attempt status as an eligibility condition.

### Unresolved Issues
The full repository unit/test gates have six unrelated failures in `tests/unit/services/checkout-refresh.test.ts` because the fixture does not implement the current checkout-lock port. The task-owned focused suite, build, schema validation, diagnostics, and diff checks pass.

### Architectural Concerns
No new architecture concerns identified. The classifier is 6 lines; touched existing production modules are 270 lines (`whatsapp-provider-status.service.ts`) and 194 lines (`recovery-outreach-follow-up-processor.service.ts`), both below the 300-line ceiling.

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
