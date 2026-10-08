---
id: ARCH-028-DATABASE-001
architecture_id: ARCH-028
title: Persist WhatsApp failure, recipient reachability and compensation provenance
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: copilot
claimed_at: 2026-10-08T13:49:15Z
attempt: 1
depends_on:
  - ARCH-027-DATABASE-001
enables:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-DATABASE-003
  - ARCH-028-ADMIN-001
  - ARCH-028-BACKGROUND-001
created: 2026-10-03
updated: 2026-10-08
---

# Persist WhatsApp failure, recipient reachability and compensation provenance

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Add one coherent pre-production migration for bounded provider-failure evidence, Shop-scoped recipient reachability/suppression, platform suppression duration, recovery admission-block reasons and exact committed-recovery compensation provenance. Do not change recovery-attempt creation contracts in this task.

## Context

ARCH-028 associates provider delivery failure with the exact Shop/recovery through existing `providerMessageId -> ConversationMessage -> RecoveryOutreachAttempt -> CheckoutRecovery` relations. Phone numbers are therefore not used to infer Shop ownership.

This initiative is pre-production. No legacy-row/backfill compatibility is required. Former DATABASE-002 (compensation provenance) is consolidated here; it is superseded without losing its original contract. DATABASE-003 remains independent because its mandatory attempt-recipient field changes Background write inputs.

**Canonical database baseline:** architect-accepted `ARCH-027-DATABASE-001` is already Complete and introduces provider-neutral Woo billing persistence. Start from the database repository's integrated accepted migration/schema (including `BillingOperation`, Woo provider receipts, `Subscription.providerCoverageEndAt` and `BillingPeriodEntitlementCounter.currentAllowanceQuantity`); do not generate ARCH-028 against the older nested database snapshot still present in Background.

## Scope

Modify `moda-interact-database` schema/migration/validators/tests/ERD as required. Preserve the accepted ARCH-027 migration and provider-neutral billing models; ARCH-028 adds its own bounded failure/reachability/compensation schema on top and does not rewrite Woo billing history.

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

### Committed recovery compensation provenance

Extend `billing.UsageReservation` with the following nullable, all-or-nothing correction fields and add the inverse UsageEvent relation:

```prisma
compensationUsageEventId String? @unique
compensationUsageEvent   UsageEvent? @relation("CompensatedReservation", fields: [compensationUsageEventId], references: [id], onDelete: Restrict)
compensationReason       UsageReservationCompensationReason?
compensationDisposition  UsageReservationCompensationDisposition?
compensatedAt            DateTime?
```

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

A compensated reservation stays `COMMITTED` with its original positive UsageEvent unchanged. At most one negative compensation UsageEvent may be linked. The correction must belong to the same Shop, use `RECOVERY_CONVERSATION`, have exact negative quantity and reference the original committed UsageEvent through `correctionOfUsageEventId`. A still-`RESERVED` source is released through its existing status transition and creates no negative correction. No provider monetary refund state or purchased-credit refund-cancellation state is introduced.

### Integrity

Require canonical digits-only recipient values and bounded provider codes. A non-null `suppressUntil` requires failure evidence and must be later than `lastFailureAt`. Enforce all-or-none compensation fields and exact-correction integrity in the schema/migration/validators as appropriate.

## Out of Scope

- Provider-code classification.
- Shared/Messaging runtime contract work.
- Recovery compensation runtime/counter/source adjustment (BACKGROUND-004/009).
- Admin UI implementation.
- Suppression/pre-admission runtime implementation.
- Synchronous provider rejection handling.
- Missing-phone candidate-materialisation handling.
- Merchant notification.
- New Customer/Conversation recipient relationship.
- Historical/legacy data backfill or upgrade compatibility.
- Provider monetary refund state or new make-good bucket.
- Required per-outreach-attempt recipient (DATABASE-003).

## Requirements

- [x] The same recipient may appear in many Shops; reachability uniqueness is `(shopId, recipient)` only.
- [x] `ConversationMessage` failure evidence is bounded and raw provider payload/text is not stored.
- [x] Suppression is finite evidence, not a permanent unreachability state.
- [x] `whatsappRecipientSuppressionDays` defaults to `7` and must be positive.
- [x] New block reason supports finite WhatsApp recipient suppression; missing recipient does not materialise a `CheckoutRecovery` and therefore requires no recovery block reason.
- [x] No Conversation/Customer phone ownership redesign is introduced.
- [x] The ARCH-028 migration is derived from the accepted ARCH-027 schema/migration lineage; it does not overwrite, duplicate or regress provider-neutral Woo billing persistence.
- [x] Every COMMITTED compensation has exactly one auditable linked negative UsageEvent, reason, disposition and timestamp or has all four fields null.
- [x] The correction is same-Shop, exact negative `RECOVERY_CONVERSATION` quantity, and points to the original committed UsageEvent.
- [x] No provider-monetary-refund state is introduced.

## Work Items

- [x] Verify `ARCH-027-DATABASE-001` accepted migration/schema is present in the canonical database branch before authoring ARCH-028; preserve its Woo billing models and fields.
- [x] Add message failure fields and constraints.
- [x] Extend recovery admission-block enum with `WHATSAPP_RECIPIENT_SUPPRESSED` only.
- [x] Add Shop-scoped reachability model, relation, unique/indexes and integrity constraints.
- [x] Add `PlatformBillingPolicy.whatsappRecipientSuppressionDays` default `7` and positive constraint.
- [x] Add compensation reason/disposition enums, UsageReservation fields, inverse UsageEvent relation and exact-correction integrity validation.
- [x] Add architecture-specific schema/migration validation.
- [x] Add fresh disposable PostgreSQL migration rehearsal.
- [x] Regenerate ERD.

