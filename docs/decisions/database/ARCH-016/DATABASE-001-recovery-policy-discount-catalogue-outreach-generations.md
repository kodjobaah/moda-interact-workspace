---
id: ARCH-016-DATABASE-001
architecture_id: ARCH-016
title: Persist recovery policy, Shopify discount catalogue, outreach attempts and recovery generations
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
attempt: 1
depends_on: []
enables:
- ARCH-016-SHOPIFY-001
- ARCH-016-BACKGROUND-001
- ARCH-016-SHOPIFY-002
- ARCH-016-ADMIN-001
- ARCH-016-ADMIN-002
- ARCH-016-BACKGROUND-002
- ARCH-016-BACKGROUND-003
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-DATABASE-001

## Objective

Create the complete durable schema required by ARCH-016. This is one database-owned migration/schema task. Do not split the agreed model across later repository tasks.

## Read before editing

```text
prisma/schema.prisma
prisma/migrations/
docs/architecture/ARCH-016-merchant-recovery-policy-shopify-discounts-followups-expiry.md
current ERD generation/validation scripts in package.json
```

## Authorized implementation surface

```text
prisma/schema.prisma
prisma/migrations/<new-ARCH-016-migration>/migration.sql
ERD source/output used by this repository
scripts/validate-*.mjs or scripts/validate-*.ts only when an ARCH-016 schema validator belongs here
package.json only when adding the matching validator command
package-lock.json only if package.json changes
```

No background/application/admin implementation.

## Required schema: merchant offer policy

Add enum in the `shopify` schema:

```prisma
enum RecoveryOfferMode {
  NONE
  FIXED
  AI_BEST_APPLICABLE

  @@schema("shopify")
}
```

Extend existing `ShopSettings` without moving `recoveryDelayMinutes`:

```text
recoveryOfferMode          RecoveryOfferMode @default(NONE)
fixedShopifyDiscountId     String?
followUpEnabled            Boolean @default(false)
followUpDelayMinutes       Int?
```

Add the relation from `fixedShopifyDiscountId` to the local `ShopifyDiscount` row using `onDelete: SetNull`.

Migration CHECK constraints MUST enforce:

```text
recoveryDelayMinutes between 0 and 10080

followUpEnabled = false
  -> followUpDelayMinutes IS NULL

followUpEnabled = true
  -> followUpDelayMinutes between 1 and 10080

recoveryOfferMode = FIXED
  -> fixedShopifyDiscountId IS NOT NULL

recoveryOfferMode != FIXED
  -> fixedShopifyDiscountId IS NULL
```

Cross-shop ownership/current-catalogue validity cannot be fully expressed as a simple CHECK; application/admin writes MUST validate those conditions. Do not add cross-row trigger logic unless required by an existing repository convention.

## Required schema: platform admin override

Create `ShopRecoveryPolicyOverride` in the `shopify` schema.

Required fields:

```text
id                         String @id @default(cuid())
shopId                     String @unique
shop                       Shop relation onDelete Cascade
recoveryDelayMinutes       Int
recoveryOfferMode          RecoveryOfferMode
fixedShopifyDiscountId     String?
fixedShopifyDiscount       ShopifyDiscount? relation onDelete SetNull
followUpEnabled            Boolean
followUpDelayMinutes       Int?
reason                     String @db.VarChar(1000)
expiresAt                  DateTime?
updatedByPlatformAdminId   String
updatedByPlatformAdmin     PlatformAdmin relation
createdAt                  DateTime @default(now())
updatedAt                  DateTime @updatedAt
```

Use the same numeric/mode CHECK constraints as `ShopSettings`.

This row is a complete override snapshot. Do NOT create nullable override fields whose null value means "inherit".

Add durable override audit state in the `shopify` schema:

```text
ShopRecoveryPolicyOverrideAuditAction:
  UPSERT
  CLEAR

ShopRecoveryPolicyOverrideAuditEvent
  id                 String @id @default(cuid())
  shopId             String
  shop               Shop relation onDelete Cascade
  platformAdminId    String
  platformAdmin      PlatformAdmin relation
  action             ShopRecoveryPolicyOverrideAuditAction
  reason             String @db.VarChar(1000)
  beforeValue        Json?
  afterValue         Json?
  occurredAt         DateTime @default(now())

  @@index([shopId, occurredAt])
  @@index([platformAdminId, occurredAt])
```

