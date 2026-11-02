---
id: ARCH-055-DATABASE-001
architecture_id: ARCH-055
title: Add explicit persistence metadata and narrowly correct existing guards
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
- ARCH-055-BACKGROUND-001
- ARCH-055-API-001
- ARCH-055-API-005
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-02
---

# ARCH-055-DATABASE-001: Add explicit persistence metadata and narrowly correct existing guards

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 3. Explicit narrow persistence contract, including the bounded ARCH-040 validator compatibility amendment. Attempt 2 addresses the published Attempt 1 review.

**Definition state:** materialised in the canonical launcher-prepared worktrees. Attempt 2 corrections and required validation are complete and submitted for architect review. The implementation is not accepted and no dependent task was advanced.

## Objective

Add exactly two nullable persistence fields, one claim-key backfill, one original-intake partial unique index and one narrowly scoped correction to the existing REST attempt guard/time CHECK, through three new forward-only migration scripts. API/Shopify/Background services own workflow validation; no new business-policy trigger is authorised.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E09`, `E11`, `E12`, `E29`, `E39`, `E40`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

All implementation paths below are relative to `moda-interact-database`. This is an edit allowlist, not permission to modify consumer schema copies.

**Modify exactly these existing files (revision 3 includes a bounded validator compatibility amendment):**

- `prisma/schema.prisma`: only the two field insertions shown below.
- `package.json`: only the three script entries shown below; preserve every existing key, dependency and command.
- `scripts/validate-arch040-human-prepared-schema.mjs`: only migration-boundary compatibility needed to retain all existing structural assertions after forward migrations.
- `scripts/test-arch040-human-prepared-postgres.mjs`: only migration-boundary compatibility and reuse/execution of the unchanged prepared-body/permit/state/release behavioral assertions against the ARCH-055 post-migration schema.

**Create exactly these files:**

- `prisma/migrations/20261102120000_arch055_rest_read_lifecycle/migration.sql`
- `prisma/migrations/20261102121000_arch055_human_follow_up_claim_identity/migration.sql`
- `prisma/migrations/20261102122000_arch055_upload_intake_identity/migration.sql`
- `scripts/test-arch055-database-contracts-postgres.mjs`
- `scripts/validate-arch055-database-contracts.mjs`
- `scripts/fixtures/arch055/legacy-fixtures.mjs`
- `scripts/fixtures/arch055/assertions.mjs`

These are **eleven permitted implementation files in total** after the revision 3 validator compatibility amendment. Attempt 1 changed only the original nine. This task file's execution metadata/Completion Report is the separately permitted parent-repository write. No other implementation file is authorised. All other existing validators and every prior migration file remain read-only. The two named ARCH-040 validator exceptions do not authorize changing expected guard behavior or weakening assertions. If a new task-relevant blocker genuinely requires another path, return it before editing that path.

### Exact Prisma insertions — not replacement models

In `MerchantConversationSendCommand`, insert the field immediately after the existing `idempotencyKey` field:

```prisma
model MerchantConversationSendCommand {
  // Existing surrounding fields remain; this is only the insertion location.
  idempotencyKey    String  @db.VarChar(128)
  followUpClaimKey  String? @db.VarChar(255)
  payloadSha256    String  @db.VarChar(64)
  // Preserve every other field, relation, @@unique/@@index and @@schema("whatsapp").
}
```

In `MerchantKnowledgeUploadedAsset`, insert the field immediately after `dataFormatId`:

```prisma
model MerchantKnowledgeUploadedAsset {
  // Existing surrounding fields remain; retain the actual repository alignment.
  dataFormatId      String  @db.Text
  intentPurposeKey  String? @db.VarChar(64)
  // Preserve status, objectKey and every other field, relation/index and @@schema("commerce").
}
```

Neither new field has a default, `@unique`, relation, enum, index or required/non-null declaration. No new models. No Prisma `@unique` on revision `uploadedAssetId`: the SQL index below is partial and must not forbid REPROCESS/ENTITLEMENT_CHANGE.

### Exact package.json additions

Insert only these keys into the existing `scripts` object; do not replace that object:

```json
{
  "test:arch055-database-contracts": "node scripts/validate-arch055-database-contracts.mjs",
  "test:arch055-database-contracts:postgres:fresh": "node scripts/test-arch055-database-contracts-postgres.mjs --mode fresh",
  "test:arch055-database-contracts:postgres:upgrade": "node scripts/test-arch055-database-contracts-postgres.mjs --mode upgrade"
}
```

### Migration application rules

Create the three paths above in that order, with the exact executable SQL specified below. Comments/formatting may be normalised; SQL predicates, names, ordering and transaction boundaries must not change. They are implementation deliverables—not scripts run by this architecture patch.

No existing migration file, checksum/history row, seed or table contents may be reset. Do not use `db push`, `migrate reset`, migration squashing, `migrate resolve` to conceal drift, `IF NOT EXISTS` to hide an unexpected pre-existing change, or an automatic down migration. Apply later corrections through another architect-approved forward migration. An occupied target migration name or changed baseline guard is a stop-and-report condition; do not silently choose a different timestamp or reconstruct another baseline.

**Forward does not mean the old SQL function can never be corrected.** Migration 1 replaces its currently installed definition through a *new* script and replaces exactly one existing CHECK. Those explicit DDL replacements are authorised; dropping columns/tables/data, grant guards or unrelated constraints is not.

No application calls, data grants, provider operations or storage deletion occur in a migration.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

### Ownership boundary

Database owns storage and the explicitly named structural index/correction below. API-001 owns current ACTIVE Shop/installation/version admission, callback expiry decisions and revoke predicates; API-004/SHOPIFY-001 own key generation and atomic claim admission; BACKGROUND-001 owns persisted-key fences/release; API-005 owns purpose nonblank/unchanged validation, complete retry comparison, MIME/expiry checks and asset locking. Do not duplicate these workflows in new triggers. SQL deliberately allows null storage for legacy/unaffected writers; an API-validated field is not a new blanket database non-null policy.

No new command-key trigger, key=command.id CHECK, upload-purpose nonblank CHECK or upload-purpose immutability trigger is allowed. Preserve all pre-existing foreign keys, lifecycle, prepared-body, provider-permit, release and accounting safeguards except the exact correction in migration 1.

### Migration 1 — failed terminalisation only

`prisma/migrations/20261102120000_arch055_rest_read_lifecycle/migration.sql`

The baseline `arch026_rest_read_attempt_guard` AND `WooCommerceRestReadAttempt_consumption_time_check` reject expired FAILED terminalisation. Correct both. The early FAILED branch remains after immutable-identity/single-use checks, requires a terminal timestamp, assigns the transaction ID and cannot mint a grant. The unchanged lifecycle CHECK still requires a nonblank failure code. FAILED timestamps may be after expiry but never before creation. Successful consumption retains its expiry/generation/active-installation checks, same-transaction grant relationship and deferred commit guard. Do not add a Shop ACTIVE/revokedAt query here: those newly selected checks belong to API admission.

Expected SQL:

```sql
BEGIN;

