---
id: ARCH-028-DATABASE-002
architecture_id: ARCH-028
title: Persist recovery usage-compensation provenance
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 12
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-03
updated: 2026-10-08
---

# Persist recovery usage-compensation provenance

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

**Superseded on 2026-10-08 by ARCH-028-DATABASE-001. Do not execute this task.** Its schema fields, exact-correction integrity, acceptance criteria and fresh-PostgreSQL validation have been transferred to DATABASE-001 so both additive persistence changes use one coherent pre-production migration.

Originally intended to persist exactly one auditable correction link/disposition for an already-COMMITTED recovery reservation without rewriting its original commit history or introducing provider monetary refund state.

## Context

A still-RESERVED recovery is released and needs no negative UsageEvent. A COMMITTED recovery retains the original positive event and receives one exact negative correction. Committed purchased-credit compensation is implemented later by BACKGROUND-009, but uses the same generic provenance.

ARCH-028 is pre-production; no legacy-row migration compatibility is required.

## Scope

Extend `billing.UsageReservation` with:

```prisma
compensationUsageEventId String? @unique
compensationUsageEvent   UsageEvent? @relation("CompensatedReservation", fields: [compensationUsageEventId], references: [id], onDelete: Restrict)
compensationReason       UsageReservationCompensationReason?
compensationDisposition  UsageReservationCompensationDisposition?
compensatedAt            DateTime?
```

Add inverse UsageEvent relation and:

```prisma
enum UsageReservationCompensationReason {
  WHATSAPP_RECIPIENT_UNDELIVERABLE
  @@schema("billing")
}

enum UsageReservationCompensationDisposition {
  RESTORED_SPENDABLE
  HELD_FOR_REFUND
  HISTORICAL_ONLY
  @@schema("billing")
}
```

A compensated reservation remains `COMMITTED`.

## Out of Scope

- Counter/source compensation implementation.
- RESERVED release persistence beyond existing reservation status.
- Provider monetary refunds or reopening refund attempts.
- Recipient suppression/notification.
- Purchased pre-commit/refund-cancellation provenance.
- Legacy/backfill compatibility.

## Requirements

- [ ] Preserve original COMMITTED reservation and positive UsageEvent.
- [ ] Permit at most one correction UsageEvent per reservation.
- [ ] Compensation fields are all-null or all-present.
- [ ] Linked correction is same Shop, `RECOVERY_CONVERSATION`, exact negative quantity and `correctionOfUsageEventId = committedUsageEventId`.
- [ ] Persist `RESTORED_SPENDABLE`, `HELD_FOR_REFUND` or `HISTORICAL_ONLY`.
- [ ] No provider refund provenance/model is added.

## Work Items

- [ ] Add reason/disposition enums.
- [ ] Add compensation link/reason/disposition/time and inverse relation.
- [ ] Add exact-correction integrity validation.
- [ ] Add fresh migration/schema/PostgreSQL validation and regenerate ERD.

## Interfaces / Contracts

Consumed by `ARCH-028-BACKGROUND-004` and `ARCH-028-BACKGROUND-009`.

## Dependencies

None; superseded task is not executable.

## Enables

None; BACKGROUND-004 now depends on DATABASE-001.

## Acceptance Criteria

- [ ] One COMMITTED reservation links to at most one exact negative correction.
- [ ] Reason/disposition/time/link presence is atomic.
- [ ] Cross-Shop/wrong-metric/wrong-original/non-negative correction is rejected.
- [ ] No purchased/refund-cancellation provenance or make-good bucket is added.
- [ ] Fresh migration/schema validation passes.

## Validation

Use repository-declared Prisma/schema/migration/PostgreSQL/ERD commands plus `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not require current Subscription state to identify the compensated source. Source authority remains the original `UsageReservation`/UsageEvent linkage.

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

Superseded before implementation; scope preserved in DATABASE-001. No acceptance or implementation claim is made.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
