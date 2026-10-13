---
id: ARCH-036-DATABASE-003
architecture_id: ARCH-036
title: "Add PostgreSQL global lease name for Woo coupon dispatch"
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-036-BACKGROUND-001"]
created: 2026-10-13
updated: 2026-10-13
---

# ARCH-036-DATABASE-003 — Add global Woo coupon dispatch lease name

## Architecture

- Parent: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; implementation owner: `moda_database`, repository `moda-interact-database`.
- **Defined but not materialised** in the developer's canonical workspace. This portable definition does not create a worktree, branch, migration, commit or claim.
- A single global lease is shared by **all** Background replicas and shops; **no per-shop runtime lease rows** are needed.

## Objective

Extend the existing `public.BackgroundRuntimeLeaseName` Prisma/PostgreSQL enum with **one** value, `WOO_COUPON_SYNC_DISPATCH`, and provide a checked migration so `ARCH-036-BACKGROUND-001` can reuse the existing PostgreSQL-leased global scheduler without creating a parallel scheduling mechanism.

## Context

`moda-interact-database/prisma/schema.prisma` currently defines `BackgroundRuntimeLeaseName` under `@@schema("public")` with eight existing members; it lacks `WOO_COUPON_SYNC_DISPATCH`. `public.BackgroundRuntimeLease.name` is a primary-key column of that enum and already stores `ownerToken`, `generation`, `acquiredAt`, `heartbeatAt`, `leaseUntil` and `lastFinishedAt`. These fields support global acquisition, fencing, 120-second expiry, 30-second heartbeat and completion-relative cadence. The existing lease table needs **no new rows seeded**, columns or indexes. Background will add the matching 60-second lease cadence SQL branch in its own subsequent task.

Previously superseded ARCH-036 `DATABASE-001/002` addressed changing discount schema/selection semantics, **not** this small global-scheduler enum addition; leave both superseded.

## Scope

- Add `WOO_COUPON_SYNC_DISPATCH` to the existing Prisma `BackgroundRuntimeLeaseName` enum, keeping all existing values and its `@@schema("public")` unchanged.
- Create one additive Prisma SQL migration in `prisma/migrations/<new_timestamp>_arch036_woo_coupon_dispatch_runtime_lease/migration.sql` using the repository's existing enum-addition migration pattern:

  ```sql
  ALTER TYPE "public"."BackgroundRuntimeLeaseName"
    ADD VALUE IF NOT EXISTS 'WOO_COUPON_SYNC_DISPATCH';
  ```

- Validate that an existing database can upgrade and a fresh database can apply the full ordered migrations.
- Verify generated Prisma client exposes the new enum value to the Background service after migration/generation.

## Out of Scope

- No changes to `BackgroundRuntimeLease` table structure or ownership/expiry semantics; no new lease table, per-shop lease entries, catalogue indexes, `nextSyncAt`, dispatch-claim columns or additional enums.
- No `BackgroundRuntimeConfig` column or UI/runtime configuration change; global dispatcher cadence is fixed at 60 seconds in the **Background** lease `CASE` logic, not in this database task.
- No Background source edits, BullMQ scheduler, Woo REST calls, credential handling, coupon catalogue logic, API, Woo UI, Admin, CommerceAgent, recovery processing, Shopify discount processing or system-test implementation.
- Do not modify or revive `DATABASE-001/002` or any `docs/decisions/**/_index.md` during this architecture session.

## Requirements

1. Preserve every existing `BackgroundRuntimeLeaseName` enum member, `BackgroundRuntimeLease` record and its primary-key semantics.
2. Prisma enum and SQL migration must use the **same** spelling `WOO_COUPON_SYNC_DISPATCH` and `public` schema.
3. Migration must be additive; no data loss, down migration, manual enum recreation, enum reordering requirement or existing lease deletion.
4. Verify both a fresh migration run and upgrade from the existing project baseline where PostgreSQL is available. If infrastructure is unavailable, leave the relevant Validation unchecked and report the blocker rather than claiming acceptance.
5. The migration does **not** itself create a runtime lease row: the first `BackgroundRuntimeLeaseService.tryAcquire("WOO_COUPON_SYNC_DISPATCH")` call inserts it, and subsequent cycles acquire it only when the existing ownership/cadence predicates allow.
6. Do not introduce an application-level `BackgroundRuntimeLeaseName` copy; consumers use the generated canonical Prisma enum.

## Work Items

