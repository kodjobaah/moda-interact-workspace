---
id: ARCH-010-DATABASE-008
architecture_id: ARCH-010
title: Persist Shopify subscription freeze projection and lifecycle evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 19
executor: copilot
claimed_at: 2026-09-11T12:58:56Z
attempt: 2
depends_on: []
enables:
  - ARCH-010-BACKGROUND-016
  - ARCH-010-SHOPIFY-018
created: 2026-09-11
updated: 2026-09-11T12:58:56Z
---

# ARCH-010-DATABASE-008: Persist Shopify subscription freeze projection and lifecycle evidence

## Objective

Add the minimum durable vocabulary needed to distinguish a temporary Shopify App Pricing freeze from cancellation and to retain the latest provider lifecycle evidence used by reconciliation.

This task is schema/migration only. It does not query Shopify and does not implement runtime transitions.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
existing SubscriptionProjectionStatus
billing.Subscription
DATABASE-001 nextReconcileAt task definition
DATABASE-004 BillingPeriod lifecycle task definition
package.json validation scripts
```

## Required schema changes

### 1. Subscription projection status

Extend the existing enum exactly with:

```prisma
FROZEN
```

Do not rename/remove existing values:

```text
ACTIVE
TRIALING
NO_CONTRACT
UNMAPPED
SYNC_ERROR
```

`FROZEN` means Shopify has temporarily frozen the merchant's app subscription because of a provider/store billing lifecycle event. It is not cancellation and not a shop-installation status.

### 2. Provider lifecycle evidence

Add one provider-lifecycle enum equivalent to Shopify's persisted states:

```prisma
enum ProviderSubscriptionLifecycleState {
  CREATED
  UPDATED
  CANCELLATION_SCHEDULED
  CANCELED
  FROZEN
  UNFROZEN

  @@schema("billing")
}
```

Add nullable fields to `Subscription` equivalent to:

```prisma
lastProviderLifecycleState   ProviderSubscriptionLifecycleState?
lastProviderLifecycleEventId String?
lastProviderLifecycleEventAt DateTime?
```

Use repository naming conventions if needed, but keep one clear state/id/time triplet. Do not store arbitrary provider JSON.

These fields are evidence/audit inputs for reconciliation. `Subscription.status` remains the operational local projection.

## Migration rules

1. Existing Subscription rows keep their current `status` unchanged.
2. Do NOT infer/backfill `FROZEN` from `NO_CONTRACT`, `SYNC_ERROR`, historical BillingPeriods, or timestamps.
3. New lifecycle evidence fields are null for existing rows unless exact evidence already exists in a durable provider-event table (none is assumed).
4. Do not modify current plan, BillingPeriod, counters, pending plan state or cancellation flags.
5. Do not create a BillingPeriod.
6. Do not reset `nextReconcileAt`.

## Constraints

No uniqueness constraint is required on provider lifecycle event ID. The runtime must use event ID/time idempotently but historical Shopify event IDs are provider identifiers, not Moda business keys.

No new status index is required solely for `FROZEN`; DATABASE-001's scheduling/index work owns `nextReconcileAt`. Add an index only if the final Prisma query plan demonstrably requires it and document why.

## Required tests / validation

At minimum prove:

1. Prisma accepts `SubscriptionProjectionStatus.FROZEN`;
2. the provider lifecycle enum contains exactly the required states;
3. existing rows migrate without status changes;
4. lifecycle fields are nullable and preserve null for legacy rows;
5. no entitlement/counter/BillingPeriod data is changed by the migration;
6. generated Prisma client exposes the new enum/fields;
7. `prisma format`, `prisma validate`, repository-declared migration/schema tests and `git diff --check` pass.

## Non-goals

No Shopify API query, no Background transition, no merchant UI, no Admin UI, no billing-period rollover and no cancellation implementation.

## Stop conditions

STOP if another accepted/integrated migration has already introduced an equivalent frozen projection or provider lifecycle fields with different names. Report the exact overlap to `moda_architect`; do not create duplicate state.

## Completion Report

### Status
In Progress — Attempt 2 conflict-resolution retry

### Files Changed
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260911140000_add_subscription_provider_lifecycle_evidence/migration.sql`
- `moda-interact-database/scripts/validate-billing-lifecycle-schema.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`

### Work Completed
- Added `SubscriptionProjectionStatus.FROZEN` without removing or renaming existing projection states.
- Added the exact `ProviderSubscriptionLifecycleState` enum values: `CREATED`, `UPDATED`, `CANCELLATION_SCHEDULED`, `CANCELED`, `FROZEN`, and `UNFROZEN`.
- Added nullable provider lifecycle state, event ID, and event timestamp fields to `Subscription`; existing `nextReconcileAt` scheduling state remains unchanged.
- Added an additive migration that creates the provider enum, appends `FROZEN`, and adds nullable evidence columns. It performs no data backfill, status inference, BillingPeriod/counter/entitlement changes, or event-ID uniqueness changes.
- Extended the billing lifecycle validator for exact enum values, nullable schema/DMMF fields, migration evidence, and destructive-change guards.
- Regenerated the repository PlantUML ERD.

### Validation Results
- `npm ci` completed; npm reported three high-severity audit findings in the existing dependency tree and install-script approval warnings.
- `npm run format` passed.
- `npm run validate` passed.
- `npm run prisma:generate` passed with Prisma 6.19.3.
- `npm run test:recovery-credit-packs` passed.
- `npm run test:billing-lifecycle` passed, including FROZEN/provider enum, nullable DMMF, migration, and no-unrelated-mutation assertions.
- `npm run erd:puml` passed.
- `git diff --check` passed.
- `npm run status` was inspection-only; DATABASE-001 and DATABASE-008 migrations remain pending and were not applied.

### Git / VCS
Task branch: `task/ARCH-010-DATABASE-008`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-008`
  parent branch: `task/ARCH-010-DATABASE-008`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-008`
  implementation branch: `task/ARCH-010-DATABASE-008`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-database`
  commit: `14e0281`
  remote branch: `origin/task/ARCH-010-DATABASE-008`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/database/ARCH-010/DATABASE-008-shopify-subscription-freeze-state.md`
  claim commit: `3cb2d53`
  claim remote branch: `origin/task/ARCH-010-DATABASE-008`
  claim pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architect Review
Pending
