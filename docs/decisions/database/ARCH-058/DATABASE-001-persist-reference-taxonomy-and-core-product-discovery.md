---
id: ARCH-058-DATABASE-001
architecture_id: ARCH-058
title: Persist reference taxonomy and the core product-discovery policy
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
  - ARCH-058-MCP-001
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-DATABASE-001: Persist reference taxonomy and the core product-discovery policy

## Architecture

Architecture: `ARCH-058`.

Architecture document: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`.

Evidence review: `docs/architecture/reviews/commerce-agent-product-discovery-20261104-015544-r03/review.md`, sections 4.1, 7, 8, 10 and 12.

Normative wire contract: `docs/architecture/ARCH-058/contracts.md`, section 4, including the strict built-in grant branch.

Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. This portable canonical definition has no claimed attempt, task branch, task worktree, implementation commit, push or accepted implementation. Materialise through `/moda-task ARCH-058-DATABASE-001` under `docs/task-definition-materialization.md` before execution. `ready` records the empty dependency frontier; it does not authorise deployment to a shared environment.

## Objective

Establish the database contract for standard product discovery: a separate durable global reference taxonomy plus the targeted required-feature policy consumed by every authorised store.

## Context

The uploaded snapshot already installs pgvector and uses `Unsupported("vector")` for merchant-owned knowledge. It has no conversation reference-taxonomy tables. Admin independently imports Shopify taxonomy into Redis; that implementation stays unchanged. `product_search` currently remains merchant opt-in, although its product tools are code-defined. Publishing a new resolver alone therefore cannot make discovery standard for all eligible stores.

The existing grant JSON is also guarded by database functions: the current shape checker and insert trigger reject built-ins even though no new JSON column is necessary. This task explicitly extends those two installed guard functions through the new migration, preserving the published-tool authority checks.

Use the existing database ownership and required-feature pattern. Relevant read-only precedents are `prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql`, `prisma/migrations/20261005093000_arch023_embedding_configuration/migration.sql`, and `prisma/migrations/20261005143000_ai_conversations_required/migration.sql`. The authoritative task contract below fixes new names and constraints; it does not reopen those accepted migrations.

## Scope

All implementation paths in this section are relative to `moda-interact-database`. This is the implementation edit allowlist.

Modify:

- `prisma/schema.prisma`: add exactly the two models below; preserve existing models, enums and relations.
- `prisma/seed.mjs`: change only the canonical `product_search` feature policy to the required values below; preserve every other feature, plan, configuration and seed operation.
- `package.json`: add only the three focused validation commands below; preserve existing scripts and dependencies.

Create:

- `prisma/migrations/20261104120000_reference_taxonomy_and_core_product_discovery/migration.sql`.
- `scripts/validate-reference-taxonomy-schema.mjs`.
- `scripts/test-reference-taxonomy-postgres.mjs`.
- `scripts/fixtures/reference-taxonomy-fixtures.mjs`.

The parent task file's execution metadata, progress checkboxes and Completion Report are the separately permitted governance edits. No consumer's nested `database/` copy is edited here. If a task-relevant blocker requires another path, return it to `moda_architect` before editing that path.

## Out of Scope

No taxonomy download, parser, embedding request, import command, MCP handler, provider search, merchant inventory table, discount policy, tool publication or deployment wrapper. No new embedding purpose or modification of `CommerceEmbeddingConfiguration`. No Admin code, Redis operation, Gateway wiring, schema reset, broad seed execution, ANN index, new trigger, new stored business-policy function, background job or automatic generation cleanup. The two existing grant-validation function replacements in requirement 5 are the only authorised guard changes. No edits to prior migrations, unrelated tests or `docs/decisions/**/_index.md`.

## Requirements

### 1. Exact Prisma persistence contract

Add these models in the `commerce` schema. Native types, nullability, defaults, relation actions and mapped object names are part of the contract. Formatting may follow the repository convention.

```prisma
model ReferenceTaxonomyGeneration {
  id                    String   @id(map: "ReferenceTaxonomyGeneration_pkey") @default(cuid()) @db.Text
  environment           CommerceEnvironment
  source                String   @db.VarChar(64)
  taxonomyVersion       String   @db.VarChar(64)
  languageTag           String   @db.VarChar(35)
  sourceUrl             String   @db.Text
  sourceSha256          String   @db.VarChar(64)
  embeddingProvider     String   @db.VarChar(64)
  embeddingModel        String   @db.VarChar(255)
  embeddingDimensions   Int
  embeddingIndexVersion String   @db.VarChar(64)
  embeddingTextVersion  String   @db.VarChar(64)
  importFingerprint     String   @db.VarChar(64)
  categoryCount         Int
  isActive              Boolean  @default(false)
  completedAt           DateTime @db.Timestamptz(3)
  createdAt             DateTime @default(now()) @db.Timestamptz(3)
  activatedAt           DateTime? @db.Timestamptz(3)

  categories ReferenceTaxonomyCategory[]

  @@unique([id, embeddingDimensions], map: "ReferenceTaxonomyGeneration_id_dimensions_key")
  @@unique([environment, source, languageTag, importFingerprint], map: "ReferenceTaxonomyGeneration_import_identity_key")
  @@schema("commerce")
}

