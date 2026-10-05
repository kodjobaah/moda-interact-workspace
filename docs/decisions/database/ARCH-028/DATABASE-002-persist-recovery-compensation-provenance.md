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
enables:
  - ARCH-028-BACKGROUND-004
created: 2026-10-03
updated: 2026-10-05
---

# Persist recovery usage-compensation provenance

## Objective

Add only the durable evidence required to compensate one already-`COMMITTED` recovery reservation exactly once without rewriting its original commit history.

ARCH-028 no longer stores refund-cancellation provenance for compensation. ARCH-027 owns provider monetary refunds; delivery compensation must never reopen/reconstruct a refund from old monetary state.

## Scope

Extend `billing.UsageReservation` with:

```prisma
compensationUsageEventId String? @unique
compensationUsageEvent   UsageEvent? @relation("CompensatedReservation", fields: [compensationUsageEventId], references: [id], onDelete: Restrict)
compensationReason       UsageReservationCompensationReason?
compensationDisposition  UsageReservationCompensationDisposition?
compensatedAt            DateTime?
```

Add inverse one-to-one relation on `UsageEvent`.

Enums:

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

## Option A — expired/terminal source policy

ARCH-028 v1 deliberately chooses the simplest cross-period rule:

```text
original capacity source still spendable
    -> restore the exact original source
    -> RESTORED_SPENDABLE

original purchased lot currently held by a live refund
    -> correct usage but keep the restored quantity unavailable in that refund hold
    -> HELD_FOR_REFUND

original source expired/closed/terminal
    -> correct historical accounting only
    -> create no make-good credit in another source/period
    -> HISTORICAL_ONLY
```

No delivery-compensation credit bucket is added.

## Compensation linkage integrity

When compensation fields are present require all of:

1. reservation status = COMMITTED;
2. original `committedUsageEventId` non-null;
3. reason/disposition/compensatedAt non-null;
4. linked correction UsageEvent belongs to same Shop;
5. metric = RECOVERY_CONVERSATION;
6. `correctionOfUsageEventId = committedUsageEventId`;
7. correction quantity = exact negative reservation quantity.

Conversely all compensation fields are null together or present together.

Do not constrain Shopify reporting fields in SQL; application code derives reporting from the original UsageEvent/provider context.

## Explicitly removed from the prior draft

Do **not** add:

```text
purchasedCreditPurchaseStatusAtCommit
UsageReservationRefundCancellation
refundCancellations relation
```

The final ARCH-027 refund model has one durable refund attempt per purchase and current refund/purchase state is authoritative for compensation. ARCH-028 never reconstructs monetary-refund history from a WhatsApp delivery failure.

## Out of Scope

- Compensation transaction/counter changes.
- New make-good entitlement bucket.
- Provider monetary refunds.
- Refund reactivation/reopening.
- Recipient suppression/notification.
- Shared/Messaging changes.
- `docs/architecture/_index.md`.

## Requirements

### R1 — Preserve commit history

Reservation stays COMMITTED and original positive UsageEvent remains unchanged.

### R2 — Exactly one correction

`compensationUsageEventId` is nullable+unique; one reservation has at most one compensation.

### R3 — Durable disposition

Persist `RESTORED_SPENDABLE`, `HELD_FOR_REFUND` or `HISTORICAL_ONLY` so later merchant notification does not need to infer whether usable capacity was actually restored.

### R4 — True correction integrity

Reject malformed/cross-Shop/non-negative/wrong-source compensation links.

### R5 — Additive migration

Existing rows migrate with null compensation fields; no history is invented.

### R6 — No refund provenance

Do not add purchased pre-commit/refund-cancellation provenance to ARCH-028.

## Work Items

- [ ] Add compensation reason/disposition enums.
- [ ] Add optional compensation link/reason/disposition/time and inverse UsageEvent relation.
- [ ] Add all-null/all-present and exact-correction SQL integrity.
- [ ] Add migration/schema validators and fresh+upgrade pgvector PostgreSQL rehearsals.
- [ ] Regenerate ERD.
- [ ] Prove no refund/purchased-provenance model is introduced.

## Dependencies

- `ARCH-028-DATABASE-001`

## Enables

- `ARCH-028-BACKGROUND-004`

## Acceptance Criteria

- [ ] One COMMITTED reservation can link to at most one exact negative correction.
- [ ] Reason/disposition/time/link are atomic presence.
- [ ] Correction exact quantity/shop/metric/original-event lineage is enforced.
- [ ] Existing rows remain valid with null compensation.
- [ ] No purchased/refund-cancellation provenance is added.
- [ ] No make-good capacity bucket exists.
- [ ] Fresh/upgrade migration rehearsals pass.

## Validation

Use repository-declared Prisma/schema/migration/postgres/ERD commands plus `git diff --check`.

## Stop Condition

Complete report -> review -> return to `moda_architect` -> STOP.

## Completion Report

### Status

Not Started

## Architect Review

### Review Status

Pending
