---
id: ARCH-023-DATABASE-006
architecture_id: ARCH-023
title: Add Merchant Knowledge entitlement reconciliation lease name
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 64
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-005
enables:
  - ARCH-023-BACKGROUND-005
created: 2026-10-01
updated: 2026-10-01
---

# Add Merchant Knowledge entitlement reconciliation lease name

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the existing database-owned `public.BackgroundRuntimeLeaseName` enum with the one exact lease identity required by the Merchant Knowledge entitlement-reconciliation scheduler, without changing cadence configuration, runtime lease behavior or any business schema.

## Context

`ARCH-023-BACKGROUND-005` Attempt 1 stopped at the database ownership boundary because its scheduler requires this distinct persisted lease identity:

```text
MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION
```

The pinned database contract does not currently define that enum value, so the generated Prisma type rejects the Background scheduler. Existing Merchant Knowledge lease names are not safe substitutes because they represent different periodic jobs and cadences.

`ARCH-023-DATABASE-005` already established the two lease identities required by BACKGROUND-004. This task is a later, single-value enum-only extension. The corresponding fixed 300-second cadence remains owned by `ARCH-023-BACKGROUND-005` and must not be introduced here.

## Scope

Modify only database-owned schema/migration/validation/generated artifacts required to add the one enum value.

Primary files:

```text
prisma/schema.prisma
prisma/migrations/20261001120000_arch023_merchant_knowledge_entitlement_reconciliation_lease/migration.sql
scripts/validate-arch023-merchant-knowledge-entitlement-reconciliation-lease.mjs
scripts/test-arch023-merchant-knowledge-entitlement-reconciliation-lease-postgres.mjs
package.json
docs/generated/prisma-erd.puml
docs/generated/erd.png
```

Generated ERD files are required only when the repository's normal schema workflow changes them.

## Out of Scope

- Background lease cadence mappings or scheduler intervals.
- `BackgroundRuntimeConfig` columns.
- `BackgroundRuntimeLeaseService` acquisition/release SQL or cadence `CASE` changes.
- Merchant Knowledge entitlement-reconciliation service/entrypoint implementation.
- Redis locks, PostgreSQL advisory locks or another scheduler mechanism.
- Merchant Knowledge business tables, vectors or content lifecycle schema.
- Commerce, Shopify, Admin or Gateway changes.

## Requirements

### R1 — exact enum extension

Extend only:

```prisma
enum BackgroundRuntimeLeaseName {
  ...existing values...
  MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION

  @@schema("public")
}
```

Preserve every existing enum value unchanged, including the two Merchant Knowledge values introduced by `ARCH-023-DATABASE-005`.

### R2 — exact forward migration

Create exactly:

```text
prisma/migrations/20261001120000_arch023_merchant_knowledge_entitlement_reconciliation_lease/migration.sql
```

It must add only this value to `public.BackgroundRuntimeLeaseName`:

```sql
ALTER TYPE "public"."BackgroundRuntimeLeaseName"
  ADD VALUE IF NOT EXISTS 'MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION';
```

Do not recreate the enum/table and do not modify existing rows.

### R3 — no cadence schema or runtime behavior

Do not add interval/cadence fields to `BackgroundRuntimeConfig` or modify database runtime-lease acquisition behavior.

The required scheduler cadence is a Background-owned runtime semantic in `ARCH-023-BACKGROUND-005`:

```text
MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION -> 300 seconds
```

### R4 — static validation

Add a focused validator proving:

- the exact enum value exists in `schema.prisma`;
- the fixed migration directory exists;
- the migration adds exactly this one value to the existing enum;
- all pre-existing `BackgroundRuntimeLeaseName` values remain present;
- `FeatureActivationMode` is unchanged;
- no `BackgroundRuntimeConfig`, `BackgroundRuntimeLease` column, business table, index or constraint is changed by this migration.

Add one package command for this validator using the repository's existing ARCH-023 naming convention.

### R5 — disposable PostgreSQL proof

Using the repository-approved disposable PostgreSQL/pgvector mechanism, apply the complete accepted migration chain and prove PostgreSQL accepts:

```text
MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION
```

as a `BackgroundRuntimeLease.name` value.

The proof must also confirm the three Merchant Knowledge lease values coexist after the full migration chain:

```text
MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION
MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP
MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION
```

Clean up task-owned test rows and the disposable database/container afterward. Do not use or mutate an unverified developer database.

## Work Items

- [ ] Extend `BackgroundRuntimeLeaseName` with the exact entitlement-reconciliation value.
- [ ] Add the fixed forward-only enum migration.
- [ ] Add focused static validation.
- [ ] Add disposable PostgreSQL migration/runtime proof.
- [ ] Regenerate schema documentation if required by the repository's normal schema workflow.

## Interfaces / Contracts

Produces the database-owned enum contract consumed by:

```text
ARCH-023-BACKGROUND-005
```

No cross-service payload contract changes.

## Dependencies

- `ARCH-023-DATABASE-005`

## Enables

- `ARCH-023-BACKGROUND-005`

## Acceptance Criteria

- [ ] `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION` is a valid Prisma/PostgreSQL `BackgroundRuntimeLeaseName` value.
- [ ] Every existing lease name remains unchanged.
- [ ] Migration is additive and enum-only.
- [ ] `FeatureActivationMode` remains unchanged.
- [ ] No cadence/runtime/business-state schema is introduced.
- [ ] Disposable PostgreSQL proof passes and owned infrastructure is removed.

## Validation

- [ ] repository format command
- [ ] Prisma validate
- [ ] Prisma generate
- [ ] focused ARCH-023 entitlement-reconciliation lease validator
- [ ] disposable PostgreSQL migration/runtime proof
- [ ] generated ERD validation where required by the normal schema workflow
- [ ] task script syntax checks
- [ ] changed-file diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin `ARCH-023-BACKGROUND-005`.

## Implementation Notes

This task exists only because the lease identity is a database-owned persisted enum contract. The Background scheduler already owns the job itself and will own its exact 300-second cadence after this task is accepted.

Do not copy unrelated Prisma drift into this migration. If Prisma migration generation proposes unrelated index drops, default changes, FK renames, enum values or other schema operations, exclude them and keep this migration bounded to the one required `ALTER TYPE` statement.

## Completion Report

### Status
Not Started

### Files Changed
None

### Work Completed
None

### Validation Results
None

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
Pending.

### Reviewed Files
Pending.

### Validation Reviewed
Pending.

### Architecture Conformance
Pending.

### Follow-up
Pending.