model ReferenceTaxonomyCategory {
  generationId        String                @db.Text
  categoryId          String                @db.Text
  name                String                @db.Text
  fullName            String                @db.Text
  parentId            String?               @db.Text
  level               Int
  ancestorIds         String[]              @default([]) @db.Text
  embedding           Unsupported("vector")
  embeddingDimensions Int

  generation ReferenceTaxonomyGeneration @relation(fields: [generationId, embeddingDimensions], references: [id, embeddingDimensions], onDelete: Cascade, onUpdate: Restrict, map: "ReferenceTaxonomyCategory_generation_dimensions_fkey")
  parent     ReferenceTaxonomyCategory?    @relation("ReferenceTaxonomyCategoryTree", fields: [generationId, parentId], references: [generationId, categoryId], onDelete: NoAction, onUpdate: Restrict, map: "ReferenceTaxonomyCategory_parent_fkey")
  children   ReferenceTaxonomyCategory[]   @relation("ReferenceTaxonomyCategoryTree")

  @@id([generationId, categoryId], map: "ReferenceTaxonomyCategory_pkey")
  @@index([generationId, parentId], map: "ReferenceTaxonomyCategory_generation_parent_idx")
  @@schema("commerce")
}
```

`id` is generated by Prisma's `cuid()` when Prisma creates a generation; raw SQL must supply it. Do not invent a database CUID extension/default. All fields are non-null except `activatedAt` and `parentId`; the array is non-null and defaults to `ARRAY[]::TEXT[]`. `completedAt` has no default: callers explicitly supply it for a completed candidate. No pending-import rows or import-job model are required. Retired generations retain their activation timestamp.

Use ordinary logged tables. The embedding column is `vector`, without a fixed dimension typmod. There is no `shopId`: identity and active selection are scoped by environment, source and corpus language. Initial source/language values will be `SHOPIFY_STANDARD_PRODUCT_TAXONOMY` and `en`, supplied by the importer, not database defaults.

### 2. Exact SQL constraints and indexes

Create the migration at the reserved path above. Use one explicit `BEGIN`/`COMMIT` transaction so a membership conflict or failed postcondition leaves neither partial schema nor partially converted feature data. Reuse the already-installed `vector` extension; verify its presence and that the accepted PostgreSQL/pgvector target can create these columns. Do not install server binaries, relocate the extension, rewrite extension history, or hide an unexpected pre-existing table with `IF NOT EXISTS`.

In addition to the primary keys, unique keys, foreign keys and B-tree index expressed in Prisma, add:

| SQL object | Required predicate or behavior |
|---|---|
| `ReferenceTaxonomyGeneration_active_corpus_key` | Partial unique B-tree index on `(environment, source, languageTag) WHERE "isActive" = true`; SQL-only because it is partial. Do not replace it with an unconditional Prisma unique constraint. |
| `ReferenceTaxonomyGeneration_nonblank_check` | `btrim` of `id`, `source`, `taxonomyVersion`, `languageTag`, `sourceUrl`, `embeddingProvider`, `embeddingModel`, `embeddingIndexVersion` and `embeddingTextVersion` is nonempty. |
| `ReferenceTaxonomyGeneration_hashes_check` | Both `sourceSha256` and `importFingerprint` match `^[0-9a-f]{64}$`. |
| `ReferenceTaxonomyGeneration_positive_check` | `embeddingDimensions > 0 AND categoryCount > 0`. |
| `ReferenceTaxonomyGeneration_activation_check` | `NOT "isActive" OR "activatedAt" IS NOT NULL`. `completedAt` is independently `NOT NULL` for every stored generation. |
| `ReferenceTaxonomyCategory_identity_check` | Nonblank `generationId`, `categoryId`, `name`, `fullName`; `parentId` is null or nonblank and different from `categoryId`. |
| `ReferenceTaxonomyCategory_level_check` | `level >= 0`; `cardinality(ancestorIds) = level`; no null ancestor element; `categoryId` does not occur in `ancestorIds`; level zero has null parent; positive level has non-null parent equal to the last ancestor. |
| `ReferenceTaxonomyCategory_embedding_check` | `embeddingDimensions > 0 AND vector_dims(embedding) = embeddingDimensions`. |

Use immediate, non-deferrable foreign keys. The importer inserts each generation's categories **parent before child**, including across bounded insert statements. `parentId` resolves through `(generationId, categoryId)`, so a parent in another generation cannot satisfy the relationship. The category's dimension metadata resolves through `(generationId, embeddingDimensions)`, so a vector of the wrong dimension cannot be smuggled into a generation by changing its row metadata.

The generation FK cascades category deletion if a later explicitly authorised inactive-generation cleanup deletes a generation. The self-parent FK uses `NO ACTION`, allowing a complete generation's cascade to remove its tree in the same statement while preventing an isolated parent deletion that strands children. This task introduces no cleanup operation; activation never deletes the previous generation.

The application importer owns full ancestor-chain/cycle validation, source checksum verification, finite/nonzero-norm vector validation, exact final row-count verification, and immutability after completion. Do not implement those workflows with a new trigger or claim that a local CHECK verifies an entire hierarchy or count. The database guarantees the specified row/key/dimension/active-selection invariants. No additional taxonomy indexes, uniqueness on human-readable paths, ANN index, or per-model/per-store table are authorised.

### 3. Guard the global feature conversion

This migration changes the eligibility policy for an existing feature. A tool sharing that feature must not become globally eligible accidentally.

Before mutation, require the existing `billing.Feature` row with key `product_search`; do not create a replacement feature or reuse another feature's ID. Under the migration transaction, lock the existing feature row and protect the capability/tool inventory from concurrent writes while checking it. Use `SHARE` table locks on `commerce.CommerceCapability` and `commerce.CommerceTool`, then select the feature row `FOR UPDATE`; use a bounded lock wait and preserve its original PostgreSQL diagnostic if it times out. A safe failure is preferable to continuing with an incomplete inventory.

Inventory **all** capabilities whose `featureId` is that feature, including disabled or currently unpublished members. The only allowed capability-key/tool-name pairs are identical names from:

- `commerce_resolve_product_categories`;
- `commerce_search_products`;
- `commerce_get_product`.

For each existing allowed pair require the synchronizer's existing ownership evidence: `CommerceAuditEvent.action = CREATE_TOOL` for that tool and `CREATE_CAPABILITY` for that capability, with each audit `id` beginning with the exact literal `system-commerce-tools:v1:<ENVIRONMENT>:<tool-name>:` for one of the five existing `CommerceEnvironment` values. Compare literal prefixes; underscores in names must not become SQL `LIKE` wildcards. Empty membership is valid for a fresh database. Do not fabricate ownership audits, adopt manually authored tools, reassign capabilities, or delete unexpected members. A name match alone is insufficient. The ownership precedent is `moda-interact-commerce/src/commerce/bootstrap/system-commerce-tool-sync.ts:80–99`.

If a member is unknown, points to a different tool name, lacks ownership evidence, or references a missing expected identity, raise an actionable `PRODUCT_DISCOVERY_MEMBERSHIP_CONFLICT` with bounded identifying details and roll back. A missing feature raises `PRODUCT_DISCOVERY_FEATURE_MISSING`. Do not add an unsafe skip/force flag.

The deployment preflight owned by `ARCH-058-COMMERCE-001` also inventories active releases/pinned definitions and verifies approved canonical content, names and ownership before invoking `migrate:deploy`. It must stop for a same-name manually changed definition or unexpected release member. It preserves existing published revisions and obtains explicit reconciliation before any global enablement. Database's guard is an independent identity check, not a replacement for that content/publication check. Pause concurrent feature/tool authoring during the controlled rollout; this task does not publish or repair release definitions.

### 4. Apply only the targeted required-feature policy

After the guard succeeds, in the same transaction:

1. Update the existing `product_search` feature to `activationMode = 'ALWAYS_ENABLED'`, `systemRequired = true`, `active = true`, and set `updatedAt = CURRENT_TIMESTAMP`. Preserve its ID, key, display text, descriptions, capabilities and all unrelated features.
2. Insert a missing `MerchantPricingPlanFeature` for **every** existing catalogue plan, including Free/paid and inactive plans, using that feature ID. Use `ON CONFLICT (merchantPricingPlanId, featureId) DO NOTHING`; preserve existing `configuration` and timestamps.
3. Upsert `BillingPlanFeature` for **every** existing operational plan with `enabled = true`. A new row ID is the deterministic `required-product-search:` plus plan ID; on `(planId, featureId)` conflict change only `enabled`. Preserve an existing row's ID and `configuration`. A primary-key collision with another pair is a real conflict, not permission to overwrite it.
4. Delete `ShopFeaturePreference` rows only for this feature, since merchant opt-in no longer controls it. Preserve all other feature preferences and all shop/subscription data.
5. Assert the feature's exact policy, complete catalogue/operational plan coverage, and absence of this feature's obsolete preferences before commit. Failure raises `PRODUCT_DISCOVERY_POSTCONDITION_FAILED` and rolls back.

For new mapping rows, retain the existing mapping-column defaults, including `{}` configuration. The canonical seed's `product_search` entry must use the same `ALWAYS_ENABLED`, `systemRequired: true`, `active: true` policy. Do not run `prisma/seed.mjs` as migration/provisioning: its broader plan rewrite is outside this task.

Future plans use existing generic required-feature handling in Admin and existing Shopify/Woo plan materialization. The database policy makes `product_search` part of that path; a one-time migration does not automatically constrain arbitrary future raw SQL inserts. No new plan trigger or Admin code change is authorised. `ARCH-058-SYSTEM-TEST-001` proves the actual supported future-plan and new-store paths. Keep current public/native product categories and `CommerceStoreCategoryTaxonomyMapping` unchanged.

### 5. Extend the existing grant JSON guards without new storage

`CommerceConversationGrant.grantedTools` remains the same JSONB column; no Prisma field or grant table is added. Existing CHECK `arch021_grant_bounds` invokes `commerce.arch020_grant_tools(jsonb)`. Existing trigger `arch021_conversation_grant_guard` invokes `commerce.arch021_conversation_grant_guard()` and currently compares the whole JSON array with the release-derived published union. Both would reject the new branch unless corrected. The source definitions are in migrations `20260920182429_arch020_commerce_capability_releases/migration.sql:332–347` and `20260929120000_arch021_feature_capability_simplification/migration.sql:258–315`.

In this task's **new forward migration**, replace only these existing function bodies with the SQL below. Preserve names, argument/return types, owners, grants and the existing CHECK/trigger bindings. `CREATE OR REPLACE FUNCTION` preserves the installed function identity; do not drop/recreate its trigger, alter ownership, grant a new privilege, disable the CHECK, or weaken grant immutability. Explicit `SECURITY INVOKER` retains caller privileges; `SET search_path = pg_catalog` prevents caller-controlled name resolution. All application helpers/tables remain schema-qualified. The structural helper remains `IMMUTABLE STRICT`; the trigger function remains `VOLATILE` and non-strict.

```sql
CREATE OR REPLACE FUNCTION commerce.arch020_grant_tools(v jsonb)
RETURNS boolean
LANGUAGE plpgsql IMMUTABLE STRICT SECURITY INVOKER
SET search_path = pg_catalog
AS $$
DECLARE
  item jsonb;
  ids text[] := '{}';
  names text[] := '{}';
