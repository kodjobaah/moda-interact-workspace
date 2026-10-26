---
id: ARCH-007-BACKGROUND-012
architecture_id: ARCH-007
title: Repair settled conversation-turn scheduling under concurrent inbound fragments
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 25
executor: copilot
claimed_at: 2026-10-26T22:09:29Z
attempt: 1
depends_on:
  - ARCH-007-BACKGROUND-010
  - ARCH-007-BACKGROUND-011
enables:
  - ARCH-007-SYSTEM-TEST-005
created: 2026-10-26
updated: 2026-10-26T22:30:00Z
---

# ARCH-007-BACKGROUND-012: Repair settled conversation-turn scheduling under concurrent inbound fragments

## Architecture

Architecture ID:

ARCH-007

Architecture document:

docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md

Coordinator:

moda_architect

## Objective

Correct the reproducible Background conversation-turn scheduling failure where a newer persisted inbound version remains unprocessed while an older version holds or interacts with the conversation processing lease.

## Context

The `ARCH-050-BACKGROUND-001` validation at Background revision `6cce2b18f288d4cabc6f7dcea3ef251acbb15323` passes all 291 unit files / 3,013 tests after `npm ci`, but disposable integration validation times out in `tests/integration/conversation-turn-scheduling.integration.test.ts` at `coalesces three persisted fragments and claims only the settled current version`.

The failure reproduces under the repository's npm-isolated integration invocation. Diagnostic state showed `inboundVersion: 3`, `lastProcessedVersion: 0`, `processingInboundVersion: 2`, and version 3 still pending after the test's five-second wait. `ARCH-028-BACKGROUND-007` previously recorded this exact test identity as an unresolved follow-up. This task owns diagnosis and correction of the Background scheduling/lease behavior; it does not assume the observed state alone proves the root cause.

The accepted `ARCH-007-BACKGROUND-010` contract remains authoritative: preserve every inbound message, the configured quiet window and maximum settle window, one live processor per conversation, stale-response suppression, and concurrent progress across different conversations. Do not satisfy this task by only increasing test timeouts or removing assertions.

## Scope

- Reproduce the failing disposable PostgreSQL/Redis integration test on the synchronized task starting revision and inspect the current scheduler, processor, persistence and BullMQ lifecycle involved.
- Identify the cause of the stale-version/live-lease state and make the smallest Background-owned correction that guarantees the latest settled inbound version can be processed after earlier work releases or expires.
- Add or adjust focused regression coverage for three persisted fragments, a newer version arriving around an active claim, and recovery/retry from a stale or released processing lease as applicable to the demonstrated cause.
- Run the focused scheduling integration case and the repository-declared unit/integration validation required below; report unrelated failures without masking them.

## Out of Scope

- Changes to ARCH-050 task status, report, files or implementation.
- Changes to the accepted quiet-window, maximum-settle-window or processing-lease policy solely to make the timeout disappear.
- Raising timeouts, skipping the case, reducing assertions, or changing the test to accept an unprocessed latest version.
- Database schema/migrations, Shared contracts, Messaging ingress, Gateway/deployment, abuse-admission policy, billing, or unrelated Background failures.
- Starting `ARCH-007-SYSTEM-TEST-005` as part of this implementation task.

## Requirements

- Preserve idempotent inbound persistence and deterministic conversation/version job identity.
- Preserve the B010 settle calculation and conversation-scoped processor lease semantics unless concrete evidence demonstrates an architectural contradiction; any such contradiction must be returned to `moda_architect` before widening scope.
- When fragments settle to version 3, exactly the current settled version is claimed and processed once; versions 1 and 2 cannot produce stale replies.
- A live lease must not permit concurrent CommerceAgent work for the same conversation. Once the lease is released, completed, or safely determined stale, the latest eligible version must make forward progress without requiring another customer message.
- Preserve processing across different conversations and all existing outbound admission, abuse admission, provider ambiguity, tenant ownership, and stale-response protections.
- Do not introduce custom generic logging; use existing shared logging conventions for any new runtime diagnostic events.

