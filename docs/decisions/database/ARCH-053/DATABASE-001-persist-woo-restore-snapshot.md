---
id: ARCH-053-DATABASE-001
architecture_id: ARCH-053
title: Persist generation-specific Woo restoration snapshot
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
- ARCH-053-API-002
- ARCH-053-BACKGROUND-002
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-DATABASE-001 — Persist generation-specific Woo restoration snapshot

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. Task was materialised and executed in dedicated mirrored task worktrees. Attempt 1 is now architect-accepted; no producer deployment is implied.

## Objective

Persist generation-specific Woo restoration snapshot. One bounded outcome in `moda-interact-database` owned by `moda_database`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Ready** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

**Exact Prisma edit — `moda-interact-database/prisma/schema.prisma` (one field; no new model):**

```prisma
model CheckoutRecovery {
  // Preserve every existing field and relation. In particular, this section
  // already exists and should become:
  currency           String?
  totalPrice         Decimal?
  checkoutUrl        String?
  lineItems          Json?
  wooRestoreSnapshot Json?

  // Preserve the existing generation and all unique/index declarations:
  // generation Int @default(1)
  // @@unique([shopId, checkoutToken, generation])
  // @@schema("commerce")
}
```

This is an **insertion into the existing `CheckoutRecovery` model**, not a replacement for that model. Preserve the actual field ordering/formatting used by the repository. `Json?` maps to nullable PostgreSQL `JSONB` by Prisma's PostgreSQL connector; do **not** introduce `@default`, `@db.Text`, an enum, a relation, an index, or a new table.

**Create one additive Prisma migration:**

`moda-interact-database/prisma/migrations/<timestamp>_arch053_woo_restore_snapshot/migration.sql`

