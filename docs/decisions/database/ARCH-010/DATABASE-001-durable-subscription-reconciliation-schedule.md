---
id: ARCH-010-DATABASE-001
architecture_id: ARCH-010
title: Add durable subscription reconciliation scheduling state
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
claimed_at: 2026-09-11T11:42:11Z
attempt: 1
depends_on:
  - ARCH-007-DATABASE-006
  - ARCH-009-DATABASE-001
enables:
  - ARCH-010-BACKGROUND-001
  - ARCH-010-BACKGROUND-016
  - ARCH-010-DATABASE-002
  - ARCH-010-DATABASE-003
  - ARCH-010-SHOPIFY-002
created: 2026-09-11
updated: 2026-09-11T11:45:17Z
---

# ARCH-010-DATABASE-001: Add durable subscription reconciliation scheduling state

## Architecture

Canonical: `docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`.

## Objective

Make pending subscription verification reconstructable after Redis/BullMQ loss by persisting the next reconciliation time on the durable `Subscription` projection.

## Repository / files

Repository: `moda-interact-database/`.

Inspect before editing:

```text
prisma/schema.prisma
scripts/validate-billing-lifecycle-schema.mjs
package.json
```

Also inspect existing migrations and repository migration conventions; do not invent a migration layout.

## Required schema change

Add exactly this scheduler field to `billing.Subscription`:

```prisma
nextReconcileAt DateTime?
```

Add an index suitable for due/pending reconstruction queries:

```prisma
@@index([nextReconcileAt])
```

Do not add a new subscription projection status for "pending activation". The durable initial activation state is represented by:

```text
status = NO_CONTRACT
pendingPlanId != null
pendingShopifyPlanHandle != null
pendingEffectiveAt != null
nextReconcileAt != null
```

Do not change existing pending-plan relations in this task.

## Migration requirements

Create the normal repository migration for the nullable field/index. Existing rows must require no backfill: `NULL` means no scheduled reconciliation is currently required.

The migration must be safe with existing ARCH-007/009 data and must not rewrite or delete Subscription, BillingPeriod, entitlement, purchase, refund or cancellation data.

## Required validation

Run repository-declared Prisma format/validate/migration validation commands after inspecting `package.json`. Run the existing billing lifecycle schema validator if declared/applicable. Run `git diff --check`.

Add/update schema-focused tests/validation proving:

1. `nextReconcileAt` is nullable;
2. existing Subscription rows remain valid with null;
3. the generated client exposes the field;
4. an index exists for `nextReconcileAt`;
5. no new projection status was introduced.

## Non-goals

Do not implement queue code, Shopify calls, retry policy, UI, plan activation, billing-period rollover, credit changes, or migrations for the broader proposed ARCH-010 data model.

## Stop conditions

STOP and return to `moda_architect` if the current integrated schema differs materially from the inspected baseline, the migration would conflict with a newer Subscription redesign, or implementing this field would require modifying another repository.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260911000000_add_subscription_reconciliation_schedule/migration.sql`
- `scripts/validate-billing-lifecycle-schema.mjs`

### Work Completed
- Added nullable `Subscription.nextReconcileAt DateTime?` and `@@index([nextReconcileAt])`.
- Added the additive migration without backfill or changes to existing subscription statuses and pending-plan relations.
- Extended billing schema validation for nullability, generated Prisma client exposure, index presence, and the unchanged `SubscriptionProjectionStatus` values.

### Validation Results
- `npm run format` passed.
- `npm run prisma:generate` passed.
- `npm run validate` passed.
- `npm run test:billing-lifecycle` passed.
- `npm run status` passed and reported the new migration as pending in the configured database.
- `git diff --check` passed.
- `npm ci` installed the repository dependencies in the isolated worktree; npm reported existing audit findings unrelated to this task.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-001`
- Implementation branch: `task/ARCH-010-DATABASE-001`
- Implementation commit: `d3d631b feat(database): add subscription reconciliation schedule`
- Implementation branch pushed to `origin`.
- Parent task claim commit: `8c542a2 chore: claim ARCH-010-DATABASE-001`.
- Parent task branch pushed to `origin`.

### Deviations / Assumptions
- No deviations from the task scope. The configured database was not mutated; migration status was inspected only.

### Architect Review
Pending.