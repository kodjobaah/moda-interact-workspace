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
status: review
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-036-BACKGROUND-001"]
created: 2026-10-13
updated: 2026-10-13
---

# ARCH-036-DATABASE-003 — Add global Woo coupon dispatch lease name

## Architecture

- Parent: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; implementation owner: `moda_database`, repository `moda-interact-database`.
- The task definition was present on `origin/main`; the canonical task branches and worktrees were prepared for developer attempt 1.
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

- [x] Add `WOO_COUPON_SYNC_DISPATCH` to `prisma/schema.prisma` under `enum BackgroundRuntimeLeaseName`.
- [x] Create one additive Prisma migration with the exact enum value.
- [x] Regenerate and validate Prisma client/schema using repository-declared scripts.
- [x] Validate fresh-install and existing-database upgrade; record migration status, preserving previous lease rows and enum values.
- [x] Record changed files and verification in the task Completion Report; stop without editing Background.

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

- [x] Canonical Prisma enum contains exactly the new `WOO_COUPON_SYNC_DISPATCH` member in addition to all eight existing values, in `public`.
- [x] Migration adds the member to the existing Postgres type without replacing it, resetting leases or modifying other table schemas.
- [x] Prisma validation/client generation succeed; existing lease names remain usable.
- [x] Fresh and upgrade migration rehearsals pass on isolated disposable PostgreSQL databases.
- [x] No Background/API/Woo/Admin/CommerceAgent/Shopify implementation or domain `_index.md` files changed.

## Validation

- [x] `npm run prisma:validate` and `npm run prisma:generate`.
- [x] Apply all migrations to a fresh disposable PostgreSQL database; assert the new enum label exists under `public`.
- [x] Apply the new migration to a disposable database from the pre-change baseline; assert legacy lease rows and previous enum labels remain intact.
- [x] `npm run status`: 47 migrations found; configured database schema up to date.
- [x] `git diff --check` and inspect the SQL/Prisma change scope.

## Stop Condition

After required Work Items, Acceptance Criteria and Validation pass, complete the implementation Completion Report, set `status: review` and STOP. Do not edit Background, start a different task, or mark this task Complete yourself. Because `completion_mode: developer`, explicit developer completion is required after accepted review.

## Implementation Notes

- Follow the existing enum-add migration convention in `prisma/migrations/20261001120000_arch023_merchant_knowledge_entitlement_reconciliation_lease/migration.sql`.
- The single lease row is **runtime-created**, keyed by `WOO_COUPON_SYNC_DISPATCH`, and shared across all replicas. It is unrelated to per-shop `ShopifyDiscountCatalogue.activeSyncToken`/`syncGeneration`.
- The lease service's `CASE` mapping is a separate **Background** code change. New enum value without its `CASE` branch is insufficient for a reliable recurring scheduler; `BACKGROUND-001` explicitly depends on this task.
- Execute only in launcher-resolved dedicated task worktrees and record physical isolation, synchronization and nested-submodule evidence required by repository policy.

## Completion Report

### Status

In Review; passing developer self-review recorded, explicit developer completion pending.

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261013080000_arch036_woo_coupon_dispatch_runtime_lease/migration.sql`
- `moda-interact-database/package.json`
- `moda-interact-database/scripts/validate-arch036-woo-coupon-dispatch-runtime-lease.mjs`
- `moda-interact-database/scripts/test-arch036-woo-coupon-dispatch-runtime-lease-postgres.mjs`

### Work Completed

- Added `WOO_COUPON_SYNC_DISPATCH` to the canonical `public.BackgroundRuntimeLeaseName` Prisma enum and added its idempotent PostgreSQL enum migration.
- Added static enum/migration contract validation and isolated PostgreSQL fresh/upgrade migration rehearsals. The harness verifies the eight existing labels, preserves a pre-existing lease row on upgrade, confirms the migration does not seed the new runtime lease row, and exercises insert, ownership transition and removal.
- Implementation changes are present in the published implementation task branch history. They were already included in `origin/main` when the canonical implementation worktree was prepared, so the task branch currently has no unique source diff against `origin/main`.
- No Background or other out-of-scope application source was changed. No material assigned-agent assistance occurred.

### Validation Results

Passed: `npm run prisma:validate`, `npm run prisma:generate`, and `npm run test:arch036-woo-coupon-dispatch-runtime-lease`.

Passed: `npm run test:arch036-woo-coupon-dispatch-runtime-lease:postgres:fresh` and `npm run test:arch036-woo-coupon-dispatch-runtime-lease:postgres:upgrade`. Both applied the real ordered migrations in invocation-owned `pgvector/pg17` containers with networking disabled. The upgrade rehearsal verified that the legacy lease row's owner, generation and timestamps remained unchanged. Both rehearsals verified legacy enum labels, the new label, no migration-created runtime row, lease insert/ownership transition/removal, and safe migration reapplication; both containers were removed.

Passed: `npm run status` reported 47 migrations found and the configured database schema up to date. This was a read-only status check.

Passed: `git diff --check`; the implementation worktree is clean. Prisma generation left no tracked worktree changes.

### Deviations

None.

### Assumptions

No SQL changes beyond adding the one enum label will be required.

### Unresolved Issues

None known. Formal developer completion remains pending after this passing review.

### Architectural Concerns

The task-specific implementation and test commits are already ancestors of `origin/main` and the pushed implementation task branch. The branch has no unique source diff against current `origin/main`; no merge to `main` was performed as part of this reconciliation. The developer-supplied architectural assessment reports that the migration requirements are met.

## Developer Self-Review

### Review Result

Passed. Explicit developer completion is pending.

### Attempt

1

### Reviewed Scope

`prisma/schema.prisma`, `prisma/migrations/20261013080000_arch036_woo_coupon_dispatch_runtime_lease/migration.sql`, `package.json`, `scripts/validate-arch036-woo-coupon-dispatch-runtime-lease.mjs`, and `scripts/test-arch036-woo-coupon-dispatch-runtime-lease-postgres.mjs` in `moda-interact-database`.

### Validation Evidence

Prisma validation and generation, static enum/migration contract check, PostgreSQL fresh and upgrade rehearsals, configured migration status, and `git diff --check` all passed. The canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-DATABASE-003` is clean on `task/ARCH-036-DATABASE-003`, synchronized to its published upstream, and contains the implementation/test commits. The canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-DATABASE-003` contains this task report on the matching task branch.

### Decision

Transition to `review` under `completion_mode: developer`; do not mark Complete. The developer may explicitly complete with `/moda_developer_update ARCH-036-DATABASE-003 complete`.

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