## Work Items

- [x] Reproduce and capture the failing test state and exact runtime/test command on the task starting revision.
- [x] Trace scheduling, lease claim/release/completion, delayed-job identity, and worker retry behavior to identify the cause.
- [x] Implement the smallest correction within Background ownership, or stop and report an architectural dependency if the root cause is outside Background.
- [x] Add focused regression coverage that would fail on the original defect and proves the latest settled version progresses exactly once.
- [x] Run the required focused and full validation, preserving and reporting unrelated failures.
- [x] Complete the report and return this task to review; do not start SYSTEM-TEST-005.

## Interfaces / Contracts

Consumes the durable conversation-turn fields from `ARCH-007-DATABASE-006`, the Background turn coalescing contract from `ARCH-007-BACKGROUND-010`, and the inbound abuse admission boundary from `ARCH-007-BACKGROUND-011`. No cross-repository contract change is authorized.

## Dependencies

- ARCH-007-BACKGROUND-010
- ARCH-007-BACKGROUND-011

## Enables

- ARCH-007-SYSTEM-TEST-005

## Acceptance Criteria

- [x] The original `coalesces three persisted fragments and claims only the settled current version` failure is reproduced before the fix or its non-reproduction is explained against synchronized starting state.
- [x] The demonstrated root cause is documented and fixed without only raising timeouts, skipping coverage, weakening assertions, or changing B010 policy constants.
- [x] A deterministic regression proves three persisted fragments reach the current version, only that settled version is claimed, and one agent/provider outcome occurs.
- [x] Regression coverage proves an active/live lease cannot cause duplicate same-conversation processing and that the newest eligible version progresses after the prior processor releases or becomes safely stale.
- [x] Existing stale-response, idempotency, abuse-admission and cross-conversation concurrency protections remain intact.
- [x] No schema/Shared/Messaging/Gateway changes or unrelated production behavior are included.
- [x] Required validation results and any unrelated failures are recorded accurately in the Completion Report.

## Validation

- [x] Run the focused failing integration test through the repository's declared disposable `npm run test:integration` harness.
- [x] Run focused turn-processor/scheduling unit tests.
- [x] Run `npm run test:unit` and `npm run test:integration` on the final task revision; report exact totals and all remaining failures without masking.
- [x] Run the repository-declared build/typecheck if required by its package scripts and `git diff --check`.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are complete, set the task to review, finish the Completion Report, return control to moda_architect and STOP. Do not start `ARCH-007-SYSTEM-TEST-005` or other follow-up work.

## Implementation Notes

Start from the launcher-prepared task worktrees and inspect the exact current repository `package.json` and task validation commands. The ARCH-050 attempt reports all 291 unit files / 3,013 tests passing and a single integration timeout reproduced both in the full suite and the npm-isolated invocation. The previously reported diagnostic state is evidence for investigation, not a prescribed implementation. Preserve any other failures encountered and do not modify unrelated tests or runtime paths.

## Completion Report

### Status

Ready for Review (Attempt 1)

### Files Changed

- `moda-interact-background/src/services/conversation.service.ts`
- `moda-interact-background/tests/integration/conversation-turn-scheduling.integration.test.ts`
- `moda-interact-background/tests/unit/services/conversation.service.test.ts`
- `moda-interact-background/tests/unit/services/conversation-turn-processor/facade-claims-and-state.cases.ts`

### Work Completed

