---
id: ARCH-028-DATABASE-001
architecture_id: ARCH-028
title: Persist WhatsApp failure and recipient reachability policy state
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
  - ARCH-028-DATABASE-002
  - ARCH-028-DATABASE-003
  - ARCH-028-ADMIN-001
  - ARCH-028-BACKGROUND-001
created: 2026-10-03
updated: 2026-10-07
---

# Persist WhatsApp failure and recipient reachability policy state

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Add the strict pre-production persistence required for bounded WhatsApp provider-failure evidence, Shop-scoped temporary reachability suppression, the default/configurable suppression duration, and recovery admission-block reasons without yet changing recovery-attempt creation contracts.

## Context

ARCH-028 associates provider delivery failure with the exact Shop/recovery through existing `providerMessageId -> ConversationMessage -> RecoveryOutreachAttempt -> CheckoutRecovery` relations. Phone numbers are therefore not used to infer Shop ownership.

This initiative is pre-production. No legacy-row/backfill compatibility is required.

## Scope

Modify `moda-interact-database` schema/migration/validators/tests/ERD as required.

### ConversationMessage failure evidence

Add:

```prisma
providerFailureCode String? @db.VarChar(64)
failedAt            DateTime?
```

A non-null code is trimmed/non-empty/bounded and requires `failedAt`. Not every FAILED message must carry provider evidence.

### Recovery admission block reasons

Extend:

```prisma
enum RecoveryAdmissionBlockReason {
  RECOVERY_CAPACITY_EXHAUSTED
  WHATSAPP_RECIPIENT_SUPPRESSED
  NO_WHATSAPP_RECIPIENT
}
```

### Tenant-scoped reachability

Add:

```prisma
model WhatsAppRecipientReachability {
  id String @id @default(cuid())
  shopId String
  shop Shop @relation(fields: [shopId], references: [id], onDelete: Cascade)
  recipient String @db.VarChar(64)
  lastProviderFailureCode String? @db.VarChar(64)
  lastFailureAt DateTime?
  suppressUntil DateTime?
  lastSuccessfulAt DateTime?
  version Int @default(0)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  @@unique([shopId, recipient])
  @@index([shopId, suppressUntil])
  @@schema("whatsapp")
}
```

Add the corresponding collection relation on `Shop`.

### Platform suppression policy

Extend `billing.PlatformBillingPolicy` with:

```prisma
whatsappRecipientSuppressionDays Int @default(7)
```

Migration/database validation must require a positive value. The policy is platform-level; no per-Shop override is introduced by ARCH-028.

### Integrity

Require canonical digits-only recipient values and bounded provider codes. A non-null `suppressUntil` requires failure evidence and must be later than `lastFailureAt`.

## Out of Scope

- Provider-code classification.
- Shared/Messaging runtime contract work.
- Recovery compensation implementation.
- Admin UI implementation.
- Suppression/pre-admission runtime implementation.
- Synchronous provider rejection handling.
- Missing-phone runtime handling.
- Merchant notification.
- New Customer/Conversation recipient relationship.
- Historical/legacy data backfill or upgrade compatibility.
- Provider monetary refund state.

## Requirements

- [ ] The same recipient may appear in many Shops; reachability uniqueness is `(shopId, recipient)` only.
- [ ] `ConversationMessage` failure evidence is bounded and raw provider payload/text is not stored.
- [ ] Suppression is finite evidence, not a permanent unreachability state.
- [ ] `whatsappRecipientSuppressionDays` defaults to `7` and must be positive.
- [ ] New block reasons support suppression and no-recipient preprocessing.
- [ ] No Conversation/Customer phone ownership redesign is introduced.

## Work Items

- [ ] Add message failure fields and constraints.
- [ ] Extend recovery admission-block enum.
- [ ] Add Shop-scoped reachability model, relation, unique/indexes and integrity constraints.
- [ ] Add `PlatformBillingPolicy.whatsappRecipientSuppressionDays` default `7` and positive constraint.
- [ ] Add architecture-specific schema/migration validation.
- [ ] Add fresh disposable PostgreSQL migration rehearsal.
- [ ] Regenerate ERD.

## Interfaces / Contracts

Persistence consumed by later ARCH-028 Background/Admin tasks:

```text
ConversationMessage.providerFailureCode / failedAt
WhatsAppRecipientReachability(shopId, recipient)
PlatformBillingPolicy.whatsappRecipientSuppressionDays
RecoveryAdmissionBlockReason.{WHATSAPP_RECIPIENT_SUPPRESSED,NO_WHATSAPP_RECIPIENT}
```

## Dependencies

None.

## Enables

- `ARCH-028-DATABASE-002`
- `ARCH-028-DATABASE-003`
- `ARCH-028-ADMIN-001`
- `ARCH-028-BACKGROUND-001`

## Acceptance Criteria

- [ ] Fresh schema contains all required fields/models/enums/defaults/indexes/constraints.
- [ ] Same phone number is independently representable for different Shops.
- [ ] Suppression duration default is exactly seven days.
- [ ] No permanent recipient-unreachable boolean/enum is introduced.
- [ ] No raw Meta error payload/text field is introduced.
- [ ] No legacy/backfill migration machinery is introduced.
- [ ] Prisma validation/generation, architecture validators, PostgreSQL fresh rehearsal, ERD and `git diff --check` pass.

## Validation

Use repository-declared format/Prisma/schema/migration/PostgreSQL/ERD commands after inspecting the current `package.json`, plus `git diff --check`. Fresh-database migration correctness is required; a backwards-compatible upgrade rehearsal is not an ARCH-028 requirement.

## Stop Condition

Complete the report, set `status: review`, return to `moda_architect` and STOP.

## Implementation Notes

Do not add a recipient field to `Conversation` or `ConversationMessage`. The strict recovery-attempt recipient snapshot is owned by DATABASE-003 so BACKGROUND-001 can consume DATABASE-001 without prematurely breaking existing attempt-creation call sites.

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