ALTER TABLE "woocommerce"."WooCommerceRestReadAttempt"
  DROP CONSTRAINT "WooCommerceRestReadAttempt_consumption_time_check";
ALTER TABLE "woocommerce"."WooCommerceRestReadAttempt"
  ADD CONSTRAINT "WooCommerceRestReadAttempt_consumption_time_check"
  CHECK (
    "consumedAt" IS NULL OR
    ("consumedAt" >= "createdAt" AND
      ("status" = 'FAILED' OR "consumedAt" <= "expiresAt"))
  );

CREATE OR REPLACE FUNCTION "woocommerce"."arch026_rest_read_attempt_guard"()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
  current_version INTEGER;
  current_status "woocommerce"."WooCommerceInstallationStatus";
  shop_platform "commerce"."ShopPlatform";
BEGIN
  IF TG_OP = 'UPDATE' THEN
    IF (NEW."id", NEW."installationId", NEW."shopId", NEW."tokenDigest",
        NEW."attemptSequence", NEW."credentialVersionSnapshot", NEW."expiresAt", NEW."createdAt")
       IS DISTINCT FROM
       (OLD."id", OLD."installationId", OLD."shopId", OLD."tokenDigest",
        OLD."attemptSequence", OLD."credentialVersionSnapshot", OLD."expiresAt", OLD."createdAt") THEN
      RAISE EXCEPTION 'Woo REST authorisation attempt identity is immutable' USING ERRCODE = '23514';
    END IF;
    IF OLD."status" <> 'PENDING' OR NEW."status" = 'PENDING' THEN
      RAISE EXCEPTION 'Woo REST authorisation attempt is single use' USING ERRCODE = '23514';
    END IF;
    -- Failure terminalisation is not bearer consumption that can mint a grant.
    -- Preserve identity and single-use checks above; lifecycle CHECK still requires failureCode.
    IF NEW."status" = 'FAILED' THEN
      IF NEW."consumedAt" IS NULL THEN
        RAISE EXCEPTION 'Woo REST failed attempt requires terminal timestamp' USING ERRCODE = '23514';
      END IF;
      NEW."consumptionTransactionId" := txid_current();
      RETURN NEW;
    END IF;
    IF NEW."consumedAt" IS NULL OR clock_timestamp() > NEW."expiresAt" THEN
      RAISE EXCEPTION 'Woo REST authorisation attempt expired or not consumed' USING ERRCODE = '23514';
    END IF;
    -- A grant may only be minted by the SAME database transaction that consumed
    -- the bearer. Once committed, the bearer cannot mint another grant even if
    -- a selected grant was subsequently deleted.
    NEW."consumptionTransactionId" := txid_current();
  ELSIF NEW."status" <> 'PENDING' OR NEW."consumedAt" IS NOT NULL OR
        NEW."consumptionTransactionId" IS NOT NULL THEN
    RAISE EXCEPTION 'Woo REST authorisation attempt must begin pending' USING ERRCODE = '23514';
  END IF;

  SELECT installation."credentialVersion", installation."status", shop."platform"
    INTO current_version, current_status, shop_platform
  FROM "woocommerce"."WooCommerceInstallation" installation
  JOIN "commerce"."Shop" shop ON shop."id" = installation."shopId"
  WHERE installation."id" = NEW."installationId"
    AND installation."shopId" = NEW."shopId"
  FOR SHARE OF installation, shop;
  IF NOT FOUND OR shop_platform <> 'WOOCOMMERCE' OR current_status <> 'ACTIVE' THEN
    RAISE EXCEPTION 'Woo REST authorisation requires active Woo installation' USING ERRCODE = '23514';
  END IF;
  IF NEW."credentialVersionSnapshot" <> current_version THEN
    RAISE EXCEPTION 'Woo REST authorisation installation generation is stale' USING ERRCODE = '23514';
  END IF;
  IF TG_OP = 'INSERT' AND NEW."expiresAt" <= clock_timestamp() THEN
    RAISE EXCEPTION 'Woo REST authorisation attempt is already expired' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$$;

