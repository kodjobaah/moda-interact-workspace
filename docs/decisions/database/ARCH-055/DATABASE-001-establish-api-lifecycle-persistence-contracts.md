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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-055-BACKGROUND-001
- ARCH-055-API-001
- ARCH-055-API-005
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-DATABASE-001: Add explicit persistence metadata and narrowly correct existing guards

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. Explicit narrow persistence contract; no implementation attempt claimed.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `ready` solely from the dependency graph below.

## Objective

Add exactly two nullable persistence fields, one claim-key backfill, one original-intake partial unique index and one narrowly scoped correction to the existing REST attempt guard/time CHECK, through three new forward-only migration scripts. API/Shopify/Background services own workflow validation; no new business-policy trigger is authorised.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E09`, `E11`, `E12`, `E29`, `E39`, `E40`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

All implementation paths below are relative to `moda-interact-database`. This is an edit allowlist, not permission to modify consumer schema copies.

**Modify exactly these existing files:**

- `prisma/schema.prisma`: only the two field insertions shown below.
- `package.json`: only the three script entries shown below; preserve every existing key, dependency and command.

**Create exactly these files:**

- `prisma/migrations/20261102120000_arch055_rest_read_lifecycle/migration.sql`
- `prisma/migrations/20261102121000_arch055_human_follow_up_claim_identity/migration.sql`
- `prisma/migrations/20261102122000_arch055_upload_intake_identity/migration.sql`
- `scripts/test-arch055-database-contracts-postgres.mjs`
- `scripts/validate-arch055-database-contracts.mjs`
- `scripts/fixtures/arch055/legacy-fixtures.mjs`
- `scripts/fixtures/arch055/assertions.mjs`

These are **nine implementation files in total**. This task file's execution metadata/Completion Report is the separately permitted parent-repository write. No other implementation file is authorised. Existing validators and prior migration files are read-only. If a new task-relevant blocker genuinely requires another path, return it before editing that path.

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

- [ ] Insert the two exact nullable Prisma fields; preserve all other schema declarations.
- [ ] Create the three forward migration files with the expected SQL; predecessor hashes remain unchanged.
- [ ] Add the three exact package script keys, static validator and modular fresh/upgrade runner.
- [ ] Implement every F/U case in the acceptance matrix, including CLAIMED backfill and transactional trigger re-enable failure.
- [ ] Run declared schema/client/diff/static/fresh/upgrade checks; record actual results and cleanup.
- [ ] Record the accepted database-pin handoff and coordinated producer/consumer rollout; return for review without executing consumers.

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

- [ ] Every F/U case passed on canonical disposable PostgreSQL or remains explicitly unchecked with a blocked return.
- [ ] Exactly the approved implementation files changed; original application policy moved to owning service tasks, not replaced by new database triggers.
- [ ] Migration application order, SQL hashes, fixture identities, backfill counts, diff evidence and cleanup recorded.
- [ ] Tasks remain unaccepted until architect review; no consumer deployment or production migration claimed.

## Validation

Run from the launcher-resolved Database implementation worktree, using its installed toolchain:

- [ ] `npm run validate`
- [ ] `npm run prisma:generate`
- [ ] `npm run test:arch055-database-contracts`
- [ ] `npm run test:arch055-database-contracts:postgres:fresh`
- [ ] `npm run test:arch055-database-contracts:postgres:upgrade`
- [ ] `npm run test:arch026-woocommerce-rest-read-grant`
- [ ] `npm run test:arch040-human-prepared-schema`
- [ ] `npm run test:arch040-human-prepared:postgres`
- [ ] `npx eslint --max-warnings=0 scripts/test-arch055-database-contracts-postgres.mjs scripts/validate-arch055-database-contracts.mjs scripts/fixtures/arch055/legacy-fixtures.mjs scripts/fixtures/arch055/assertions.mjs`
- [ ] `git diff --check`

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

Not Started.

### Files Changed

None.

### Work Completed

None. Task definition only.

### Validation Results

Not run. Record each command, outcome, fixture/migration identity, actual SQL/rows, concurrency schedule and resource cleanup here.

### Worktree and Git Evidence

Not materialised. Record launcher packet, physical parent/implementation worktrees, both task branches, synchronized SHAs, accepted nested Database pin, commits/pushes and any exact publication failure.

### Deviations

None authorised.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

Required implementation/validation has not started. Do not pre-check acceptance items.

### Architectural Concerns

Report ownership, schema, contract, external dependency, new index/infrastructure or transaction-boundary gaps here. Do not expand scope silently.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition issued; implementation has not been reviewed or accepted.

### Reviewed Files

No implementation submitted for this task.

### Validation Reviewed

No implementation validation submitted.

### Architecture Conformance

To be assessed against ARCH-055 and this task's frozen contract.

### Follow-up

Only the authorised review may accept this task and promote dependants.
