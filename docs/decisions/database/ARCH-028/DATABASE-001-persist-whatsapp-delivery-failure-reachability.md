---
id: ARCH-028-DATABASE-001
architecture_id: ARCH-028
title: Persist WhatsApp delivery-failure and recipient reachability evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-028-BACKGROUND-001
  - ARCH-028-DATABASE-002
created: 2026-10-03
updated: 2026-10-03
---

# Persist WhatsApp delivery-failure and recipient reachability evidence

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Add the minimum durable database state required for later ARCH-028 Messaging/Background work to preserve bounded WhatsApp delivery-failure evidence and maintain tenant-scoped recipient reachability/suppression state.

This task is **persistence only**. It must not implement provider-error classification, webhook normalization, recovery compensation, follow-up suppression or merchant notification.

## Context

`whatsapp.ConversationMessage` currently stores provider message identity and lifecycle timestamps (`sentAt`, `deliveredAt`, `readAt`) but no durable provider-failure code/time.

The platform also has no durable tenant-scoped record stating that a particular WhatsApp recipient is currently reachable or has been classified as terminally undeliverable for proactive messaging.

ARCH-028 needs those durable facts before Messaging and Background can safely converge asynchronous `FAILED` statuses. The persistence must remain conservative: one provider failure must not become a permanent `customer.hasWhatsApp = false` assertion.

The current billing schema already supports correction lineage through `UsageEvent.correctionOfUsageEventId`. This task therefore does not add compensation/refund fields to `UsageReservation` or create another usage-correction model.

## Scope

Modify only `moda-interact-database` files required for the schema, migration, validation, disposable PostgreSQL rehearsal and generated ERD, plus this assigned parent task report.

Expected primary implementation files:

```text
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/<timestamp>_arch028_whatsapp_delivery_failure_reachability/migration.sql
moda-interact-database/scripts/validate-arch028-whatsapp-delivery-failure-schema.mjs
moda-interact-database/scripts/validate-arch028-whatsapp-delivery-failure-migration.mjs
moda-interact-database/scripts/test-arch028-whatsapp-delivery-failure-postgres.mjs
moda-interact-database/package.json
moda-interact-database/docs/generated/prisma-erd.puml
```

If another accepted database migration lands before this task is executed, the ARCH-028 migration timestamp must sort after that accepted migration. Do not rewrite historical migrations.

### A. ConversationMessage failure evidence

Add exactly these logical nullable fields to `whatsapp.ConversationMessage`:

```prisma
providerFailureCode String?   @db.VarChar(64)
failedAt            DateTime?
```

Formatting/order may differ after Prisma formatting, but names, nullability and bounded code storage are architectural requirements.

`providerFailureCode` stores a bounded normalized provider error code (for example a Meta numeric code represented as text). It is **not** a free-form provider message/body field.

`failedAt` stores the provider failure occurrence time when known.

Do not backfill existing FAILED messages with invented timestamps or error codes.

Add deterministic migration constraints so a non-null `providerFailureCode`:

- is non-empty after trimming;
- is at most 64 characters;
- requires `failedAt IS NOT NULL`.

Do **not** require every existing/future `MessageStatus.FAILED` row to have a provider failure code. Moda-originated or legacy failures may legitimately lack provider evidence.

### B. Tenant-scoped recipient reachability evidence

Add a new `whatsapp.WhatsAppRecipientReachability` model with this logical shape:

```prisma
model WhatsAppRecipientReachability {
  id String @id @default(cuid())

  shopId String
  shop   Shop   @relation(fields: [shopId], references: [id], onDelete: Cascade)

  recipient String @db.VarChar(64)

  lastProviderFailureCode String? @db.VarChar(64)
  lastFailureAt           DateTime?
  suppressUntil           DateTime?
  lastSuccessfulAt        DateTime?
  version                 Int       @default(0)

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([shopId, recipient])
  @@index([shopId, suppressUntil])
  @@schema("whatsapp")
}
```

This row stores **evidence and a temporary suppression window**, not a permanent current-state assertion.

There is deliberately no durable `UNDELIVERABLE` status. A person who is unreachable on WhatsApp today may become reachable tomorrow.

Effective application semantics for later tasks are:

```text
suppressUntil > now
    -> temporarily suppress proactive WhatsApp recovery sends

suppressUntil <= now (or null)
    -> no active suppression; do not infer permanent unreachability

new successful delivery or inbound WhatsApp evidence
    -> record lastSuccessfulAt
    -> clear active suppression
```

The row may retain historical failure evidence after suppression expires. Expired failure evidence is not authority to keep suppressing sends.

Absence of a reachability row remains UNKNOWN.

