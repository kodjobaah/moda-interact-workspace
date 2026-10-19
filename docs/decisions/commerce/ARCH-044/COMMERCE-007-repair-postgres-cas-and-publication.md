---
id: ARCH-044-COMMERCE-007
architecture_id: ARCH-044
title: Repair durable agent-configuration CAS and publication transaction validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-044-COMMERCE-002]
enables: []
created: '2026-10-18'
updated: '2026-10-18'
---

# Repair durable agent-configuration CAS and publication transaction validation

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Resolve the two existing PostgreSQL-backed correctness failures involving retained agent-configuration versions and publication transaction lifecycle while preserving CAS, rollback and idempotency guarantees.

## Context

Baseline `tests/agent-configuration-retained-read.test.ts:93` expected `{kind:"ok"}` during model/prompt pointer clear/set across one retained row, but received `{kind:"error"}`. This uses an in-memory Prisma substitute; determine whether the service contract, test-double methods/versions or real database behavior diverge. Separately `tests/backend-postgres-rehearsal.test.ts` failed in `src/commerce/integration/backend/publication-storage.ts:139` during `commerceAuditEvent.create()` with Prisma `Transaction not found` (closed/expired transaction) after roughly 50 seconds. No evidence yet proves whether this reflects timeout, test-fixture loading or actual transaction design. These are two specific cases of durable-state test correctness; if their root causes prove independent and substantial, report a bounded split to the architect instead of opportunistic refactoring.

## Scope

- Use ARCH-044-COMMERCE-002 disposable test infrastructure for controlled PostgreSQL reproduction; inspect `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/publication/lifecycle.ts`, and the model/prompt configuration services.
- Compare test-double capabilities and accepted state transitions for retained model and prompt pointers, CAS versions and replay behavior; verify real PostgreSQL semantics where relevant.
- Reproduce publication audit write transaction expiry under measured conditions, including query count/duration, isolation, retries, event ownership and rollback semantics; correct bounded implementation/test setup as evidence requires.
- Preserve durable idempotency, stale-version denial, audit write atomicity and rollback. Do not mask Transaction-not-found by ignoring failed writes.

## Out of Scope

- No Prisma schema/migrations in Commerce, no global transaction-timeout override without measurement, and no production database mutation during tests.
- No changes to unrelated Studio form/UI tests or Redis admission quota.

## Requirements

1. Model and prompt mutations have separate CAS versions on one retained row; clear actions preserve the counterpart's version and pointer.
2. Replayed operation IDs must be idempotent, stale versions rejected and audit effects not duplicated.
3. Publication writes and audits must remain atomic, with rollback after injected failure and no partial commit after transaction expiry.
4. PostgreSQL integration must use isolated disposable data, bounded concurrency and cleanup, and record effective transaction settings before changing them.

## Work Items

- [ ] Reproduce retained-read test with a current Prisma test double and identify exact source of `{kind:"error"}`.
- [ ] Validate model/prompt pointer and edit-version semantics in real disposable PostgreSQL.
- [ ] Reproduce publication transaction expiry with bounded diagnostics and inspect transaction scopes/audit queries.
- [ ] Fix test-double/fixture or production behavior only according to evidence, preserving atomicity.
- [ ] Add regression coverage for idempotency, CAS races and audit rollback.

## Interfaces / Contracts

PostgreSQL durable state via canonical `moda-interact-database` Prisma schema; model/prompt `modelEditVersion` and `promptEditVersion`; `CommerceAuditEvent`, publication CAS and operation IDs. No database-owned schema edits allowed in Commerce; refer migration need to moda_architect/moda_database.

## Dependencies

- `ARCH-044-COMMERCE-002` — accepted Complete, with a reproducible fixture handoff.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [ ] `tests/agent-configuration-retained-read.test.ts` passes with proven separate model/prompt CAS semantics.
- [ ] `tests/backend-postgres-rehearsal.test.ts` passes repeatedly using disposable PostgreSQL without closed/expired transaction errors.
- [ ] Publication rollback, replay, stale CAS and two-client race scenarios all pass and remain atomic.
- [ ] No test suppresses errors, extends transaction settings arbitrarily or writes to non-disposable resources.
- [ ] Complete evidence distinguishes environment, fixture and production defects for each original failure.

## Validation

- [ ] `npx vitest run tests/agent-configuration-retained-read.test.ts`.
- [ ] Existing `npm run test:arch020-backend-integration:postgres` rehearsal and `tests/backend-postgres-rehearsal.test.ts` under disposable infrastructure (follow actual script requirements).
- [ ] `npx vitest run tests/agent-configuration-model.test.ts tests/agent-configuration-effective.test.ts tests/commerce-lifecycle.test.ts`.
- [ ] `npm run typecheck`, affected integration validation, `git diff --check`.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

Dependent on ARCH-044-COMMERCE-002 so tests have an explicit disposable PostgreSQL path. If investigation requires a Prisma model/constraint change, stop and return the ownership gap to moda_architect for a database-owned task rather than editing nested `database/` schema source.

### Exact failing tests

- `tests/agent-configuration-retained-read.test.ts` — `tracks model and prompt CAS versions on one retained row across clear operations`.
- `tests/backend-postgres-rehearsal.test.ts` — `publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure`.

## Completion Report

### Status

Not Started

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run. Record each exact command, environment, exit code, test totals and any known-baseline differences. Baseline failures may not be silently treated as task successes.

### Worktree / Synchronisation Evidence

Not yet materialised. Record launcher-resolved canonical workspace root, dedicated parent and implementation worktrees, initial branch/commit identities and recursive submodule state when execution begins.

### Deviations

None yet.

### Assumptions

Task definition based on the 2026-10-18 source snapshot and supplied baseline/task logs; re-inspect current implementation when executing.

### Unresolved Issues

None beyond the explicitly described diagnostics to investigate.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation evidence.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

Not assessed.

### Follow-up

None yet.
