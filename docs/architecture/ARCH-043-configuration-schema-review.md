# ARCH-043 — Approved simplified database proposal

**Decision (17 October 2026, amended):** Keep exactly two generic, versioned PostgreSQL models, but allow BOTH validated non-secret settings and encrypted application secrets. Only protected `value` envelopes may contain encrypted secret material; the audit table never contains plaintext or replayable ciphertext. This is the schema and contract proposal for review, not an implementation.

## 1. Exact proposed Prisma models

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
  id              String   @id @default(cuid())
  environment     String   @db.VarChar(32)
  key             String   @db.VarChar(128)
  expectedVersion Int
  resultingVersion Int
  beforeValue     Json?
  afterValue      Json
  actorId         String   @db.VarChar(191)
  reason          String?  @db.VarChar(1000)
  createdAt       DateTime @default(now())

  @@unique([environment, key, resultingVersion])
  @@index([environment, key, createdAt])
  @@index([actorId, createdAt])
  @@schema("public")
}
```

**Implementation constraints:** The schema is intentionally not linked by an FK to `PlatformAdmin` to avoid expanding existing `PlatformAdmin` relations; the Admin writer MUST authenticate the actor and use their verified platform-admin ID. `environment` is a canonical deployment identity such as `local`, `test`, `development`, `staging`, or `production`, resolved once from trusted server configuration. No arbitrary environment strings supplied by clients; no cross-environment fallback. `key` must be on the Admin-owned allowlist. `value` is either a strict typed non-secret settings object or a validated, encrypted secret envelope for an allowlisted secret key. Never store plaintext secrets or arbitrary JSON. `updatedBy` is attribution only, not a source of authorisation.

**Database invariants:** SQL CHECK constraints enforce nonempty `environment`/`key`, positive `version`, and maximum sizes as appropriate. The unique `(environment,key)` index prevents duplicates. `PlatformConfigurationAudit` records are append-only and updates/inserts must be transactionally coupled to the corresponding CAS update. First write: expected version 0 => new row version 1; subsequent edits: expected N => N+1. Clearing a non-secret setting REPLACES its value with the explicit validated default; revoking a secret writes the strict `{ "kind":"disabled", "schemaVersion":1 }` tombstone (not a plaintext secret or deletion), increments the version and writes an audit record; it must not delete the row or reset its version. Concurrent/stale updates return a conflict without writing an audit event. The repository task implements and proves the SQL transactional contract; the Admin task provides the authorised mutator. No Redis, network or provider operation inside the DB transaction. Audit values must be safe to store: for secret rows write redacted non-sensitive metadata only (no plaintext, ciphertext, IVs, authentication tags, tokens, root keys, personal data or authentication headers).

## 2. Exact supported non-secret setting keys

These names are **proposed canonical identifiers**, not pre-existing DB rows. All shapes are closed/strict (unknown fields rejected), values are limited by the existing service code and Admin and service-local validators; runtime code owns absolute safety ceilings. No mass migration of environment values into the database is performed by Prisma.

### `woo.couponSync` — Background only

```json
{
  "dispatchBatchSize": 500,
  "refreshIntervalMinutes": 30,
  "dispatchCooldownMinutes": 5,
  "unavailableRecheckMinutes": 30,
  "staleScanMinutes": 15,
  "maxPages": 50,
  "requestTimeoutMs": 8000,
  "maxResponseBytes": 1048576,
  "maxScanDurationMs": 120000,
  "workerConcurrency": 4
}
```

| Property | Min | Max |
|---|---:|---:|
| dispatchBatchSize | 1 | 500 |
| refreshIntervalMinutes | 1 | 1440 |
| dispatchCooldownMinutes | 1 | 120 |
| unavailableRecheckMinutes | 1 | 1440 |
| staleScanMinutes | 1 | 120 |
| maxPages | 1 | 200 |
| requestTimeoutMs | 1000 | 30000 |
| maxResponseBytes | 16384 | 4194304 |
| maxScanDurationMs | 30000 | 600000 |
| workerConcurrency | 1 | 32 |

The first nine bounds are from `moda-interact-background/src/services/woo-coupon-sync-config.ts`. Worker concurrency has the proposed existing default 4 and the prior review-suggested 1..32 guard; the Background implementer must verify it against the active worker before adoption. The Background task must distinguish settings safe to refresh live from worker concurrency requiring explicit worker restart/recreation; no accidental dual queue consumer or duplicate processing.

### `merchantKnowledge.upload` — API and Shopify server-side read

```json
{
  "maxUploadBytes": 10485760,
  "maxXlsxUncompressedBytes": 52428800,
  "r2Endpoint": "https://example.invalid",
  "r2Bucket": "configured-bucket"
}
```

The numeric values above are **illustrative placeholders only**, not authorised production defaults. The real code's hard caps and format-specific limits take precedence; operator must set endpoints/buckets explicitly and both server-side consumers must validate endpoint host, HTTPS, SSRF rules and bucket syntax. Absent configuration must not initiate an R2 transfer. R2 access-key IDs, secret-access keys, signed URLs and any presigned request credentials are never stored here. Shopify is not granted access to ARCH-039 decryption keys. Where the API's hosted-signing endpoint replaces Shopify-local signing, that is a separate architecture decision.

### `speech.transcription` — Background

```json
{"provider":"groq","groqModelId":"whisper-large-v3-turbo","openaiModelId":"gpt-4o-mini-transcribe"}
```

`provider` is `groq` or `openai`; both model identifiers use the current 128-character model-ID validation. These are existing code defaults, not an automatic production switch. Provider API credentials are outside the initial listed secret purposes unless separately authorised; never insert them into non-secret `speech.transcription`.

### `support.translation` — Background, support-message flow ONLY

```json
{"provider":"openai","model":"example-model"}
```

Example only: confirm actual provider/model validation and supported values against the `MerchantMessageTranslation` flow before implementation. Do not overwrite Commerce's product/pricing translation models or `BackgroundRuntimeConfig` translation job cadence. If an existing database record is already authoritative for this identical support-message flow, read it instead and document why no `support.translation` row is needed.

### `commerce.preview` — Commerce

```json
{"deadlineMs":60000,"outputTokens":1200}
```

`deadlineMs` must be a positive integer <= `PREVIEW_SLOT_MS - 30000`; `outputTokens` must be 1..32768. Retain the existing fixed `modelSteps` and `remoteCalls` safety defaults (4 each), preview expiry and provider limits. This configuration must not change live agent behaviour.

### `admin.grafana` — Admin only

```json
{"baseUrl":null,"logsUrl":null,"metricsUrl":null,"tracesUrl":null,"platformDashboardUrl":null}
```

All fields are nullable validated HTTPS URLs (max 2048 characters, no embedded credentials/tokens). `null` means no link. No OTLP/LOKI exporter routing, service telemetry credentials or monitoring collection moves into this key.

## 3. Encrypted application-secret keys (approved extension)

These names are **proposed canonical secret purposes**, not existing rows. They share `PlatformConfiguration` with policy keys; each configured secret key stores **only** the following strict envelope shape, never the underlying plaintext structure (an explicit revoked secret may instead store the strict disabled tombstone):

```json
{
  "kind": "sealed",
  "schemaVersion": 1,
  "algorithm": "AES-256-GCM",
  "wrappingKeyId": "config-unseal-v1",
  "nonce": "base64",
  "ciphertext": "base64",
  "authTag": "base64"
}
```

The sealed plaintext payload MUST itself be validated after decryption against an exact purpose-specific shape. Bind authenticated-data (AAD) to canonical `environment`, `key`, `version` and envelope schema version. The exact UTF-8 AAD bytes are `JSON.stringify(["moda-platform-config-v1", environment, key, resultingVersion, 1])`, constructed only after strict identifier and revision validation; the writer and readers MUST test byte identity and reject tampering. Fresh random nonce on every write/re-wrap; deny unknown keys, algorithms, versions and fields; use the already published ARCH-039 `@modainteract/moda-interact-shared/security/credentials/node` `encryptCredential`/`decryptCredential` and `CredentialEnvelope`, together with the frozen canonical JSON/byte mapping and AAD convention defined in this architecture (implemented in each authorised reader/writer and byte-vector tested). Do not introduce another cipher, decryption routine or keyring parser. Rewrapping a Commerce keyring does **not** change the bytes or AAD of existing Commerce-encrypted database credentials.

| Secret purpose | Sealed plaintext fields (never displayed) | Primary consumers |
|---|---|---|
| `commerce.connectionKeys` | existing `COMMERCE_CONNECTION_KEYS_JSON` keyring, `COMMERCE_CONNECTION_ACTIVE_KEY_ID`, and command HMAC key if its current consumer requires it | Commerce, API, Background, Admin, MCP |
| `auth.admin` | `AUTH_SECRET`, existing Google OAuth client ID/secret where required | Admin |
| `auth.commerce` | `AUTH_SECRET`, existing Google OAuth client ID/secret where required | Commerce |
| `shopify.oauth` | `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET` | Shopify app, Background session-refresh consumer |
| `messaging.meta` | `META_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN` | Encrypted Admin-managed record and purpose-scoped private API-003 reader only; no Messaging integration in ARCH-043 |

**Independent unlock material is mandatory:** a deployment-held `MODA_CONFIG_UNSEAL_KEY` or managed KMS identity/key must be accessible to approved server-side decryptors. Never store this unseal key in the same database, an audit row, source, public build or browser. Rotation must support old/new wrapping keys during deliberate re-encryption, with fail-closed unknown-key handling. For a single env-key deployment, rotation must use a bounded controlled dual-key cutover before deleting the old key. Database connectivity and service identity are separate startup dependencies; encryption-at-rest using a DB-stored key alone would not protect these secrets.

**Secret validation:** all five secret-purpose keys must be covered by closed-shape checks. SQL-level check constraints should prohibit a non-redacted `afterValue`/`beforeValue` for these keys, even when application validation is bypassed; ciphertext belongs only in `PlatformConfiguration.value`.

**Editable R2 configuration:** `merchantKnowledge.upload.r2Endpoint` and `.r2Bucket` remain authorised editable fields. Storage relocation and existing/in-flight object handling are outside ARCH-043 and remain with the separately assigned tasks.

**Secret audit:** `PlatformConfigurationAudit.beforeValue`/`afterValue` for secret keys contain only `{ "redacted": true, "configured": boolean }` and optionally safe revision/key-status metadata. No ciphertext, recoverable fingerprints, root keys, OAuth tokens or authentication headers. Secret reads never return raw `value` to browser/admin JSON or ordinary configuration APIs; Admin may display configured/unconfigured, last rotation time and version only. Updates are write-only and separately authorised.

**Bootstrap and outage:** initial import must occur BEFORE switching participating login/OAuth providers to DB-only retrieval. Messaging webhook ingress is not a participating consumer and retains current environment verification credentials. Resolve required authentication/library configuration safely before a server starts accepting protected requests, including Shopify's current synchronous `shopifyApp({...})` module initialisation. Messaging has no Prisma/PostgreSQL client in the inspected snapshot and **has no ARCH-043 integration task**. Its existing `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN` environment-based ingress verification stays in use. A private API-003 reader may be implemented as an independent, purpose-scoped platform capability, but no Messaging caller or secret-cutover is authorised. No generic public secret-fetch endpoint or caching is introduced. Do not log secrets. Session cookie / OAuth / HMAC key rotation must be tested for expected compatibility and bounded old-key overlap when supported; do not assume frameworks can accept multiple verification keys.

## 4. Runtime and editor behaviour

- **Bootstrap:** `DATABASE_URL`, deployment identity, Redis/Render networking, `OTEL_*` and one independent configuration-unseal root/KMS identity remain external. Application OAuth/session/webhook secrets and the Commerce credential keyring are intended to move into encrypted database rows after a verified bootstrap/cutover. WordPress plugin bootstrap URLs stay in WordPress.
- **Read:** each service retrieves and validates its required PostgreSQL configuration afresh for each relevant operation, with no cross-operation cache or stale snapshot fallback. Never cross environment/tenant scopes. An absent row uses a safe, code-defined default only where the service already has one and the feature can operate safely; otherwise fail closed. No plaintext-secret-in-JSON fallback. An encrypted record must never be treated as an ordinary non-secret policy.
- **Write:** only authorised platform administrators can modify allowlisted keys; authorise on the server, prohibit plaintext secrets in ordinary policy keys, encrypt approved write-only secret inputs before persistence, enforce environment-scoped CAS/audit transactions, and prevent duplicate submit.
- **Activation/cutover:** backfill non-secret values from verified deployment configuration through Admin/import with audit. Remove old environment reads only when the matching consumer has working database-only tests. Preserve a safe transition plan; no implicit silent env fallback after cutover.
- **Rollback:** additive schema can remain in place if a consumer rolls back. Gateway removes only proven-unused declarations after consumer acceptance. Do not delete historic audit.

## 5. Out of scope

Do not create `PlatformProviderCredential*`, nine policy tables, new Woo integer columns in `BackgroundRuntimeConfig`, duplicate cryptographic codecs, or a database-stored configuration-unseal root. Do not rewrite any existing `Commerce*` encrypted-credential rows or AAD bytes, `BackgroundRuntimeConfig`, `PlatformBillingPolicy`, `ShopFeaturePreference`, `ShopSettings` or prior migrations. Provider credentials outside the explicit list below remain under their existing domain owners.
