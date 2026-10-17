---
id: ARCH-043-DATABASE-001
architecture_id: ARCH-043
title: Create generic platform configuration and audit schema
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-043-ADMIN-001
- ARCH-043-ADMIN-002
- ARCH-043-API-001
- ARCH-043-API-002
- ARCH-043-API-003
- ARCH-043-BACKGROUND-001
- ARCH-043-BACKGROUND-002
- ARCH-043-COMMERCE-001
- ARCH-043-COMMERCE-002
- ARCH-043-MCP-001
- ARCH-043-SHOPIFY-001
- ARCH-043-SHOPIFY-002
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Create the platform configuration and audit schema

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Exact supported policy shapes and sealed-secret contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_database`, repository `moda-interact-database`.
- This is **the only database implementation task for ARCH-043**. It is materialized in the canonical parent task worktree; implementation remains owned by the developer under the normal database-agent domain ownership.

## Objective

Add **exactly two** PostgreSQL/Prisma models and their additive migration, then demonstrate atomic revision-checked configuration updates with append-only, secret-safe audit records. Support ordinary validated JSON policies and encrypted application-secret envelopes in the same configuration table, without modifying existing domain configuration models.

## Context

The developer rejected separate tables for each configuration domain and the earlier multi-table credential design. The platform already has database-backed `BackgroundRuntimeConfig`, billing and Commerce configuration, and domain-owned credentials. ARCH-043 adds a small storage boundary only for the remaining specifically allowlisted settings and application bootstrap secrets.

## Scope

1. Add the **two exact Prisma models** specified below to `moda-interact-database/prisma/schema.prisma`, in schema `public`.
2. Add **one additive Prisma migration** creating their tables, unique constraints, indexes, and SQL CHECK constraints. If append-only enforcement requires a PostgreSQL trigger/function, include it in the same migration; it does not count as a new table.
3. Supply DB-repository tests or tested transaction examples proving first-write, revision compare-and-swap (CAS), conflict, reset, secret rotation/revocation, redacted audit, environment isolation, and migration compatibility.
4. Do not create policy-specific or provider-specific tables, re-encrypt existing Commerce credentials, or copy environment-variable values into the migration.

## Out of Scope

- No additional Prisma models, enums or new columns on existing models.
- No changes to `BackgroundRuntimeConfig`, its audit model, `PlatformBillingPolicy`, `ShopSettings`, `ShopFeaturePreference`, Commerce provider credential tables or prior migrations.
- No Admin UI, provider calls, login/bootstrap changes, Redis/queue publishing, service configuration caches, Shared cryptographic implementation or Render environment cleanup. These belong to their existing ARCH-043 tasks.
- No changes to any `docs/decisions/**/_index.md`.

## Requirements

### A. Exact Prisma schema

```prisma
model PlatformConfiguration {
  id          String   @id @default(cuid())
  environment String   @db.VarChar(32)
  key         String   @db.VarChar(128)
  value       Json
  version     Int      @default(1)
  updatedBy   String?  @db.VarChar(191)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@unique([environment, key])
  @@index([environment, updatedAt])
  @@schema("public")
}