- [ ] Add `WOO_COUPON_SYNC_DISPATCH` to `prisma/schema.prisma` under `enum BackgroundRuntimeLeaseName`.
- [ ] Create one additive Prisma migration with the exact enum value.
- [ ] Regenerate and validate Prisma client/schema using repository-declared scripts.
- [ ] Validate fresh-install and existing-database upgrade; record migration status, preserving previous lease rows and enum values.
- [ ] Record changed files and verification in the task Completion Report; stop without editing Background.

## Interfaces / Contracts

- **Database owner:** `moda-interact-database` / `moda_database`.
- **Prisma schema:** `prisma/schema.prisma`, `BackgroundRuntimeLeaseName.WOO_COUPON_SYNC_DISPATCH` in `public`.
- **SQL migration:** `ALTER TYPE "public"."BackgroundRuntimeLeaseName" ADD VALUE IF NOT EXISTS 'WOO_COUPON_SYNC_DISPATCH';`.
- **Existing lease model:** `public.BackgroundRuntimeLease`, keyed by `name`.
- **Consumer:** `ARCH-036-BACKGROUND-001`, `src/runtime/background-runtime-lease.ts` and `src/entrypoints/recovery.ts` in `moda-interact-background` (not edited here).
- **No Shared npm publication:** the Prisma client/schema already carries the typed database enum; this is not a new cross-service queue payload.

## Dependencies

None. `ARCH-026-API-007` independently gates Background's provider access but does **not** gate this enum-only schema task.

## Enables

- `ARCH-036-BACKGROUND-001` (only when `DATABASE-003` is architect-accepted **and** explicitly completed under developer completion authority).

## Acceptance Criteria

- [ ] Canonical Prisma enum contains exactly the new `WOO_COUPON_SYNC_DISPATCH` member in addition to all eight existing values, in `public`.
- [ ] Migration adds the member to the existing Postgres type without replacing it, resetting leases or modifying other table schemas.
- [ ] Prisma validation/client generation succeed; existing lease names remain usable.
- [ ] Fresh and upgrade migration rehearsals pass on a disposable PostgreSQL database, or unresolved infrastructure blockers are explicitly reported without falsely completing the task.
- [ ] No Background/API/Woo/Admin/CommerceAgent/Shopify implementation or domain `_index.md` files changed.

## Validation

- [ ] `npm run prisma:validate` (or documented equivalent in the database repository).
- [ ] `npm run prisma:generate` (and relevant repository-provided focused schema checks).
- [ ] Apply all migrations to a fresh disposable PostgreSQL database; assert the new enum label exists in `pg_enum` / `pg_type` under `public`.
- [ ] Apply the new migration to a disposable database created from the pre-change migration baseline; assert legacy lease rows and previous enum labels remain intact.
- [ ] `npm run status` or equivalent to record migration status where database access is available.
- [ ] `git diff --check` and inspect the complete SQL/Prisma diff for unrelated modifications.

## Stop Condition

After required Work Items, Acceptance Criteria and Validation pass, complete the implementation Completion Report, set `status: review` and STOP. Do not edit Background, start a different task, or mark this task Complete yourself. Because `completion_mode: developer`, explicit developer completion is required after accepted review.

## Implementation Notes

- Follow the existing enum-add migration convention in `prisma/migrations/20261001120000_arch023_merchant_knowledge_entitlement_reconciliation_lease/migration.sql`.
- The single lease row is **runtime-created**, keyed by `WOO_COUPON_SYNC_DISPATCH`, and shared across all replicas. It is unrelated to per-shop `ShopifyDiscountCatalogue.activeSyncToken`/`syncGeneration`.
- The lease service's `CASE` mapping is a separate **Background** code change. New enum value without its `CASE` branch is insufficient for a reliable recurring scheduler; `BACKGROUND-001` explicitly depends on this task.
- Execute only in launcher-resolved dedicated task worktrees and record physical isolation, synchronization and nested-submodule evidence required by repository policy.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task is a portable definition.

### Deviations

None.

### Assumptions

No SQL changes beyond adding the one enum label will be required.

### Unresolved Issues

None identified at task-definition time.

### Architectural Concerns

If a real baseline database cannot apply the additive migration without an additional schema/data change, return the blocker to `moda_architect` rather than expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only; no source implementation submitted.

### Reviewed Files

Current Prisma enum/model and earlier enum-addition migration precedent.

### Validation Reviewed

Task-document patch only; no migration test has been executed.

### Architecture Conformance

Pending implementation review.

### Follow-up

Once developer completion occurs, `ARCH-036-BACKGROUND-001` becomes eligible only when its independent `ARCH-026-API-007` dependency is also Complete.
