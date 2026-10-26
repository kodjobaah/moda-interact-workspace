---
id: ARCH-050-DATABASE-001
architecture_id: ARCH-050
title: Persist the merchant notification preference and optional Support recovery target
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-050-BACKGROUND-001
  - ARCH-050-SHOPIFY-001
  - ARCH-050-SHOPIFY-002
  - ARCH-050-API-001
  - ARCH-050-API-002
created: 2026-10-26
updated: 2026-10-26
---

# Persist the merchant notification preference and optional Support recovery target

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Extend existing Prisma persistence so every shop can opt into first-outreach Support alerts and a system Support message can reference an authorised recovery without storing a URL.

## Context

`ShopSettings`, `CheckoutRecovery` and `MerchantSupportMessage` already exist in `prisma/schema.prisma`; both merchant surfaces use the same shop settings row and Support table. Do not introduce a separate notification entity.

## Scope

**Exact Prisma edits in `moda-interact-database/prisma/schema.prisma` (no new models):**

```prisma
model ShopSettings {
  // Existing id, shopId, recovery and feature fields unchanged.
  notifyOnInitialRecoveryOutreach Boolean @default(false)
}

model CheckoutRecovery {
  // Existing fields/relations unchanged.
  merchantSupportMessages MerchantSupportMessage[] @relation("RecoverySupportNotificationTarget")
}

model MerchantSupportMessage {
  // Existing fields/relations unchanged.
  checkoutRecoveryId String?
  checkoutRecovery   CheckoutRecovery? @relation(
    "RecoverySupportNotificationTarget",
    fields: [checkoutRecoveryId], references: [id], onDelete: SetNull
  )

  @@index([checkoutRecoveryId])
}
```

These are **insertions into existing declarations**, not replacement model blocks. `ShopSettings` is in `@@schema("shopify")`, `CheckoutRecovery` is in `@@schema("commerce")`, and `MerchantSupportMessage` is in `@@schema("support")`; do not move models or duplicate relation fields.

**Create:** `moda-interact-database/prisma/migrations/<timestamp>_arch050_initial_recovery_support_notification/migration.sql`. Expected SQL operations (use Prisma-generated constraint/index names if they differ):

```sql
ALTER TABLE "shopify"."ShopSettings"
  ADD COLUMN "notifyOnInitialRecoveryOutreach" BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE "support"."MerchantSupportMessage"
  ADD COLUMN "checkoutRecoveryId" TEXT;
CREATE INDEX "MerchantSupportMessage_checkoutRecoveryId_idx"
  ON "support"."MerchantSupportMessage"("checkoutRecoveryId");
ALTER TABLE "support"."MerchantSupportMessage"
  ADD CONSTRAINT "MerchantSupportMessage_checkoutRecoveryId_fkey"
  FOREIGN KEY ("checkoutRecoveryId") REFERENCES "commerce"."CheckoutRecovery"("id")
  ON DELETE SET NULL ON UPDATE CASCADE;
```