model PlatformConfigurationAudit {
  id               String   @id @default(cuid())
  environment      String   @db.VarChar(32)
  key              String   @db.VarChar(128)
  expectedVersion  Int
  resultingVersion Int
  beforeValue      Json?
  afterValue       Json
  actorId          String   @db.VarChar(191)
  reason           String?  @db.VarChar(1000)
  createdAt        DateTime @default(now())

  @@unique([environment, key, resultingVersion])
  @@index([environment, key, createdAt])
  @@index([actorId, createdAt])
  @@schema("public")
}
```

No foreign key to `PlatformAdmin` is proposed: Admin authenticates and authorises `actorId` and `updatedBy` before performing the mutation; neither field confers authorisation on its own. Audit records keep a historical actor identifier even if that administrator's account is subsequently removed. No foreign key from audit to mutable configuration: keep history immutable and independent of current configuration-row lifecycle.

### B. Exact PostgreSQL tables, constraints, indexes

**`public."PlatformConfiguration"`:**

| Column | PostgreSQL type | Nullable | Rule |
|---|---|---|---|
| `id` | TEXT | No | Primary key, Prisma-generated CUID |
| `environment` | VARCHAR(32) | No | Nonblank; chosen from trusted deployment identity, not client input |
| `key` | VARCHAR(128) | No | Nonblank; Admin allowlist validated before write |
| `value` | JSONB | No | JSON object; strict settings payload or approved sealed/disabled envelope |
| `version` | INTEGER | No | Defaults to 1; CHECK `version >= 1` |
| `updatedBy` | VARCHAR(191) | Yes | Verified actor identifier |
| `createdAt` | TIMESTAMP(3) | No | Defaults to current timestamp |
| `updatedAt` | TIMESTAMP(3) | No | Maintained by Prisma on updates |

Indexes/constraints: primary key on `id`; unique `(environment,key)`; nonunique `(environment,updatedAt)`; SQL CHECK that `btrim(environment) <> ''`, `btrim(key) <> ''`, `version >= 1` and `jsonb_typeof(value) = 'object'` (using quoted identifiers where needed). Prevent SQL insertion of a **non-enveloped value** for one of the five secret keys: `commerce.connectionKeys`, `auth.admin`, `auth.commerce`, `shopify.oauth`, `messaging.meta`. For such keys, `value` must be either a sealed envelope with required markers (`kind=sealed`, integer `schemaVersion=1`, `algorithm=AES-256-GCM`, nonempty wrapping key ID/nonce/ciphertext/tag), or exactly `{ "kind": "disabled", "schemaVersion": 1 }`. Envelope decoding, cryptographic authenticity and nonsecret payload validation remain in the documented ARCH-043 configuration contract, not duplicated in SQL. Unknown and malformed values are denied by the relevant authorised writer.

**`public."PlatformConfigurationAudit"`:**

| Column | PostgreSQL type | Nullable | Rule |
|---|---|---|---|
| `id` | TEXT | No | Primary key, Prisma-generated CUID |
| `environment` | VARCHAR(32) | No | Same canonical environment as mutated row |
| `key` | VARCHAR(128) | No | Configuration key |
| `expectedVersion` | INTEGER | No | CHECK `>= 0` |
| `resultingVersion` | INTEGER | No | CHECK `= expectedVersion + 1` |
| `beforeValue` | JSONB | Yes | `NULL` for initial create; redacted metadata for secrets |
| `afterValue` | JSONB | No | Settings value or redacted metadata for secrets |
| `actorId` | VARCHAR(191) | No | Nonblank, verified platform-admin ID |
| `reason` | VARCHAR(1000) | Yes | Operator justification |
| `createdAt` | TIMESTAMP(3) | No | Defaults to current timestamp |

Indexes/constraints: primary key `id`; unique `(environment,key,resultingVersion)`; nonunique `(environment,key,createdAt)` and `(actorId,createdAt)`; checks for nonblank environment/key/actor, `expectedVersion >= 0`, `resultingVersion = expectedVersion+1`, and object-shaped `afterValue`. Secret-key audit JSON must conform to **only** `{ "redacted": true, "configured": boolean }` (or a separately approved equally non-sensitive closed metadata shape); enforce this for `beforeValue` and `afterValue` in SQL so bypassing application validation cannot persist ciphertext or a secret in the audit JSON. No arbitrary extra fields. `beforeValue` is nullable for initial creation.

Audit rows are **append-only**: database permissions and/or a migration-owned trigger must prevent UPDATE/DELETE by the normal application database role. Tests must prove the invariant, not just promise it in the UI. The migration adds no merchant FK, new tenant table or audit payload containing a secret.

### C. Exact supported configuration keys

**Ordinary settings** (strict payloads owned by the ARCH-043 schema review):

| Key | Stored fields | Reader |
|---|---|---|
| `woo.couponSync` | `dispatchBatchSize`, `refreshIntervalMinutes`, `dispatchCooldownMinutes`, `unavailableRecheckMinutes`, `staleScanMinutes`, `maxPages`, `requestTimeoutMs`, `maxResponseBytes`, `maxScanDurationMs`, `workerConcurrency` | Background |
| `merchantKnowledge.upload` | `maxUploadBytes`, `maxXlsxUncompressedBytes`, `r2Endpoint`, `r2Bucket` | Hosted API, trusted Shopify server |
| `speech.transcription` | `provider`, `groqModelId`, `openaiModelId` | Background |
| `support.translation` | `provider`, `model` | Background support-message translation only |
| `commerce.preview` | `deadlineMs`, `outputTokens` | Commerce |
| `admin.grafana` | `baseUrl`, `logsUrl`, `metricsUrl`, `tracesUrl`, `platformDashboardUrl` | Admin |

All field types, bounds and defaults are defined explicitly in `ARCH-043-configuration-schema-review.md`. Its R2 endpoint and bucket examples are **placeholders**, not production seed data. Where a domain already has an authoritative DB setting for the same purpose, that domain retains ownership; avoid creating a redundant active row.

**Encrypted application secrets** (sealed value only, validated under the ARCH-043 schema review using existing ARCH-039 credential crypto):

| Key | Decrypted fields represented by envelope | Reader |
|---|---|---|
| `commerce.connectionKeys` | Existing Commerce connection keyring + active key ID; command HMAC key if required by that consumer | Commerce, API, Background, Admin, MCP |
| `auth.admin` | `AUTH_SECRET` and existing Admin OAuth client credentials where required | Admin |
| `auth.commerce` | `AUTH_SECRET` and existing Commerce OAuth client credentials where required | Commerce |
| `shopify.oauth` | `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET` | Shopify app, Background token refresh |
| `messaging.meta` | `META_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN` | Messaging through authenticated private resolver |

**Exact permitted sealed `value` object** (no plaintext secret fields):

```json
{
  "kind": "sealed",
  "schemaVersion": 1,
  "algorithm": "AES-256-GCM",
  "wrappingKeyId": "config-unseal-v1",
  "nonce": "<base64>",
  "ciphertext": "<base64>",
  "authTag": "<base64>"
}
```

The encrypted plaintext is a separate purpose-specific object validated **after** decrypting. Authenticated data must bind environment, key, record revision and schema version. Revocation/reset replaces the row with the exact tombstone `{ "kind": "disabled", "schemaVersion": 1 }`, **not** deletion. Root/unseal material (e.g. `MODA_CONFIG_UNSEAL_KEY` or managed KMS identity), `DATABASE_URL` and infrastructure bootstrap stay outside these tables. The database task does not attempt to deploy or rotate encryption material; Shared and service tasks own those mechanics.

### D. Exact transaction rules

All mutations occur within one PostgreSQL transaction using a single authenticated actor and trusted deployment environment:

1. **Create:** When no row exists, `expectedVersion=0` inserts version 1 and one audit record `(expectedVersion=0,resultingVersion=1,beforeValue=NULL)`; a concurrent duplicate insert loses via unique constraint and writes no audit.
2. **Update / rotate:** Require `expectedVersion=N` and update only the row matching `(environment,key,version=N)` to version `N+1`; insert exactly one audit record in the same transaction. Zero updated rows => stale/conflict response and no audit.
3. **Reset ordinary configuration:** Write the key's explicitly validated safe default as a normal CAS update. Never delete the row and never reset `version` to 0.
4. **Disable/revoke secret:** Write the exact disabled tombstone as a normal CAS update with redacted before/after audit; do not delete the row.
5. **Failed write:** Roll back both row and audit on constraint violation, invalid value, lost CAS or audit-insert failure. No transaction contains Redis, provider calls, secret decrypt/network calls or queue publishing.
6. **Environment isolation:** All SELECT/UPDATE predicates include canonical `environment` and exact `key`; a writer cannot set one environment from another's request input; no cross-environment fallback.
7. **Version-bound encryption:** For sealed secrets, the ciphertext must have been prepared for the resulting revision before the transaction. Any CAS conflict discards that candidate; a retry produces fresh ciphertext/nonce with AAD for the newly expected revision.

The database task owns the SQL schema/transaction proof and test helpers or examples in the database repository. Authorised Admin writes, HTTP validation, live secret import, decrypt, purpose-scoped authorised remote access and UI are implemented by their owning follow-on tasks. SQL checks supplement—not replace—the Admin and service-local validators using the documented ARCH-043 shapes.

### E. Migration and retention

- Additive fresh/upgrade migration; exactly **two** new tables and any supporting CHECKs/indexes/append-only function/trigger, no existing table alteration.
- Do not seed credential values, fictional R2 buckets/endpoints or secrets; no environment-to-database import as part of migration.
- Preserve existing records in `BackgroundRuntimeConfig`, Commerce credentials, billing/tenant schemas and prior migrations.
- Rollback of consumers may leave tables/audit safely in place. No destructive down migration, mass deletion or silent reassignment of configuration ownership.

## Work Items

- [ ] Add the exact two Prisma models in schema `public`.
- [ ] Create one additive SQL migration with table definitions, indexes, CHECK constraints and database-level audit protection.
- [ ] Prove atomic create/CAS update/reset/revoke and append-one-audit semantics, including conflicts and concurrent writers.
- [ ] Validate SQL-level secret-envelope/tombstone requirements and secret audit redaction; test bypass attempts where feasible.
- [ ] Validate environment isolation, safe schema compatibility and no modifications to existing domain models.
- [ ] Complete disposable PostgreSQL fresh and upgrade rehearsals, with real Prisma client generation and validation.
- [ ] Record actual changed files, checks, worktree isolation and synchronization evidence in Completion Report; return task to Review.

## Interfaces / Contracts

- Database schema owner: this task, `ARCH-043-DATABASE-001`.
- Non-secret key/payload allowlist: the ARCH-043 schema review (published by the existing ARCH-039 Shared package).
- Existing Node-only encryption/decryption: `@modainteract/moda-interact-shared/security/credentials/node` (ARCH-039); AAD, canonical JSON-envelope mapping and purpose-specific payload validation: the ARCH-043 schema review (published by the existing ARCH-039 Shared package).
- Platform Admin's authenticated mutation API and audit attribution: `ARCH-043-ADMIN-001` / `ARCH-043-ADMIN-002`.
- No database-owned cross-service secret distribution endpoint.

## Dependencies

None. No ARCH-043 Shared implementation is required. Database-only SQL shape constraints must align with the architecture's versioned envelope; consumers validate against ARCH-043 documented shapes and reuse existing ARCH-039 crypto.

## Enables

- `ARCH-043-ADMIN-001`
- `ARCH-043-ADMIN-002`
- `ARCH-043-API-001`
- `ARCH-043-API-002`
- `ARCH-043-API-003`
- `ARCH-043-BACKGROUND-001`
- `ARCH-043-BACKGROUND-002`
- `ARCH-043-COMMERCE-001`
- `ARCH-043-COMMERCE-002`
- `ARCH-043-MCP-001`
- `ARCH-043-SHOPIFY-001`
- `ARCH-043-SHOPIFY-002`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Exactly two new models/tables; no changes to existing model definitions or migration history.
- [ ] Unique `(environment,key)` and all documented CHECK/index/append-only guards enforced by PostgreSQL.
- [ ] Non-secret settings and sealed/tombstone secret rows coexist without a generic plaintext secret write path.
- [ ] Secret audit cannot persist plaintext or replayable ciphertext, even through direct invalid SQL/Prisma writes.
- [ ] Every successful mutation atomically increments revision exactly once and appends exactly one audit; stale writes produce neither partial state nor an audit.
- [ ] Reset/revocation preserves monotonic revision and prior audit history.
- [ ] Fresh and upgrade migrations preserve existing Background, Commerce, billing and tenant data.

## Validation

- [ ] Use the database repository's declared Prisma generate/validate/migration commands, not assumed npm scripts.
- [ ] PostgreSQL migration fresh/upgrade rehearsal and schema constraints verification.
- [ ] Concurrent CAS / stale replay / reset / revoke / failed-audit rollback tests.
- [ ] Secret-envelope and SQL-audit-redaction negative tests.
- [ ] `git diff --check` and any task-specific test/lint/typecheck mandated by database repository tooling.

## Stop Condition

After Work Items, Acceptance Criteria and Validation are complete, record the Completion Report, change task status to Review, return to `moda_architect` and STOP. Do not implement Admin/Shared/consumer work or edit `_index.md` files.

## Implementation Notes

- Keep the two-table design. Do not add `PlatformProviderCredential*`, per-domain policy tables, Woo coupon columns, new migration dependencies on live service secrets or plaintext secret fallbacks.
- The SQL envelope markers are structural safety checks. Encryption/authentication and strict per-purpose JSON validation belong to the Shared runtime contract; avoid a competing database cryptography implementation.
- Do not assume migrations automatically initialise operational settings. Their initial import is a later controlled Admin/Gateway cutover.
- Use dedicated launcher-resolved task worktrees and record synchronization evidence.

## Developer Ownership Amendment

On 2026-10-17, the developer explicitly invoked `/moda_developer_create ARCH-043-DATABASE-001`, taking over execution of this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_database`, repository ownership, scope, dependencies, and acceptance criteria are unchanged. The canonical developer launcher will record the attempt claim separately.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None