Add the corresponding collection relation on shared `commerce.Shop` using a clear plural relation field such as:

```prisma
whatsappRecipientReachabilities WhatsAppRecipientReachability[]
```

The model is keyed by **Shop + recipient**, not Customer. Provider reachability applies to the WhatsApp destination that was actually used, while Customer/CustomerPhone identity may evolve independently.

`recipient` is the canonical/bounded recipient string supplied by later application code. DATABASE-001 does not define E.164 normalization or provider-specific phone parsing.

### C. Reachability evidence integrity constraints

The migration must enforce:

1. `recipient` is trimmed, non-empty and at most 64 characters;
2. non-null `lastProviderFailureCode` is trimmed/non-empty, bounded to 64 characters and requires `lastFailureAt IS NOT NULL`;
3. non-null `suppressUntil` requires `lastFailureAt IS NOT NULL`;
4. when `suppressUntil` is non-null, it must be later than `lastFailureAt`.

Do not add a database constraint or enum state that permanently classifies a recipient as unreachable.

DATABASE-001 must permit the same row to retain historical failure evidence while later application code clears suppression and records newer successful evidence.

## Out of Scope

- Extending `NormalizedWhatsAppStatusSchema`; owned by a later Shared task.
- Parsing Meta `statuses[].errors`; owned by a later Messaging task.
- Provider failure classification (terminal-recipient vs temporary/configuration/ambiguous).
- Synchronous send-error classification.
- Changing `ConversationMessage.status` transition logic.
- Updating `RecoveryOutreachAttempt`, `CheckoutRecovery` or follow-up state.
- Releasing or compensating recovery usage/capacity.
- Adding `UsageReservation` compensation status/fields.
- Adding a second usage-correction table; existing `UsageEvent.correctionOfUsageEventId` must be assessed first.
- Writing Merchant Support notifications.
- Recipient suppression policy/TTL value; later application work must choose a finite duration.
- E.164 normalization or permanent `Customer.hasWhatsApp` state.
- Removing or rewriting historical migrations.

## Requirements

### R1 — Failure evidence is bounded

Persist only bounded provider failure code/time on `ConversationMessage`. Do not add raw webhook/error payload storage.

### R2 — Reachability is evidence, not a permanent assertion

Do not introduce `Customer.hasWhatsApp`, a durable `UNDELIVERABLE` enum state, or an equivalent permanent boolean/classification.

A missing reachability row means unknown. An existing row with an expired or null `suppressUntil` does **not** mean the recipient is still unreachable.

### R3 — Reachability is tenant scoped

The same recipient may have independent reachability state for different Shops. Enforce uniqueness on `(shopId, recipient)`.

### R4 — Reachability can recover without destructive history

The schema must support a recipient being temporarily suppressed after a failure, later becoming eligible again after suppression expires, and later receiving positive success/inbound evidence without deleting the row or erasing historical failure evidence.

### R5 — Suppression is finite application policy

Persist optional `suppressUntil`, but do not hard-code suppression duration in the database. Later application tasks must choose a finite suppression window.

Once `suppressUntil` has expired, the database row must not by itself authorize continued suppression.

### R6 — Billing schema remains unchanged

Do not change `UsageReservation`, entitlement counters, recovery-credit purchases/refunds or usage correction semantics in DATABASE-001.

### R7 — Existing data remains valid

The migration is additive. Existing ConversationMessage/Shop rows remain valid with null failure evidence and no reachability rows.

## Work Items

- [ ] Add bounded provider failure code/time fields to `ConversationMessage`.
- [ ] Add tenant-scoped `WhatsAppRecipientReachability` and the Shop relation.
- [ ] Add unique/index/SQL check constraints for recipient, bounded failure evidence and temporary suppression invariants.
- [ ] Add one new ARCH-028 migration ordered after every migration accepted before task execution.
- [ ] Add deterministic schema validator coverage.
- [ ] Add deterministic migration validator coverage.
- [ ] Add disposable PostgreSQL fresh-install coverage.
- [ ] Add disposable PostgreSQL upgrade coverage proving existing message/shop rows remain valid and no evidence is invented.
- [ ] Regenerate the Prisma ERD through the repository's normal workflow.
- [ ] Add only the package scripts required to run the new ARCH-028 validators/rehearsals.

## Interfaces / Contracts

### Database owner

`ARCH-028-DATABASE-001`

### Durable message evidence

```text
whatsapp.ConversationMessage.providerFailureCode
whatsapp.ConversationMessage.failedAt
```

### Durable reachability

```text
whatsapp.WhatsAppRecipientReachability
UNIQUE(shopId, recipient)

active suppression is derived from:
suppressUntil > application current time
```

### Consumer expectations