The audit event MUST NOT foreign-key to the override row itself because CLEAR removes the live override while audit history must survive.

## Required schema: Shopify discount catalogue

Add enums in the `shopify` schema:

```text
ShopifyDiscountCatalogueStatus:
  UNAVAILABLE
  SYNC_REQUIRED
  SYNCING
  CURRENT
  ERROR

ShopifyDiscountMethod:
  AUTOMATIC
  CODE
```

Create one `ShopifyDiscountCatalogue` per shop:

```text
id                    String @id @default(cuid())
shopId                String @unique
shop                  Shop relation onDelete Cascade
status                ShopifyDiscountCatalogueStatus @default(UNAVAILABLE)
syncGeneration        Int @default(0)
activeSyncToken       String?
syncRequestedAt       DateTime?
syncStartedAt         DateTime?
lastSuccessfulSyncAt  DateTime?
lastErrorAt           DateTime?
lastErrorCode         String? @db.VarChar(128)
unavailableAt         DateTime?
createdAt             DateTime @default(now())
updatedAt             DateTime @updatedAt
```

CHECK:

```text
syncGeneration >= 0
status = SYNCING -> activeSyncToken IS NOT NULL AND syncStartedAt IS NOT NULL
status != SYNCING -> activeSyncToken IS NULL
```

Create `ShopifyDiscount` in the `shopify` schema:

```text
id                       String @id @default(cuid())
shopId                   String
shop                     Shop relation onDelete Cascade
shopifyDiscountNodeId    String
providerType             String @db.VarChar(128)
method                   ShopifyDiscountMethod
providerStatus           String @db.VarChar(64)
title                    String
summary                  String?
startsAt                 DateTime?
endsAt                   DateTime?
codeCount                Int?
singleRedeemCode         String?
fixedSelectable          Boolean @default(false)
providerSnapshot         Json
isAvailable              Boolean @default(false)
lastSeenSyncGeneration   Int
lastSyncedAt             DateTime
unavailableAt            DateTime?
createdAt                DateTime @default(now())
updatedAt                DateTime @updatedAt
```

Constraints/indexes:

```text
@@unique([shopId, shopifyDiscountNodeId])
@@index([shopId, isAvailable, providerStatus])
@@index([shopId, fixedSelectable, isAvailable])
@@index([shopId, startsAt, endsAt])

codeCount IS NULL OR codeCount >= 0
lastSeenSyncGeneration >= 0
method = AUTOMATIC -> singleRedeemCode IS NULL
singleRedeemCode IS NOT NULL -> codeCount = 1
fixedSelectable + method CODE -> codeCount = 1 AND singleRedeemCode IS NOT NULL
```

Do not use ARCH-010 promotion tables.

## Required schema: recovery generations

Extend `CheckoutRecovery`:

```text
generation             Int @default(1)
lastExternalActivityAt DateTime
outreachAttempts       RecoveryOutreachAttempt[]
```

Remove:

```prisma
@@unique([shopId, checkoutToken])
```

Add:

```prisma
@@unique([shopId, checkoutToken, generation])
@@index([shopId, checkoutToken, generation])
@@index([status, lastExternalActivityAt])
```

Migration SQL MUST add a PostgreSQL partial unique index for at most one active generation:

```sql
CREATE UNIQUE INDEX ...
ON commerce."CheckoutRecovery" ("shopId", "checkoutToken")
WHERE status IN ('DETECTED', 'MESSAGE_SENT', 'ENGAGED');
```

Use the actual generated enum/storage syntax for this schema. Do not create a second uniqueness mechanism that prevents multiple historical EXPIRED generations.

CHECK:

```text
generation >= 1
lastExternalActivityAt >= detectedAt is NOT required
```

Do not require `lastExternalActivityAt >= detectedAt` because provider activity timestamps may precede local materialisation time.

## Backfill

Existing rows are development data but MUST be migrated, not deleted.

Backfill before applying NOT NULL:

```text
generation = 1
lastExternalActivityAt = GREATEST(detectedAt, COALESCE(engagedAt, detectedAt))
```

Then make `generation` and `lastExternalActivityAt` NOT NULL.

## Required schema: RecoveryOutreachAttempt

Add enums in `commerce`:

```text
RecoveryOutreachTrigger:
  INITIAL
  NO_RESPONSE_FOLLOW_UP

RecoveryOutreachStatus:
  PENDING
  WAITING_FOR_RESPONSE
  ENGAGED
  NO_RESPONSE
  CAPACITY_BLOCKED
  CANCELLED
  FAILED
```

Create:

```text
RecoveryOutreachAttempt
  id                         String @id @default(cuid())
  checkoutRecoveryId         String
  checkoutRecovery           CheckoutRecovery relation onDelete Cascade
  sequence                   Int
  trigger                    RecoveryOutreachTrigger
  status                     RecoveryOutreachStatus @default(PENDING)

  configuredOfferMode        RecoveryOfferMode
  fixedShopifyDiscountId     String?
  fixedShopifyDiscount       ShopifyDiscount? relation onDelete SetNull
  offerSnapshot              Json?

  outboundMessageId          String? @unique
  outboundMessage            ConversationMessage? relation onDelete SetNull

  followUpDueAt              DateTime?
  sentAt                     DateTime?
  customerRespondedAt        DateTime?
  closedAt                   DateTime?
  failureCode                String? @db.VarChar(128)

  createdAt                  DateTime @default(now())
  updatedAt                  DateTime @updatedAt

  @@unique([checkoutRecoveryId, sequence])
  @@index([checkoutRecoveryId, status, sequence])
  @@index([status, followUpDueAt])
```

Add the inverse relation field required by Prisma on `ConversationMessage`; do NOT alter the `Conversation` identity/uniqueness model.

CHECK constraints:

```text
sequence >= 1
trigger INITIAL -> sequence = 1
trigger NO_RESPONSE_FOLLOW_UP -> sequence >= 2
configuredOfferMode FIXED -> fixedShopifyDiscountId IS NOT NULL
configuredOfferMode != FIXED -> fixedShopifyDiscountId IS NULL
status WAITING_FOR_RESPONSE -> sentAt IS NOT NULL AND outboundMessageId IS NOT NULL
customerRespondedAt IS NOT NULL -> sentAt IS NOT NULL
```

Do not persist an `aiSelectedDiscountId`, AI reason, AI candidate list or AI score in ARCH-016.

## Required schema: runtime lifetime + lease

Extend `BackgroundRuntimeConfig`:

```text
checkoutRecoveryLifetimeDays Int @default(21)
```

Add CHECK:

```text
checkoutRecoveryLifetimeDays BETWEEN 1 AND 90
```

Extend `BackgroundRuntimeLeaseName`:

```text
CHECKOUT_RECOVERY_EXPIRY
```

Do not add another expiry cadence field.

## Relations on Shop / PlatformAdmin

Add all inverse relations required by Prisma without changing unrelated semantics.

At minimum Shop must expose:

```text
discountCatalogue
shopifyDiscounts
recoveryPolicyOverride
```

PlatformAdmin must expose its policy overrides if the relation requires an inverse field.

## Migration compatibility

This is a development environment with no live merchants. Still:

- preserve all existing data;
- do not drop Conversation or message history;
- do not drop ARCH-010 promotion data;
- do not recreate databases;
- do not modify unrelated billing ledger models.

## Required validation

Inspect actual `package.json` first. Run repository-declared equivalents of:

```text
npm run validate
npm run prisma:generate
npm run erd        # only if this is the declared ERD command
npm test           # when repository declares tests
```

Also:

```text
npx prisma validate --schema prisma/schema.prisma
npx prisma generate --schema prisma/schema.prisma
```

Run the migration against the repository's configured test/development validation database only when the task environment provides it. If no DB is available, record that exact limitation; do not claim migration execution passed.

## Required tests/validators

Prove via schema/migration validator where practical:

- two EXPIRED generations for same shop+checkout are permitted;
- two active generations for same shop+checkout violate partial unique index;
- generation 1 + active generation 2 after generation 1 EXPIRED is permitted;
- ShopSettings FIXED without discount fails constraint;
- non-FIXED with fixed discount fails constraint;
- follow-up enabled without delay fails constraint;
- lifetime outside 1..90 fails constraint;
- code-selectability constraints reject an invalid single-code claim;
- one outreach sequence per recovery is unique.

## Stop conditions

STOP and return to `moda_architect` if:

- implementing this task would require changing `Conversation @@unique([checkoutRecoveryId])`;
- a proposed schema reuses ARCH-010 promotion entities for Shopify discounts;
- another in-progress database architecture already changed one of these models incompatibly;
- the partial unique active-generation invariant cannot be implemented safely in PostgreSQL migration SQL.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Ready for Review

Implementation commit: `c7a31a1` on `task/ARCH-016-DATABASE-001`, pushed to `origin/task/ARCH-016-DATABASE-001`.

Authorized files changed:

- `prisma/schema.prisma`
- `prisma/migrations/20260916150000_arch016_recovery_policy_discounts_outreach_generations/migration.sql`
- `docs/generated/prisma-erd.puml`
- `docs/generated/erd.png`
- `scripts/validate-arch016-recovery-schema.mjs`
- `package.json`

Implemented the complete ARCH-016 database contract: merchant and platform-admin recovery policy snapshots with audit history; Shopify discount catalogue and selectable-discount constraints; recovery generations with data-preserving backfill and partial active-generation uniqueness; outreach attempts and inverse message relation/checks; runtime lifetime and expiry lease; required tenant/admin inverses; and the focused static validator/ERD updates. Conversation identity uniqueness and ARCH-010 promotion models were preserved.

Validation:

- `npm run validate` passed.
- `npm run prisma:generate` passed.
- `npx prisma validate --schema prisma/schema.prisma` passed.
- `npx prisma generate --schema prisma/schema.prisma` passed.
- `npm run erd` passed, including PlantUML PNG generation.
- `npm run test:arch016-recovery-schema` passed.
- `git diff --check` passed.
- `npm test` was not run successfully because this repository declares no `test` script (`npm error Missing script: "test"`).

Database validation limitation: the verified local database is reachable at `localhost:5432/moda_interact`, but `npx prisma migrate deploy` could not apply pending migrations because the database already contains the failed migration `20260915140000_arch015_fractional_provider_usage_snapshots` (Prisma error P3009). No migration was applied or marked resolved, and the unrelated baseline migration was not changed. The repository-configured remote database was not used for migration execution.

Implementation worktree is clean after commit. Awaiting `moda_architect` review; this agent did not mark the task complete or start dependent tasks.

## Architect Review — Attempt 1

### Status

**Changes Requested — three migration-integrity corrections plus mandatory execution-evidence completion**

This review prioritises ARCH-016 runtime/data correctness over exhaustive test
coverage. The Prisma model shape is otherwise accepted and must not be redesigned in
Attempt 2.

Architect review verified the intended bounded model is present:

```text
merchant ShopSettings recovery policy fields remain merchant-owned
complete ShopRecoveryPolicyOverride snapshot + independent durable audit history
one ShopifyDiscountCatalogue per shop + retained ShopifyDiscount projections
CheckoutRecovery generation identity + partial-active-generation design
RecoveryOutreachAttempt sequence identity + outbound-message provenance
Conversation @@unique([checkoutRecoveryId]) preserved
BackgroundRuntimeConfig.checkoutRecoveryLifetimeDays + CHECKOUT_RECOVERY_EXPIRY lease
ARCH-010 promotion and unrelated billing models preserved
```

The P3009 reported for
`20260915140000_arch015_fractional_provider_usage_snapshots` prevented this ARCH-016
migration from executing, so migration correctness must be reviewed from the checked-in
PostgreSQL SQL as well as from Prisma validation. Three defects remain in that SQL.

### Finding 1 — the old CheckoutRecovery uniqueness object is an index, not a constraint

The immutable first-production migration creates:

```sql
CREATE UNIQUE INDEX "CheckoutRecovery_shopId_checkoutToken_key"
ON "commerce"."CheckoutRecovery"("shopId", "checkoutToken");
```

but the ARCH-016 migration currently attempts:

```sql
ALTER TABLE "commerce"."CheckoutRecovery"
    DROP CONSTRAINT "CheckoutRecovery_shopId_checkoutToken_key",
    ...;
```

PostgreSQL will reject that statement because the named object is a standalone unique
index. Once the pre-existing P3009 is cleared, ARCH-016 would therefore fail before the
generation indexes are installed.

#### Required Attempt-2 correction

In:

