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
status: pending
priority: 12
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-DATABASE-001
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Persist recovery usage-compensation provenance

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Add the minimum durable billing provenance required for a later Background task to compensate one already-`COMMITTED` recovery reservation exactly once while preserving the original commit history and, for purchased credits, preserving the purchase/refund state that existed when the committed reservation consumed the credit.

This task is **persistence only**. It must not perform compensation, modify counters, create correction events, restore purchased credits, reopen refunds, or notify merchants.

## Context

ARCH-028 requires a definitively undelivered recovery not to ultimately consume merchant recovery capacity. The existing schema already supports negative correction lineage through `UsageEvent.correctionOfUsageEventId`, so ARCH-028 must reuse that mechanism rather than invent a second refund ledger.

A deeper source review after `ARCH-028-BACKGROUND-002` showed that correction lineage alone is insufficient to compensate every current capacity source deterministically.

For lifetime-free, paid-included and promotional capacity, later Background code can restore the committed quantity from the existing reservation source links.

Purchased credits have an additional valid race/lifecycle:

```text
purchase lot ACTIVE
    -> recovery reserves one credit
    -> merchant requests refund
    -> purchase becomes WITHDRAWN while the reservation remains RESERVED
    -> recovery send is provider-accepted
    -> reservation commits
    -> final reserved credit may move purchase WITHDRAWN -> COMPLETED
    -> live refund request(s) are cancelled as NO_CREDITS_REMAINING
    -> Meta later reports recipient-undeliverable
```

After that commit, the current schema no longer provides one authoritative relation proving:

- whether the purchase was `ACTIVE` or `WITHDRAWN` at commit time; or
- which live refund request rows were cancelled specifically because this reservation consumed the final reserved credits, nor what each refund status was immediately before that cancellation.

A later compensation task must not guess those facts from current purchase/refund state or from timestamps. DATABASE-002 records only that missing provenance plus the one-to-one compensation linkage.

## Scope

Modify only `moda-interact-database` files required for schema, migration, deterministic validation, disposable PostgreSQL rehearsal and generated ERD, plus this assigned parent task report.

Expected primary implementation files:

```text
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/<timestamp>_arch028_recovery_compensation_provenance/migration.sql
moda-interact-database/scripts/validate-arch028-recovery-compensation-schema.mjs
moda-interact-database/scripts/validate-arch028-recovery-compensation-migration.mjs
moda-interact-database/scripts/test-arch028-recovery-compensation-postgres.mjs
moda-interact-database/package.json
moda-interact-database/docs/generated/prisma-erd.puml
```

If another accepted database migration lands before execution, the ARCH-028 migration timestamp must sort after that accepted migration. Do not rewrite historical migrations.

### A. UsageReservation compensation evidence

Extend `billing.UsageReservation` with this logical optional state:

```prisma
compensationUsageEventId String? @unique
compensationUsageEvent   UsageEvent? @relation("CompensatedReservation", fields: [compensationUsageEventId], references: [id], onDelete: Restrict)
compensationReason       UsageReservationCompensationReason?
compensatedAt            DateTime?

purchasedCreditPurchaseStatusAtCommit RecoveryCreditPurchaseStatus?

refundCancellations UsageReservationRefundCancellation[]
```

Add the inverse optional one-to-one relation on `billing.UsageEvent` using the same relation name, for example:

```prisma
compensatedReservation UsageReservation? @relation("CompensatedReservation")
```

Exact Prisma field ordering may differ after formatting, but the logical fields/relations are architectural requirements.

Add one bounded enum:

```prisma
enum UsageReservationCompensationReason {
  WHATSAPP_RECIPIENT_UNDELIVERABLE

  @@schema("billing")
}
```

Do **not** add `COMPENSATED` to `UsageReservationStatus`. A compensated reservation remains historically `COMMITTED`; the compensation fields and negative correction event are the durable compensation evidence.

### B. Purchased-credit commit provenance