Later Messaging/Background tasks may consume these fields/models only after this task is Complete and architect-accepted.

No HTTP, queue or Shared-package runtime contract is created by DATABASE-001.

## Dependencies

None.

DATABASE-001 is additive and can be implemented independently of the later ARCH-028 runtime tasks. If another architecture's database task is already in progress when this task is prepared, do not execute two schema/migration tasks in the same physical implementation worktree; report the concurrent database frontier to `moda_architect` for sequencing/rebase guidance.

## Enables

- `ARCH-028-BACKGROUND-001`
- `ARCH-028-DATABASE-002`

BACKGROUND-001 also depends on the published Shared contract from `ARCH-028-SHARED-002`. It becomes executable only after both prerequisites are Complete.

## Acceptance Criteria

- [ ] `ConversationMessage` has nullable bounded `providerFailureCode` and `failedAt` fields.
- [ ] Existing FAILED messages are not backfilled with invented provider evidence.
- [ ] Non-null message `providerFailureCode` requires a failure timestamp and passes trim/bound checks.
- [ ] `WhatsAppRecipientReachability` is persisted in PostgreSQL schema `whatsapp`.
- [ ] Reachability is unique per `(shopId, recipient)` and cascades with Shop deletion.
- [ ] Missing reachability row remains the representation of UNKNOWN.
- [ ] A non-null `suppressUntil` requires failure evidence and is strictly later than `lastFailureAt`.
- [ ] There is no durable permanent-unreachable status/boolean.
- [ ] An expired or null `suppressUntil` does not encode continuing suppression.
- [ ] The same row can later record `lastSuccessfulAt` and clear suppression while retaining historical failure evidence.
- [ ] No raw Meta/webhook error body field is introduced.
- [ ] No billing/UsageReservation/usage-correction schema is changed.
- [ ] Fresh disposable PostgreSQL migration rehearsal succeeds.
- [ ] Upgrade rehearsal from the pre-ARCH-028 schema succeeds and preserves representative existing ConversationMessage/Shop rows.
- [ ] Prisma validation/client generation, architecture-specific validators and ERD generation pass.

## Validation

Required validation categories for this task:

- [ ] `npm run format` (then verify no unintended formatting churn);
- [ ] `npm run validate` / `npm run prisma:validate`;
- [ ] `npm run prisma:generate`;
- [ ] architecture-specific schema validator;
- [ ] architecture-specific migration validator;
- [ ] disposable PostgreSQL fresh migration rehearsal;
- [ ] disposable PostgreSQL upgrade rehearsal from the exact pre-ARCH-028 migration state;
- [ ] SQL/catalog assertions for enum/table/columns/unique/index/check constraints;
- [ ] `npm run erd:puml` and generated-ERD review;
- [ ] `git diff --check`;
- [ ] changed-file inspection proving no historical migration or unrelated billing schema changed.

The implementing agent must inspect the current `package.json` before running validation and use the commands actually declared by the repository. A missing generic lint/typecheck script is not itself a validation failure.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, clear the execution claim as required by the normal task workflow, return control to `moda_architect` and STOP.

Do not begin Shared, Messaging, Background or compensation work from this task.

## Implementation Notes

- Prefer one additive migration for DATABASE-001.
- Do not manufacture failure timestamps/codes for legacy rows.
- Do not bind recipient storage to `Customer` identity; use the provider destination string scoped by Shop.
- Do not introduce a closed provider-error enum in the database. Error-code classification belongs in application/runtime architecture.
- Do not add compensation persistence inside DATABASE-001. `ARCH-028-DATABASE-002` separately records only the additional provenance proven necessary after source review; existing `UsageEvent.correctionOfUsageEventId` remains the correction lineage mechanism.
- `version` exists to support bounded optimistic/concurrent reachability updates later; DATABASE-001 does not define the updater algorithm.
- `lastFailureAt` / `lastProviderFailureCode` are historical evidence. They must not be interpreted as an indefinite block once `suppressUntil` expires.
- Later positive evidence should clear active suppression rather than deleting the row; historical failure evidence may remain for audit/diagnostics.

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

- The current Prisma schema and accepted migrations in the prepared task worktree are authoritative at execution time.
- Later runtime tasks will supply already-normalized/bounded recipient and failure-code values.

### Unresolved Issues

- Exact failure-code classification is intentionally deferred to later ARCH-028 runtime tasks.
- A later source review resolved the compensation-schema question: generic correction lineage is reusable, but purchased-credit/refund provenance requires the separate `ARCH-028-DATABASE-002` task.

### Architectural Concerns

None at definition time.

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

After acceptance, define the next ARCH-028 task iteratively from the then-current codebase.
