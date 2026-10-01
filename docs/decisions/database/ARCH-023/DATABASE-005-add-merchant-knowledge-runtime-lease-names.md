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
status: in_progress
priority: 63
executor: copilot
claimed_at: 2026-10-01T08:30:33Z
attempt: 2
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

- [x] Extend `BackgroundRuntimeLeaseName` with both exact values.
- [x] Add the fixed forward-only enum migration.
- [x] Add focused static validation.
- [x] Add disposable PostgreSQL migration/runtime proof.
- [x] Regenerate schema documentation if required by the normal schema workflow.

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

- [x] Both exact Merchant Knowledge lease names are valid Prisma/PostgreSQL enum values.
- [x] Existing lease names remain unchanged.
- [x] Migration is additive and enum-only.
- [x] No cadence/runtime/business-state schema is introduced.
- [x] Disposable PostgreSQL proof passes and owned infrastructure is removed.

## Validation

- [x] repository format command: `npm run format`
- [x] Prisma validate: `npm run validate`
- [x] Prisma generate: `npm run prisma:generate`
- [x] focused ARCH-023 lease-name validator: passed
- [x] disposable PostgreSQL migration/runtime proof: passed
- [x] generated ERD validation: `npm run erd` completed
- [x] `git diff --check`

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin BACKGROUND-007.

## Implementation Notes

This task must not solve the Background runtime cadence mapping. Enum ownership is the only missing database capability.

## Completion Report

### Status
Ready for architect review.

### Files Changed
Implementation changes:
- `prisma/schema.prisma`
- `prisma/migrations/20261001010000_arch023_merchant_knowledge_runtime_leases/migration.sql`
- `scripts/validate-arch023-merchant-knowledge-runtime-leases.mjs`
- `scripts/test-arch023-merchant-knowledge-runtime-leases-postgres.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`
- `docs/generated/erd.png`

### Work Completed
Added the two exact Merchant Knowledge lease labels to the existing `BackgroundRuntimeLeaseName` enum and the fixed additive migration. The static validator confirms the full expected enum value set and exact enum-only migration text. The PostgreSQL proof applied the complete migration chain in an invocation-owned, network-isolated `pgvector/pgvector:pg17` container, inserted both enum labels as lease rows, verified them, deleted the fixture rows, and removed the container. No cadence columns, lease table columns, business tables, indexes, or constraints were changed.

### Validation Results
Passed:
- `npm run format`
- `npm run validate`
- `npm run prisma:generate`
- `npm run test:arch023-merchant-knowledge-runtime-leases`
- `npm run test:arch023-merchant-knowledge-runtime-leases:postgres`
- `npm run erd`
- `node --check` for both new scripts
- changed-file diagnostics: no errors
- `git diff --check`

The disposable PostgreSQL proof applied migrations through `20261001010000_arch023_merchant_knowledge_runtime_leases`; both labels were accepted by PostgreSQL and persisted on `BackgroundRuntimeLease.name`. The invocation-owned container was removed in cleanup.

### Deviations
None. The ERD artifacts were regenerated by the repository's normal `npm run erd` workflow.

### Assumptions
The fixed scheduler cadence mapping remains owned by `ARCH-023-BACKGROUND-007`; this task adds enum labels only.

### Unresolved Issues
None.

### Architectural Concerns
None. No runtime cadence or business-state schema was introduced.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes
The database implementation is substantively architecture-conformant and no source/schema correction is requested. The Prisma enum adds exactly `MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION` and `MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP`; `FeatureActivationMode` remains unchanged; and the migration contains only the two additive `ALTER TYPE ... ADD VALUE IF NOT EXISTS` statements required by this task. The focused static validator and disposable PostgreSQL proof are appropriately bounded to the accepted enum-only contract.

Acceptance is withheld only because the durable Completion Report does not record the mandatory launcher/preparation provenance required for repository-task review. The report must contain the launcher-resolved parent and implementation worktree paths and branches, start-of-attempt synchronization evidence for both worktrees, and recursive submodule preparation/status evidence. A conversational handoff that the branches are clean and pushed does not substitute for this durable evidence.

Attempt 2 is therefore an evidence/workflow correction. Do not change database implementation source merely to manufacture a new implementation commit. Reclaim the same task through `/moda-task ARCH-023-DATABASE-005`, record the prepared execution packet in the Completion Report, rerun the task-defined validation from the canonical prepared implementation worktree, and return the task to review. Source changes are authorised only if the refreshed baseline/validation exposes a real regression.

### Reviewed Files
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261001010000_arch023_merchant_knowledge_runtime_leases/migration.sql`
- `moda-interact-database/scripts/validate-arch023-merchant-knowledge-runtime-leases.mjs`
- `moda-interact-database/scripts/test-arch023-merchant-knowledge-runtime-leases-postgres.mjs`
- `moda-interact-database/package.json`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `docs/decisions/database/ARCH-023/DATABASE-005-add-merchant-knowledge-runtime-lease-names.md`

### Validation Reviewed
Reviewed the recorded passing format, Prisma validate/generate, focused static validator, disposable `pgvector/pgvector:pg17` migration/runtime proof, ERD generation, script syntax checks, changed-file diagnostics and `git diff --check`. The review archive confirms the exact schema/migration/test implementation but does not carry the developer's live Git/Docker execution environment, so these commands were not redundantly rerun by the architect.

### Architecture Conformance
Implementation semantics conform to the ARCH-023 ownership boundary: Database owns only the two representable lease identities; no cadence mapping, `BackgroundRuntimeConfig` field, business table, index or constraint is introduced. `ARCH-023-BACKGROUND-007` remains the owner of the 60-second / 3600-second runtime cadence mapping. Workflow acceptance remains open solely for the missing durable preparation evidence.

### Follow-up
Return this same task to `ready` with `attempt: 1` preserved and the claim cleared. Attempt 2 must record exact launcher-resolved worktree/branch, synchronization and recursive-submodule evidence, rerun the task-defined validation from that prepared implementation worktree, then return to `review`. `ARCH-023-BACKGROUND-007` remains Pending and `ARCH-023-BACKGROUND-004` remains Blocked until DATABASE-005 is architect-accepted Complete.