BEGIN
  IF jsonb_typeof(v) IS DISTINCT FROM 'array'
    OR octet_length(v::text) > 65536 THEN
    RETURN false;
  END IF;
  IF jsonb_array_length(v) > 32 THEN RETURN false; END IF;

  FOR item IN SELECT value FROM jsonb_array_elements(v) AS entries(value) LOOP
    IF jsonb_typeof(item) IS DISTINCT FROM 'object' THEN RETURN false; END IF;
    IF item ? 'kind' THEN
      IF commerce.arch020_object(item,
          ARRAY['kind','toolName','definitionVersion','contractHash']) IS DISTINCT FROM true
        OR item->>'kind' IS DISTINCT FROM 'BUILT_IN'
        OR commerce.arch020_string(item->'toolName',128) IS DISTINCT FROM true
        OR item->>'toolName' NOT IN
          ('commerce_get_discount_options','commerce_get_discount_details')
        OR item->>'definitionVersion' IS DISTINCT FROM '1.0.0'
        OR jsonb_typeof(item->'contractHash') IS DISTINCT FROM 'string'
        OR item->>'contractHash' !~ '^[0-9a-f]{64}$' THEN
        RETURN false;
      END IF;
    ELSE
      IF commerce.arch020_object(item,
          ARRAY['toolId','toolRevisionId','toolName','definitionVersion','capabilityKeys']) IS DISTINCT FROM true
        OR commerce.arch020_string(item->'toolId',128) IS DISTINCT FROM true
        OR commerce.arch020_string(item->'toolRevisionId',128) IS DISTINCT FROM true
        OR commerce.arch020_string(item->'toolName',128) IS DISTINCT FROM true
        OR commerce.arch020_string(item->'definitionVersion',64) IS DISTINCT FROM true
        OR commerce.arch020_strings(item->'capabilityKeys',1,32,true) IS DISTINCT FROM true
        OR item->>'toolId' = ANY(ids) THEN
        RETURN false;
      END IF;
      ids := array_append(ids,item->>'toolId');
    END IF;
    IF item->>'toolName' = ANY(names) THEN RETURN false; END IF;
    names := array_append(names,item->>'toolName');
  END LOOP;
  RETURN true;