**Create:** `moda-interact-database/scripts/test-arch050-initial-recovery-support-notification-postgres.mjs` (or use the existing repository's disposable-Postgres harness and an equivalent named test). Test both fresh and populated database migration paths. No other repository source files are owned by this task.

## Out of Scope

- A notification writer, UI fields, API endpoints, automated sends, a new Support table, or merchant billing changes.

## Requirements

- `notifyOnInitialRecoveryOutreach` is a **non-nullable per-shop Boolean**, database default `false`. It is not a field of `ShopRecoveryPolicyOverride`; an admin recovery-policy override must not change it. New settings rows and upgraded rows both default OFF.
- The new Support FK is nullable for all existing unrelated messages. PostgreSQL enforces reference existence and `ON DELETE SET NULL`; it does **not** independently prove same-shop ownership, which must be enforced by the Background writer and read APIs.
- Preserve `MerchantSupportMessage.sourceKey @unique`, `MerchantSupportThread.shopId @unique`, and `RecoveryOutreachAttempt @@unique([checkoutRecoveryId, sequence])`; no extra dedupe table/index is required.
- Preserve every pre-existing Support field and its `systemVersion String?` type. New notices use the string literal `"1"` (not an integer).
- Migration must be additive; no dropping/rebuilding production Support, recovery or preference rows. Use correct schema-qualified cross-schema foreign keys.
- Prisma generated clients in Background, API and Shopify must be updated in **their respective consumer tasks**, not committed to unrelated repositories by DATABASE-001.

## Work Items

- [ ] Insert the three Prisma model modifications above, with matching relation names and proper spacing/ordering.
- [ ] Generate and inspect a single additive migration, including `DEFAULT false`, nullable FK, `ON DELETE SET NULL` and index.
- [ ] Add isolated database validation for old row migration, default false, FK reference, deletion nulling and unaffected Support sourceKey dedupe.
- [ ] Regenerate Prisma client in the database repository and record schema/migration validation, fresh and upgrade Postgres test evidence.

## Interfaces / Contracts

- **Canonical preference:** `ShopSettings.notifyOnInitialRecoveryOutreach: boolean` (Prisma/SQL name exactly as spelled).
- **Canonical target:** `MerchantSupportMessage.checkoutRecoveryId: string | null` and `checkoutRecovery?: CheckoutRecovery | null` with `@relation("RecoverySupportNotificationTarget")`.
- **Inverse relation:** `CheckoutRecovery.merchantSupportMessages: MerchantSupportMessage[]` with same relation name.
- Existing `MerchantSupportMessage.systemVersion: string | null` remains unchanged; all ARCH-050 writers/readers compare `"1"`.
- Cross-tenant association is a service contract: `message.thread.shopId === message.checkoutRecovery.shopId` whenever the target is projected; relational FK alone is insufficient.

## Dependencies

None. This is the initial eligible architecture implementation task.

## Enables

- `ARCH-050-BACKGROUND-001` may become eligible only after architect acceptance and Complete state.
- `ARCH-050-SHOPIFY-001` may become eligible only after architect acceptance and Complete state.
- `ARCH-050-SHOPIFY-002` may become eligible only after architect acceptance and Complete state.
- `ARCH-050-API-001` may become eligible only after architect acceptance and Complete state.
- `ARCH-050-API-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] Prisma `validate` succeeds with all `shopify`, `commerce`, and `support` schema references.
- [ ] New/old `ShopSettings` rows have `notifyOnInitialRecoveryOutreach === false` until explicitly updated.
- [ ] New Support messages can link to an existing recovery; deleting the recovery leaves the Support message but nulls its link.
- [ ] Existing Support messages/threads and unique `sourceKey` remain valid; migration applies to populated and fresh disposable databases.
- [ ] Migration SQL is only additive (plus non-destructive FK/index) and does not modify unrelated tables.

## Validation

- [ ] From `moda-interact-database`: `npm run validate`, `npm run prisma:generate` (only as declared in `package.json`).
- [ ] Run the new disposable PostgreSQL migration/schema test for both fresh and upgraded layouts; capture DB evidence for `DEFAULT false` and `ON DELETE SET NULL`.
- [ ] Check generated SQL for qualified schemas and non-destructive operations; `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

All SQL/Prisma changes are **implementation instructions**, not already applied changes. Test the actual generated migration against the canonical Prisma engine rather than replacing `@relation` with an ad-hoc SQL-only FK.

The architect supplied a portable task definition only (**defined but not materialised**). Follow launcher-resolved mirrored task branches, physically isolated parent/implementation worktrees and start-of-attempt evidence. Do not update `docs/decisions/**/_index.md` until the architecture session is explicitly closed.

## Completion Report

### Status

Not Started.

### Files Changed

None (definition only).

### Work Completed

None.

### Validation Results

Not executed; no implementation claimed.

### Deviations

None.

### Assumptions

The task is based on the 2026-10-26 uploaded snapshot and must recheck current canonical code during execution.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Not materialised. Launcher-resolved parent/implementation task worktree, synchronization and branch evidence are required at execution.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet reviewed.

### Follow-up

None.
