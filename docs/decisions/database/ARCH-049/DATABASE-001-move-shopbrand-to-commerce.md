---
id: ARCH-049-DATABASE-001
architecture_id: ARCH-049
title: Move ShopBrand to commerce and add WhatsApp media JSONB
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-049-BACKGROUND-002", "ARCH-049-BACKGROUND-003", "ARCH-049-BACKGROUND-004", "ARCH-049-API-001", "ARCH-049-ADMIN-002"]
created: 2026-10-25
updated: 2026-10-27
---

# Move ShopBrand to commerce and add WhatsApp media JSONB

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. This task was supplied as a portable definition and is now materialised in the canonical developer parent task worktree.

## Objective

Deliver exactly one additive ARCH-049 schema migration: preserve the existing one-per-Shop `ShopBrand` table, move it from `shopify` to `commerce`, and add a JSONB field for processed R2 media evidence. Do not create a separate asset table.

## Context

The attached snapshot contains `shopify.ShopBrand` and `Shop.brand`; its existing fields and row identity must survive. The Admin merchant-support queries still use `shopify."ShopBrand"` and are an explicit coordinated deployment concern.

## Scope

- Move the existing Prisma `ShopBrand` model mapping to `@@schema("commerce")`, without renaming fields or changing the existing `Shop.brand` and `ShopBrand.shop` relation.
- Add exactly `whatsAppMedia Json @default("{}") @db.JsonB` to `ShopBrand`; do not add additional fields or new tables.
- Add fixed ARCH-049 migration, precise schema/SQL validators and focused PostgreSQL fresh/upgrade/negative tests.

## Out of Scope

- Any Prisma application code in Admin, Shopify, API or Background; full image processing, R2 clients, triggers, domain-specific CHECK constraints, allowed-role/status enums, business validation, GraphQL/HTTP integration.

## Requirements

### R1. Exact Prisma declaration

Keep existing fields unchanged, except add the following and move the schema annotation:

```prisma
model ShopBrand {
  id                String   @id @default(cuid())
  shopId            String   @unique
  shop              Shop     @relation(fields: [shopId], references: [id], onDelete: Cascade)
  brandName         String?
  logoUrl           String?
  logoAltText       String?
  logoWidth         Int?
  logoHeight        Int?
  squareLogoUrl     String?
  squareLogoAltText String?
  coverImageUrl     String?
  whatsAppMedia     Json     @default("{}") @db.JsonB
  fetchedAt         DateTime @default(now())
  lastRefreshedAt   DateTime @updatedAt

  @@schema("commerce")
}
```

If the formatting tool aligns fields differently, preserve these exact types, nullability, defaults and relation actions. **No `ShopBrandMediaAsset`, no media status enum and no new reverse relation.**

### R2. Migration exact DDL

Use the fixed migration path `prisma/migrations/20261025170000_arch049_shopbrand_commerce_media/migration.sql` (the timestamp is a proposed new migration identifier; verify it does not conflict with current migrations before implementation). The core DDL is:

```sql
ALTER TABLE "shopify"."ShopBrand" SET SCHEMA "commerce";
ALTER TABLE "commerce"."ShopBrand"
  ADD COLUMN "whatsAppMedia" JSONB NOT NULL DEFAULT '{}'::jsonb;
```

Use any additional SQL only when required to preserve/reconcile existing table-backed sequences, indexes, FK references or database-specific migration behaviour. Do not drop/re-create the table; preserve original row IDs, `shopId` uniqueness, FK actions and all existing values. Do not edit historical migrations. No brand/media seed or backfill is required; existing rows receive `{}`.

### R3. Database ownership

The database enforces PK, `shopId` FK/unique and JSONB storage. It **does not** enforce media readiness, status values, dimensions, R2 bucket, shop platform, source-generation comparisons or Meta eligibility. Applications own those rules transactionally.

### R4. Exact validation

Add `scripts/validate-arch049-shopbrand-schema.mjs` and `scripts/validate-arch049-shopbrand-migration.mjs` with matching `test:arch049-shopbrand-schema` / `test:arch049-shopbrand-migration` package scripts. Validators check exact model and DDL, absence of invented tables/triggers and preservation of existing relationships. Use existing repository testing conventions for a disposable PostgreSQL migration integration test, not a second generic framework.

## Work Items

- [x] Update Prisma and migration.
- [x] Add both exact validators and package scripts.
- [x] Run a fresh database migration.
- [x] Run upgrade migration with representative existing Shop and ShopBrand rows and record before/after data.
- [x] Prove invalid FK and duplicate ShopBrand.shopId reject while JSON business-invalid values remain database-storable.

## Interfaces / Contracts

