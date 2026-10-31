---
id: ARCH-016-DATABASE-002
architecture_id: ARCH-016
title: Remove the fixed PostgreSQL checkout-recovery lifetime range constraint
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-31T11:31:08Z
attempt: 1
depends_on:
  - ARCH-016-DATABASE-001
enables:
  - ARCH-016-BACKGROUND-005
  - ARCH-016-ADMIN-003
  - ARCH-016-SYSTEM-TEST-001
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-016-DATABASE-002 — Remove fixed recovery-lifetime range constraint

## Architecture

- Architecture: `ARCH-016` — `docs/architecture/ARCH-016-merchant-recovery-policy-shopify-discounts-followups-expiry.md`.
- Coordinator: `moda_architect`; implementation owner: `moda_database`.

## Objective

Remove the historical `1..90`-day **business-policy** `CHECK` constraint from the existing `public."BackgroundRuntimeConfig"` row through a forward-only Prisma migration, without changing the column, its 21-day default, or other database constraints.

## Context

The accepted ARCH-016 migration `prisma/migrations/20260916150000_arch016_recovery_policy_discounts_outreach_generations/migration.sql` added:

```sql
ALTER TABLE "public"."BackgroundRuntimeConfig"
    ADD CONSTRAINT "ck_arch016_checkout_recovery_lifetime"
        CHECK ("checkoutRecoveryLifetimeDays" BETWEEN 1 AND 90);
```

The updated policy allows **all non-negative whole-number days** representable by the existing PostgreSQL `INTEGER`/Prisma `Int` column. This task removes the old 90-day ceiling. Admin validates the non-negative policy for ordinary writes; Background rejects malformed/negative configuration at runtime. Do **not** introduce a replacement SQL `CHECK` on this field: the user has assigned this policy validation to Admin. SQL `INTEGER` still enforces its native storage/type bounds, which are not a new business maximum.

## Scope

Authorized changes in `moda-interact-database` only:

```text
prisma/migrations/20261031110000_arch016_remove_recovery_lifetime_check/migration.sql          NEW
scripts/test-arch016-recovery-lifetime-postgres.mjs                                             NEW
package.json                                                                                  two test scripts
scripts/validate-arch016-recovery-schema.mjs                                                   only if existing validator contradicts forward migration
```

`prisma/schema.prisma` is inspect-only: `checkoutRecoveryLifetimeDays Int @default(21)` is already correct, and must remain unchanged. Additional focused tests in this repository are allowed only if necessary.

## Out of Scope

- Do not edit an existing historical migration, Admin UI, Background runtime, API, Shared contracts, WooCommerce plugin, `docs/decisions/**/_index.md` or unrelated tables.
- Do not change the column to `BIGINT`, introduce another configuration field, reset existing values, or relax constraints on other runtime fields.
- Do not add a `CHECK >= 0` replacement. Admin is the primary write gate; runtime safety is delegated to BACKGROUND-005.

## Requirements

1. Create exactly one forward migration named `20261031110000_arch016_remove_recovery_lifetime_check` unless an identical migration already exists on the task branch; if the path is occupied, stop and report the collision rather than overwriting.
2. The complete migration body must be:

   ```sql
   ALTER TABLE "public"."BackgroundRuntimeConfig"
       DROP CONSTRAINT "ck_arch016_checkout_recovery_lifetime";
   ```

3. Preserve the existing `INTEGER NOT NULL DEFAULT 21` column, the singleton row, optimistic-version field, audit events, other check constraints and index definitions.
4. Never rewrite or delete prior migration history. The new migration must apply both to a **fresh database** (all migrations in order) and to an **upgrade database** (all preceding migrations and an existing configuration row).
5. Accept `0`, `1`, `21`, `90`, `91`, `180`, `365` and `2147483647` as column values following the migration. PostgreSQL `INTEGER` is the *storage* representation; this task does not promise integers outside the representable SQL range.
6. Because the old check is dropped, direct SQL can technically store a negative value; **do not advertise the database as preventing negative values**. ARCH-016-ADMIN-003 rejects them on normal mutations; ARCH-016-BACKGROUND-005 fails closed on a corrupted row.

## Work Items

- [ ] Verify schema column, old migration and new migration path.
- [ ] Create only the forward `DROP CONSTRAINT` migration.
- [ ] Add `scripts/test-arch016-recovery-lifetime-postgres.mjs` using the disposable `pgvector/pgvector:pg17` pattern from `scripts/test-arch050-initial-recovery-support-notification-postgres.mjs`, with `--mode fresh|upgrade`, a unique container name, `--network none`, and unconditional `finally` cleanup.
- [ ] Add `test:arch016-recovery-lifetime:postgres:fresh` and `test:arch016-recovery-lifetime:postgres:upgrade` package commands.
- [ ] Verify the legacy ARCH-016 schema validator does not assert that the old constraint remains **present in the current migrated schema**; if it does, scope the check to the historical migration or correct its expectation without changing unrelated assertions.
- [ ] Record exact commands, container cleanup evidence and migration checks in the Completion Report.

## Interfaces / Contracts

```prisma
model BackgroundRuntimeConfig {
  // existing fields unchanged
  checkoutRecoveryLifetimeDays Int @default(21)
}
```

SQL post-migration invariant: `pg_constraint` has no `ck_arch016_checkout_recovery_lifetime` on `public."BackgroundRuntimeConfig"`; `information_schema.columns` still reports `integer`, `NO`, and default `21`. No wire contract change.

## Dependencies

- `ARCH-016-DATABASE-001` (Complete in the supplied snapshot).

## Enables

- `ARCH-016-BACKGROUND-005`
- `ARCH-016-ADMIN-003`
- Existing terminal `ARCH-016-SYSTEM-TEST-001` once every required implementation is accepted.

## Acceptance Criteria

- [ ] New migration drops **only** the exact named lifetime CHECK constraint.
- [ ] Fresh and upgrade PostgreSQL tests both pass without modifying the original migration.
- [ ] Upgrade fixture seeded with an existing `21`-day singleton row preserves its ID, version and value; applying the migration does not reset it.
- [ ] Fresh fixture retains the 21-day default; no `1..90` check survives.
- [ ] All listed non-negative INTEGER examples including `0`, `91`, `180`, `365`, and `2147483647` can be persisted and read back.
- [ ] Tests assert another existing constraint remains intact (use a concrete independent constraint found in the schema).
- [ ] No data deletion, other schema changes or `_index.md` edits.

## Validation

Run declared repository scripts, including:

```bash
npm run validate
npm run prisma:generate
npm run test:arch016-recovery-schema
npm run test:arch016-recovery-lifetime:postgres:fresh
npm run test:arch016-recovery-lifetime:postgres:upgrade
git diff --check
```

The PostgreSQL tests require disposable Docker/pgvector. If unavailable, report the exact blocker; do not mark them passed. Include the migration order and container-cleanup results.

## Stop Condition

After the specified implementation, acceptance criteria and validation, complete the task's Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not implement Background or Admin changes.

## Implementation Notes

Preserve already accepted ARCH-016 history. Do not change the schema default. Source migrations may still contain the historical `BETWEEN 1 AND 90`; that text documents what the earlier migration did and must not be rewritten. Final database state is determined by ordered migration application, not by searching a single historical file.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

Not Started

### Validation Results

Not Run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation evidence.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not assessed.

### Follow-up

None