`purchasedCreditPurchaseStatusAtCommit` exists only so later Background code can restore the exact purchased-lot lifecycle after a delivery failure.

The later application implementation will populate it when a purchased-credit reservation transitions to `COMMITTED`, using the purchase status actually read/locked by that commit transaction.

DATABASE-002 must allow null for legacy/non-purchased reservations. Add migration-level integrity so any non-null value:

- requires `purchasedCreditPurchaseId IS NOT NULL`; and
- is one of the only two statuses that current purchased reservation commit accepts: `ACTIVE` or `WITHDRAWN`.

Do not backfill historical reservations by guessing the purchase status.

### C. Refund-cancellation provenance

Add a normalized billing model that records exactly which refund rows were cancelled by a particular purchased-credit reservation commit and the status of each row immediately before cancellation.

Logical shape:

```prisma
model UsageReservationRefundCancellation {
  usageReservationId String
  usageReservation   UsageReservation @relation(fields: [usageReservationId], references: [id], onDelete: Cascade)

  refundId String @unique
  refund   RecoveryCreditRefund @relation(fields: [refundId], references: [id], onDelete: Restrict)

  previousStatus RecoveryCreditRefundStatus
  createdAt      DateTime @default(now())

  @@id([usageReservationId, refundId])
  @@index([usageReservationId])
  @@schema("billing")
}
```

Add the inverse optional relation on `RecoveryCreditRefund` with a clear name such as:

```prisma
usageReservationCancellation UsageReservationRefundCancellation?
```