COMMIT;
```

Leave `arch026_rest_read_grant_guard`, `arch026_rest_read_attempt_commit_guard`, their attached triggers and all grant rows byte-/value-equivalent. The complete replacement function above is derived from the uploaded baseline, not from an obsolete earlier handover guard.

### Migration 2 — storage and historical claim identity

`prisma/migrations/20261102121000_arch055_human_follow_up_claim_identity/migration.sql`

All historical template commands, including CLAIMED/SENT/UNKNOWN/CANCELLED, keep their own original `idempotencyKey` as the persisted claim key. HUMAN_TEXT receives SQL NULL. Never obtain a historical key from its current attempt: cancellation/reclaim can have assigned that attempt to a later owner. Never rewrite `RecoveryOutreachAttempt.initiationKey`, public keys, IDs, timestamps, messages, moderation, counters, provider permits or state.

The pre-existing command guard rejects ordinary CLAIMED-to-CLAIMED updates, so a plain metadata backfill is insufficient. The only authorised bypass is the one named trigger under the exclusive table lock within this one transaction. Other triggers/FKs remain active; no `DISABLE TRIGGER ALL/USER`, replication-role override or trigger-function rewrite is allowed. Failure before re-enable must roll back the disable, column and backfill together. The original function body and trigger enabled state must be restored unchanged before commit.

Expected SQL:

```sql
BEGIN;

-- Quiesce the relevant producers/consumers before deployment. This lock also
-- prevents a concurrent writer observing the one-trigger backfill exception.
LOCK TABLE "whatsapp"."MerchantConversationSendCommand" IN ACCESS EXCLUSIVE MODE;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger
    WHERE tgrelid = '"whatsapp"."MerchantConversationSendCommand"'::regclass
      AND tgname = 'arch040_command_guard'
      AND NOT tgisinternal AND tgenabled = 'O'
  ) THEN
    RAISE EXCEPTION 'ARCH055 expected enabled arch040_command_guard; stop upgrade';
  END IF;
END;
$$;

ALTER TABLE "whatsapp"."MerchantConversationSendCommand"
  ADD COLUMN "followUpClaimKey" VARCHAR(255);

-- The baseline command guard rejects ordinary CLAIMED -> CLAIMED writes,
-- including metadata-only writes. Bypass ONLY that trigger, ONLY under the
-- exclusive lock and in this transaction. Do not change its function body.
ALTER TABLE "whatsapp"."MerchantConversationSendCommand"
  DISABLE TRIGGER arch040_command_guard;
UPDATE "whatsapp"."MerchantConversationSendCommand"
  SET "followUpClaimKey" = "idempotencyKey"
  WHERE "kind" = 'RECOVERY_FOLLOW_UP_TEMPLATE';
ALTER TABLE "whatsapp"."MerchantConversationSendCommand"
  ENABLE TRIGGER arch040_command_guard;

COMMIT;
```

New writers set the key correctly and treat it as immutable in service code; the database does not add a new key-policy trigger. Missing keys are fail-closed at Background dispatch, never silently derived from public request data.

### Migration 3 — upload metadata and one original intake

`prisma/migrations/20261102122000_arch055_upload_intake_identity/migration.sql`

All existing assets retain SQL NULL for purpose; no inferred purpose or destructive storage cleanup. New Woo intent writers supply the canonical key. Original-intake uniqueness applies only to non-null assets referenced by CREATE/FILE_REPLACE; multiple REPROCESS/ENTITLEMENT_CHANGE rows remain legal. Duplicate intake history must block the entire migration before the index exists; report bounded counts, not file contents or credentials. No history deduplication, relabelling or deletion is authorised.

Expected SQL:

```sql
BEGIN;

ALTER TABLE "commerce"."MerchantKnowledgeUploadedAsset"
  ADD COLUMN "intentPurposeKey" VARCHAR(64);

LOCK TABLE "commerce"."MerchantKnowledgeSourceRevision" IN SHARE ROW EXCLUSIVE MODE;
DO $$
DECLARE duplicate_asset_count BIGINT;
BEGIN
  SELECT count(*) INTO duplicate_asset_count
  FROM (
    SELECT "uploadedAssetId"
    FROM "commerce"."MerchantKnowledgeSourceRevision"
    WHERE "uploadedAssetId" IS NOT NULL
      AND "reason" IN ('CREATE', 'FILE_REPLACE')
    GROUP BY "uploadedAssetId"
    HAVING count(*) > 1
  ) duplicate_intakes;
  IF duplicate_asset_count > 0 THEN
    RAISE EXCEPTION 'ARCH055 original-intake uniqueness blocked: % assets', duplicate_asset_count
      USING ERRCODE = '23505';
  END IF;
END;
$$;

CREATE UNIQUE INDEX "MerchantKnowledgeSourceRevision_original_intake_asset_key"
  ON "commerce"."MerchantKnowledgeSourceRevision" ("uploadedAssetId")
  WHERE "uploadedAssetId" IS NOT NULL AND "reason" IN ('CREATE', 'FILE_REPLACE');

