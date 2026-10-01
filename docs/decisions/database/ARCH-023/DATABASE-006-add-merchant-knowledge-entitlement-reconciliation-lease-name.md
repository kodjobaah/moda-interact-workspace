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
status: complete
priority: 64
executor: null
claimed_at: null
attempt: 1
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

- [x] Extend `BackgroundRuntimeLeaseName` with the exact entitlement-reconciliation value.
- [x] Add the fixed forward-only enum migration.
- [x] Add focused static validation.
- [x] Add disposable PostgreSQL migration/runtime proof.
- [x] Regenerate schema documentation if required by the repository's normal schema workflow.

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

- [x] `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION` is a valid Prisma/PostgreSQL `BackgroundRuntimeLeaseName` value.
- [x] Every existing lease name remains unchanged.
- [x] Migration is additive and enum-only.
- [x] `FeatureActivationMode` remains unchanged.
- [x] No cadence/runtime/business-state schema is introduced.
- [x] Disposable PostgreSQL proof passes and owned infrastructure is removed.

## Validation

- [x] repository format command
- [x] Prisma validate
- [x] Prisma generate
- [x] focused ARCH-023 entitlement-reconciliation lease validator
- [x] disposable PostgreSQL migration/runtime proof
- [x] generated ERD validation where required by the normal schema workflow
- [x] task script syntax checks
- [x] changed-file diagnostics (scripts and package manifest clean; editor reports the pre-existing `datasource.url` Prisma 7 compatibility diagnostic, while repository Prisma 6 validation passes)
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin `ARCH-023-BACKGROUND-005`.

## Implementation Notes

This task exists only because the lease identity is a database-owned persisted enum contract. The Background scheduler already owns the job itself and will own its exact 300-second cadence after this task is accepted.

Do not copy unrelated Prisma drift into this migration. If Prisma migration generation proposes unrelated index drops, default changes, FK renames, enum values or other schema operations, exclude them and keep this migration bounded to the one required `ALTER TYPE` statement.

## Completion Report

### Status
Complete; submitted for architect review.

### Files Changed
`moda-interact-database/prisma/schema.prisma`; `moda-interact-database/prisma/migrations/20261001120000_arch023_merchant_knowledge_entitlement_reconciliation_lease/migration.sql`; `moda-interact-database/scripts/validate-arch023-merchant-knowledge-entitlement-reconciliation-lease.mjs`; `moda-interact-database/scripts/test-arch023-merchant-knowledge-entitlement-reconciliation-lease-postgres.mjs`; `moda-interact-database/package.json`; `moda-interact-database/docs/generated/prisma-erd.puml`; `moda-interact-database/docs/generated/erd.png`.

### Work Completed
Added the single `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION` label to `BackgroundRuntimeLeaseName` and an additive migration containing only the requested `ALTER TYPE ... ADD VALUE IF NOT EXISTS`. Added a focused static validator that pins the complete lease-label list, unchanged `FeatureActivationMode` values, fixed migration directory and exact one-statement migration. Added a network-isolated disposable `pgvector/pgvector:pg17` proof that applies the complete migration chain, inserts and verifies all three Merchant Knowledge lease labels as `BackgroundRuntimeLease.name`, removes its test rows, and removes its invocation-owned container. Added ARCH-023 package commands and regenerated the ERD through the repository's normal workflow. No cadence, runtime lease SQL, configuration columns or business schema were changed.

### Validation Results
Passed: `npm run format`; `npm run prisma:validate`; `npm run prisma:generate`; `npm run test:arch023-merchant-knowledge-entitlement-reconciliation-lease`; `npm run test:arch023-merchant-knowledge-entitlement-reconciliation-lease:postgres`; `npm run erd`; `node --check` for both new scripts; and `git diff --check`. The PostgreSQL proof applied migrations through `20261001120000_arch023_merchant_knowledge_entitlement_reconciliation_lease`, verified all three lease labels, and logged cleanup of the owned container. Changed-file diagnostics report no issues in either script or `package.json`; the Prisma schema diagnostic flags the existing `datasource.url` as unsupported under Prisma 7 guidance, while the repository-locked Prisma 6.19.3 validation succeeds. The diagnostic is on the pre-existing datasource declaration, not the changed enum.

