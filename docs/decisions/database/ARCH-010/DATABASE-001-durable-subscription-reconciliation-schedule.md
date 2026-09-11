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
status: in_progress
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
updated: 2026-09-11T11:42:11Z
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
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.