`previousStatus` is provenance, not a new refund status. Migration integrity must restrict it to the statuses the current purchased commit can cancel because no credits remain:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
```

Later Background implementation will create these provenance rows inside the same purchased-credit commit transaction immediately before/with the corresponding `NO_CREDITS_REMAINING` cancellation. DATABASE-002 itself does not alter that application code.

Add database integrity (trigger or equivalent deterministic mechanism) so a cancellation-provenance row is valid only when:

- the referenced UsageReservation has a non-null `purchasedCreditPurchaseId`;
- the referenced RecoveryCreditRefund belongs to that same purchase; and
- both reservation/refund belong to the same Shop through their existing relations.

Do not infer linkage by timestamps.

### D. Compensation linkage integrity

When later Background code sets `compensationUsageEventId`, the database must reject incoherent compensation links.

Add deterministic migration-level integrity so all of these hold whenever a compensation link is non-null:

1. `UsageReservation.status = COMMITTED`;
2. `committedUsageEventId IS NOT NULL`;
3. `compensationReason IS NOT NULL`;
4. `compensatedAt IS NOT NULL`;
5. the linked compensation UsageEvent belongs to the same Shop;
6. the linked compensation UsageEvent has `metric = RECOVERY_CONVERSATION`;
7. its `correctionOfUsageEventId` equals the reservation's `committedUsageEventId`;
8. its quantity equals the exact negative of the reservation quantity.

Conversely, enforce that `compensationUsageEventId`, `compensationReason` and `compensatedAt` are either all null or all non-null.

Do not require a particular provider-report state/event handle in the database. Paid-provider reporting provenance remains application-owned because non-paid recovery events are intentionally `NOT_APPLICABLE` while paid included recovery corrections must later reuse the original reportable usage context.

## Out of Scope

- Performing recovery compensation.
- Changing any recovery counter quantity.
- Creating any negative `UsageEvent` in application code.
- Releasing a COMMITTED reservation or adding a `COMPENSATED` reservation status.
- Changing existing `UsageEvent.correctionOfUsageEventId` semantics.
- Choosing correction event idempotency keys/sourceType/sourceId; owned by the later Background task, subject to the database integrity above.
- Publishing negative Shopify usage.
- Reopening or changing `RecoveryCreditRefund` application state.
- Changing purchased-credit refund policy.
- Recipient reachability/suppression updates; owned by later Background tasks.
- Merchant support/system notification.
- Shared/Messaging changes.
- `docs/architecture/_index.md` updates.

## Requirements

### R1 — Preserve original commit history

A compensated recovery reservation remains `UsageReservationStatus.COMMITTED` with its original `committedUsageEventId` unchanged.

Do not rewrite a committed reservation to `RELEASED` merely because later delivery failed.

### R2 — Exactly one durable compensation link

`compensationUsageEventId` is nullable and unique. One reservation may link to at most one compensation UsageEvent.

The compensation triplet (`compensationUsageEventId`, `compensationReason`, `compensatedAt`) is all-null or all-present.

### R3 — Compensation must be a true correction

The database must reject a linked compensation event that does not correct the exact original committed recovery UsageEvent with the exact negative reservation quantity for the same Shop and `RECOVERY_CONVERSATION` metric.

### R4 — Purchased-credit provenance is explicit

Do not make later compensation infer pre-commit purchased-lot state from the current `RecoveryCreditPurchase.status`.

Persist the status observed at commit (`ACTIVE` or `WITHDRAWN`) in the reservation when Background later implements the commit-path change.

### R5 — Refund cancellations are relational provenance

Do not store cancelled refund IDs in JSON and do not infer them from timestamps.

Use a normalized relation that records each refund row cancelled by the exact UsageReservation and its previous status.

### R6 — Additive rolling compatibility

All new reservation fields are nullable and the new provenance table starts empty. Existing Background code remains able to read/write existing reservation/refund rows before the later application task adopts the fields.

Do not add a migration constraint requiring current Background commit code to populate the new fields immediately on migration deployment.

### R7 — Existing billing semantics remain unchanged

DATABASE-002 does not modify:

- reservation admission;
- reserve/commit/release/ambiguous transitions;
- counter arithmetic;
- purchase/refund statuses;
- usage-event provider reporting;
- Shopify provider billing.

It only adds provenance/integrity needed by later implementation.

## Work Items

- [ ] Add `UsageReservationCompensationReason` with only `WHATSAPP_RECIPIENT_UNDELIVERABLE`.
- [ ] Add optional compensation linkage/reason/time to `UsageReservation` plus inverse UsageEvent relation.
- [ ] Add optional `purchasedCreditPurchaseStatusAtCommit` provenance.
- [ ] Add normalized `UsageReservationRefundCancellation` plus inverse refund/reservation relations.
- [ ] Add SQL constraints/triggers for compensation coherence and purchased/refund provenance ownership.
- [ ] Add one new ARCH-028 migration ordered after every accepted migration at execution time.
- [ ] Add deterministic schema validator coverage.
- [ ] Add deterministic migration validator coverage.
- [ ] Add disposable PostgreSQL fresh-install coverage.
- [ ] Add disposable PostgreSQL upgrade coverage proving existing reservations/refunds remain valid with null/empty provenance.
- [ ] Add PostgreSQL negative cases proving malformed correction links and cross-purchase refund provenance are rejected.
- [ ] Regenerate the Prisma ERD through the repository's normal workflow.
- [ ] Add only package scripts required to run the new ARCH-028 validators/rehearsals.

## Interfaces / Contracts

### Database owner

`ARCH-028-DATABASE-002`

### Durable compensation evidence

```text
UsageReservation.status = COMMITTED                 # remains historical truth
UsageReservation.committedUsageEventId              # original +1 usage
UsageReservation.compensationUsageEventId?           # exact linked correction
UsageReservation.compensationReason?                 # WHATSAPP_RECIPIENT_UNDELIVERABLE
UsageReservation.compensatedAt?
```

### Purchased compensation provenance

```text
UsageReservation.purchasedCreditPurchaseStatusAtCommit?
UsageReservationRefundCancellation(
  usageReservationId,
  refundId,
  previousStatus
)
```

### Later consumer expectations

The later Background compensation task may use these fields only after DATABASE-002 is Complete and architect-accepted.

DATABASE-002 does not create or alter an HTTP/queue/Shared runtime contract.

## Dependencies

- `ARCH-028-DATABASE-001`

DATABASE-001 must be Complete before DATABASE-002 starts so ARCH-028 database migrations remain a single ordered accepted frontier in `moda-interact-database`.

## Enables

None yet.

The later Background compensation task will be defined iteratively after DATABASE-002 is accepted/available in the architecture frontier and will add its dependency explicitly.

## Acceptance Criteria

- [ ] A COMMITTED reservation can link to at most one compensation UsageEvent without changing its original status/committed event.
- [ ] Compensation link/reason/time are enforced as all-null or all-present.
- [ ] The database rejects compensation linking for non-COMMITTED reservations.
- [ ] The database rejects compensation events that do not correct the exact committed event with exact negative quantity, same Shop and RECOVERY_CONVERSATION metric.
- [ ] `purchasedCreditPurchaseStatusAtCommit` is nullable for compatibility but, when populated, requires a purchased-credit reservation and is limited to ACTIVE/WITHDRAWN.
- [ ] Refund-cancellation provenance is normalized and cannot point across purchase/shop ownership.
- [ ] Refund-cancellation `previousStatus` is limited to REQUESTED/PROVIDER_ACTION_REQUIRED.
- [ ] Existing reservations/refunds migrate with null/empty provenance and no invented compensation state.
- [ ] No counter, purchase/refund status, reservation transition or provider-reporting semantics change.
- [ ] Fresh and upgrade disposable PostgreSQL rehearsals pass.
- [ ] Prisma validation/generation, architecture-specific validators and ERD generation pass.

## Validation

Required validation categories:

- [ ] inspect current `package.json` and use the repository-declared database commands;
- [ ] Prisma format/validate/generate through the repository's normal scripts;
- [ ] ARCH-028 compensation schema validator;
- [ ] ARCH-028 compensation migration validator;
- [ ] disposable PostgreSQL fresh migration rehearsal;
- [ ] disposable PostgreSQL upgrade rehearsal from the exact pre-DATABASE-002 accepted migration frontier;
- [ ] SQL/catalog positive assertions for enum/columns/relations/indexes/constraints/triggers;
- [ ] SQL/catalog negative assertions for malformed compensation links and cross-purchase refund provenance;
- [ ] `npm run erd:puml` (or current repository equivalent) and generated-ERD review;
- [ ] `git diff --check`;
- [ ] changed-file inspection proving no historical migration or unrelated billing semantics changed.

Do not invent lint/typecheck commands that the database repository does not declare.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, clear execution claim fields as required by the task workflow, return control to `moda_architect` and STOP.

Do not implement Background compensation from this task.

## Implementation Notes

- This task exists because post-ARCH-028 source review proved that the existing generic correction relation is sufficient for correction lineage but not sufficient to reconstruct purchased-credit/refund provenance after a final reserved WITHDRAWN credit is consumed.
- Prefer additive nullable fields plus one normalized provenance model. Do not redesign the reservation/refund subsystem.
- Do not add `COMPENSATED` to `UsageReservationStatus`.
- Do not infer pre-commit purchase/refund state during migration.
- Compensation/reporting policy stays in Background; database integrity only ensures a linked compensation is structurally the exact correction of the committed recovery usage.

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

- ARCH-028 remains in pre-production/additive rollout and existing rows may legitimately have null provenance.
- Current purchased commit accepts only ACTIVE/WITHDRAWN purchase rows and only cancels REQUESTED/PROVIDER_ACTION_REQUIRED refunds as `NO_CREDITS_REMAINING`.

### Unresolved Issues

- Exact Background compensation transaction/order remains intentionally deferred to the later Background task.
- Exact merchant notification wording and suppression TTL remain later ARCH-028 decisions.

### Architectural Concerns

None at definition time beyond the purchased-credit provenance gap this task resolves.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

After acceptance, define/reconcile the Background compensation task against the accepted schema and then-current reservation services.