Produced: `commerce."ShopBrand"` with the original id, source fields and new `whatsAppMedia` JSONB. `Shop.brand` is unchanged. JSON shape is owned by ARCH-049 application code and documented in the parent architecture. Raw SQL consumers must update `shopify."ShopBrand"` → `commerce."ShopBrand"`; that code change is **not** authorised in this Database repository.

## Dependencies

None.

## Enables

- ARCH-049-BACKGROUND-002
- ARCH-049-BACKGROUND-003
- ARCH-049-BACKGROUND-004
- ARCH-049-API-001
- ARCH-049-ADMIN-002

## Acceptance Criteria

- [x] Migration preserves every existing ShopBrand row and all original fields with `whatsAppMedia={}` for legacy rows.
- [x] Prisma relations remain valid and exactly one ShopBrand row per shop remains enforced.
- [x] No new media table, business-rule SQL CHECK/trigger or extra source columns.
- [x] Fresh and upgrade PostgreSQL tests pass with exact validators.

## Validation

- [x] Prisma format and validate with repository-declared commands.
- [x] Exact schema/SQL validators and mutation tests reject missing/wrong types, FK or schema location.
- [x] Disposable PostgreSQL fresh/upgrade and direct invalid FK/duplicate tests.
- [x] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

Coordinated rollout must update `moda-interact-admin/src/lib/admin/merchant-support.ts` raw SQL references before the database migration is deployed to a running environment. This change is assigned to ADMIN-002, not made by the DB agent.

## Completion Report

### Status

Attempt 1 implementation and required validation passed developer self-review on 2026-10-27. The developer explicitly completed the task on 2026-10-27 after confirming the passing review and published implementation. Neither branch was merged to `main`.

### Files Changed

- `package.json` — added the ARCH-049 schema, migration, mutation and disposable PostgreSQL test commands.
- `prisma/schema.prisma` — moved `ShopBrand` to `commerce` and added only the required non-null JSONB `whatsAppMedia` field; existing fields and Shop relations are preserved.
- `prisma/migrations/20261025170000_arch049_shopbrand_commerce_media/migration.sql` — atomically moved the existing table and added the JSONB column without rebuilding the table.
- `scripts/validate-arch049-shopbrand-schema.mjs` — exact Prisma model/relation validation.
- `scripts/validate-arch049-shopbrand-migration.mjs` — exact DDL and historical constraint validation.
- `scripts/test-arch049-shopbrand-validator-mutations.mjs` — mutation cases for invalid schema/migration variations.
- `scripts/test-arch049-shopbrand-postgres.mjs` — disposable PostgreSQL fresh/upgrade, preservation and constraint behavior tests.

### Work Completed

- Preserved the existing `ShopBrand` table identity and moved its Prisma mapping from `shopify` to `commerce`; retained all original fields, the unique `shopId`, `Shop.brand`, and cascading `Shop` relation.
- Added `whatsAppMedia Json @default("{}") @db.JsonB` as the sole new model field. No asset table, extra relation, media enum, trigger or business-rule constraint was added.
- Added the fixed migration using `ALTER TABLE ... SET SCHEMA` and `ADD COLUMN`; PostgreSQL tests verified the table, primary key, foreign key and unique-index OIDs survived the move.
- Added repository scripts for exact validators, validator mutation coverage, and isolated PostgreSQL fresh/upgrade runs.

### Validation Results

- **PASS** — `npm run test:arch049-shopbrand-schema`: exact `commerce.ShopBrand` shape and existing `Shop.brand` relation.
- **PASS** — `npm run test:arch049-shopbrand-migration`: exactly two DDL statements, with the expected JSONB default.
- **PASS** — `npm run test:arch049-shopbrand-validator-mutations`: all schema and migration mutations rejected, including wrong type/default/schema, missing FK/uniqueness, rebuilt table, extra field/model, CHECK and trigger.
- **PASS** — `npm run validate`: Prisma schema valid.
- **PASS** — `npx prisma format --check --schema prisma/schema.prisma`: all files formatted.
- **PASS** — `npm run lint`: ESLint with zero warnings.
- **PASS** — `npm run test:arch049-shopbrand:postgres:fresh`: all 65 migrations applied in a randomized Docker PostgreSQL container; table/default/FK/unique behavior verified.
- **PASS** — `npm run test:arch049-shopbrand:postgres:upgrade`: all 65 migrations applied with representative pre-existing Shop and ShopBrand rows; every original row value and table/PK/FK/unique-index identity preserved, and legacy rows received `{}`. Invalid FK, duplicate shopId, null/invalid JSON, update/delete cascade and application-owned JSON rules were verified.
- **PASS** — `git diff --check origin/main...HEAD` and `git diff --check` on the implementation task branch.
- The PostgreSQL harness used unique containers with `--network none` and removed them on completion. No persistent database or application environment was used.
- Validation ran both before and after the origin/main synchronization merge; the final pass is against implementation HEAD `728734b7f1c05a9175ada032e113babeb8066cda`.

### Deviations