COMMIT;
```

### Harness requirements

Copy the disposable test **pattern** from `scripts/test-arch053-woo-restore-snapshot-postgres.mjs`, not its restoration schema assertions. Runner accepts exactly `--mode fresh` or `--mode upgrade`, rejects missing/extra/unknown arguments before Docker, provisions a uniquely named `pgvector/pgvector:pg17` container with network `none`, uses container-local psql with `ON_ERROR_STOP=1`, and always removes its own container in `finally`. Do not read a hosted `DATABASE_URL`, accept an external DB URL or contact R2/providers.

Fresh mode applies canonical migrations in sorted order through `20261102122000_arch055_upload_intake_identity`, then runs the F cases below. Upgrade mode applies all predecessors before migration 1, seeds legacy fixtures using the real canonical constraints, records complete existing-row snapshots excluding only the new fields, then applies the three new scripts in order and runs U cases. Do not assume these migrations remain the last migrations forever; apply only through the named target. Record every applied migration name/hash. Duplicate-intake and rollback-failure cases use separate disposable databases inside the same container, not invalid state in the positive fixture database.

The static validator checks exactly two Prisma additions, three ordered migration files, expected executable SQL, absence of unapproved DDL, unchanged predecessor hashes, expected script keys and guard-function preservation. Prisma schema-to-schema diff should show only the two nullable column additions; the guard/CHECK replacement, exact metadata backfill and partial index are deliberately hand-authored SQL, not unexplained ORM drift. Store no generated Prisma client in consumer repositories.

### Common execution and safety contract

- Read this task, the parent architecture, `docs/observability/shared-logging.md` and the four workspace VCS/worktree/developer/materialisation policies. Use the launcher-resolved dedicated parent and implementation worktrees; do not invent paths or start another task. A prepared launcher packet is accepted startup evidence.
- Use the existing Node/toolchain. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. Do not select/install a different Node version to make validation appear to pass.
- All workspace edits use repository-relative paths. Never edit another repository's implementation or a nested Database schema copy. A consumer records/updates only its own accepted nested Database pin under the task contract; never stage the parent workspace gitlink to an unmerged implementation commit.
- Shared logging is `@modainteract/moda-interact-shared/logging`. Preserve the actual original Prisma/SDK/provider message, code, cause and relevant safe response details through typed errors. Internal reason codes supplement, never replace, that evidence. Redact secrets, signed capabilities, customer content and connection URLs; public responses stay bounded. No generic local logger or duplicate framework telemetry.
- Preserve tenant scoping, canonical Shared schemas, immutable evidence, deliberate no-op/replay rules and original provider ambiguity. No provider/Redis/R2 I/O inside a database transaction. Read endpoints remain free of writes unless an explicitly unchanged contract says otherwise.
- Review baseline observations are static. Run regression tests against canonical migrations on disposable PostgreSQL 17 + pgvector, using separate connections and explicit barriers for races. Do not substitute mocks, `db push` or review-only Python models for lock/trigger proof.
- This schema task records before/after catalogue definitions, row preservation, migration checksums and affected backfill rows. It does not benchmark API query/latency savings or certify API policy validation.
- Existing baseline failures are handled through `docs/development-baseline.md` only when actually encountered and relevant. Do not waive new regressions. Record commands actually executed and leave unavailable validations unchecked.
- Do not edit any `docs/decisions/**/_index.md`, old task status, the parent architecture, another task or shared execution rollup from a repository implementation task. Parent report updates are confined to this task file. No merge or push to main.

## Work Items

- [x] Insert the two exact nullable Prisma fields; preserve all other schema declarations.
- [x] Create the three forward migration files with the expected SQL; predecessor hashes remain unchanged.
- [x] Add the three exact package script keys, static validator and modular fresh/upgrade runner.
- [x] Implement and exercise every F/U case in the acceptance matrix, including CLAIMED backfill and transactional trigger re-enable failure.
- [x] Run declared schema/client/diff/static/fresh/upgrade and predecessor checks, including ARCH-040 checks after ARCH-055.
- [x] Record that consumer pin adoption and coordinated rollout remain gated on acceptance and belong to downstream tasks; return for review without executing consumers.

## Interfaces / Contracts

| Prisma/storage field | SQL representation | Writer / consumer contract |
|---|---|---|
| `MerchantConversationSendCommand.followUpClaimKey: string \| null` | `whatsapp."MerchantConversationSendCommand"."followUpClaimKey" VARCHAR(255) NULL`, no default/index | API-004/SHOPIFY-001 set new template key to preallocated command ID; Background reads the persisted field. Legacy templates preserve their old public key; HUMAN_TEXT null. |
| `MerchantKnowledgeUploadedAsset.intentPurposeKey: string \| null` | `commerce."MerchantKnowledgeUploadedAsset"."intentPurposeKey" VARCHAR(64) NULL`, no default/index | API-005 writes requested canonical purpose once and rejects changed retry metadata. Unknown legacy pending purpose is not inferred. |
| Original intake | partial index `MerchantKnowledgeSourceRevision_original_intake_asset_key` | One CREATE/FILE_REPLACE per non-null uploaded asset; later reprocessing remains legal. |
| Failed REST attempt | existing row/enum/function; no new model or public schema | API-001 authorises cancellation; storage permits safe terminalisation after expiry/rotation without permitting a grant. |

New fields are internal only. No Shared release, public request/response version, provider key or queue payload changes. Existing grants, provider permits, command identity, prepared moderation, receipt/history and all unrelated data remain unchanged. Consumers adopt the accepted Database pin through their own tasks.

## Dependencies

None. The source baseline is context, not a fabricated dependency on historical review evidence.

## Enables

- `ARCH-055-BACKGROUND-001`
- `ARCH-055-API-001`
- `ARCH-055-API-005`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

| ID | Required database proof | Expected outcome |
|---|---|---|
| F01 | Inspect `information_schema.columns` for both new columns | Correct schema/table, varchar lengths 255/64, nullable, SQL NULL when omitted, no default. |
| F02 | Inspect functions, triggers, constraints and indexes | Only named attempt function/CHECK changed; no new business-policy trigger; original-intake index has exactly the supplied predicate. |
| F03 | Pending attempt -> FAILED after expiry; repeat after installation rotation | Succeeds with current terminal timestamp/nonblank failure code; identity unchanged; cannot mint a grant. |
| F04 | Expired/stale attempt -> SUCCEEDED; successful consumption without same-transaction grant; terminal retry/identity edit | Existing rejection/rollback retained. A failure timestamp before creation remains rejected. |
| F05 | One original intake plus multiple reprocessing/entitlement revisions | Legal; second CREATE/FILE_REPLACE using the asset rejected. Null asset web revisions unaffected. |
| F06 | Existing command prepared-body, permit, same-recovery, state and release guard tests | Preserved; no relaxation to obtain the metadata backfill. |
| U01 | Seed valid template commands in ACCEPTED, CLAIMED (active lease), DISPATCH_ADMITTED, UNKNOWN, SENT, FAILED and CANCELLED, plus HUMAN_TEXT | Each template backfills its own old idempotencyKey; HUMAN_TEXT stays SQL NULL; all old columns unchanged, including updatedAt. |
| U02 | Seed historical cancellation/reclaim pairs using the same attempt but different keys | Backfill each command from its own key, never current attempt key. Attempt and provider evidence unchanged. |
| U03 | Abort the migration transaction after the single trigger disable in a disposable failure fixture | Column/data/trigger enablement rollback; trigger remains enabled; normal migration subsequently succeeds. |
| U04 | Snapshot legacy pending/completed/deleted assets and original/reprocess revisions | Old columns/history unchanged; intentPurposeKey SQL NULL; no R2 deletion/backfill. |
| U05 | Separate upgrade DB with duplicate original-intake rows | Migration 3 fails with bounded count; its column/index additions roll back; no history changes. |
| U06 | Hash all predecessor migrations and snapshot non-target schema objects | No predecessor edits, missing objects, changed grant function or leftover disabled triggers. |
| U07 | Invalid/missing/extra mode args; forced SQL assertion failure | Non-zero result, no external DB contact, container cleanup even on failure. |

- [x] Every F/U case passed on canonical disposable PostgreSQL, with U07 invalid-argument Docker-sentinel evidence and forced top-level failure cleanup evidence recorded below.
- [x] Exactly the approved implementation files changed; original application policy moved to owning service tasks, not replaced by new database triggers.
- [x] Migration application order, SQL hashes, fixture identities, backfill counts, diff evidence and cleanup recorded.
- [ ] Tasks remain unaccepted until architect review; no consumer deployment or production migration claimed.

## Validation

Run from the launcher-resolved Database implementation worktree, using its installed toolchain:

- [x] `npm run validate`
- [x] `npm run prisma:generate`
- [x] `npm run test:arch055-database-contracts`
- [x] `npm run test:arch055-database-contracts:postgres:fresh`
- [x] `npm run test:arch055-database-contracts:postgres:upgrade`
- [x] `npm run test:arch026-woocommerce-rest-read-grant`
- [x] `npm run test:arch040-human-prepared-schema`
- [x] `npm run test:arch040-human-prepared:postgres`
- [x] `npx eslint --max-warnings=0 scripts/test-arch055-database-contracts-postgres.mjs scripts/validate-arch055-database-contracts.mjs scripts/fixtures/arch055/legacy-fixtures.mjs scripts/fixtures/arch055/assertions.mjs scripts/test-arch040-human-prepared-postgres.mjs scripts/validate-arch040-human-prepared-schema.mjs`
- [x] `git diff --check`

Before editing, the runner/static validator captures the pre-change schema and canonical migration hashes in its disposable work directory. Run the installed Prisma v6 schema-to-schema diff with `--from-schema-datamodel <captured-baseline-schema> --to-schema-datamodel prisma/schema.prisma --script` and assert exactly the two column additions, no unrelated Prisma changes. This baseline path is runtime-generated test evidence, not a developer-specific hardcoded location. Static validator tests the hand-authored SQL separately.

The three `test:arch055-*` script keys are required new deliverables, not baseline commands claimed to exist already. Other named npm keys exist in the inspected package. Do not run deployed migration apply commands against a hosted database in this task. No automatic down/reset is provided.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

Reference `ARCH-053-DATABASE-001` for the same deterministic definition style: explicit insertions, preserved fields, schema-qualified expected SQL, package script additions, independent fresh/upgrade cases and forward-only migration discipline. Do not copy that task's completed status, historical commits, fixture schema or acceptance into this task.

All three SQL scripts are forward deployments. The one existing CHECK replacement and one temporarily disabled guard are specifically enumerated above and fully transactional; there is no blanket permission to weaken/drop guards. Table/row snapshots and failure injection must prove that only the intended metadata changes persist. No unbound purpose is invented.

If any ARCH-055 migration from a different definition was already executed anywhere relevant, STOP: do not rewrite that history or reuse these names for different SQL. Return the applied migration names/checksums so a separately named forward reconciliation can be defined. The same applies if the pinned baseline function has changed. No application implementation is authorised here.

## Completion Report

### Status

Attempt 1 was published and returned to **Ready** after architect review. Attempt 2 corrections are implemented and all required validations pass; this task is submitted as **Review** for architect acceptance. No dependent task is advanced before acceptance.

The Files Changed, Work Completed, Validation Results, Worktree and Git Evidence, Deviations, Assumptions, Unresolved Issues, and Architectural Concerns immediately below are the historical Attempt 1 report. Attempt 2's current evidence is recorded after the immutable Attempt 1 architect review.

### Files Changed

Exactly the nine allowlisted implementation files: the three package script entries, two nullable Prisma fields, three forward-only SQL migrations, the static contract validator, the disposable PostgreSQL fresh/upgrade runner, and two ARCH-055 fixture/assertion modules. No other implementation paths changed.

### Work Completed

- Added `followUpClaimKey VARCHAR(255) NULL` and `intentPurposeKey VARCHAR(64) NULL` in Prisma and forward migrations.
- Migration 1 permits only failed REST-attempt terminalisation after expiry/credential rotation while retaining success/grant and identity safeguards.
- Migration 2 backfills each historical follow-up template from its own `idempotencyKey`, with HUMAN_TEXT remaining NULL. The exclusive-lock, single-trigger disable/re-enable sequence is transactional.
- Migration 3 adds the partial unique original-intake index and rejects pre-existing duplicates transactionally.
- Added exact-change validation and isolated fresh/upgrade PostgreSQL 17 harnesses. U03 now seeds legacy rows and proves rollback restores the column, all row data, and enabled trigger before a normal retry.
- No consumer pin or rollout was performed: the Database change has not been accepted, and those handoffs belong to downstream tasks.

### Validation Results

Passed:

- `npm run validate` — Prisma schema valid.
- `npm run prisma:generate` — generated Prisma Client v6.19.3. The first ordinary attempt hit a node_modules permission error; retry with elevated filesystem access passed.
- `npm run test:arch055-database-contracts` — exactly two Prisma column additions; exact file allowlist; three expected migrations; all 68 predecessor migration hashes unchanged.
- `npm run test:arch055-database-contracts:postgres:fresh` — passed F01–F05, U03 rollback with seeded row preservation, U05 duplicate rejection, and U06 non-target catalogue snapshots; disposable container removed.
- `npm run test:arch055-database-contracts:postgres:upgrade` — passed F01–F05, U01/U02/U04 historical backfill and row preservation, U03 rollback with seeded row preservation, U05 duplicate rejection, and U06 non-target catalogue snapshots; disposable container removed.
- `npm run test:arch026-woocommerce-rest-read-grant` — passed.
- Focused ESLint for the four new JavaScript files and `git diff --check` — passed.
- The harness ran the canonical 68 predecessor migrations plus the 3 target migrations in both modes; target SHA-256 values: `c129466fdb53190b7f8ce6c2d3a04867c6bacbd55e334c5e0bceeb1b28e4e53b`, `e4689790fbba7f606803b2d0370a66ba8b4f57bb3cb0b67b154336f90c2d41fb`, `e9ce08d49576f84a4e1b95c39637c69e97f0f620b4fae608fadf2712fefb6a37`.

Blocked or incomplete:

- `npm run test:arch040-human-prepared-schema` — fails before its checks because it asserts `20261026080000_arch040_prepared_human_message_content` is the last migration; actual last migration is `20261102122000_arch055_upload_intake_identity`. The validator is outside this task's edit allowlist.
- `npm run test:arch040-human-prepared:postgres` — ordinary invocation could not access the Colima Docker socket. An elevated retry was started but interrupted before an outcome was captured. Prior execution evidence in this task session also identified the same stale last-migration assumption in this script. Treat F06 as unchecked until the architect reconciles the predecessor validators and the PostgreSQL guard suite is run successfully.
- U07's invalid/missing/extra argument subprocess cases were not explicitly executed. The runner rejects arguments before Docker startup, and U03/U05 demonstrate SQL-failure cleanup, but this does not replace the requested argument-case evidence.

The ARCH-040 validator failure is a migration-chain compatibility issue, not evidence that ARCH-055 changed the prepared-body guard: the task harness snapshots all non-target functions, constraints, indexes and triggers before and after migration and found no change. No out-of-scope predecessor file was modified to hide the failure.

### Worktree and Git Evidence

- Launcher root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-DATABASE-001`, branch `task/ARCH-055-DATABASE-001`, synchronized SHA `6a7f325663fd43adb9008bb10e8538f9265c6864`; parent task branch fast-forward not needed; `origin/main` already current.
- Database implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-DATABASE-001`, branch `task/ARCH-055-DATABASE-001`, synchronized SHA `7c377282aa5819b3008b7d7f3018f44f4161523e`; implementation branch fast-forward not needed; `origin/main` already current.
- Recursive submodule sync and init/update passed; no submodule entries were present.
- Claim publication: `a6f369aa761b9878d82ed679d9b3a4d640b8ddcc`.
- Implementation commit: `4fded01` (`task(ARCH-055-DATABASE-001): add lifecycle persistence contracts`), pushed to `origin/task/ARCH-055-DATABASE-001`.
- No task implementation changes outside the nine allowlisted files. Parent report update will be published separately; no implementation submodule gitlink was staged.

### Deviations

No SQL or application-scope deviations. The required ARCH-040 validations and U07 argument-case evidence remain incomplete because the predecessor validation scripts assume the ARCH-040 migration remains the end of the chain. No unapproved validator edits were made.

### Assumptions

The canonical source baseline remained unchanged at task start: all 68 predecessor migration checksums match the baseline. PostgreSQL evidence is from disposable PostgreSQL 17 + pgvector containers with network disabled, never a hosted or production database.

### Unresolved Issues

- Ask `moda_architect` to reconcile the ARCH-040 “must remain last migration” assumptions with forward migrations, then rerun both required ARCH-040 validations and complete F06.
- Explicitly exercise U07 invalid/missing/extra argument cases and preserve no-Docker-contact evidence.
- After acceptance, downstream consumer tasks must adopt the accepted Database pin and coordinate migration rollout.

### Architectural Concerns

No storage or transaction-boundary concern found in the tested ARCH-055 migrations. The predecessor validator/order coupling is a cross-task validation blocker. The static catalogue snapshot showed no non-target functions, constraints, indexes or triggers changed; U01–U06 database proof passed in both fresh and upgrade harnesses.

## Attempt 2 Completion Report

### Corrections

- `scripts/validate-arch055-database-contracts.mjs` now uses immutable verified baseline `7c377282aa5819b3008b7d7f3018f44f4161523e`, checks it is an ancestor of the task checkout, and computes the exact allowlist from the baseline-to-HEAD committed diff plus local tracked and untracked changes. The schema/package snapshots and all 68 predecessor hashes are read from that baseline, so validation passes from the clean published checkout as well as during local work.
- `scripts/test-arch055-database-contracts-postgres.mjs` and the static validator locate the three named target migrations, assert their relative order, and validate/apply canonical migrations only through target 3. They no longer require ARCH-055 to remain the latest migration.
- `scripts/validate-arch040-human-prepared-schema.mjs` and `scripts/test-arch040-human-prepared-postgres.mjs` now validate the ARCH-040 boundary independently of later migrations and run against the canonical chain through ARCH-055. Existing prepared-body, permit, state, release, moderation, lease, tenant, and concurrency assertions were preserved.
- The ARCH-055 PostgreSQL runner now applies one migration per `psql` connection. Combining eight predecessor migrations in one session caused PostgreSQL to stop accepting connections in this local Docker environment; applying them individually completed successfully in both modes. Each applied migration name and SHA-256 is emitted after success.
- The upgrade fixtures now include both sides of an actual cancellation/reclaim on one attempt: the cancelled command retains and backfills `key-cancelled`, while the later accepted command backfills `later-owner-key`. The full old row snapshots include attempt and provider evidence and are compared after migration.
- F03/F04 now explicitly exercise failed-attempt grant rejection, stale successful consumption after credential rotation, terminal retry, and immutable identity rejection, in addition to the existing expired failure, successful-consumption-without-same-transaction-grant, and failure-time-before-creation checks.
- U05 compares the full duplicate-intake history snapshot after migration 3 fails, as well as checking the column/index rollback. U07 has both the six invalid/missing/extra argument cases with zero Docker invocations (independent architect execution) and a forced top-level assertion failure after startup; the latter exits 1 and confirms the runner's `finally` removes its isolated container.

### Attempt 2 Validation Results

- **PASS** — `npm run validate`: Prisma schema valid.
- **PASS** — `npm run prisma:generate`: Prisma Client v6.19.3 generated. The ordinary attempt encountered `EPERM` replacing a generated file; the same required command passed on retry with elevated filesystem access.
- **PASS** — `npm run test:arch055-database-contracts`: exactly two nullable Prisma additions, approved 11-path implementation allowlist, named target ordering through `20261102122000_arch055_upload_intake_identity`, and all 68 predecessor hashes verified from the immutable baseline. Reran after pushing implementation commit `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; the implementation worktree was clean and `HEAD` matched `origin/task/ARCH-055-DATABASE-001`.
- **PASS** — `npm run test:arch055-database-contracts:postgres:fresh` and `...:upgrade`: canonical migrations through target 3; F01–F05, U01–U06, full failure rollback snapshots, and cleanup. Fresh prints `PASS ARCH-055 PostgreSQL fresh`; upgrade prints `PASS ARCH-055 PostgreSQL upgrade`. Both network-disabled PostgreSQL 17 containers were removed.
- **PASS** — `npm run test:arch040-human-prepared-schema`: existing structural and trigger checks preserved with ARCH-055 later in the chain.
- **PASS** — `npm run test:arch040-human-prepared:postgres`: fresh and upgrade scenarios both passed on the schema through ARCH-055, including frozen body/digest and template checks, nonhuman actors, lease/tenant guards, terminal tombstones, provider permits, concurrency first-writer behavior, and historical assessment/provider/terminal/pending intent preservation.
- **PASS** — `npm run test:arch026-woocommerce-rest-read-grant`: REST read-only grant static invariants.
- **PASS** — Focused ESLint on all four ARCH-055 scripts/modules and both authorized ARCH-040 validators/runners; `git diff --check`.
- **PASS** — U07 invalid argument evidence: six invocations (no arguments; missing mode value; invalid mode; extra argument; unknown option; repeated mode) each exited 1 before Docker, with a PATH-injected Docker sentinel recording zero invocations. This evidence was independently collected by the architect and is retained from the Attempt 1 review.
- **PASS** — U07 forced process-failure cleanup: `ARCH055_TEST_FORCE_TOP_LEVEL_ASSERTION=1 node scripts/test-arch055-database-contracts-postgres.mjs --mode fresh` emitted the expected assertion after startup, exited 1, and `docker inspect` confirmed `moda-arch055-c52550e5-d08c-4c85-b511-e0167128f132` had been removed.
- **PASS** — Target migration SHA-256 values unchanged: `c129466fdb53190b7f8ce6c2d3a04867c6bacbd55e334c5e0bceeb1b28e4e53b`, `e4689790fbba7f606803b2d0370a66ba8b4f57bb3cb0b67b154336f90c2d41fb`, `e9ce08d49576f84a4e1b95c39637c69e97f0f620b4fae608fadf2712fefb6a37`.

