---
id: ARCH-028-DATABASE-003
architecture_id: ARCH-028
title: Persist exact recovery outreach recipient
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 13
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-DATABASE-001
enables:
  - ARCH-028-BACKGROUND-005
created: 2026-10-07
updated: 2026-10-08
---

# Persist exact recovery outreach recipient

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Add the strict required canonical recipient snapshot to `RecoveryOutreachAttempt` as a separate database gate so the later Background reachability task can update all attempt-creation paths atomically with adopting this database revision.

## Context

ARCH-028 needs the exact destination used by each recovery attempt for `(shopId, recipient)` reachability. Putting the required field in DATABASE-001 would make BACKGROUND-001 consume a Prisma model that existing attempt-creation code cannot satisfy. This bounded database task preserves strict pre-production invariants without nullable legacy accommodation.

## Scope

Add required:

```prisma
model RecoveryOutreachAttempt {
  recipient String @db.VarChar(64)
}
```

Migration/database constraints require canonical digits-only, non-empty, maximum 64 characters.

ARCH-028 is pre-production: no backfill/default/nullable compatibility mechanism is required. Fresh migration validation is authoritative; development databases with incompatible rows may be reset.

## Out of Scope

- Candidate pre-materialisation recipient prerequisite (BACKGROUND-007).
- Runtime attempt-recipient persistence (BACKGROUND-005).
- Conversation/ConversationMessage recipient fields.
- Customer identity redesign.
- Reachability runtime logic.
- Legacy backfill/upgrade compatibility.

## Requirements

- [ ] `RecoveryOutreachAttempt.recipient` is required.
- [ ] Stored value is digits-only, non-empty and <=64 chars.
- [ ] No default empty value or nullable compatibility escape hatch is introduced.
- [ ] Existing database consumers need not adopt this gitlink until their runtime task is ready to populate the field.

## Work Items

- [ ] Add required field and SQL integrity.
- [ ] Add schema/migration validator.
- [ ] Run fresh disposable PostgreSQL migration rehearsal.
- [ ] Regenerate ERD.

## Interfaces / Contracts

Consumed by `ARCH-028-BACKGROUND-005` for mandatory per-attempt snapshots. BACKGROUND-007 independently resolves the pre-materialisation recipient before this breaking field is adopted.

## Dependencies

- `ARCH-028-DATABASE-001`

## Enables

- `ARCH-028-BACKGROUND-005`

## Acceptance Criteria

- [ ] Fresh schema enforces required canonical recipient.
- [ ] No Conversation/ConversationMessage recipient field is added.
- [ ] No legacy/backfill compatibility is added.
- [ ] Prisma/schema/migration/PostgreSQL/ERD validation passes.

## Validation

Use repository-declared format/Prisma/schema/migration/PostgreSQL/ERD commands plus `git diff --check`; fresh-database correctness is required.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

This split is an execution/deployment compatibility boundary, not a relaxation of the final invariant. BACKGROUND-005 must adopt this exact database revision while changing all recovery attempt creation paths to provide the recipient.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

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

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