Expected SQL (confirm against Prisma's generated schema-to-schema diff and use its canonical formatting):

```sql
ALTER TABLE "commerce"."CheckoutRecovery"
  ADD COLUMN "wooRestoreSnapshot" JSONB;
```

The migration must contain no `DROP`, data rewrite, backfill, trigger, new constraint, new index or DDL on another table. Existing rows receive **SQL NULL** in the new column; do not write the JSON literal `null` in place of SQL NULL.

**Create one isolated PostgreSQL regression script, following ARCH-050-DATABASE-001:**

`moda-interact-database/scripts/test-arch053-woo-restore-snapshot-postgres.mjs`

It must accept only `--mode fresh` or `--mode upgrade`, use the repository's existing disposable-PostgreSQL/Docker test pattern (see `scripts/test-arch050-initial-recovery-support-notification-postgres.mjs`), clean up its own container in `finally`, and fail with a non-zero exit code on assertion or migration failure. The test must not contact any hosted Moda database.

**Add the following exact script keys to `moda-interact-database/package.json`:**

```json
{
  "scripts": {
    "test:arch053-woo-restore-snapshot:postgres:fresh": "node scripts/test-arch053-woo-restore-snapshot-postgres.mjs --mode fresh",
    "test:arch053-woo-restore-snapshot:postgres:upgrade": "node scripts/test-arch053-woo-restore-snapshot-postgres.mjs --mode upgrade"
  }
}
```

These keys are **insertions into the existing `scripts` object**, not a replacement `package.json`. Keep all existing scripts and dependencies unchanged. Limit implementation source changes to these four items (schema file, one migration, one test script and the script-key additions), plus this task's permitted Completion Report updates.

## Out of Scope

- Generating, signing, resolving or persisting recovery URLs beyond preserving the existing `checkoutUrl` column; token storage, link expiry or authentication.
- WooCommerce plugin code, API and Background writers/readers, new Prisma clients committed to consumer repositories, Shared/Zod implementation, dynamic discount discovery (ARCH-052), coupon business rules or outreach.
- New database models, indices, uniqueness constraints, triggers, outbox tables, `CHECKOUT_RESUMED` events, or modification of the recovery-generation lifecycle (ARCH-048).
- API/Background validation of invalid, replayed or stale link events; those are **not database migration acceptance tests**.
- Broad migrations cleanup, unrelated tests and changes to `_index.md` files.

## Requirements

1. **Persist one snapshot per admitted generation.** `wooRestoreSnapshot` stores the exact `WooCartRestoreSnapshotV1` value selected and validated by the owning Background admission writer. The value may be `supported` or `unsupported`; it is not a live cart projection. The Database repository adds storage only, and must not implement writer logic, mutate old-generation snapshots or rederive coupon eligibility.
2. **Preserve existing semantics.** Keep `CheckoutRecovery.id`, `shopId`, `checkoutToken`, `generation`, `status`, `lineItems`, `checkoutUrl`, `currency`, `totalPrice`, timestamps, relations, foreign keys, indexes and `@@unique([shopId, checkoutToken, generation])` unchanged. Independent generations can hold independent JSON values.
3. **Nullable legacy behaviour.** Historical and new recoveries with no restoration evidence have SQL `NULL`. `NULL` means restoration data is unavailable; it **does not** mean an empty cart, a verified empty coupon list or a restorable basket. A populated `kind: 'unsupported'` snapshot also cannot be used to issue a restore URL. API/Background must enforce these rules in their own tasks.
4. **Contract ownership.** The JSON shape is defined by `ARCH-053-SHARED-001` (published through `ARCH-053-SHARED-002`), not by local Prisma enums or additional database constraints. The database does not validate product availability, coupon validity/stacking, or offer eligibility. Retain **original customer-applied coupons** within the immutable snapshot; confirmed outreach-recommended offers belong to separate confirmed-message evidence, not this field.
5. **No new access path.** Consumers already select recoveries by recovery ID, shop and generation. Do not add a JSONB index without a documented query requiring one. The DB field alone does not establish tenant authorisation; API/Background must use the authoritative shop principal.
6. **Security and retention.** Do not insert bearer recovery tokens, contact details, request headers or WhatsApp contents into `wooRestoreSnapshot`. Coupon codes are permitted in their defined original-coupon array, but should not be emitted in diagnostics. Do not create new logs or a service-local logger for this schema-only change.
7. **Migration discipline.** Additive, forward-only migration. Existing rows are preserved on upgrade; dropping the new column later would delete stored restore evidence and requires an explicit backup/rollback decision, not an automatic `down` step.

### Mandatory task execution boundaries

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md` and `docs/task-definition-materialization.md`, including the launcher-prepared dedicated parent/implementation worktree and start-of-attempt synchronization evidence. Re-read this task and parent architecture before claiming Ready; preserve the `moda_database` ownership boundary. Record actual validation and worktree evidence in the Completion Report. Do not claim any remote push, acceptance or merged commit without evidence. The implementing agent must stop at `review` and return control to `moda_architect`.

## Work Items

- [x] Insert `wooRestoreSnapshot Json?` into the existing `CheckoutRecovery` declaration; no other schema changes.
- [x] Generate/inspect the single additive, schema-qualified JSONB migration; verify the SQL matches Prisma's schema diff.
- [x] Implement `scripts/test-arch053-woo-restore-snapshot-postgres.mjs` with independent `fresh` and `upgrade` modes and the assertions below.
- [x] Add the **two exact** `package.json` test commands specified above without removing or renaming existing commands.
- [x] Generate the Prisma client **inside the Database repository** and run the declared schema, migration and PostgreSQL checks.
- [x] Record validation evidence, rollout/rollback limitation, changed files and worktree evidence in the task Completion Report; return for architect review.

## Interfaces / Contracts

**New database field:**

| Layer | Exact name/type | Semantics |
|---|---|---|
| Prisma | `CheckoutRecovery.wooRestoreSnapshot: Prisma.JsonValue \| null` | `Json?` column, absent when no evidence |
| PostgreSQL | `commerce."CheckoutRecovery"."wooRestoreSnapshot" JSONB NULL` | SQL NULL by default; no index or default |
| Background writer | `ARCH-053-BACKGROUND-002` | Sets validated snapshot **on admission** for the correct shop/checkout/generation |
| Hosted API reader | `ARCH-053-API-002` | Reads only after authenticating shop and resolving eligible generation |
| Schema authority | `ARCH-053-SHARED-001` | `WooCartRestoreSnapshotV1Schema`; Database does not duplicate it |

**Representative persisted JSON fixtures** (illustrative test values that conform to the planned Shared v1 structure):

Supported, including the customer's originally selected coupons:

```json
{
  "schemaVersion": "woo.cart-restore.v1",
  "kind": "supported",
  "appliedCouponCodes": ["SAVE10", "SHIPFREE"],
  "lines": [
    { "productId": "101", "quantity": 2 },
    {
      "productId": "202",
      "variationId": "205",
      "quantity": 1,
      "attributes": { "attribute_pa_size": "large" }
    }
  ]
}
```

Unsupported (persistable as evidence, **not** an eligible restore basket):

```json
{
  "schemaVersion": "woo.cart-restore.v1",
  "kind": "unsupported",
  "reason": "CUSTOM_CART_ITEM_DATA",
  "appliedCouponCodes": ["SAVE10"]
}
```

The `wooRestoreSnapshot` field must **not** contain an `outreachOffer` or any recommended coupon sourced from a later WhatsApp message. That information is resolved separately under the ARCH-053 outreach-offer tasks.

## Dependencies

None. Eligible when launcher re-gating verifies `status: ready`; do not wait for a system-test task. `ARCH-053-SHARED-001` is the shape owner for consumer code, but is **not** a database migration prerequisite because the field is generic nullable JSONB.

## Enables

- `ARCH-053-BACKGROUND-002` can become Ready only after architect acceptance and Complete state, subject to its other dependencies.
- `ARCH-053-API-002` can become Ready only after architect acceptance and Complete state, subject to its other dependencies.

## Acceptance Criteria

- [x] Prisma's `CheckoutRecovery` model contains exactly one new nullable `Json?` field named `wooRestoreSnapshot`, preserving all other properties and schema qualifiers.
- [x] Generated migration only adds a nullable `JSONB` column in `commerce."CheckoutRecovery"`; it has **no default**, new index, trigger, backfill or destructive DDL.
- [x] A migrated legacy recovery retains its `id`, `shopId`, `checkoutToken`, `generation`, `status`, `lineItems`, `checkoutUrl` and other existing values; new column is SQL NULL.
- [x] A newly created recovery without a snapshot also has SQL NULL; storing and selecting the two JSON fixtures above yields their exact JSONB content without coercion or overwriting `lineItems`.
- [x] Two recoveries of **different generations**, same shop and checkout token can hold different snapshots independently; the existing `(shopId, checkoutToken, generation)` uniqueness still rejects duplicates.
- [x] Tests demonstrate fresh schema creation and populated-schema upgrade using disposable PostgreSQL, with container cleanup even when tests fail.
- [x] Database-only changes stay within approved files and task metadata; existing `package.json` commands, multi-schema relations and all unrelated tables remain unaffected.

## Validation

- [x] From `moda-interact-database`: `npm run validate` and `npm run prisma:generate` (both exist in the inspected `package.json`).
- [x] Verify schema-to-schema migration diff against the pre-change schema using the installed Prisma CLI, and inspect the checked-in SQL for a single additive `ALTER TABLE` statement.
- [x] `npm run test:arch053-woo-restore-snapshot:postgres:fresh` — **fresh mode** applies migrations through the new ARCH-053 migration in a private PostgreSQL test instance, verifies nullable JSONB via `information_schema.columns`, inserts (a) a recovery with omitted snapshot, (b) supported JSON, (c) unsupported JSON, and checks JSONB round trips, generation independence and existing unique constraint.
- [x] `npm run test:arch053-woo-restore-snapshot:postgres:upgrade` — **upgrade mode** applies all prior migrations, seeds a real pre-migration shop and `CheckoutRecovery` row (including nonempty `lineItems`, `checkoutUrl`, generation and timestamps), applies the ARCH-053 migration, and proves existing row values are unchanged while `wooRestoreSnapshot IS NULL`. Then repeat supported/unsupported JSONB and generation checks.
- [x] Script rejects invalid or missing `--mode`, uses PostgreSQL `ON_ERROR_STOP=1`, asserts migration order, avoids a hosted DB connection, and removes its uniquely named disposable container in `finally`.
- [x] `git diff --check`; report commands, results and any environment limitation honestly in the Completion Report. Required validation that could not run remains unchecked and must not be described as passed.

## Stop Condition

When all required Work Items, Acceptance Criteria and Validation are satisfied, update only this task's permitted execution metadata, checklist and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not implement Enabled tasks, change `_index.md`, merge task branches, push `main` or mark the task Complete yourself.

## Implementation Notes

- Copy the **test pattern**, not ARCH-050's notification schema: use `scripts/test-arch050-initial-recovery-support-notification-postgres.mjs` for unique Docker container naming, mode parsing, no external DB, migration execution order and cleanup. The ARCH-053 assertions must focus on JSONB persistence, legacy-row preservation and generation uniqueness, not Support messages or settings defaults.
- Use the existing `commerce."CheckoutRecovery"` table casing and `@@schema("commerce")`; do not create the column on a default `public` schema. The expected Prisma-generated DDL is shown in Scope.
- The scripted migration run should include the target migration and its predecessors; if newer migrations exist, isolate testing through the ARCH-053 target or update the harness deliberately rather than relying on a stale assumption that the target must remain the repository's last migration forever.
- No downstream client or merchant WordPress code belongs in this task. The Background/API consumers adopt the accepted Database repository revision through their own dedicated task worktrees.
- **Original coupons** are a property of the historical snapshot; checkout prices, expiry, usage limits and coupon stacking are revalidated by WooCommerce when the customer actually restores checkout. PostgreSQL must not attempt business-rule validation.

## Completion Report

### Status

Implemented and architect-accepted at Attempt 1 (`status: complete`). Implementation commit `33d2f6b6107ea57bd9dfe38e2e3d6e24df9556be` and parent task/report commit `af0f1853c6f4995e845baf1fcd5db4fe2335f972` are published.

### Files Changed

- `prisma/schema.prisma` — added nullable `CheckoutRecovery.wooRestoreSnapshot Json?`.
- `prisma/migrations/20261030131833_arch053_woo_restore_snapshot/migration.sql` — added one nullable JSONB column to `commerce."CheckoutRecovery"`.
- `scripts/test-arch053-woo-restore-snapshot-postgres.mjs` — added isolated fresh/upgrade PostgreSQL regression coverage.
- `package.json` — added the two requested fresh/upgrade test commands.
- This task file — reconciled execution metadata, checklists and Completion Report only. No architecture index or review section was changed.

### Work Completed

Added generic nullable JSONB persistence only; no local schema for the Shared contract, new index, default, backfill, trigger, or unrelated database changes. The migration was checked against the pre-change Prisma schema and contains one `ALTER TABLE` adding `wooRestoreSnapshot` as `JSONB`, with no default.

The PostgreSQL harness has strict `--mode fresh|upgrade` parsing, applies migrations in sorted order only through the target migration, uses `ON_ERROR_STOP=1`, connects only to its uniquely named disposable `pgvector/pgvector:pg17` container on Docker's `none` network, and removes the container in `finally`. It checks nullable/no-default JSONB metadata, SQL NULL for omitted and legacy values, exact supported/unsupported JSONB round trips, unchanged display `lineItems`, different generation snapshots for the same shop/token, and duplicate-generation rejection. The existing partial unique index permits only one active generation, so the fixture uses `COMPLETED` for generation 1 and `DETECTED` for generation 2; duplicate generation 1 is also `COMPLETED`, isolating the existing three-column uniqueness constraint.

### Validation Results

- `npm run validate` — passed; Prisma schema valid.
- `npm run prisma:generate` — passed; Prisma Client 6.19.3 generated inside the Database worktree. An initial sandbox attempt returned `EPERM` replacing a generated client file; the same command passed on the permitted retry.
- `npx prisma migrate diff --from-schema-datamodel /private/tmp/arch053-database-001-schema-before.prisma --to-schema-datamodel prisma/schema.prisma --script` — passed; output was exactly `ALTER TABLE "commerce"."CheckoutRecovery" ADD COLUMN     "wooRestoreSnapshot" JSONB;` (Prisma output includes the `-- AlterTable` comment).
- `npm run test:arch053-woo-restore-snapshot:postgres:fresh` — passed; 66 migrations through the target, including SQL NULL/default metadata, JSONB round trips and uniqueness checks.
- `npm run test:arch053-woo-restore-snapshot:postgres:upgrade` — passed; 66 migrations through the target; seeded pre-migration row retained all checked values, with new snapshot SQL NULL, then JSONB and uniqueness checks passed.
- Missing `--mode` and `--mode invalid` both exited non-zero before starting Docker.
- `git diff --check` — passed.
- Docker emitted existing migration notices (identifier truncation and an idempotent missing-index notice); both suites completed successfully. No hosted database was contacted.

### Physical worktree isolation and start-of-attempt synchronization

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-DATABASE-001`, branch `task/ARCH-053-DATABASE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-DATABASE-001`, branch `task/ARCH-053-DATABASE-001`.
- Parent synchronized head at attempt start: `e6a8d668192a14ae71f1cc93fd0c887552726d3f`; implementation synchronized head: `c3bb038c062cdf2f549aa4204538ac2d16088e91`.
- Both task branches reported remote fast-forward `not-needed`; `origin/main` was `already-current` in each worktree. Recursive submodule sync/init passed with no submodule entries. Dependency gate passed (none); task claim commit `e20c217d74e01666e89bd9188b73d8ff898a3547` was pushed before implementation.

### Deviations

None. The test fixture accounts for the repository's pre-existing partial unique index by using one completed historical generation and one active generation; no existing index or lifecycle rule was changed.

### Assumptions

The representative fixtures follow the task's illustrative Shared v1 shape; contract validation remains owned by ARCH-053-SHARED-001 and consumers.

### Unresolved Issues

No implementation issue found. The database task is accepted. No downstream task was promoted because `ARCH-053-SHARED-002` remains Pending; its consumers are still dependency-gated.

### Architectural Concerns

Rollback is forward-only: dropping `wooRestoreSnapshot` later would delete restoration evidence and requires an explicit backup and retention decision. No automatic down migration is provided. The ARCH-053 index remains architect-owned and unchanged.

## Architect Review — Attempt 1 (Accepted)

### Review Status

Accepted. The implementation branch `task/ARCH-053-DATABASE-001` is published at `33d2f6b6107ea57bd9dfe38e2e3d6e24df9556be`; the parent task/report branch is published at `af0f1853c6f4995e845baf1fcd5db4fe2335f972`. Task status is Complete; attempt remains 1.

### Review Notes

The schema adds only nullable `Json?` storage on `CheckoutRecovery`; the migration adds a nullable JSONB column without default or backfill. The harness isolates fresh and upgrade modes on disposable PostgreSQL, preserves existing recovery data, checks SQL NULL and supported/unsupported JSONB round trips, tests per-generation independence and the existing uniqueness constraint, and cleans up its container in `finally`. No unrelated schema, table, index, or business validation was introduced.

### Reviewed Files

Reviewed `prisma/schema.prisma`, migration `20261030131833_arch053_woo_restore_snapshot`, the fresh/upgrade PostgreSQL harness, the package script additions, and the Completion Report/worktree evidence.

### Validation Reviewed

The report records Prisma validation and client generation, schema-to-schema diff inspection, fresh and upgrade PostgreSQL runs through 66 migrations, invalid-mode rejection, and `git diff --check` passing. These results were reviewed as reported and were not independently rerun.

### Architecture Conformance

Conforms to the database-only persistence contract. No downstream task is promoted: `ARCH-053-SHARED-002` remains Pending, so the dependent API and Background work is still gated. No consumer rollout or production activation is implied.

### Follow-up

None for this database task. Restore-evidence writers and readers remain owned by their separate API and Background tasks; the JSONB field is not itself an authorization decision.