```text
moda-interact-database/prisma/migrations/20260916150000_arch016_recovery_policy_discounts_outreach_generations/migration.sql
```

replace the invalid constraint drop with an explicit schema-qualified index drop:

```sql
DROP INDEX "commerce"."CheckoutRecovery_shopId_checkoutToken_key";

ALTER TABLE "commerce"."CheckoutRecovery"
    ADD COLUMN "generation" INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN "lastExternalActivityAt" TIMESTAMP(3);
```

Do **not** modify the historical ARCH-010 migration, rename the old index, add a second
legacy uniqueness mechanism, or use `DROP ... IF EXISTS` to conceal an unexpected
migration-chain mismatch.

### Finding 2 — both follow-up CHECK constraints accept enabled + NULL delay

The current ShopSettings and ShopRecoveryPolicyOverride predicates use the form:

```sql
(NOT "followUpEnabled" AND "followUpDelayMinutes" IS NULL)
OR
("followUpEnabled" AND "followUpDelayMinutes" BETWEEN 1 AND 10080)
```

For `followUpEnabled = true` and `followUpDelayMinutes = NULL`, the second branch
evaluates to SQL `NULL`; PostgreSQL CHECK constraints reject only `FALSE`, so that
invalid row is accepted.

#### Required Attempt-2 correction

Change **both** ARCH-016 follow-up constraints so the enabled branch explicitly proves
non-nullness:

```sql
CHECK (
    ("followUpEnabled" = false AND "followUpDelayMinutes" IS NULL)
    OR
    ("followUpEnabled" = true
        AND "followUpDelayMinutes" IS NOT NULL
        AND "followUpDelayMinutes" BETWEEN 1 AND 10080)
)
```

Apply this to exactly:

```text
ck_arch016_shop_settings_follow_up
ck_arch016_policy_override_follow_up
```

The required behavior is:

```text
disabled + NULL delay       -> allowed
disabled + non-NULL delay   -> rejected
enabled + NULL delay        -> rejected
enabled + 0                 -> rejected
enabled + 1..10080          -> allowed
enabled + 10081             -> rejected
```

Do not change the Prisma field nullability: `followUpDelayMinutes` remains nullable
because disabled policy requires NULL.

### Finding 3 — CODE single-redeem constraints also admit an unknown NULL codeCount

The current predicate:

```sql
"singleRedeemCode" IS NULL OR "codeCount" = 1
```

accepts `singleRedeemCode IS NOT NULL` with `codeCount IS NULL`, again because the
CHECK result becomes SQL `NULL` rather than `FALSE`.

The current fixed-selectable CODE predicate has the same problem when
`fixedSelectable = true`, `method = 'CODE'`, `singleRedeemCode IS NOT NULL`, and
`codeCount IS NULL`.

#### Required Attempt-2 correction

Use predicates that explicitly reject unknown count when claiming one redeem code:

```sql
ADD CONSTRAINT "ck_arch016_discount_single_code"
    CHECK (
        "singleRedeemCode" IS NULL
        OR ("codeCount" IS NOT NULL AND "codeCount" = 1)
    ),
ADD CONSTRAINT "ck_arch016_discount_fixed_selectable"
    CHECK (
        NOT "fixedSelectable"
        OR "method" <> 'CODE'
        OR (
            "codeCount" IS NOT NULL
            AND "codeCount" = 1
            AND "singleRedeemCode" IS NOT NULL
        )
    );
```

The required functional cases are:

```text
CODE + singleRedeemCode non-null + codeCount NULL   -> rejected
CODE + singleRedeemCode non-null + codeCount 0      -> rejected
CODE + singleRedeemCode non-null + codeCount 1      -> allowed by single-code rule
fixedSelectable CODE + codeCount NULL               -> rejected
fixedSelectable CODE + codeCount 1 + code non-null  -> allowed
AUTOMATIC + singleRedeemCode non-null                -> still rejected by existing automatic-code rule
```

Preserve the existing rule that non-selectable catalogue rows may carry zero,
multiple, or unknown code counts when no deterministic single code is claimed.

### Focused validator correction

Update:

```text
moda-interact-database/scripts/validate-arch016-recovery-schema.mjs
```

The current validator checks constraint/index **names** but does not prove the SQL
semantics that failed this review. Strengthen it so Attempt 2 fails deterministically
if any of the three defects is reintroduced.

