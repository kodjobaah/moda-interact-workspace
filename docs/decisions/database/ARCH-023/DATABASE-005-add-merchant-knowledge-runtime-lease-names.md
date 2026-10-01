---
id: ARCH-023-DATABASE-005
architecture_id: ARCH-023
title: Add Merchant Knowledge runtime lease names
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 63
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-DATABASE-004
enables:
  - ARCH-023-BACKGROUND-007
created: 2026-10-01
updated: 2026-10-01
---

# Add Merchant Knowledge runtime lease names

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the existing database-owned `public.BackgroundRuntimeLeaseName` enum with the two exact lease identities required by the accepted Merchant Knowledge worker scheduling design, without changing runtime cadence configuration or any business table.

## Context

`ARCH-023-BACKGROUND-004` Attempt 1 proved that its final dedicated entrypoint cannot safely compile/run against the pinned database contract because these exact names do not exist:

```text
MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION
MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP
```

The lease table/runtime model already exists and remains the approved distributed scheduler mechanism. This task only makes those two identities representable in PostgreSQL/Prisma. `ARCH-023-BACKGROUND-007` owns the runtime cadence mapping after this task is accepted.

## Scope

Modify only database-owned schema/migration/validation/generated artifacts required to add the two enum values.

Primary files:

```text
prisma/schema.prisma
prisma/migrations/20261001010000_arch023_merchant_knowledge_runtime_leases/migration.sql
scripts/validate-arch023-merchant-knowledge-runtime-leases.mjs
scripts/test-arch023-merchant-knowledge-runtime-leases-postgres.mjs
package.json
docs/generated/prisma-erd.puml
docs/generated/erd.png
```

Generated ERD files are required only when the repository's normal schema workflow changes them.

## Out of Scope

- `BackgroundRuntimeConfig` columns or cadence values.
- Background lease acquisition/release SQL.
- Merchant Knowledge entrypoint/schedulers.
- Redis/advisory locks or another scheduler mechanism.
- Merchant Knowledge persistence tables.
- Commerce, Shopify, Admin or Gateway changes.

## Requirements

### R1 — exact enum extension

Extend only:

```prisma
enum BackgroundRuntimeLeaseName {
  ...existing values...
  MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION
  MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP

  @@schema("public")
}
```

Preserve every existing enum value unchanged.

### R2 — exact forward migration

Create exactly:

```text
prisma/migrations/20261001010000_arch023_merchant_knowledge_runtime_leases/migration.sql
```

It must add only the two values to `public.BackgroundRuntimeLeaseName`:

```sql
ALTER TYPE "public"."BackgroundRuntimeLeaseName"
  ADD VALUE IF NOT EXISTS 'MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION';

ALTER TYPE "public"."BackgroundRuntimeLeaseName"
  ADD VALUE IF NOT EXISTS 'MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP';
```

Do not recreate the enum/table and do not modify existing rows.

### R3 — no cadence schema

Do not add Merchant Knowledge interval columns to `BackgroundRuntimeConfig`. The agreed scheduler intervals are fixed runtime semantics owned by `ARCH-023-BACKGROUND-007`:

```text
PENDING reconciliation: 60 seconds
upload cleanup:          3600 seconds
```

### R4 — static validation

Add a focused validator proving:

- both exact enum values exist in `schema.prisma`;
- the fixed migration directory exists;
- the migration adds exactly those two values to the existing enum;
- no enum value is removed/renamed;
- no `BackgroundRuntimeConfig`, `BackgroundRuntimeLease` column, business table, index or constraint is changed by this migration.

Add one package command for this validator using the repository's existing naming convention.

### R5 — disposable PostgreSQL proof

Using the repository-approved disposable PostgreSQL/pgvector mechanism, apply the complete accepted migration chain and prove PostgreSQL accepts both exact enum labels as `BackgroundRuntimeLease.name` values. Clean up test rows and the task-owned database/container afterward.

Do not use or mutate an unverified developer database.

## Work Items

- [ ] Extend `BackgroundRuntimeLeaseName` with both exact values.
- [ ] Add the fixed forward-only enum migration.
- [ ] Add focused static validation.
- [ ] Add disposable PostgreSQL migration/runtime proof.
- [ ] Regenerate schema documentation if required by the normal repository workflow.

## Interfaces / Contracts

Produces the database-owned enum contract consumed by:

```text
ARCH-023-BACKGROUND-007
  -> ARCH-023-BACKGROUND-004
```

No cross-service payload contract changes.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-DATABASE-004`

## Enables

- `ARCH-023-BACKGROUND-007`

## Acceptance Criteria

- [ ] Both exact Merchant Knowledge lease names are valid Prisma/PostgreSQL enum values.
- [ ] Existing lease names remain unchanged.
- [ ] Migration is additive and enum-only.
- [ ] No cadence/runtime/business-state schema is introduced.
- [ ] Disposable PostgreSQL proof passes and owned infrastructure is removed.

## Validation

- [ ] repository format command
- [ ] Prisma validate
- [ ] Prisma generate
- [ ] focused ARCH-023 lease-name validator
- [ ] disposable PostgreSQL migration/runtime proof
- [ ] generated ERD validation if required
- [ ] `git diff --check`

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin BACKGROUND-007.

## Implementation Notes

This task must not solve the Background runtime cadence mapping. Enum ownership is the only missing database capability.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
None.

### Deviations
None.

### Assumptions
None.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status
Pending

### Review Notes
Pending.

### Reviewed Files
Pending.

### Validation Reviewed
Pending.

### Architecture Conformance
Pending.

### Follow-up
Pending.
