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
status: ready
priority: 10
executor:
claimed_at:
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
updated: 2026-09-11T12:00:53Z
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

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested (workflow evidence only)

The implementation itself is architecturally conformant. No source, schema, migration, or validator correction is required by this review.

Architect inspection verified:

- `billing.Subscription.nextReconcileAt` is added exactly as nullable `DateTime?`;
- `@@index([nextReconcileAt])` is present;
- the migration is additive and nullable, with no backfill, status rewrite, or billing-data mutation;
- `SubscriptionProjectionStatus` remains exactly `ACTIVE`, `TRIALING`, `NO_CONTRACT`, `UNMAPPED`, `SYNC_ERROR`;
- the billing lifecycle validator checks schema nullability, generated Prisma-client/DMMF exposure, index presence, migration DDL, and unchanged projection-status vocabulary;
- comparison with the pre-task repository snapshot found no unrelated implementation changes beyond the schema, migration, and validator listed in the Completion Report.

The task cannot be accepted yet because the Completion Report does not contain the mandatory physical-worktree and start-of-attempt synchronization evidence required by `docs/agent-worktree-isolation-policy.md`.

Attempt 2 is therefore evidence/workflow remediation only. Do **not** make code churn merely to create another implementation commit.

##### Required correction 1 — record complete physical worktree isolation evidence

Update the Completion Report to record the launcher-resolved values for all of the following:

```text
Physical worktree isolation:
  canonical workspace root: <absolute launcher-resolved path>
  parent worktree: <absolute launcher-resolved path>
  parent branch: task/ARCH-010-DATABASE-001
  implementation worktree: <absolute launcher-resolved path>
  implementation branch: task/ARCH-010-DATABASE-001
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no
```

The Attempt 1 report currently identifies only the implementation worktree/branch. Branch cleanliness and a pushed implementation branch do not substitute for the missing parent-worktree/isolation evidence.

##### Required correction 2 — perform and record Attempt 2 synchronization

On reclaim, use the same canonical parent and implementation task worktrees and perform the mandatory start-of-attempt synchronization for **both** repositories before any report update or validation:

```text
Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

If either canonical worktree cannot be established with the expected repository/branch mapping, STOP and report `MODA_WORKTREE_ISOLATION_ERROR` rather than using a shared/default checkout.

##### Required correction 3 — rerun the task validation from the canonical implementation worktree

After Attempt 2 synchronization, rerun the task-required validation from the canonical `moda-interact-database` implementation worktree and record the results:

```text
npm run format
npm run prisma:generate
npm run validate
npm run test:billing-lifecycle
npm run status
git diff --check
```

`npm run status` remains inspection-only; do not apply the migration to the configured database merely for this review.

If the already-pushed implementation commit remains unchanged after synchronization, no replacement implementation commit is required. Push only any branch synchronization commit that is actually necessary. The parent task branch must receive the corrected Completion Report and return to `status: review` for architect review.

#### Independent review validation note

The architect directly inspected the submitted schema, migration, validator, package scripts, and pre-task vs submitted repository diff. A fresh package/Prisma execution in the review container did not complete within the review timeout, so the successful executable validation remains supported by the agent's recorded results; this timeout is **not** a code finding and is not part of the Changes Requested scope.