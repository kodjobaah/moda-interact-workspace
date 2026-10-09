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
status: complete
priority: 13
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-028-DATABASE-001
enables:
  - ARCH-028-BACKGROUND-005
created: 2026-10-07
updated: 2026-10-09
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

- [x] `RecoveryOutreachAttempt.recipient` is required.
- [x] Stored value is digits-only, non-empty and <=64 chars.
- [x] No default empty value or nullable compatibility escape hatch is introduced.
- [x] Existing database consumers need not adopt this gitlink until their runtime task is ready to populate the field.

## Work Items

- [x] Add required field and SQL integrity.
- [x] Add schema/migration validator.
- [x] Run fresh disposable PostgreSQL migration rehearsal.
- [x] Regenerate ERD.

## Interfaces / Contracts

Consumed by `ARCH-028-BACKGROUND-005` for mandatory per-attempt snapshots. BACKGROUND-007 independently resolves the pre-materialisation recipient before this breaking field is adopted.

## Dependencies

- `ARCH-028-DATABASE-001`

## Enables

- `ARCH-028-BACKGROUND-005`

## Acceptance Criteria

- [x] Fresh schema enforces required canonical recipient.
- [x] No Conversation/ConversationMessage recipient field is added.
- [x] No legacy/backfill compatibility is added.
- [x] Prisma/schema/migration/PostgreSQL/ERD validation passes.

## Validation

Use repository-declared format/Prisma/schema/migration/PostgreSQL/ERD commands plus `git diff --check`; fresh-database correctness is required.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

This split is an execution/deployment compatibility boundary, not a relaxation of the final invariant. BACKGROUND-005 must adopt this exact database revision while changing all recovery attempt creation paths to provide the recipient.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

In `moda-interact-database`: `prisma/schema.prisma`; migration `20261009103000_arch028_recovery_outreach_attempt_recipient`; `scripts/validate-arch028-recovery-outreach-recipient.mjs`; `scripts/test-arch028-whatsapp-failure-postgres.mjs`; `package.json`; and generated `docs/generated/prisma-erd.puml`.

### Work Completed

Added required `RecoveryOutreachAttempt.recipient String @db.VarChar(64)` and a migration with no default/backfill plus a C-collation digits-only check. Added a focused schema/migration validator and extended the existing fresh ARCH-028 PostgreSQL rehearsal to accept 1- and 64-digit values while rejecting missing, empty, non-digit, newline, and overlength values. Regenerated the ERD; generation also included the two ARCH-028 compensation enums already present in the Prisma schema.

### Validation Results

Passed `npm ci` (the install reported three high-severity audit advisories and pending install-script approvals, but completed); `npm run format`; `npm run validate`; `npm run test:arch028-recovery-outreach-recipient`; `npm run test:arch028-whatsapp-failure-schema`; `npm run test:arch028-whatsapp-failure:postgres` on fresh PostgreSQL 17.0011; `npm run erd:puml`; and `git diff --check`. The final fresh PostgreSQL rehearsal applied the entire migration chain and passed the new recipient boundary checks. The disposable container was removed after validation.

### Execution Evidence

- Launcher prepared `ARCH-028-DATABASE-003` as Attempt 1 for canonical executor `copilot` at `2026-10-09T10:27:40Z`; dependency `ARCH-028-DATABASE-001` passed. Claim commit: `133ede885cae2cb454968a46f9ae73f6b5e50526`.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-DATABASE-003`, branch `task/ARCH-028-DATABASE-003`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-DATABASE-003`, branch `task/ARCH-028-DATABASE-003`.
- Parent prepared head: `e6422250fbade8dc296bb7fa8b104b1d2c6fa894`; implementation prepared head: `ef51500b2728bc0c894e627dfa1c9e6c9d4d9a13`.
- Start synchronization: parent remote task branch fast-forward `not-needed`, parent `origin/main` `already-current`; implementation remote task branch fast-forward `not-needed`, implementation `origin/main` `already-current`.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; status `ready`, no entries.
- Physical isolation: shared workspace checkout was not switched or mutated; shared implementation checkout was not switched or mutated; no other task worktree was reused.
- Implementation commit `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce` was pushed to `origin/task/ARCH-028-DATABASE-003`; local and remote heads matched after push.