### Attempt 2 Worktree and Git Evidence

- Launcher-resolved root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-DATABASE-001`, branch `task/ARCH-055-DATABASE-001`. Attempt 2 claim publication is `fd83fdb27`; synchronized parent SHA at the start of the attempt was `5e3afd7f27750a4442f914e0f5514df5a5b7080c`, with `origin/main` already incorporated and no fast-forward required.
- Database implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-DATABASE-001`, branch `task/ARCH-055-DATABASE-001`. Synchronized implementation SHA at attempt start was `4fded01b247d2f5d40d1ba3977f2eedbb55f4669`, with `origin/main` already current and no fast-forward required.
- Launcher recursive submodule sync and update passed; neither task worktree contained submodule entries.
- Attempt 2 implementation changes are confined to the four validator/runner files explicitly added by definition revision 3. No migration, Prisma schema, package script, consumer pin, architecture index, downstream task, or workspace gitlink changed.
- Implementation correction commit `5907b45` (`fix(ARCH-055-DATABASE-001): reconcile migration validation proofs`) is pushed to `origin/task/ARCH-055-DATABASE-001`.
- The Attempt 2 parent report is the only parent-worktree change and is published separately; no task definition, architecture index, downstream task, or workspace gitlink is staged with it.

### Attempt 2 Disposition