- Reproduced the exact scheduling integration failure on synchronized starting revision `6cce2b18f288d4cabc6f7dcea3ef251acbb15323` with `npm run test:integration -- tests/integration/conversation-turn-scheduling.integration.test.ts`. The run failed the original three-fragment case because processor claims were `[2, 3]` instead of `[3]`.
- Root cause: Background used the provider event's `occurredAt` for `ConversationMessage.createdAt`, `pendingTurnStartedAt`, and `lastInboundAt`. An inbound event delayed in delivery therefore arrived with an already-aged quiet window; the version-2 job could become eligible before the next persisted fragment, causing a second claim/turn cycle.
- `receiveMessage` now captures Background receipt time once and uses it consistently for persisted inbound ordering and both settle clocks. Provider `occurredAt` remains the timestamp for recovery-engagement evidence, preserving that lifecycle's event-time behavior.
- Strengthened the disposable three-fragment integration regression with provider event timestamps 60 seconds before receipt. It still proves all fragments persist, only version 3 is claimed, and exactly one agent/provider outcome occurs.
- Added a fake-clock ConversationService unit regression for receipt-time settle clocks and strengthened the live-lease unit regression to assert retry scheduling for the current observed version and one agent execution.
- No B010 settle/lease policy constants or schema, Shared, Messaging, Gateway, abuse-admission, or billing behavior changed.

#### Launcher and Worktree Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-007-BACKGROUND-012`, `task/ARCH-007-BACKGROUND-012`; starting revision `790f2f08f19f7bb2ee940deb56a1502822c926ab`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-007-BACKGROUND-012`, `task/ARCH-007-BACKGROUND-012`; starting revision `6cce2b18f288d4cabc6f7dcea3ef251acbb15323`.
- Launcher prepared and claimed attempt 1; claim commit `f85aeb99bfd283407f1053b7fc3771f18ce5713b`.
- Work remained in the dedicated task worktrees; shared workspace and shared implementation checkouts were not switched or mutated, and no other task worktree was reused.
- Recursive implementation submodules were initialized at launch; database submodule commit `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`.

### Validation Results

- `npm ci`: passed from the committed lockfile; no manifest or lockfile changes. npm reported 20 audit findings (8 moderate, 12 high) and install-script approval notices.
- Baseline focused disposable integration command: reproduced; 1 failed, 1 passed. After fix, focused scheduling integration: 2 passed, including the deterministic delayed-event regression.
- Final full `npm run test:integration`: 5 files passed, 13 tests passed.
- Final focused command `npm exec vitest -- run tests/unit/services/conversation.service.test.ts tests/unit/services/conversation-turn-processor.service.test.ts`: 2 files passed, 68 tests passed. The processor-only suite after the strengthened lease assertion also passed: 54 tests.
- Final `npm run test:unit`: 287 files passed, 4 failed; 3,000 tests passed, 14 failed (3,014 total). Failures are confined to untouched files: `tests/unit/services/matured-candidate.materialization.test.ts` (11 stale expectations), `tests/unit/services/checkout-refresh.test.ts` (1 stale selector expectation), `tests/unit/services/conversation-moderation/automated-template-input.test.ts` (1 stale null-header expectation), and `tests/unit/runtime/observability-startup.test.ts` (1 stale Shared-version expectation: test expects 2.5.0, manifest is 2.5.1). These are unrelated to B012 and overlap known ARCH-050 remediation findings; no failures occurred in changed unit files in the full run.
- `npm run build`: passed (Prisma Client generation and TypeScript compilation).
- `git diff --check`: passed on the final implementation diff after all source and test edits.
- Editor diagnostics for changed production/unit files: no errors.

### Deviations

The full unit suite is not green because of the 14 unrelated, pre-existing stale expectations listed above. They are outside B012 scope and were not altered.

### Assumptions

The provider event time is retained for recovery-engagement semantics, while conversation arrival ordering and the B010 quiet/max-settle clocks are based on Background receipt time.

### Unresolved Issues

The unrelated full-unit-suite failures listed in Validation Results remain for their owning remediation task.

### Architectural Concerns

None. The change is within Background ownership and preserves B010 settle calculation, lease duration, idempotency, stale-response suppression, and concurrency semantics.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending

### Follow-up

Architect review only. Do not start `ARCH-007-SYSTEM-TEST-005` from this task.