## Interfaces / Contracts

Persistence consumed by later ARCH-028 Background/Admin tasks:

```text
ConversationMessage.providerFailureCode / failedAt
WhatsAppRecipientReachability(shopId, recipient)
PlatformBillingPolicy.whatsappRecipientSuppressionDays
RecoveryAdmissionBlockReason.WHATSAPP_RECIPIENT_SUPPRESSED
UsageReservation.compensationUsageEventId / compensationReason / compensationDisposition / compensatedAt
UsageReservationCompensationReason.WHATSAPP_RECIPIENT_UNDELIVERABLE
UsageReservationCompensationDisposition.RESTORED_SPENDABLE / HELD_FOR_REFUND / HISTORICAL_ONLY
```

## Dependencies

- `ARCH-027-DATABASE-001` (architect-accepted Complete; canonical database migration baseline).

## Enables

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-DATABASE-003`
- `ARCH-028-ADMIN-001`
- `ARCH-028-BACKGROUND-001`

## Acceptance Criteria

- [x] Fresh schema contains all required fields/models/enums/defaults/indexes/constraints.
- [x] A fresh migration chain includes the accepted ARCH-027 billing persistence first and ARCH-028 additions second, without a duplicate/drop of Woo billing structures.
- [x] Same phone number is independently representable for different Shops.
- [x] Suppression duration default is exactly seven days.
- [x] A COMMITTED reservation links to at most one exact negative correction, with atomic reason/disposition/timestamp/link presence.
- [x] Cross-Shop, wrong-metric, wrong-original or non-negative corrections fail validation.
- [x] A still-RESERVED reservation requires no compensation UsageEvent.
- [x] No purchased/refund-cancellation provenance or make-good bucket is added.
- [x] No permanent recipient-unreachable boolean/enum is introduced.
- [x] No raw Meta error payload/text field is introduced.
- [x] No legacy/backfill migration machinery is introduced.
- [x] Prisma validation/generation, architecture validators, PostgreSQL fresh rehearsal, ERD and `git diff --check` pass.

## Validation

Use repository-declared format/Prisma/schema/migration/PostgreSQL/ERD commands after inspecting the current `package.json`, plus `git diff --check`. Include a focused correction-integrity validation for the consolidated schema, and verify a fresh database applies the accepted ARCH-027 migration before ARCH-028 while retaining Woo billing models/fields. Fresh-database migration correctness is required; a backwards-compatible upgrade rehearsal is not an ARCH-028 requirement.

## Stop Condition

Complete the report, set `status: review`, return to `moda_architect` and STOP.

## Implementation Notes

Do not add a recipient field to `Conversation` or `ConversationMessage`. The strict recovery-attempt recipient snapshot is owned by DATABASE-003 so BACKGROUND-001 can consume DATABASE-001 without prematurely breaking existing attempt-creation call sites.

## Completion Report

### Status

Ready for architect review

### Files Changed

Implementation repository:
- `prisma/schema.prisma`
- `prisma/migrations/20261008140724_arch028_whatsapp_failure_reachability_compensation/migration.sql`
- `scripts/validate-arch028-whatsapp-failure-schema.mjs`
- `scripts/test-arch028-whatsapp-failure-postgres.mjs`
- `scripts/test-arch027-woocommerce-billing-postgres.mjs`
- `scripts/validate-arch027-woocommerce-billing-migration.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`

### Work Completed

Added bounded WhatsApp provider failure evidence, Shop-scoped recipient reachability and finite suppression policy, the suppression admission-block reason, and exact committed recovery compensation provenance. Added PostgreSQL checks and deferred integrity triggers for failure codes, recipient values, suppression evidence, positive policy duration, and same-Shop exact negative recovery corrections. Kept the accepted ARCH-027 migration intact and updated its validators to permit subsequent ordered migrations. Added ARCH-028 schema and fresh PostgreSQL validators, generated the ERD, and verified the complete fresh chain preserves Woo billing persistence.

### Validation Results

Passed `npm run format`, `npm run validate`, `npm run prisma:generate`, `npm run test:arch028-whatsapp-failure-schema`, `npm run test:arch027-woocommerce-billing-migration`, `npm run test:arch027-woocommerce-billing-schema`, `npm run test:arch028-whatsapp-failure:postgres`, `npm run erd:puml`, and `git diff --check`. The fresh rehearsal ran against a dedicated empty localhost fixture on PostgreSQL 17.0.11 with pgvector; it applied ARCH-027 before ARCH-028 and verified the WooCommerce billing objects and fields remained present. The rehearsal also passed positive and rejection cases for recipient uniqueness/canonical digits, bounded failure codes, finite suppression, positive duration, all-or-none provenance, same-Shop exact corrections, RESERVED-without-compensation, and correction mutation guards.

### Deviations

The repository's ARCH-027 validators previously required ARCH-027 to be the latest migration. Their ordering checks now require the accepted ARCH-027 migration to remain present in the ordered chain, allowing ARCH-028 to follow without changing the ARCH-027 migration itself.

### Assumptions

The fresh PostgreSQL fixture was the task-local `arch028_fresh_fixture_20261008_copilot3` database in the local `arch028-database001-postgres` container; the configured remote `DATABASE_URL` was not used.

### Unresolved Issues

None.

### Launcher and VCS Evidence

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-DATABASE-001`
  parent branch: `task/ARCH-028-DATABASE-001`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-DATABASE-001`
  implementation branch: `task/ARCH-028-DATABASE-001`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recorded submodule commits: none

Implementation commit: `7026fe9` (`feat(database): persist WhatsApp delivery failure evidence`), pushed to `origin/task/ARCH-028-DATABASE-001`.
Parent task commit: this report update is being published to `origin/task/ARCH-028-DATABASE-001`.

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
