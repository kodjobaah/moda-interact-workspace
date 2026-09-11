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
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-010-BACKGROUND-009
created: 2026-09-11
updated: 2026-09-11T12:09:50Z
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
OR
(admissionBlockedAt IS NOT NULL AND admissionBlockReason IS NOT NULL)
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

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested (workflow/task-document evidence only)

The database implementation itself is architecturally conformant. No Prisma schema, migration, validator, package-script, or generated-ERD correction is required by this review.

Architect inspection verified:

- `commerce.RecoveryAdmissionBlockReason` contains `RECOVERY_CAPACITY_EXHAUSTED`;
- `CheckoutRecovery.admissionBlockedAt DateTime?` and `admissionBlockReason RecoveryAdmissionBlockReason?` are nullable, preserving existing rows with `NULL/NULL`;
- `@@index([shopId, admissionBlockReason, status, detectedAt])` exactly matches the bounded repair/resume access path required by the task;
- the migration is additive, creates the enum/columns/index, and adds the pairwise `CheckoutRecovery_admission_block_pair` CHECK without triggers or destructive rewriting;
- `CheckoutRecoveryStatus` remains exactly `DETECTED`, `MESSAGE_SENT`, `ENGAGED`, `COMPLETED`, `EXPIRED`, `CANCELLED`;
- the focused validator checks schema/migration shape, generated Prisma DMMF exposure, mismatch rejection, valid blocked DETECTED state, and clearing both block fields together;
- comparison with the pre-task ARCH-010 repository snapshot found no unrelated implementation changes beyond the files listed in the Completion Report;
- the generated ERD reflects the new enum and fields;
- leaving the migration pending in the configured database is consistent with this task's validation contract; applying it to that database is not required for architect review.

The task cannot be accepted yet because the parent task handoff is not workflow-conformant in two respects. Attempt 2 is therefore limited to parent/worktree evidence remediation and validation rerun; do **not** change the implementation merely to manufacture a new code commit.

##### Required correction 1 — record the complete physical worktree isolation evidence

`docs/agent-worktree-isolation-policy.md` requires every repository-task Completion Report to contain the full launcher-resolved isolation block. The Attempt 1 report records both worktree paths and the implementation branch, but it omits the canonical workspace root, parent branch, the three negative shared/reused-worktree assertions, and all four start-of-attempt synchronization outcomes.

On Attempt 2, record exactly the required evidence shape with truthful values:

```text
Physical worktree isolation:
  canonical workspace root: <absolute launcher-resolved path>
  parent worktree: <absolute launcher-resolved path>
  parent branch: task/ARCH-010-DATABASE-005
  implementation worktree: <absolute launcher-resolved path>
  implementation branch: task/ARCH-010-DATABASE-005
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Also retain the required implementation-repository and parent-workspace commit/push evidence, including `submodule gitlink staged: no` and confirmation that neither task branch was merged to `main`.

If either canonical worktree cannot be established with the expected repository/branch mapping, STOP and report `MODA_WORKTREE_ISOLATION_ERROR`; do not substitute a shared/default checkout.

##### Required correction 2 — restore the architect-owned task contract text

The Attempt 1 parent-task diff changed this architect-authored normative task text outside YAML execution metadata and the Completion Report:

```text
(admissionBlockedAt IS NULL AND admissionBlockReason IS NULL)
OR
(admissionBlockedAt IS NOT NULL AND admissionBlockReason IS NOT NULL)
```

into a two-line formatting variant. The semantics are unchanged, so this is not a database defect, but repository agents do not own arbitrary edits to the task definition. This overlay restores the canonical three-line text. Do not alter other architect-owned task-definition sections during Attempt 2.

##### Required correction 3 — synchronize both task worktrees and rerun required validation

After reclaiming the same task for Attempt 2, reuse the same canonical parent and implementation worktrees, perform the mandatory start-of-attempt synchronization in both repositories, and rerun the task-required validation from the canonical `moda-interact-database` implementation worktree:

```text
npm run prisma:generate
npm run format
npm run validate
npm run test:checkout-recovery-capacity
npm run test:recovery-credit-packs
npm run erd:puml
npm run status
git diff --check
```

`npm run status` remains inspection-only. Do not apply the pending migration to the configured database solely for this review.

If synchronization leaves implementation commit `fb0e76e` unchanged, no replacement implementation commit is required. Push only synchronization/correction commits that are actually necessary, update the same Completion Report with the complete evidence, return the task to `status: review`, and stop for architect review.

