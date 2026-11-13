---
id: ARCH-075-ADMIN-006
architecture_id: ARCH-075
title: Give each nonempty translation retry its own audit identity
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-ADMIN-005
enables:
  - ARCH-075-SYSTEM-TEST-002
created: 2026-11-13
updated: 2026-11-13
---

# Give each nonempty translation retry its own audit identity

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Give each nonempty translation retry its own audit identity.

## Context

Actual repeated failed-locale retry hits the unique audit operationId constraint because requestFailedTranslationRetry reuses the same run:retry identity. The transaction rolls back after the second genuine retry. Existing test covers only an immediate empty duplicate, not fail→retry→fail→retry. Preserve the database unique constraint and historical audit records.

## Scope

Existing translations/repository.ts retry action audit identity and focused unit/actual PostgreSQL regressions. Use a server-owned bounded unique identity for each actual nonempty serialized retry decision; no new cross-service contract.

## Out of Scope

Shared/schema/migration, provider output/parser changes, automatic retry policy changes, audit deletion/constraint relaxation, live retry/provider/database action, source merges/deploy or unrelated refactor.

## Requirements

Under the existing definition/run advisory transaction lock, each genuinely nonempty retry transition creates exactly one unique auditable operation identity within existing column bounds. Concurrent/immediate repeated clicks after that transition remain empty no-ops with no extra audit. A later legitimate failure of the same locale/run may be retried with a distinct audit event while preserving earlier audits. Keep source/model/credential/failure eligibility, retry counters/status, completed/reviewed locales and transaction rollback semantics unchanged. Audit insertion failure rolls back all retry changes. Never drop/relax the unique index, delete audits, manually reset provider/item state or recreate runs as workaround. Reuse existing server identifier facilities; no browser-supplied attempt authority or duplicate generic crypto mechanism.

## Work Items

- [ ] Reproduce fail/retry/fail/retry unique-audit rollback against existing code.
- [ ] Correct only server-owned retry-decision audit identity.
- [ ] Prove repeated/concurrent/no-op/rollback and completed-locale preservation, report and stop.

## Interfaces / Contracts

Existing Admin-only failed translation retry transaction and CommerceAuditEvent.operationId unique contract. Background batch processing and stored source hashes unchanged; no Shared release.

## Dependencies

ARCH-075-ADMIN-005

## Enables

ARCH-075-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Two legitimate nonempty retries of the same failed run/locale both commit distinct truthful audits.
- [ ] Concurrent/empty duplicate retry remains no-op, immutable completed results and all prior audits/unique constraint preserved.
- [ ] Canonical isolation and required passing checks reported, no live mutation.

## Validation

- [ ] Meaningful red/green actual PostgreSQL fail→retry→fail→retry, concurrent same cohort, empty replay, audit-failure rollback and completed locales unchanged.
- [ ] Relevant translation units/native ESM tests, types/lint/build/security and exact-head repository check evidence.
- [ ] Diff/privacy hygiene; no provider/database production writes.

## Stop Condition

After required scope/checks, submit review and STOP. Do not execute live repair, register providers, deploy, merge or begin follow-on tasks.

## Implementation Notes

You are not alone; preserve others. Canonical launcher packet owns startup/claim. Root owns all final integration and live operations. Generic logging uses published shared logging if changed. Return actual dependency gaps rather than inventing alternate protocol or local generic primitives.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

Existing eligible failed-item policy unchanged.

### Unresolved Issues

None currently.

### Architectural Concerns

Return concrete gaps before widening scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
