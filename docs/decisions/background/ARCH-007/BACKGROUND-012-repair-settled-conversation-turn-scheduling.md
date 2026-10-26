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
status: in_progress
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
updated: 2026-10-26
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

- [ ] Reproduce and capture the failing test state and exact runtime/test command on the task starting revision.
- [ ] Trace scheduling, lease claim/release/completion, delayed-job identity, and worker retry behavior to identify the cause.
- [ ] Implement the smallest correction within Background ownership, or stop and report an architectural dependency if the root cause is outside Background.
- [ ] Add focused regression coverage that would fail on the original defect and proves the latest settled version progresses exactly once.
- [ ] Run the required focused and full validation, preserving and reporting unrelated failures.
- [ ] Complete the report and return this task to review; do not start SYSTEM-TEST-005.

## Interfaces / Contracts

Consumes the durable conversation-turn fields from `ARCH-007-DATABASE-006`, the Background turn coalescing contract from `ARCH-007-BACKGROUND-010`, and the inbound abuse admission boundary from `ARCH-007-BACKGROUND-011`. No cross-repository contract change is authorized.

## Dependencies

- ARCH-007-BACKGROUND-010
- ARCH-007-BACKGROUND-011

## Enables

- ARCH-007-SYSTEM-TEST-005

## Acceptance Criteria

- [ ] The original `coalesces three persisted fragments and claims only the settled current version` failure is reproduced before the fix or its non-reproduction is explained against synchronized starting state.
- [ ] The demonstrated root cause is documented and fixed without only raising timeouts, skipping coverage, weakening assertions, or changing B010 policy constants.
- [ ] A deterministic regression proves three persisted fragments reach the current version, only that settled version is claimed, and one agent/provider outcome occurs.
- [ ] Regression coverage proves an active/live lease cannot cause duplicate same-conversation processing and that the newest eligible version progresses after the prior processor releases or becomes safely stale.
- [ ] Existing stale-response, idempotency, abuse-admission and cross-conversation concurrency protections remain intact.
- [ ] No schema/Shared/Messaging/Gateway changes or unrelated production behavior are included.
- [ ] Required validation results and any unrelated failures are recorded accurately in the Completion Report.

## Validation

- [ ] Run the focused failing integration test through the repository's declared disposable `npm run test:integration` harness.
- [ ] Run focused turn-processor/scheduling unit tests.
- [ ] Run `npm run test:unit` and `npm run test:integration` on the final task revision; report exact totals and all remaining failures without masking.
- [ ] Run the repository-declared build/typecheck if required by its package scripts and `git diff --check`.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are complete, set the task to review, finish the Completion Report, return control to moda_architect and STOP. Do not start `ARCH-007-SYSTEM-TEST-005` or other follow-up work.

## Implementation Notes

Start from the launcher-prepared task worktrees and inspect the exact current repository `package.json` and task validation commands. The ARCH-050 attempt reports all 291 unit files / 3,013 tests passing and a single integration timeout reproduced both in the full suite and the npm-isolated invocation. The previously reported diagnostic state is evidence for investigation, not a prescribed implementation. Preserve any other failures encountered and do not modify unrelated tests or runtime paths.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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

None.