END;
$$;

CREATE OR REPLACE FUNCTION commerce.arch021_conversation_grant_guard()
RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $$
DECLARE
  conv whatsapp."Conversation"%ROWTYPE;
  owner_shop text;
  expected jsonb;
  actual jsonb;
BEGIN
  PERFORM commerce.arch020_current_snapshot();
  SELECT * INTO conv FROM whatsapp."Conversation"
    WHERE id=NEW."conversationId" FOR UPDATE;
  IF NOT FOUND OR conv."checkoutRecoveryId" IS NULL
    OR conv."checkoutRecoveryId" IN ('standalone','product-only','unknown-shop') THEN
    RAISE EXCEPTION 'ARCH021 recovery conversation required' USING ERRCODE='23514';
  END IF;
  SELECT "shopId" INTO owner_shop FROM commerce."CheckoutRecovery"
    WHERE id=conv."checkoutRecoveryId" FOR UPDATE;
  IF NOT FOUND OR owner_shop IS DISTINCT FROM NEW."shopId"
    OR (conv."shopId" IS NOT NULL AND conv."shopId" IS DISTINCT FROM owner_shop)
    OR NEW."initialInboundVersion" > conv."inboundVersion" THEN
    RAISE EXCEPTION 'ARCH021 grant owner or inbound version mismatch' USING ERRCODE='23514';
  END IF;
  IF commerce.arch020_strings(NEW."selectedCapabilityKeys",0,32) IS DISTINCT FROM true
    OR octet_length(NEW."selectedCapabilityKeys"::text) > 8192
    OR commerce.arch020_grant_tools(NEW."grantedTools") IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'ARCH021 grant shape' USING ERRCODE='23514';
  END IF;
  IF EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(NEW."selectedCapabilityKeys") selected(key)
    WHERE NOT EXISTS (
      SELECT 1 FROM commerce."CommerceReleaseCapability" member
      JOIN commerce."CommerceCapability" capability ON capability.id=member."capabilityId"
      WHERE member."releaseId"=NEW."releaseId" AND capability.key=selected.key
    )
  ) THEN
    RAISE EXCEPTION 'ARCH021 selected key outside release' USING ERRCODE='23514';
  END IF;
  SELECT COALESCE(jsonb_agg(entry ORDER BY entry->>'toolId' COLLATE "C"),'[]'::jsonb)
  INTO expected
  FROM (
    SELECT jsonb_build_object(
      'toolId',tool.id,
      'toolRevisionId',tool_revision.id,
      'toolName',tool.name,
      'definitionVersion',tool_revision."definitionVersion",
      'capabilityKeys',jsonb_agg(capability.key ORDER BY capability.key COLLATE "C")
    ) AS entry
    FROM commerce."CommerceReleaseCapability" member
    JOIN commerce."CommerceCapability" capability ON capability.id=member."capabilityId"
    JOIN commerce."CommerceTool" tool ON tool.id=member."toolId"
    JOIN commerce."CommerceToolRevision" tool_revision
      ON tool_revision.id=member."toolRevisionId" AND tool_revision."toolId"=member."toolId"
      AND tool_revision.status='PUBLISHED'
    WHERE member."releaseId"=NEW."releaseId"
      AND NEW."selectedCapabilityKeys" ? capability.key
    GROUP BY tool.id,tool_revision.id,tool.name,tool_revision."definitionVersion"
  ) entries;
  SELECT COALESCE(jsonb_agg(granted ORDER BY granted->>'toolId' COLLATE "C"),'[]'::jsonb)
  INTO actual
  FROM jsonb_array_elements(NEW."grantedTools") granted
  WHERE NOT (granted ? 'kind');
  IF expected IS DISTINCT FROM actual THEN
    RAISE EXCEPTION 'ARCH021 grant must equal direct release Tool authority' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
