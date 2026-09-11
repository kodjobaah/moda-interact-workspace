---
id: ARCH-010-DATABASE-003
architecture_id: ARCH-010
title: Persist authenticated reinstall reconciliation state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 48
executor: copilot
claimed_at: 2026-09-11T23:14:10Z
attempt: 1
depends_on:
  - ARCH-010-DATABASE-001
enables:
  - ARCH-010-BACKGROUND-006
  - ARCH-010-SHOPIFY-006
created: 2026-09-11
updated: 2026-09-11T23:36:00Z
---

# ARCH-010-DATABASE-003: Persist authenticated reinstall reconciliation state

## Objective

Add the smallest durable marker required to distinguish:

```text
shop is still genuinely uninstalled
```

from:

```text
Shopify has authenticated a reinstall, but Moda deliberately keeps execution disabled until Partner subscription reconciliation succeeds
```

Do not add a new ShopStatus or subscription status.

## Inspect before editing

Repository: `moda-interact-database/`.

Inspect at minimum:

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-lifecycle-schema.mjs
package.json
docs/generated/prisma-erd.puml
```

Read the integrated ARCH-010 DATABASE-001 migration first. `Subscription.nextReconcileAt` is the durable wake-up time and must not be duplicated on Shop.

## Required schema change

Add exactly one nullable field to `commerce.Shop`:

```prisma
reinstallPendingAt DateTime?
```

Add a reconstruction-friendly index equivalent to:

```prisma
@@index([status, reinstallPendingAt])
```

Preserve existing:

```text
status
installedAt
uninstalledAt
```

semantics and data.

## Durable semantics

```text
reinstallPendingAt = NULL
  -> no authenticated reinstall is awaiting subscription reconciliation

Shop.status = UNINSTALLED
AND reinstallPendingAt != NULL
  -> authenticated reinstall has occurred, but all normal shop/customer execution remains disabled until reconciliation completes
```

The field is not Shopify subscription truth and is not an entitlement counter.

`Subscription.nextReconcileAt` remains the scheduling timestamp for the canonical BullMQ reconciliation job.

## Migration requirements

- nullable column, no backfill;
- existing Shops remain valid with NULL;
- no ShopStatus enum change;
- no rewrite of `installedAt` or `uninstalledAt`;
- no Subscription/BillingPeriod/counter/purchase/refund rewrite;
- add the composite/index using the repository's actual PostgreSQL naming conventions.

## Required validation

After inspecting `package.json`, run the repository-declared Prisma format/validate/generate/schema validation commands and `git diff --check`.

Add/update schema validation proving at least:

1. `Shop.reinstallPendingAt` exists and is nullable;
2. existing rows need no backfill;
3. `(status, reinstallPendingAt)` is indexed;
4. ShopStatus still contains exactly the existing lifecycle values unless another accepted task has changed it;
5. `Subscription.nextReconcileAt` remains present and unchanged;
6. migration does not mutate entitlement/purchase/refund data.

Regenerate the repository-owned ERD if that is part of normal schema validation.

## Non-goals

Do not implement:

- auth/reinstall routes;
- Partner API calls;
- BullMQ;
- billing-period rollover;
- shop identity redesign;
- Admin UI;
- subscription history.

## Stop conditions

STOP and return to `moda_architect` if:

- a newer integrated Shop lifecycle model already has an equivalent reinstall/reconciliation marker;
- DATABASE-001 is not integrated and `nextReconcileAt` has materially changed;
- the migration requires a ShopStatus expansion merely to add this marker;
- another repository would need modification from this task.

## Completion Report

### Work Items
- [x] Added the nullable `commerce.Shop.reinstallPendingAt` field and composite reconstruction index.
- [x] Added the additive PostgreSQL migration without backfill or lifecycle/status changes.
- [x] Extended schema validation for Shop marker nullability, index, lifecycle enum preservation, scheduler preservation, and migration safety.
- [x] Regenerated the repository-owned PlantUML ERD.

### Acceptance Criteria
- [x] `Shop.reinstallPendingAt` is nullable and existing Shops remain valid with `NULL`.
- [x] `(status, reinstallPendingAt)` is indexed using `Shop_status_reinstallPendingAt_idx`.
- [x] Existing `status`, `installedAt`, and `uninstalledAt` fields are preserved.
- [x] `ShopStatus` remains exactly `ACTIVE`, `UNINSTALLED`, and `SUSPENDED`.
- [x] `Subscription.nextReconcileAt` remains present and unchanged.
- [x] The migration contains no backfill or entitlement, purchase, refund, BillingPeriod, or reservation mutation.

### Status
Ready for Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260911160000_add_shop_reinstall_reconciliation_marker/migration.sql`
- `scripts/validate-billing-lifecycle-schema.mjs`
- `docs/generated/prisma-erd.puml`

### Work Completed
- Added `Shop.reinstallPendingAt DateTime?` and `@@index([status, reinstallPendingAt])`.
- Added a nullable, no-backfill migration using the repository's PostgreSQL naming convention.
- Added generated-client and migration assertions covering the reinstall marker and preserving the existing lifecycle and reconciliation contracts.
- Regenerated the ERD so the Shop marker is represented.

### Validation Results
- `npm install --no-package-lock`: passed; installed declared dependencies without manifest or lockfile changes.
- `npm run format`: passed.
- `npm run validate`: passed.
- `npm run prisma:generate`: passed; generated Prisma Client 6.19.3.
- `npm run test:billing-lifecycle`: passed; billing lifecycle schema assertions passed.
- `npm run erd:puml`: passed; regenerated `docs/generated/prisma-erd.puml`.
- `git diff --check`: passed.
- `DATABASE_URL="postgresql://postgres:postgres@localhost:5432/moda_interact" npm run status`: reached the intended local database configuration but failed with Prisma `P1001` because PostgreSQL was not running at `localhost:5432`; no migration was applied.

### Deviations
- Migration status could not be inspected because the local PostgreSQL server was unavailable. No destructive or migration-apply command was run.

### Assumptions
- `NULL` remains the absence-of-pending-reinstall marker, and reconciliation scheduling remains owned by `Subscription.nextReconcileAt`.

### Unresolved Issues
- Local PostgreSQL availability is required to complete `npm run status`; this does not affect the additive migration or static/schema validation.

### Architectural Concerns
- None.

### Git / VCS
- Task branch: `task/ARCH-010-DATABASE-003`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-003`
  parent branch: `task/ARCH-010-DATABASE-003`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-003`
  implementation branch: `task/ARCH-010-DATABASE-003`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed; remote task branch did not exist
  parent origin/main incorporated: yes; task worktree was created from current `origin/main`
  implementation remote task branch fast-forwarded: not-needed; remote task branch did not exist
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-database`
  commit: `a6c2af8`
  remote branch: `origin/task/ARCH-010-DATABASE-003`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/database/ARCH-010/DATABASE-003-reinstall-reconciliation-marker.md`
  claim commit: `3948e1e`
  final commit: `2ec0674`
  remote branch: `origin/task/ARCH-010-DATABASE-003`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architect Review
Pending.