- The implementation worktree had an untracked terminal transcript during the first review inspection. It was left untouched. On re-entry it was absent, and the implementation worktree was clean before validation and synchronization; no task implementation was inferred from or made to that artifact.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

- None for this task's acceptance criteria. The separate Admin raw SQL reference update remains owned by ARCH-049-ADMIN-002 and is a coordinated deployment prerequisite, not part of this Database implementation.

### Architectural Concerns

None reported.

## Developer Execution Ownership Amendment

- Date: 2026-10-27.
- The developer explicitly invoked `/moda_developer_create ARCH-049-DATABASE-001` for this ready agent-owned task. Execution and completion ownership are transferred to the developer (`execution_mode: developer`, `completion_mode: developer`) for this task lifecycle.
- Preserved logical ownership: `assigned_agent: moda_database`, `repository: moda-interact-database`, coordinator, task scope, dependencies, acceptance criteria and validation requirements are unchanged.
- Materialisation: this portable task definition was present in the shared workspace but had no canonical task worktree or task branch. It was materialised in `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-DATABASE-001` from parent `origin/main`; the matching Database implementation worktree was created from Database `origin/main`. The shared checkout was not edited.

## Developer Execution Claim (Attempt 1)

- Claim: `status: in_progress`, `executor: developer`, `claimed_at: 2026-10-27T10:08:36Z`, `attempt: 1`.
- Canonical launcher: `python3 scripts/start-agent-task.py ARCH-049-DATABASE-001 --route-only --json` from `/Users/kwadwoadomafriyie/project/moda-interact-workspace` resolved repository `moda-interact-database`, parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-DATABASE-001`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-DATABASE-001`, and branch `task/ARCH-049-DATABASE-001`.
- Dependencies: none (`depends_on: []`).
- Parent preparation: fetched `origin --prune`; no existing local/remote task branch or stale worktree registration existed. Created the canonical parent worktree from parent `origin/main` at `d09811cebcdc7498203a9156932be7a34eb4a84b`; the worktree is clean before this claim edit.
- Implementation preparation: fetched `origin --prune`; no existing local/remote task branch or stale worktree registration existed. Created the canonical implementation worktree from Database `origin/main` at `8f3d58542372fb9a71d97e5b340c2fc33a7ac8cf`; the worktree is clean. No implementation changes were made during preparation.
- No changes were made to the shared/default workspace checkout or unrelated untracked files.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.

## Developer Self-Review Passed — Attempt 1

- Review result: **PASS**. The committed implementation satisfies the task scope, all Work Items and Acceptance Criteria, and the declared Prisma, validator, lint and PostgreSQL validation requirements.
- Implementation task branch is published at `728734b7f1c05a9175ada032e113babeb8066cda` (`origin/task/ARCH-049-DATABASE-001`); it includes the implementation commit `f3e73daf647904c622cc0405e33520b32b18c0ed` and a merge of Database `origin/main` `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.
- Parent task branch was synchronized from parent `origin/main` `293ef582e731c4c578815985e9a12f0d93b64bcf` to `15a7a27cc57228dad8e9c58fa48ef9a1c0934de8` before this report update.
- Both canonical task worktrees are clean. The implementation and parent branches are not merged to `main`.
- Completion mode is `developer`; the explicit developer completion decision is recorded below. Neither task branch is merged to `main`.

## Developer Completion Decision

- The developer explicitly completed ARCH-049-DATABASE-001 Attempt 1 on 2026-10-27 after verifying the durable passing self-review, all checked Work Items and Acceptance Criteria, required validation, clean canonical worktrees, and published task branches.
- Lifecycle state: `complete`; `executor: null`; `claimed_at: null`; `attempt: 1` (unchanged).
- Published implementation branch: `task/ARCH-049-DATABASE-001` at `728734b7f1c05a9175ada032e113babeb8066cda`.
- Published parent task/report branch: `task/ARCH-049-DATABASE-001` at `9adb0a4078ed5c8bce2504301285ee0c88e2d51e` before this completion decision.
- No merge to `main`, deployment, or dependent-task implementation was performed.
- Dependency-frontier reconciliation: promote `ARCH-049-API-001`, `ARCH-049-BACKGROUND-004`, and `ARCH-049-ADMIN-002` from `pending` to `ready`, because each task's declared dependencies are now complete. Their attempt counters remain 0, with null executor/claim fields.
- Keep `ARCH-049-BACKGROUND-002` pending because `ARCH-049-BACKGROUND-001` is still `ready`, not complete. Keep `ARCH-049-BACKGROUND-003` pending because `ARCH-049-BACKGROUND-002` is pending and `ARCH-049-SHOPIFY-001` is ready, not complete. Keep `ARCH-049-SYSTEM-TEST-001` pending because its remaining declared dependencies are incomplete; it remains manual-gated and is not started.
