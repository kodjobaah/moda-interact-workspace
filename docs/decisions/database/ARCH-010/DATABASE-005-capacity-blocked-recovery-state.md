---
id: ARCH-010-DATABASE-005
architecture_id: ARCH-010
title: Persist recovery-capacity blocks on detected recoveries
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: copilot
claimed_at: 2026-09-11T11:57:54Z
attempt: 1
depends_on: []
enables:
  - ARCH-010-BACKGROUND-009
created: 2026-09-11
updated: 2026-09-11T12:01:52Z
---

# ARCH-010-DATABASE-005: Persist recovery-capacity blocks on detected recoveries

## Objective

Add the minimum durable state required to distinguish a `CheckoutRecovery` that is still `DETECTED` because all currently supported recovery capacity is exhausted from another DETECTED recovery that has not yet initiated for some unrelated reason.

Do **not** introduce a new `CheckoutRecoveryStatus`. Capacity exhaustion is an admission condition, not a customer lifecycle stage.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/**schema**
docs/generated/**
package.json
```

Also inspect current `CheckoutRecovery`, `CheckoutRecoveryStatus`, status-history and index conventions.

## Required Prisma change

Add a commerce-schema enum:

```prisma
enum RecoveryAdmissionBlockReason {
  RECOVERY_CAPACITY_EXHAUSTED

  @@schema("commerce")
}
```

Add nullable fields to `CheckoutRecovery`:

```prisma
admissionBlockedAt    DateTime?
admissionBlockReason RecoveryAdmissionBlockReason?
```

Add an index supporting bounded repair/resume scans equivalent to:

```prisma
@@index([shopId, admissionBlockReason, status, detectedAt])
```

Existing rows must remain valid with both fields null.

## Database integrity

Create a migration-level CHECK constraint so the two fields are either both null or both non-null:

```text
(admissionBlockedAt IS NULL AND admissionBlockReason IS NULL)
OR (admissionBlockedAt IS NOT NULL AND admissionBlockReason IS NOT NULL)
```

Use the repository's existing SQL quoting/schema conventions. Do not add triggers.

## Behavioural invariant represented by this schema

A row may be marked `RECOVERY_CAPACITY_EXHAUSTED` only while the recovery is still logically eligible to retry initiation later. Application code owns clearing the fields after successful initiation or making the recovery terminal if it is no longer recoverable.

The schema does not attempt to enforce `status = DETECTED` through a cross-column enum CHECK unless the repository's migration conventions already use such checks safely. If adding it would create migration risk, document the application invariant instead.

## Required validation/tests

Prove at least:

1. existing `CheckoutRecovery` rows remain valid with null block fields;
2. a DETECTED recovery can persist `RECOVERY_CAPACITY_EXHAUSTED` plus timestamp;
3. block reason without timestamp is rejected by the database constraint;
4. timestamp without block reason is rejected;
5. both fields can be cleared together;
6. generated Prisma client exposes the enum and fields;
7. the repair-query index is present in migration/schema output;
8. no CheckoutRecovery status enum value was added or renamed.

Update generated schema/ERD artifacts only through the repository's established generation workflow if they are version-controlled.

## Validation

Inspect `package.json` and run only declared commands. At minimum run the repository's Prisma format/validate/generate/schema tests plus:

```bash
git diff --check
```

Do not invent missing scripts.

## Non-goals

Do not implement Background resume logic, BullMQ, merchant UI, promotional credits, top-up purchase/refund accounting, subscription states or billing-period rollover.

## Stop conditions

STOP and return to `moda_architect` if:

- another accepted task has already introduced an equivalent durable block model;
- the current schema has moved CheckoutRecovery ownership out of `commerce`;
- migration safety would require destructive rewriting of existing recovery rows.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260911020000_add_recovery_admission_block_state/migration.sql`
- `scripts/validate-checkout-recovery-capacity-schema.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`

### Work Completed
- Added the commerce `RecoveryAdmissionBlockReason` enum with `RECOVERY_CAPACITY_EXHAUSTED`.
- Added nullable `admissionBlockedAt` and `admissionBlockReason` fields to `CheckoutRecovery`.
- Added the bounded repair/resume index on `[shopId, admissionBlockReason, status, detectedAt]`.
- Added an additive migration with the pairwise CHECK constraint requiring both admission fields to be null or both non-null; existing rows remain valid with both fields null.
- Added generated-client and live PostgreSQL validation for valid DETECTED blocked rows, both mismatch rejection cases, and clearing both fields together.
- Regenerated the version-controlled PlantUML ERD.

### Validation Results
- `npm run prisma:generate` passed.
- `npm run format` passed.
- `npm run validate` passed.
- `npm run test:checkout-recovery-capacity` passed, including live rollback-scoped PostgreSQL CHECK assertions.
- `npm run test:recovery-credit-packs` passed.
- `npm run erd:puml` passed.
- `npm run status` passed and reported only `20260911020000_add_recovery_admission_block_state` as pending in the configured database; no migration was applied to that database.
- `git diff --check` passed.
- `npm ci` installed repository dependencies; npm reported three existing high-severity audit findings.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-005`
- Implementation branch: `task/ARCH-010-DATABASE-005`
- Implementation commit: `fb0e76e feat(database): persist recovery capacity blocks`
- Implementation branch pushed to `origin`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-005`
- Parent task branch claim commit: `d92e5a9 chore: claim ARCH-010-DATABASE-005`
- Parent task definition commit: `683d4ee chore: materialize ARCH-010-DATABASE-005`

### Deviations / Assumptions
- No deviations from the task scope. The schema does not add a new `CheckoutRecoveryStatus` value and does not enforce the application-owned DETECTED-only invariant through a cross-column CHECK.

### Architect Review
Pending.