### Launcher Evidence
Prepared execution was true; dependency gate passed (`ARCH-023-DATABASE-005` complete); Attempt 1 was claimed by `copilot` at `2026-10-01T11:39:18Z`; durable parent claim commit `5f183d0a0ff8f12e97eb028f99650f073ff88786` was pushed. Implementation commit `ea94fab614564bece714c57540aef55b664e5b4e` is pushed to `task/ARCH-023-DATABASE-006`. Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-DATABASE-006`, `task/ARCH-023-DATABASE-006`. Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-DATABASE-006`, `task/ARCH-023-DATABASE-006`. Both worktrees were newly created; parent and implementation task branches did not require remote fast-forward, and both already incorporated `origin/main`. Shared workspace and shared implementation checkout were not switched or mutated; no other task worktree was reused. Recursive submodule sync and update both passed; there were no submodule entries.

### Deviations
The initial PostgreSQL readiness probe emitted expected connection/startup messages while the disposable container booted; the retry loop then completed successfully. No task scope or migration deviation.

### Assumptions
The repository's generated ERD files are included because `npm run erd` changed them when run after the schema update.

### Unresolved Issues
None. The separate Background-owned 300-second cadence and scheduler remain for `ARCH-023-BACKGROUND-005`; this database task does not introduce either.

### Architectural Concerns
None. This adds only the persisted enum identity required by the dependent Background scheduler.

## Architect Review

### Review Status
Accepted — Attempt 1

### Review Notes
Accepted the database-owned prerequisite exactly as bounded. The implementation adds only `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION` to `public.BackgroundRuntimeLeaseName`; the forward migration contains one additive `ALTER TYPE ... ADD VALUE IF NOT EXISTS` statement and does not change cadence configuration, runtime lease SQL, business tables, indexes, constraints or `FeatureActivationMode`.

The focused validator fixes the complete expected lease-label set and rejects migration drift. The disposable PostgreSQL proof applies the accepted migration chain through this task, proves all three Merchant Knowledge lease names coexist as valid `BackgroundRuntimeLease.name` values, removes task-owned rows and removes its invocation-owned `pgvector/pgvector:pg17` container.

The Completion Report records the launcher-resolved canonical parent and implementation worktrees, task branches, start-of-attempt synchronization, dependency gate and recursive submodule preparation. No artificial follow-up implementation commit is required.

### Reviewed Files
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261001120000_arch023_merchant_knowledge_entitlement_reconciliation_lease/migration.sql`
- `moda-interact-database/scripts/validate-arch023-merchant-knowledge-entitlement-reconciliation-lease.mjs`
- `moda-interact-database/scripts/test-arch023-merchant-knowledge-entitlement-reconciliation-lease-postgres.mjs`
- `moda-interact-database/package.json`
- generated ERD outputs
- this task Completion Report and launcher evidence

### Validation Reviewed
Reviewed the recorded passing format, Prisma validate/generate, focused static contract, disposable PostgreSQL migration/runtime proof, ERD generation, script syntax checks, changed-file diagnostics and `git diff --check`. The editor's Prisma 7 `datasource.url` warning is pre-existing and does not conflict with the repository-locked Prisma 6.19.3 validation result.

### Architecture Conformance
Conforms. The change remains inside database ownership and supplies only the persisted enum identity required by `ARCH-023-BACKGROUND-005`. The 300-second cadence and scheduler semantics remain Background-owned as required.

### Follow-up
Mark `ARCH-023-DATABASE-006` Complete. Restore `ARCH-023-BACKGROUND-005` from Blocked to Ready with Attempt 1 preserved now that this prerequisite is Complete; its next `/moda-task ARCH-023-BACKGROUND-005` claim becomes Attempt 2. Attempt 2 must add/prove the existing lease service's exact 300-second entitlement-reconciliation cadence branch and finish the already-started scheduler/build validation. `ARCH-023-GATEWAY-001` remains gated until BACKGROUND-005 is Complete.