### Deviations

None. Existing development databases containing outreach attempts without recipients may need reset before applying the new required-column migration, as allowed by the task's pre-production migration contract. No consumer repository or submodule gitlink was changed.

### Assumptions

None.

### Unresolved Issues

Existing consumers should adopt this database revision only with their assigned runtime changes that populate the required recipient; this task intentionally does not update those repositories.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 1 (2026-10-09).

### Review Notes

Reviewed the exact uploaded ARCH-028-DATABASE-003 snapshot against the parent ARCH-028 architecture, canonical task requirements, and the published mirrored task commits: implementation `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce`; parent report `7ffac3ebcc34dd5f7d5d385305814bb1a030d472`. Verified the important task, migration, schema, validator and PostgreSQL-script blob identities against the published task branches.

`RecoveryOutreachAttempt.recipient` is required `String @db.VarChar(64)`. The later single SQL migration adds `VARCHAR(64) NOT NULL` and the C-collation `[0-9]{1,64}` PostgreSQL check without nullable accommodation, default, or backfill. This matches the expressly approved pre-production breaking contract. The fresh migration rehearsal exercises lower/upper accepted boundaries and missing, empty, non-digit, newline, and overlength rejections. It also verifies accepted ARCH-027 Woo billing objects remain present in the full ARCH-028 chain. No Conversation or ConversationMessage recipient field was introduced. Regenerated ERD includes the required outreach attempt field; incidental regenerated compensation enums correspond to the existing Prisma schema and are not a new migration in this task.

The Completion Report includes dedicated parent/implementation worktree locations, launcher claim, start-of-attempt synchronization, recursive-submodule status, exact published implementation revision, and clean branches. Three high-severity npm audit advisories were reported during installation; no task-specific dependency modification or new runtime behavior requires changing them here.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261009103000_arch028_recovery_outreach_attempt_recipient/migration.sql`
- `moda-interact-database/scripts/validate-arch028-recovery-outreach-recipient.mjs`
- `moda-interact-database/scripts/validate-arch028-whatsapp-failure-schema.mjs`
- `moda-interact-database/scripts/test-arch028-whatsapp-failure-postgres.mjs`
- `moda-interact-database/package.json`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- Parent ARCH-028 architecture, DATABASE-001 dependency, BACKGROUND-005/BACKGROUND-007 dependency state, and DATABASE-003 task and Completion Report.

### Validation Reviewed

Independently executed `node scripts/validate-arch028-recovery-outreach-recipient.mjs` and `node scripts/validate-arch028-whatsapp-failure-schema.mjs`; both passed. Independently verified the JavaScript syntax of the recipient validator and PostgreSQL rehearsal script. Inspected the relevant fresh-PostgreSQL positive/negative assertions and migration ordering. The implementing agent reports passing Prisma format/validation, focused schema/migration validation, ERD generation, `git diff --check`, and the complete fresh PostgreSQL 17 rehearsal using a removed disposable container. PostgreSQL execution was not independently repeated because Docker and `psql` are unavailable in the architect's review environment.

### Architecture Conformance

Conforming. The strict required recipient is stored only on RecoveryOutreachAttempt, and the approved no-legacy-backfill migration split is retained. DATABASE-003 does not modify consumers or their nested database submodule gitlinks. The breaking recipient migration **must not be deployed independently ahead of compatible Background attempt writers**, because all initial and follow-up attempt creation paths must provide the exact recipient at the time of database adoption.

### Follow-up

Set `ARCH-028-DATABASE-003` to `complete` and clear any execution claim (already null); preserve `attempt: 1`. Both BACKGROUND-005 dependencies (DATABASE-003 and architect-accepted BACKGROUND-007) are now Complete, so promote `ARCH-028-BACKGROUND-005` to `ready` for `moda_background`. Its runtime implementation must adopt this accepted database revision together with initial/follow-up attempt writers and validate recipient/Meta destination parity, rather than deploying the migration separately. ARCH-028 remains in progress until the remaining implementation/system-test tasks are accepted. Do not edit `docs/decisions/**/_index.md` files until explicitly requested during final architecture reconciliation.
