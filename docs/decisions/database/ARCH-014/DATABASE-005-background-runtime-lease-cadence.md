---
id: ARCH-014-DATABASE-005
architecture_id: ARCH-014
title: Persist global scheduler cadence state on background runtime leases
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 67
executor: copilot
claimed_at: 2026-09-16T10:49:44Z
attempt: 1
depends_on:
- ARCH-014-DATABASE-004
enables:
- ARCH-014-BACKGROUND-006
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-DATABASE-005

## Objective

Close the horizontal-scaling gap discovered after `ARCH-014-DATABASE-004`: a lease currently proves exclusive ownership only while work is running, but the database does not remember when the previous **global cycle finished**. When two worker replicas have skewed local timers, they can therefore run the same global job twice within one configured cadence window without overlapping.

Persist the finish time on the existing ARCH-014 lease row so Background can enforce one global cadence window across replicas.

This task is intentionally narrow. It changes only the ARCH-014-created `public.BackgroundRuntimeLease` table and generated/database validation artifacts.

## Binding GPT-5.6 Luna rule

Do not redesign runtime configuration, add another scheduler table, add Redis coordination, or alter any pre-ARCH-014 business table. The architectural decision is already made: **retain one lease row per lease name and add `lastFinishedAt` to that row**.

## Required Prisma change

In:

```text
prisma/schema.prisma
```

change only `BackgroundRuntimeLease` by adding:

```prisma
lastFinishedAt DateTime?
```

The resulting model must retain the existing fields exactly:

```prisma
model BackgroundRuntimeLease {
  name BackgroundRuntimeLeaseName @id

  ownerToken String
  generation Int @default(0)

  acquiredAt     DateTime
  heartbeatAt    DateTime
  leaseUntil     DateTime
  lastFinishedAt DateTime?
  updatedAt      DateTime @updatedAt

  @@index([leaseUntil])
  @@schema("public")
}
```

Do not rename `leaseUntil`, `heartbeatAt`, `ownerToken`, `generation`, or the enum.

## Exact migration

Create exactly one additive migration after the current `20260916083000_arch015_refund_correction_evidence` migration:

```text
prisma/migrations/20260916110000_arch014_background_runtime_lease_cadence/migration.sql
```

Its application-schema change must be only:

```sql
ALTER TABLE "public"."BackgroundRuntimeLease"
ADD COLUMN "lastFinishedAt" TIMESTAMP(3);
```

No default. No `NOT NULL`. No seed/update/backfill. Existing lease rows may legitimately have no completed-cycle history and must therefore start with `NULL`.

Do not add another index: the lease is selected by primary-key `name`; cadence eligibility is evaluated against that one row.

## Why `NULL` is required

The semantics are binding:

```text
lastFinishedAt = NULL
    no completed global cycle is recorded yet
    first eligible owner may run immediately

lastFinishedAt = timestamp
    the most recent valid global cycle ended at that PostgreSQL time
```

The Background correction task will retain the row on release and update this column with PostgreSQL `NOW()`.

## Static validator update

Update:

```text
scripts/validate-arch014-background-runtime-config.mjs
```

Add assertions proving:

1. `BackgroundRuntimeLease` contains exact `lastFinishedAt DateTime?`;
2. migration directory `20260916110000_arch014_background_runtime_lease_cadence` exists;
3. that migration adds only `lastFinishedAt` to `public.BackgroundRuntimeLease`;
4. the migration does not alter `BackgroundRuntimeConfig`, `BackgroundRuntimeConfigAuditEvent`, `BillingPlan`, `Subscription`, `UsageEvent`, promotion tables, merchant-pricing tables, support tables, Shopify tables or WhatsApp tables;
5. no default/backfill/seed is introduced for `lastFinishedAt`;
6. the generated ERD contains `BackgroundRuntimeLease.lastFinishedAt`.

Do not weaken any existing DATABASE-004 validator assertion.

## Generated documentation

Regenerate:

```text
docs/generated/prisma-erd.puml
docs/generated/erd.png
```

Do not hand-edit generated ERD output.

## Required validation commands

Run from `moda-interact-database`:

```bash
npm run format
npm run prisma:validate
npm run prisma:generate
node scripts/validate-arch014-background-runtime-config.mjs
npm run erd:puml
npm run erd:png
git diff --check
```

Also run:

```bash
npm run status
npm run migrate:deploy
```

against the disposable/test database if available.

The snapshot used to define this task previously contained migration-history problems during DATABASE-004 work. If `migrate:deploy` is blocked by an unrelated pre-existing failed migration, record the exact Prisma code/migration name and STOP migration repair; do not reset or resolve unrelated history inside this task.

## Acceptance tests / proof

The Completion Report must show:

```text
Prisma model has nullable lastFinishedAt
migration is additive and lease-only
static validator passes
Prisma validate/generate pass
ERD regenerated
migrate deploy result or exact external blocker
```

## Non-goals

Do not implement lease acquisition/release logic here. Do not add `nextRunAt`, `intervalSeconds`, `configVersion`, scheduler owner state, cron state or queue-concurrency state to the table. `BACKGROUND-006` owns runtime semantics.

## Stop conditions

STOP and return to `moda_architect` if:

- `ARCH-014-DATABASE-004` is not present/accepted;
- the current schema no longer contains the exact lease model this task extends;
- another migration has already introduced an equivalent cadence column under a different name;
- implementation appears to require changing any table other than `BackgroundRuntimeLease`.