At minimum assert:

1. the ARCH-016 migration contains:

```sql
DROP INDEX "commerce"."CheckoutRecovery_shopId_checkoutToken_key"
```

and does **not** contain:

```text
DROP CONSTRAINT "CheckoutRecovery_shopId_checkoutToken_key"
```

2. both follow-up constraints contain an explicit enabled-branch
`"followUpDelayMinutes" IS NOT NULL` guard before/rationally together with the
`BETWEEN 1 AND 10080` bound;
3. the single-code predicate explicitly requires `"codeCount" IS NOT NULL` when
`singleRedeemCode` is present;
4. the fixed-selectable CODE predicate explicitly requires both
`"codeCount" IS NOT NULL` and `"singleRedeemCode" IS NOT NULL`.

A static migration-contract validator is sufficient for this correction while the
pre-existing P3009 prevents executing ARCH-016. Do not build a new database-test
framework solely for Attempt 2.

### Mandatory worktree / launcher evidence

The Attempt 1 Completion Report records branch cleanliness but omits the physical
worktree and start-of-attempt synchronization evidence required by
`docs/agent-worktree-isolation-policy.md`.

Attempt 2 must run through the normal `/moda-task ARCH-016-DATABASE-001` preparation
path and record the launcher's actual evidence. The Completion Report must contain:

```text
Physical worktree isolation:
  canonical workspace root: <launcher-resolved path>
  parent worktree: <launcher-resolved path>
  parent branch: task/ARCH-016-DATABASE-001
  implementation worktree: <launcher-resolved path>
  implementation branch: task/ARCH-016-DATABASE-001
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
  recursive implementation submodule preparation: passed; no recursive submodules present
  launcher claim commit: <actual claim commit>
```

If the canonical worktrees already contain the pushed Attempt 1 branches, reuse them
according to the launcher policy. Do not recreate implementation work merely to
manufacture a new commit.

### Attempt-2 authorised implementation scope

Modify only what is needed for the corrections:

```text
prisma/migrations/20260916150000_arch016_recovery_policy_discounts_outreach_generations/migration.sql
scripts/validate-arch016-recovery-schema.mjs
this task Completion Report / review metadata
```

`prisma/schema.prisma` is already conformant and should not be changed for these
findings. `package.json`, ERD source/output, and unrelated migration files must remain
unchanged unless a normal required regeneration after synchronization produces a
genuine deterministic change.

Specifically do **not** modify or resolve:

```text
prisma/migrations/20260915140000_arch015_fractional_provider_usage_snapshots/migration.sql
```

and do not mark any failed migration resolved as part of ARCH-016-DATABASE-001.

### Attempt-2 validation

After the corrections, run from the canonical implementation task worktree:

```text
npm run validate
npm run prisma:generate
npx prisma validate --schema prisma/schema.prisma
npx prisma generate --schema prisma/schema.prisma
npm run erd
npm run test:arch016-recovery-schema
git diff --check
```

Also retry:

```text
npx prisma migrate deploy --schema prisma/schema.prisma
```

against the same repository-configured local/test validation database. If the
pre-existing ARCH-015 P3009 still blocks execution **before ARCH-016 begins**, record
that exact unchanged blocker and stop database deployment there. Do not modify,
resolve, skip, or replace the ARCH-015 migration and do not use the remote database
merely to obtain a passing result.

This repository declares no generic `npm test` script; do not invent one.

### Completion / stop condition

Attempt 2 is ready for re-review only when:

```text
old CheckoutRecovery unique index is dropped with DROP INDEX
follow-up enabled + NULL delay is rejected in both policy tables
single redeem code + NULL codeCount is rejected
fixed-selectable CODE + NULL codeCount is rejected
focused validator proves all four migration predicates above
required launcher/worktree/synchronization evidence is in the Completion Report
all available required validation passes
P3009, if still present, is recorded only as the unchanged pre-existing blocker
```

Then publish the implementation and parent task branches, set this same task back to
`status: review`, clear `executor`/`claimed_at`, record Attempt 2 commits/evidence, and
return to `moda_architect`.

No dependent ARCH-016 task is promoted by this review. `attempt` remains `1` in this
Changes Requested patch; the deterministic launcher owns the increment to Attempt 2
when the task is reclaimed.
