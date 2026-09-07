---
id: ARCH-006-SYSTEM-TEST-003
architecture_id: ARCH-006
title: Verify Batch idempotency and translation self-healing
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 94
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-006-BACKGROUND-007
  - ARCH-006-GATEWAY-001
  - ARCH-006-ADMIN-001
  - ARCH-006-SHOPIFY-001
enables: []
created: 2026-09-05
updated: 2026-09-06
---

# ARCH-006-SYSTEM-TEST-003: Verify Batch idempotency and translation self-healing

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Verify the translation subsystem reconstructs required work from PostgreSQL and never blindly duplicates provider Batch submission under queue loss, retries, restarts or manual Admin reconciliation.

## Context

This task is intentionally backend/resilience focused and uses controlled/fake provider fixtures where possible. It exists because these failure paths are too important to leave only as unit tests.

## Scope

Integrated architecture scenarios around DB state, BullMQ loss/failure, worker restart, provider status/result replay and Admin-triggered reconciliation.

## Out of Scope

- General performance/load test.
- Real provider billing benchmark.
- UI presentation beyond invoking accepted Admin retry action.

## Requirements

Cover at least:
1. DB commit succeeds, initial dispatch enqueue fails -> startup/periodic reconciliation restores work.
2. Redis waiting/delayed jobs are lost -> restart reconstructs PENDING/READY/overdue-poll/provider-completed work.
3. Existing waiting/delayed/active deterministic job is reused, not duplicated.
4. Failed BullMQ job is removed and recreated with same deterministic logical ID.
5. Completed BullMQ job while DB still requires action is treated stale and recreated.
6. Many concurrent dispatch consumers race over the same PENDING pool -> row locking/skip-locked claim yields disjoint Batch membership with no duplicate current assignment and no provider/Redis call inside the claim transaction.
7. Duplicate/concurrent submit delivery results in one provider create.
8. Definite retryable provider submission failure -> durable minute-based retry occurs without BullMQ/SDK duplicate create; bounded exhaustion becomes FAILED.
9. Simulated create accepted but response persistence fails -> `SUBMISSION_UNKNOWN`; bounded provider correlation by logical metadata + input file adopts the existing provider Batch and does not re-create.
10. OpenAI/fake provider completes while Moda worker is offline -> overdue minute-scale poll discovers completion after restart.
11. Transient provider poll/read failure -> minute retry occurs without marking translations failed.
12. Known Batch/per-request retryable failure -> affected translations retry in a new logical Batch only up to configured bound; exhausted/non-retryable failures become durable FAILED.
13. Partial result application crash -> replay applies remaining translations only.
14. Admin targeted reconciliation request accepted while Redis unavailable -> remains durable and later completes through same reconciler.
15. No job IDs contain `:` and no queue payload/log contains message body/secrets.

## Work Items

- [ ] Build/reuse fake provider + controllable Redis/system-test fixtures.
- [ ] Add queue-loss/restart reconstruction scenarios.
- [ ] Add deterministic job reuse/failed/stale repair scenarios.
- [ ] Add concurrent `FOR UPDATE SKIP LOCKED` batch-claim scenario with 20+ logical consumers.
- [ ] Add definite-retryable, duplicate and ambiguous provider submission scenarios.
- [ ] Add transient poll and bounded per-item/provider-terminal retry scenarios.
- [ ] Add offline provider completion + partial result replay.
- [ ] Add Admin reconciliation request while Redis unavailable.
- [ ] Record evidence and any non-deterministic external prerequisites.

## Interfaces / Contracts

Test against accepted public/internal system-test surfaces. Prefer provider fakes over paid real OpenAI calls for deterministic failure injection.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

None

## Acceptance Criteria

- [ ] No accepted translation is permanently stranded by Redis loss.
- [ ] Concurrent assemblers never assign one translation to two current batches.
- [ ] Same logical Batch is not blindly submitted twice.
- [ ] Safe provider failures retry automatically only when non-creation/terminal state is known; ambiguous create never auto-retries.
- [ ] Ambiguous submission is recovered by provider metadata correlation.
- [ ] Deterministic queue jobs are reused or safely remove/recreated according to state.
- [ ] Minute-scale poll scheduling recovers after worker downtime.
- [ ] Partial result processing is idempotent.
- [ ] Admin retry is durable when Redis is down.
- [ ] PostgreSQL remains the authoritative recovery ledger.

## Validation

Run the dedicated resilience system-test scenarios and record commands/evidence. If destructive Redis reset is not safe in shared environments, use isolated local/test Redis or controlled fixture; do not weaken the assertions.

## Implementation Notes

This task must not become a prerequisite for any non-system-test implementation task.

## Completion Report

### Status

Not started.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

None yet.

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