All listed Work Items, Acceptance Criteria, and required Validation are checked against execution evidence. Task status is `review`, Attempt 2 preserved, `executor: null`, and `claimed_at: null`. No acceptance, consumer rollout, dependency promotion, or main-branch merge is claimed; those remain gated on architect review.

## Architect Review

### Review Status

**Changes Requested — Attempt 1, 2 November 2026.** Remain Ready with null executor/claimed_at and Attempt 1 unchanged. Not accepted; no dependent task promoted.

### Findings

1. **P2 — static validation is tied to an uncommitted working tree.** `scripts/validate-arch055-database-contracts.mjs:28–36` requires every implementation path in `git diff HEAD` or untracked files, then uses `HEAD` as the pre-change schema/package/hash baseline. Published `4fded01` is clean, so the required command cannot validate that revision; even removing the dirty-file requirement would insert the fields into an already-updated baseline. Use a stable, verified pre-ARCH-055 baseline (the recorded `7c377282aa5819b3008b7d7f3018f44f4161523e`, or an equivalent explicit immutable baseline), and validate the task commit diff plus any local task changes. Required checks must pass on the clean published checkout. Preserve exact-schema/package/allowlist/predecessor assertions; do not simply remove them.
2. **P2 — new harnesses repeat the forbidden latest-migration assumption.** The PostgreSQL runner asserts `migrations.slice(-3)` equals the ARCH-055 targets (line 15), and the static validator does the same (line 20). The task explicitly requires compatibility with later migrations. Locate the named target boundaries, validate their relative order, and apply only predecessors plus these targets; later migrations must not break historical tests. The existing ARCH-040 latest-only assumptions are confirmed in its static validator and PostgreSQL runner. Revision 3 narrowly authorizes the two named validator files above to remove this ordering blocker while preserving all guard checks. Ensure F06 runs on the schema **after ARCH-055**, not only a historical ARCH-040-only database.
3. **P2 — complete the claimed acceptance-matrix proof.** U02 seeds a cancelled command whose attempt already has `later-owner-key`, but creates no later command sharing that attempt; it is not the required actual cancellation/reclaim pair. Add both historical owners under canonical guards and prove each backfills its own key with attempt/provider evidence unchanged. F03/F04 assertions also need explicit failed-attempt grant rejection, stale successful consumption, terminal retry and immutable-identity rejection; checking zero grants without attempting the forbidden grant does not prove rejection. U05 must snapshot and compare duplicate history after failed migration, not only column/index absence. U07 must prove runner cleanup after a failing top-level assertion/nonzero exit; caught U03/U05 failures inside an otherwise successful run do not by themselves establish that exit path. Keep each case's results explicit rather than broadly claiming U01–U06 complete.

