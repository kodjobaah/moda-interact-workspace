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
status: review
priority: 63
executor: null
claimed_at: null
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
Ready for architect review. Attempt 2 completed as the requested evidence/workflow correction; the task is returned to `review` with the claim cleared.

### Attempt 2 Preparation Evidence
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-DATABASE-005`, branch `task/ARCH-023-DATABASE-005`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-DATABASE-005`, branch `task/ARCH-023-DATABASE-005`.
- Both canonical task worktrees were reused. Launcher synchronization reported remote task fast-forward not needed and `origin/main` already current for both worktrees; parent synchronization HEAD was `c086739e3e35c5100bb9c77e56210797a8e379cb`. The parent task claim commit is `2d06b1db3d011482a1b014684441aa118bee698d`.
- Dependency gate passed: `ARCH-023-DATABASE-001` and `ARCH-023-DATABASE-004` were complete.
- Recursive `git submodule sync --recursive` and `git submodule update --init --recursive` passed. Launcher status was ready, recursive true, entries `[]` (no implementation submodules).
- The implementation worktree started at `b34a563436bbc89b6ca3e26b43a0bd03116a1a66` (`feat(database): add Merchant Knowledge lease names`). Its `HEAD` equaled `origin/task/ARCH-023-DATABASE-005`; the worktree was clean before and after validation. This is the existing Attempt 1 implementation commit, already pushed/upstream. No implementation commit was created for Attempt 2 because no implementation changes were needed or authorized.

### Files Changed
Attempt 1 implementation files, unchanged in Attempt 2:
- `prisma/schema.prisma`
- `prisma/migrations/20261001010000_arch023_merchant_knowledge_runtime_leases/migration.sql`
- `scripts/validate-arch023-merchant-knowledge-runtime-leases.mjs`
- `scripts/test-arch023-merchant-knowledge-runtime-leases-postgres.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`
- `docs/generated/erd.png`

Attempt 2 changes only this task report on the parent task branch.

### Work Completed
Attempt 1 added the two exact Merchant Knowledge lease labels to the existing `BackgroundRuntimeLeaseName` enum and the fixed additive migration. Attempt 2 made no schema, migration, validator, package, or generated-artifact changes. The rerun PostgreSQL proof applied the complete migration chain in an invocation-owned, network-isolated `pgvector/pgvector:pg17` container, inserted and verified both labels as `BackgroundRuntimeLease.name` values, cleaned up fixture rows, and removed its container. No cadence columns, lease table columns, business tables, indexes, or constraints were changed.

### Validation Results
All required validations were rerun from the canonical implementation worktree and passed:
- `npm run format` completed; no working-tree changes resulted.
- `npm run validate` passed; Prisma reported the schema valid.
- `npm run prisma:generate` passed with Prisma Client v6.19.3.
- `npm run test:arch023-merchant-knowledge-runtime-leases` passed the focused static contract.
- `npm run test:arch023-merchant-knowledge-runtime-leases:postgres` passed. It applied migrations through `20261001010000_arch023_merchant_knowledge_runtime_leases`, accepted and verified both enum labels on `BackgroundRuntimeLease.name`, cleaned fixture rows, and logged removal of its invocation-owned isolated container. Initial connection-not-ready messages were emitted during container startup and did not affect the successful proof.
- `npm run erd` completed successfully; ERD generation left the implementation worktree clean.
- `node --check scripts/validate-arch023-merchant-knowledge-runtime-leases.mjs` passed (exit 0).
- `node --check scripts/test-arch023-merchant-knowledge-runtime-leases-postgres.mjs` passed (exit 0).
- Changed-file diagnostics reported no errors for `prisma/schema.prisma`, both new scripts, and `package.json`.
- `git diff --check` passed (exit 0).
- Final implementation status was clean, and implementation `HEAD` still equaled its upstream task branch at `b34a563436bbc89b6ca3e26b43a0bd03116a1a66`.

Prisma printed an informational notice that a newer major/RC release is available; it was not a validation failure.

### Deviations
None. No implementation changes or additional implementation commit were required; the normal `npm run erd` workflow regenerated artifacts without leaving changes.

### Assumptions
The fixed scheduler cadence mapping remains owned by `ARCH-023-BACKGROUND-007`; this task adds enum labels only.

### Unresolved Issues
None. No new baseline issue or blocker appeared during Attempt 2 validation.

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