END;
$$;
```

The untagged published branch keeps its existing exact keys, bounds, sorted unique provenance and unique tool IDs. It must still equal the selected release-derived union, with no missing, extra, wrong-revision or changed-provenance entry. Built-ins cannot satisfy a missing published grant and have no `toolId`, `toolRevisionId` or `capabilityKeys`. The only new branch has exactly `kind`, `toolName`, `definitionVersion`, `contractHash`, the two canonical names, literal version `1.0.0`, and a lowercase 64-hex hash. A tagged `PUBLISHED` branch, unknown kind/name, duplicate name across either branch, or additional field fails. Combined array length remains at most 32 and JSON storage size remains at most 65,536 bytes.

The database validates built-in **structure and the fixed name/version allowlist**. It does not authenticate a syntactically valid hash against source code, grant current merchant policy, or create fake release/tool/capability records. Trusted Shared descriptors and MCP/Background enforce the exact current code-contract hash, current shop/policy and retained-grant equality. Existing owner/recovery/inbound checks, release membership, expiry/positive-version bounds, snapshot-isolation guard, row locks, foreign keys and immutable-update trigger remain unchanged. Existing valid published-only grants continue to pass. No grant row is rewritten, widened, reset or deleted by this migration.

Contracts are frozen in `docs/architecture/ARCH-058/contracts.md`; this database task does not import unpublished Shared code or need SHARED-001 completion to implement structural SQL. Shared runtime acceptance tests separately prove code hash and policy authority.

### 6. Rollout and diagnostics

Implement and validate against disposable PostgreSQL 17 with pgvector. Do not apply this task to a developer's existing database, shared environment or provider database. Preserve the explicit task environment over any role's default local database URL.

Consumer schema adoption belongs to the dependent tasks. During deployment, compatible MCP eligibility/readiness and host behavior must be deployed before core activation/publication becomes customer-visible. The parent setup command later runs the pinned migration, taxonomy import and controlled tool publication in order. This database task alone neither makes taxonomy ready nor certifies provider execution.

Do not replace original Prisma/PostgreSQL errors with only a generic status code. SQL exceptions retain their original cause; focused test runners retain bounded stderr and nonzero exit status. No new logging framework or runtime logging dependency is needed for this schema task. If an implementation adds application logging, it must use the existing `@modainteract/moda-interact-shared/logging` API and safe redaction, not a private logger. Never print connection credentials. Unexpected migration history, an occupied reserved migration path, unsupported extension, or required scope expansion is a stop-and-report condition.

## Work Items

- [ ] Add the two exact Prisma models, forward SQL schema and named constraints/indexes.
- [ ] Add transactional membership/ownership guards and targeted `product_search` conversion with postconditions.
- [ ] Extend only the two existing grant-validation function bodies for the strict built-in branch while retaining published union/owner/immutability guards.
- [ ] Align only the canonical `product_search` seed policy.
- [ ] Add the semantic-named validators and isolated PostgreSQL 17 fresh/upgrade/constraint fixtures.
- [ ] Record constraint, upgrade-preservation and conflict-rollback results; hand off the accepted Database revision without editing consumers.

## Interfaces / Contracts

This task produces the exact Prisma/SQL contract above for `ARCH-058-MCP-001`. It consumes the frozen built-in grant JSON branch and adds no tool descriptor, credential authority or queue message. `ARCH-058-SHARED-001` owns customer-facing discovery contracts; no dependency on its unpublished implementation is required here.

MCP owns prepared-candidate publication: a corpus advisory lock, current active-generation comparison, a shared row lock on the selected `REFERENCE_TAXONOMY` configuration through commit, bounded parent-first inserts, count verification and atomic old/new active-marker changes. Generation source/model data and category vectors are immutable after completion. Retain prior generations for in-flight pinned reads. The partial unique index means deactivate the prior generation before activating its successor within the same transaction. This task creates the structural support, not the importer.

The existing `CommerceEnvironment` and `REFERENCE_TAXONOMY` configuration purpose are consumed unchanged. Admin's independently stored Redis taxonomy and its configuration writer are not migrated or invoked.

## Dependencies

None. Snapshot source and existing accepted migration history are the baseline, not new task dependencies.

## Enables

- `ARCH-058-MCP-001`, once this task and its other declared prerequisites are Complete.
- `ARCH-058-SYSTEM-TEST-001`, once all seven implementation/publication prerequisites are Complete.

## Acceptance Criteria

- [ ] Exactly two separate logged commerce taxonomy tables exist, with the specified native types/defaults, composite identity/dimension/parent constraints, and one active generation per environment/source/language.
- [ ] The same provider category ID can appear in different generations; independent environments/corpora can each have an active generation; duplicate identity/fingerprint or a second active generation in the same scope is rejected.
- [ ] Missing/cross-generation parents, self-parent rows, inconsistent root/ancestor metadata, wrong vector dimensions, mismatched generation dimensions, malformed hashes, nonpositive counts and active rows without activation time are rejected by the intended constraints.
- [ ] Parent-first insertion and an atomic old/new activation succeed; rollback preserves the old active generation and its categories. A normal exact cosine query against one pinned generation succeeds using a bound vector value.
- [ ] Existing published-only grants still pass. A valid published union plus the two allowlisted built-in grant objects inserts without any fabricated database tool/capability/revision row.
- [ ] Unknown kinds/names, incorrect built-in version/hash shape, missing/extra keys, extra published IDs on a built-in, duplicate names across branches, combined overflow and wrong published union/provenance are rejected. A built-in cannot conceal a missing published grant.
- [ ] Existing recovery/shop/inbound/release/expiry/snapshot-isolation and immutable-update checks still reject invalid grants. Function owners/ACLs and trigger/CHECK bindings are retained; functions use `SECURITY INVOKER` and fixed `pg_catalog` search path.
- [ ] Fresh migration requires no taxonomy download, embedding key, live merchant, Admin service or broad seed.
- [ ] Upgrade preserves existing merchant knowledge, Admin mappings/settings, immutable tool/release/audit rows and unrelated feature/plan/preference data; only the named feature's policy/mappings/preferences change.
- [ ] All existing Free/paid catalogue and operational plans contain enabled product-discovery support, existing mapping configuration is retained, and the canonical seed cannot restore opt-in.
- [ ] Unknown/custom or unauthorised same-name feature members stop the migration before conversion; missing feature and lock/conflict failure are actionable. Failed upgrade leaves the pre-upgrade feature/data state intact.
- [ ] Reapplying through the normal migration runner reports no pending application; it does not rerun DDL, duplicate mappings or erase data. No manual migration-history repair is used.
- [ ] Changes are confined to the allowlist. Admin code/Redis, earlier migrations, consumer schema copies, business-policy triggers and decision indexes remain untouched; only the two expressly authorised existing grant function bodies change.

## Validation

Add exactly these entries to the existing `package.json` scripts object:

```json
{
  "test:reference-taxonomy-schema": "node scripts/validate-reference-taxonomy-schema.mjs",
  "test:reference-taxonomy:postgres:fresh": "node scripts/test-reference-taxonomy-postgres.mjs --mode fresh",
  "test:reference-taxonomy:postgres:upgrade": "node scripts/test-reference-taxonomy-postgres.mjs --mode upgrade"
}
```

Run from the Database implementation checkout, using the prepared workspace Node environment. Before the first Node command follow the existing bootstrap rule; do not install or select a different runtime. For Prisma commands the test harness must supply its own disposable database URL; do not inherit a live/shared URL.

- [ ] `npm run validate`.
- [ ] `npm run prisma:generate`.
- [ ] `npm run test:reference-taxonomy-schema` — checks schema/migration contract, named partial index and narrowly aligned seed; it does not substitute for actual SQL behavior.
- [ ] `npm run test:reference-taxonomy:postgres:fresh` — apply the unchanged migration chain plus the new migration to isolated PostgreSQL 17/pgvector; inspect real constraints/types/index definitions and run valid/invalid taxonomy and mixed grant inserts plus exact cosine retrieval.
- [ ] `npm run test:reference-taxonomy:postgres:upgrade` — apply predecessors, add legacy plan/preference/configuration and system-tool fixtures, then migrate; verify targeted conversion and preservation. Run separate conflict fixtures for an unknown capability, a same-name member without ownership, a missing feature and a concurrent inventory write/lock timeout; verify rollback. Verify the old published-grant restrictions against real trigger execution, the new strict built-in branch, unchanged function owners/ACLs and binding identities, and normal `migrate:deploy` rerun through recorded migration history as a no-op.
- [ ] `git diff --check`.

The fixture runner creates a unique disposable container/database using `pgvector/pgvector:pg17`, ignores/rejects inherited external database targets, uses bounded readiness waits, and removes its own container/volumes on success or failure. If host Prisma needs a port, bind a random loopback port only. Do not use an existing developer database or MCP's pg16 fixture. Apply historical migrations unchanged; do not create a reduced lookalike schema or run the broad seed to make tests pass.

For upgrade preservation, include an existing `product_search` mapping with nonempty configuration, disabled/missing mappings on other plans, both true/false product-search preferences, unrelated optional-feature preferences, and immutable release/tool ownership fixtures. Grant fixtures must include valid published-only and published-plus-two-built-in grants, unknown or mixed-shape entries, duplicate/colliding names, wrong hash/version, 33 combined entries, oversized JSON, selected-key/revision/provenance mismatches and unchanged shop/recovery/inbound/expiry/immutability failures. Test the SQL helper and real `CommerceConversationGrant` insertion path; a helper-only test would miss the release-union trigger. Test fixture hashes are structural data, not claims of approved production hashes. Database assertions cover current rows; real future-plan authoring and merchant admission remain the integrated System Test responsibility.

These are required implementation checks, not claimed results of task authorship. No provider embedding or semantic ranking benchmark belongs in this task. Stop additional validation once the named risks and required gates are resolved.

## Implementation Notes

The source archive is a review snapshot, not a verified deployed database. Before implementation, confirm the target migration filename is free, the declared baseline fields still exist, and the prepared task's Database revision is correct. Preserve applied checksums and stop on incompatible drift. Do not use `db push`, `migrate reset`, migration squashing, or `migrate resolve` to conceal a conflict.

Keep generation metadata and category vectors separate from merchant-owned knowledge and from the broad store-profile/prompt taxonomy mapping. Shared settings are read-only consumption by MCP; no new embedding-configuration enum value is required. Foreign-key integrity, the active partial unique index and bounded stored-grant structure are database responsibilities; semantic parsing, immutable generation use, exact built-in code-hash/policy authority and setup orchestration remain their specified owners. Replacing the two installed functions through the new migration is authorised; editing their historical migration files is not.

### Stop condition

After every Work Item, Acceptance Criterion and required Validation has passed, update the Completion Report, set this task to `review`, return control to `moda_architect` and stop. Do not implement dependent tasks, deploy to a shared environment, publish a Shared package, mark your own task Complete, or merge to `main`.

## Completion Report

### Status

Not started. Portable definition only; no implementation attempt is claimed.

### Files Changed

None. Populate with actual implementation paths during execution.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, disposable PostgreSQL/pgvector versions, results and any original safe diagnostic.

### Deviations / Assumptions / Unresolved Issues / Architectural Concerns

None recorded. Return any schema-contract, membership, migration-baseline or dependency conflict before broadening scope.

### Worktree and Git Evidence

Not materialised. No branch, worktree, commit, push or deployment is claimed. Record launcher-resolved parent and implementation worktrees, task branches, start revisions and submitted commits during a real attempt.

## Architect Review

### Review Status

Not reviewed.

### Review Notes

None. This definition is not implementation acceptance.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation review.

### Follow-up

Do not advance dependants until the task is accepted and Complete under the normal architecture workflow.