### Scope disposition

The three migration SQL bodies match the prescribed executable SQL after whitespace/comments are normalized, and the Prisma diff contains only the two nullable insertions. No new migration change is requested by this review. Do not edit existing migration history, relax guard behavior, or deploy consumers. The definition's edit allowlist is now eleven files solely to unblock the two named ARCH-040 validator adaptations. All other scope boundaries remain intact.

### Validation provenance

Implementation remote ref verified: `4fded01b247d2f5d40d1ba3977f2eedbb55f4669`. Fresh/upgrade PostgreSQL results above remain executor-reported; not independently rerun during this static review. The known missing F06 proof is not waived. Review execution evidence is appended below when available. No implementation changes or main merge performed.

### Follow-up

Claim the next attempt normally on the same task branches, address the harness and matrix findings, run all required commands on the committed revision, and publish the updated evidence. The next launcher claim increments the attempt once. All downstream tasks remain gated on accepted Database completion; no consumer pin is approved yet.


### Independent execution evidence

Using installed workspace-selected Node v24.19.0, the clean published revision's static validator failed with `AssertionError: Expected task file is absent: package.json` at line 32. This independently confirms finding 1; the earlier pre-commit passing result is not a passing result for the published checkout. All three executable migration bodies were compared with the definition after whitespace/comment normalization and matched exactly.

U07 argument checks independently passed for six inputs: no arguments; `--mode`; `--mode invalid`; `--mode fresh extra`; `--unknown fresh`; and `--mode upgrade --mode fresh`. Each exited 1 with the expected usage assertion. A PATH-injected Docker sentinel recorded zero Docker invocations across all six cases. No external database was contacted. The missing invalid-argument evidence is now supplied; the separate forced top-level SQL/assertion-failure cleanup proof remains required.
