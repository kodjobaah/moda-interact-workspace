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
status: in_progress
priority: 10
executor: developer
claimed_at: '2026-10-27T10:08:36Z'
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

- [ ] Update Prisma and migration.
- [ ] Add both exact validators and package scripts.
- [ ] Run a fresh database migration.
- [ ] Run upgrade migration with representative existing Shop and ShopBrand rows and record before/after data.
- [ ] Prove invalid FK and duplicate ShopBrand.shopId reject while JSON business-invalid values remain database-storable.

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

- [ ] Migration preserves every existing ShopBrand row and all original fields with `whatsAppMedia={}` for legacy rows.
- [ ] Prisma relations remain valid and exactly one ShopBrand row per shop remains enforced.
- [ ] No new media table, business-rule SQL CHECK/trigger or extra source columns.
- [ ] Fresh and upgrade PostgreSQL tests pass with exact validators.

## Validation

- [ ] Prisma format and validate with repository-declared commands.
- [ ] Exact schema/SQL validators and mutation tests reject missing/wrong types, FK or schema location.
- [ ] Disposable PostgreSQL fresh/upgrade and direct invalid FK/duplicate tests.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

Coordinated rollout must update `moda-interact-admin/src/lib/admin/merchant-support.ts` raw SQL references before the database migration is deployed to a running environment. This change is assigned to ADMIN-002, not made by the DB agent.

## Completion Report

### Status

In Progress — developer Attempt 1 claimed 2026-10-27 after materializing the portable definition in the canonical task worktrees.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

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
