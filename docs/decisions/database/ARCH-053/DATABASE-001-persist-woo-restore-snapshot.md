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
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-10-30T13:08:38Z
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

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

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

- [ ] Insert `wooRestoreSnapshot Json?` into the existing `CheckoutRecovery` declaration; no other schema changes.
- [ ] Generate/inspect the single additive, schema-qualified JSONB migration; verify the SQL matches Prisma's schema diff.
- [ ] Implement `scripts/test-arch053-woo-restore-snapshot-postgres.mjs` with independent `fresh` and `upgrade` modes and the assertions below.
- [ ] Add the **two exact** `package.json` test commands specified above without removing or renaming existing commands.
- [ ] Generate the Prisma client **inside the Database repository** and run the declared schema, migration and PostgreSQL checks.
- [ ] Record validation evidence, rollout/rollback limitation, changed files and worktree evidence in the task Completion Report; return for architect review.

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

- [ ] Prisma's `CheckoutRecovery` model contains exactly one new nullable `Json?` field named `wooRestoreSnapshot`, preserving all other properties and schema qualifiers.
- [ ] Generated migration only adds a nullable `JSONB` column in `commerce."CheckoutRecovery"`; it has **no default**, new index, trigger, backfill or destructive DDL.
- [ ] A migrated legacy recovery retains its `id`, `shopId`, `checkoutToken`, `generation`, `status`, `lineItems`, `checkoutUrl` and other existing values; new column is SQL NULL.
- [ ] A newly created recovery without a snapshot also has SQL NULL; storing and selecting the two JSON fixtures above yields their exact JSONB content without coercion or overwriting `lineItems`.
- [ ] Two recoveries of **different generations**, same shop and checkout token can hold different snapshots independently; the existing `(shopId, checkoutToken, generation)` uniqueness still rejects duplicates.
- [ ] Tests demonstrate fresh schema creation and populated-schema upgrade using disposable PostgreSQL, with container cleanup even when tests fail.
- [ ] Database-only changes stay within approved files and task metadata; existing `package.json` commands, multi-schema relations and all unrelated tables remain unaffected.

## Validation

- [ ] From `moda-interact-database`: `npm run validate` and `npm run prisma:generate` (both exist in the inspected `package.json`).
- [ ] Verify schema-to-schema migration diff against the pre-change schema using the installed Prisma CLI, and inspect the checked-in SQL for a single additive `ALTER TABLE` statement.
- [ ] `npm run test:arch053-woo-restore-snapshot:postgres:fresh` — **fresh mode** applies migrations through the new ARCH-053 migration in a private PostgreSQL test instance, verifies nullable JSONB via `information_schema.columns`, inserts (a) a recovery with omitted snapshot, (b) supported JSON, (c) unsupported JSON, and checks JSONB round trips, generation independence and existing unique constraint.
- [ ] `npm run test:arch053-woo-restore-snapshot:postgres:upgrade` — **upgrade mode** applies all prior migrations, seeds a real pre-migration shop and `CheckoutRecovery` row (including nonempty `lineItems`, `checkoutUrl`, generation and timestamps), applies the ARCH-053 migration, and proves existing row values are unchanged while `wooRestoreSnapshot IS NULL`. Then repeat supported/unsupported JSONB and generation checks.
- [ ] Script rejects invalid or missing `--mode`, uses PostgreSQL `ON_ERROR_STOP=1`, asserts migration order, avoids a hosted DB connection, and removes its uniquely named disposable container in `finally`.
- [ ] `git diff --check`; report commands, results and any environment limitation honestly in the Completion Report. Required validation that could not run remains unchecked and must not be described as passed.

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

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
